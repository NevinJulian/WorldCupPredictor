"""Match-outcome and goals models.

Two models live here:

    EloLogisticModel — the **baseline** the whole project is measured against (PLAN.md §7):
    a multinomial logistic regression on just `elo_diff` and the neutral-venue flag. It is
    deliberately minimal — the point of a baseline is to be the bar a fancier model must
    clear, not to be a contender — so it gets exactly two inputs.

    DixonColesModel — the **statistical goals model** (PLAN.md §5): per-team attack/defence
    plus a home term, fit by time-decay-weighted MLE with the Dixon-Coles low-score
    correlation correction. It produces a full scoreline distribution, so it both derives
    H/D/A probabilities AND satisfies the simulator's `sample_scoreline` interface.

    GBMOutcomeModel — the **ML outcome classifier** (PLAN.md §5): gradient-boosted multiclass
    H/D/A on the full feature_columns() set, isotonic-calibrated on a time-based inner split.
    The first model aimed squarely at beating the Elo bar.

    EnsembleModel — blends the GBM outcome probabilities with Dixon-Coles' H/D/A under a single
    mixing weight chosen on a time-based inner validation window (never the test folds). Two
    models that fail differently; the blend is the candidate to clear the bar with margin.

`walk_forward_*` helpers fit and score each model the only way we evaluate anything here —
time-based, training strictly before each World Cup (see datasets.walk_forward_tournaments)
— returning the per-tournament normalized RPS.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.special import gammaln
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression

from . import datasets, metrics
from .features import feature_columns

# The baseline's entire feature set. Order matters only for the design matrix layout.
BASELINE_FEATURES: tuple[str, ...] = ("elo_diff", "neutral")
DEFAULT_WC_YEARS: tuple[int, ...] = (2010, 2014, 2018, 2022)


class EloLogisticModel:
    """Multinomial logistic P(H/D/A) from `elo_diff` + `neutral`. The bar to beat.

    Predicts a full H/D/A distribution (columns ordered 0=H, 1=D, 2=A, matching
    datasets.RESULT_TO_INT). This is an *outcome* model; it does not implement the
    simulator's `sample_scoreline` goals interface.
    """

    def __init__(self, max_iter: int = 2000):
        self.max_iter = max_iter
        self.clf = LogisticRegression(max_iter=max_iter)

    def _design(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build the two-column design matrix. NaN elo_diff -> 0 (as in the baseline notebook)."""
        return pd.DataFrame({
            "elo_diff": pd.to_numeric(df["elo_diff"], errors="coerce").fillna(0.0).astype(float).to_numpy(),
            "neutral": df["neutral"].astype(int).to_numpy(),
        })

    def fit(self, df: pd.DataFrame) -> "EloLogisticModel":
        X = self._design(df)
        y = df["result"].map(datasets.RESULT_TO_INT).astype(int)
        self.clf.fit(X, y)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Return an (n, 3) array of P(H/D/A), columns always in H,D,A order.

        Re-indexes the classifier's columns into fixed 0,1,2 positions so the output is
        well-defined even if a class was absent from a (tiny) training fold.
        """
        proba = self.clf.predict_proba(self._design(df))
        full = np.zeros((len(df), 3), dtype=float)
        for j, c in enumerate(self.clf.classes_):
            full[:, int(c)] = proba[:, j]
        return full


def walk_forward_elo_baseline(
    df: pd.DataFrame, years: tuple[int, ...] = DEFAULT_WC_YEARS
) -> list[dict]:
    """Fit the Elo-logistic baseline per World Cup and score normalized RPS.

    For each year, train on every match strictly before that tournament and test on its
    finals (datasets.walk_forward_tournaments enforces the time-based split — never random).
    Returns one dict per tournament: ``{"year", "n", "rps"}`` with RPS in the standard
    normalized convention (metrics.rps).
    """
    rows: list[dict] = []
    for year, train, test in datasets.walk_forward_tournaments(df, years):
        model = EloLogisticModel().fit(train)
        proba = model.predict_proba(test)
        y_true = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        rows.append({"year": year, "n": int(len(test)), "rps": metrics.rps(proba, y_true)})
    return rows


# --------------------------------------------------------------------------- #
# Dixon-Coles goals model
# --------------------------------------------------------------------------- #
class DixonColesModel:
    """Time-decay-weighted Dixon-Coles bivariate-Poisson goals model.

    For a match (home h, away a) the two scoring rates are, in log space::

        log lambda_home = base + home_adv * is_home + attack[h] - defence[a]
        log mu_away      = base               +      attack[a] - defence[h]

    where `attack` (higher = scores more) and `defence` (higher = concedes fewer) are per
    team, `base` sets the overall goal level and `home_adv` the venue effect (applied only
    at non-neutral venues). Scores are bivariate-Poisson with the Dixon-Coles low-score
    correlation correction `tau` on the (0,0)/(0,1)/(1,0)/(1,1) cells (parameter `rho`),
    which nudges the very common 0-0 / 1-1 draws that independent Poissons under-predict.

    **Fitting** maximises a recency-weighted likelihood: match `m` gets weight
    ``exp(-ln2 * age_days / half_life_days)`` relative to the most recent training match, so
    form half a half-life old counts for half (the default half-life is ~5 years — chosen on the
    broadened competitive-internationals backtest, reports/eval_and_decay.md). An optional
    ``comp_weights`` multiplier (off by default) scales that weight by competition tier so
    friendlies can count less than competitive internationals. Strengths (base,
    home_adv, attack, defence) are
    fit first by weighted Poisson MLE with an L2 ridge; `rho` is then fit by a 1-D MLE with
    the strengths held fixed (the ridge-free, near-identical Dixon-Coles factorisation — the
    correction barely moves the strength estimates but materially improves low scores).

    **Cold start** is handled by that same ridge: it shrinks every team toward 0 (= the
    league-average prior in this centred parameterisation), so teams with little history are
    pulled to average, and a team never seen in training falls back to attack = defence = 0
    — a valid, average-strength distribution rather than a blow-up. This matters for sparse /
    debutant 2026 sides (Curaçao, Cape Verde, …).

    Leakage-safe by construction: `fit` consumes only the rows handed to it and the decay
    reference is the training set's own last date; nothing peeks past the cutoff.
    """

    # Shootout/seeding scale for `team_strength` (see team_strength). In log-goal units a
    # strength difference Δ is the log goal-rate supremacy, so ln 10 makes the simulator's
    # base-10 logistic 1/(1+10**(-Δ/scale)) equal the natural logistic of that supremacy.
    strength_scale: float = math.log(10.0)

    def __init__(
        self,
        half_life_days: float = 1825.0,  # ~5 years (reports/eval_and_decay.md)
        reg: float = 5.0,                # ridge strength -> cold-start shrinkage
        max_goals: int = 10,
        rho_bounds: tuple[float, float] = (-0.2, 0.2),
        max_iter: int = 1000,
        overdispersion: float = 0.0,
        comp_weights: dict[str, float] | None = None,
    ):
        self.half_life_days = half_life_days
        self.reg = reg
        self.max_goals = max_goals
        self.rho_bounds = rho_bounds
        self.max_iter = max_iter
        # Mean-preserving over-dispersion of the per-team goal counts (Step 4 lever). 0 == the
        # eloratings/Poisson default (so all existing behaviour is unchanged). With a > 0 each
        # marginal is a negative-binomial at the SAME mean lambda but variance lambda*(1+a*lambda),
        # fattening the high-score tail; the fit (attack/defence/rho) is untouched, only the output
        # matrix shape changes. Reweighting then restores the target W/D/L (see scripts/overdispersion_gate.py).
        self.overdispersion = float(overdispersion)
        # Optional per-match COMPETITION weight (off by default), multiplied into the recency
        # weight in the likelihood. A dict {tier -> multiplier} keyed by datasets.competition_class
        # ("competitive"/"friendly"/"other"); any tier absent from the dict defaults to 1.0. So
        # e.g. {"friendly": 0.4} makes a friendly count 0.4x a competitive match of the same age,
        # letting the goals-model MLE lean on qualifiers/continental/WC over noisy friendlies.
        # Depends only on the tournament label + date, never the outcome -> leakage-free. None (the
        # default) -> every match weight 1.0, i.e. recency-only, exactly the previous behaviour.
        self.comp_weights = dict(comp_weights) if comp_weights else None
        # Fitted state (populated by .fit)
        self.base_ = 0.0
        self.home_adv_ = 0.0
        self.rho = 0.0
        self.attack_: dict[str, float] = {}
        self.defence_: dict[str, float] = {}

    # -- fitting ----------------------------------------------------------- #
    def fit(self, df: pd.DataFrame, ref_date: "pd.Timestamp | None" = None) -> "DixonColesModel":
        d = df.dropna(subset=["home_score", "away_score"]).copy()
        if d.empty:
            raise ValueError("DixonColesModel.fit got no played matches.")

        teams = sorted(set(d["home_team"]) | set(d["away_team"]))
        index = {t: i for i, t in enumerate(teams)}
        n = len(teams)
        hidx = d["home_team"].map(index).to_numpy()
        aidx = d["away_team"].map(index).to_numpy()
        hs = d["home_score"].to_numpy(dtype=float)
        as_ = d["away_score"].to_numpy(dtype=float)
        home_flag = (~d["neutral"].astype(bool).to_numpy()).astype(float)

        # Recency weights relative to the training cutoff (as-of: training dates only).
        ref = pd.Timestamp(ref_date) if ref_date is not None else d["date"].max()
        age_days = np.clip((ref - d["date"]).dt.days.to_numpy(dtype=float), 0.0, None)
        xi = np.log(2.0) / self.half_life_days
        w = np.exp(-xi * age_days)

        # Optional competition weight: down-weight noisier tiers (e.g. friendlies) relative to
        # competitive internationals. Keyed only on the tournament label (datasets.competition_class)
        # -> leakage-free; applied to BOTH fit stages below because they share this `w`.
        if self.comp_weights:
            tiers = datasets.competition_class(d)
            cw = tiers.map(lambda t: self.comp_weights.get(t, 1.0)).to_numpy(dtype=float)
            w = w * cw

        # --- Stage 1: strengths via ridge-penalised weighted Poisson MLE -----
        def nll_and_grad(theta: np.ndarray) -> tuple[float, np.ndarray]:
            base, adv = theta[0], theta[1]
            att = theta[2:2 + n]
            dfc = theta[2 + n:2 + 2 * n]
            eta_l = base + adv * home_flag + att[hidx] - dfc[aidx]
            eta_m = base + att[aidx] - dfc[hidx]
            lam, mu = np.exp(eta_l), np.exp(eta_m)
            nll = float(np.sum(w * (lam - hs * eta_l)) + np.sum(w * (mu - as_ * eta_m)))
            nll += self.reg * (float(att @ att) + float(dfc @ dfc))
            r_l, r_m = w * (lam - hs), w * (mu - as_)   # dNLL/d-eta
            g_base = r_l.sum() + r_m.sum()
            g_adv = float(r_l @ home_flag)
            g_att = np.bincount(hidx, r_l, n) + np.bincount(aidx, r_m, n) + 2 * self.reg * att
            g_def = -(np.bincount(aidx, r_l, n) + np.bincount(hidx, r_m, n)) + 2 * self.reg * dfc
            grad = np.concatenate(([g_base], [g_adv], g_att, g_def))
            return nll, grad

        avg_goals = np.average(np.concatenate([hs, as_]), weights=np.concatenate([w, w]))
        theta0 = np.concatenate(([np.log(max(avg_goals, 0.1))], [0.25], np.zeros(2 * n)))
        res = optimize.minimize(
            nll_and_grad, theta0, jac=True, method="L-BFGS-B",
            options={"maxiter": self.max_iter},
        )
        theta = res.x
        self.base_, self.home_adv_ = float(theta[0]), float(theta[1])
        att, dfc = theta[2:2 + n], theta[2 + n:2 + 2 * n]
        self.attack_ = {t: float(att[index[t]]) for t in teams}
        self.defence_ = {t: float(dfc[index[t]]) for t in teams}

        # --- Stage 2: rho via 1-D MLE with the strengths fixed ---------------
        lam = np.exp(theta[0] + theta[1] * home_flag + att[hidx] - dfc[aidx])
        mu = np.exp(theta[0] + att[aidx] - dfc[hidx])
        m00 = (hs == 0) & (as_ == 0)
        m01 = (hs == 0) & (as_ == 1)
        m10 = (hs == 1) & (as_ == 0)
        m11 = (hs == 1) & (as_ == 1)

        def nll_rho(rho: float) -> float:
            tau = np.ones_like(lam)
            tau[m00] = 1.0 - lam[m00] * mu[m00] * rho
            tau[m01] = 1.0 + lam[m01] * rho
            tau[m10] = 1.0 + mu[m10] * rho
            tau[m11] = 1.0 - rho
            return float(-np.sum(w * np.log(np.clip(tau, 1e-12, None))))

        rho_res = optimize.minimize_scalar(nll_rho, bounds=self.rho_bounds, method="bounded")
        self.rho = float(rho_res.x) if rho_res.success else 0.0
        return self

    # -- prediction -------------------------------------------------------- #
    def _pois_pmf(self, lam: float) -> np.ndarray:
        k = np.arange(self.max_goals + 1)
        return np.exp(-lam + k * np.log(lam) - gammaln(k + 1))

    def _count_pmf(self, lam: float) -> np.ndarray:
        """Marginal goal-count pmf over 0..max_goals at mean ``lam``.

        ``overdispersion == 0`` returns the Poisson pmf (the default — identical to ``_pois_pmf``).
        ``overdispersion = a > 0`` returns a negative-binomial with the SAME mean ``lam`` and
        variance ``lam*(1 + a*lam)`` (Poisson-Gamma; ``r = 1/a``, ``p = 1/(1 + a*lam)``), which
        fattens the high-score tail without moving the mean. ``a -> 0`` recovers Poisson.
        """
        if self.overdispersion <= 0.0:
            return self._pois_pmf(lam)
        k = np.arange(self.max_goals + 1)
        r = 1.0 / self.overdispersion
        p = r / (r + lam)                       # mean = r*(1-p)/p = lam
        return np.exp(gammaln(k + r) - gammaln(r) - gammaln(k + 1)
                      + r * np.log(p) + k * np.log1p(-p))

    def _lambdas(self, home: str, away: str, neutral: bool = True) -> tuple[float, float]:
        ah, dh = self.attack_.get(home, 0.0), self.defence_.get(home, 0.0)
        aa, da = self.attack_.get(away, 0.0), self.defence_.get(away, 0.0)
        adv = 0.0 if neutral else self.home_adv_
        lam = np.exp(self.base_ + adv + ah - da)
        mu = np.exp(self.base_ + aa - dh)
        return float(lam), float(mu)

    def team_strength(self, team: str) -> float:
        """Net strength vs a league-average team: ``attack + defence`` (0 = average).

        The match-model interface the simulator uses for knockout seeding and the shootout
        tiebreak. ``team_strength(a) - team_strength(b)`` is exactly the log goal-rate
        supremacy of *a* over *b* on neutral ground (see `_lambdas`), so paired with
        ``strength_scale = ln 10`` the simulator's base-10 logistic recovers the natural
        logistic of that supremacy. An unseen team falls back to 0 (league average).
        """
        return self.attack_.get(team, 0.0) + self.defence_.get(team, 0.0)

    def score_matrix(self, home: str, away: str, neutral: bool = True) -> np.ndarray:
        """(max_goals+1) x (max_goals+1) probability matrix P[x, y] = P(home x, away y)."""
        lam, mu = self._lambdas(home, away, neutral)
        P = np.outer(self._count_pmf(lam), self._count_pmf(mu))
        rho = self.rho
        P[0, 0] *= 1.0 - lam * mu * rho
        P[0, 1] *= 1.0 + lam * rho
        P[1, 0] *= 1.0 + mu * rho
        P[1, 1] *= 1.0 - rho
        np.clip(P, 0.0, None, out=P)
        total = P.sum()
        if total <= 0:  # degenerate rho guard -> fall back to independent counts
            P = np.outer(self._count_pmf(lam), self._count_pmf(mu))
            total = P.sum()
        return P / total

    def outcome_probs(self, home: str, away: str, neutral: bool = True) -> tuple[float, float, float]:
        """(P_home, P_draw, P_away) from the scoreline matrix."""
        P = self.score_matrix(home, away, neutral)
        return float(np.tril(P, -1).sum()), float(np.trace(P)), float(np.triu(P, 1).sum())

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Return an (n, 3) array of P(H/D/A), columns in H,D,A order (matches RESULT_TO_INT)."""
        neutral = df["neutral"].astype(bool).to_numpy()
        out = np.array([
            self.outcome_probs(h, a, bool(neu))
            for h, a, neu in zip(df["home_team"], df["away_team"], neutral)
        ], dtype=float)
        return out / out.sum(axis=1, keepdims=True)

    def sample_scoreline(self, home, away, neutral=True, rng=None) -> tuple[int, int]:
        """Draw a (home_goals, away_goals) scoreline — the simulator's match-model interface."""
        rng = rng or np.random.default_rng()
        P = self.score_matrix(home, away, neutral)
        cdf = np.cumsum(P.ravel())
        idx = int(np.searchsorted(cdf, rng.random() * cdf[-1]))
        ncols = P.shape[1]
        return idx // ncols, idx % ncols


def walk_forward_dixon_coles(
    df: pd.DataFrame, years: tuple[int, ...] = DEFAULT_WC_YEARS, **model_kwargs
) -> list[dict]:
    """Fit the Dixon-Coles model per World Cup (train strictly before) and score normalized RPS.

    Mirrors walk_forward_elo_baseline: time-based via datasets.walk_forward_tournaments,
    H/D/A derived from the DC scoreline matrix, scored with metrics.rps. Returns one dict per
    tournament: ``{"year", "n", "rps"}``.
    """
    rows: list[dict] = []
    for year, train, test in datasets.walk_forward_tournaments(df, years):
        model = DixonColesModel(**model_kwargs).fit(train)
        proba = model.predict_proba(test)
        y_true = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        rows.append({"year": year, "n": int(len(test)), "rps": metrics.rps(proba, y_true)})
    return rows


# --------------------------------------------------------------------------- #
# Broad block backtest — the larger, lower-variance evaluator
# --------------------------------------------------------------------------- #
# The WC-finals walk-forward above is the product-relevance metric, but ~256 matches is too
# noisy to detect small modelling changes. This refits a model at yearly checkpoints and
# predicts the whole next year from prior data only, then pools the predictions so they can be
# sliced by competitiveness tier (datasets.competition_class). Far more matches -> far lower
# variance, so a real improvement on competitive internationals is actually visible.
def walk_forward_block_predictions(
    df: pd.DataFrame, model_factory, years: range, *, min_train: int = 2000
) -> pd.DataFrame:
    """Pooled, as-of H/D/A predictions from an expanding-window yearly-refit block backtest.

    ``model_factory()`` returns a fresh, unfitted model exposing ``.fit(train_df)`` and
    ``.predict_proba(df) -> (n, 3)`` in H,D,A order. For each yearly checkpoint
    (datasets.walk_forward_blocks: train strictly before the year, block = that year) a fresh
    model is fit and used to predict the block; every played match in the span is therefore
    predicted exactly once, from its own past. Returns the concatenated block rows with added
    ``pH``/``pD``/``pA`` columns and a ``comp_class`` tier label.
    """
    frames: list[pd.DataFrame] = []
    for _year, train, block in datasets.walk_forward_blocks(df, years, min_train=min_train):
        proba = model_factory().fit(train).predict_proba(block)
        b = block.copy()
        b[["pH", "pD", "pA"]] = proba
        frames.append(b)
    if not frames:
        raise ValueError("walk_forward_block_predictions produced no folds (check years/min_train).")
    pooled = pd.concat(frames, ignore_index=True)
    pooled["comp_class"] = datasets.competition_class(pooled)
    return pooled


def block_rps_by_class(pooled: pd.DataFrame) -> dict:
    """Normalized RPS over the pooled block predictions, overall and per competitiveness tier.

    Consumes the frame from `walk_forward_block_predictions`. Returns
    ``{"all": {...}, "competitive": {...}, "friendly": {...}, "other": {...}}`` with each value
    ``{"rps", "n"}`` (a tier with no matches is omitted). 'competitive' is metric (a), 'all' is
    metric (b); the WC-finals-only metric (c) stays the existing walk_forward_* helper.
    """
    P = pooled[["pH", "pD", "pA"]].to_numpy(dtype=float)
    y = pooled["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
    out = {"all": {"rps": metrics.rps(P, y), "n": int(len(y))}}
    cls = pooled["comp_class"].to_numpy()
    for tier in ("competitive", "friendly", "other"):
        mask = cls == tier
        if mask.any():
            out[tier] = {"rps": metrics.rps(P[mask], y[mask]), "n": int(mask.sum())}
    return out


# --------------------------------------------------------------------------- #
# Gradient-boosted outcome model
# --------------------------------------------------------------------------- #
# Context / fatigue / host columns are kept in the pipeline for the 2026 layer but excluded
# from the model inputs: `is_host` is constant-0 across history (hosts default to empty when
# the historical table is built), and rest/congestion add noise more than signal here.
_GBM_DROP_KEYS: tuple[str, ...] = ("rest_days", "matches_30d", "is_host")


def gbm_feature_columns(df: pd.DataFrame) -> list[str]:
    """The model-input columns for the GBM: the full feature set minus rest/context/host.

    Starts from features.feature_columns(df) (the leakage gate — drops targets, identifiers
    and object columns) and keeps the absolute home_*/away_*, *_diff and 5/10-match form
    windows, i.e. NOT a diff-only subset.
    """
    return [c for c in feature_columns(df) if not any(k in c for k in _GBM_DROP_KEYS)]


class GBMOutcomeModel:
    """Gradient-boosted multiclass H/D/A model on the full feature set, isotonic-calibrated.

    Uses HistGradientBoostingClassifier — it handles NaNs natively, which matters because the
    rank features are ~45% NaN before 1992 and rolling form is NaN for a team's first matches;
    no imputation (hence no imputation-leakage) is needed.

    Probabilities are isotonic-calibrated on a **time-based inner split**: the booster trains
    on the older ``1 - calib_fraction`` of the training window and the per-class isotonic
    calibrators are fit on the most recent ``calib_fraction`` (held out, but still strictly
    before the test tournament — no leakage). The booster is frozen before calibration so the
    calibrator never refits it.

    Feature inputs are gbm_feature_columns(): the full feature_columns() set (absolute
    home_*/away_*, *_diff, 5/10-match form windows) minus rest/context/host.
    """

    def __init__(
        self,
        calib_fraction: float = 0.2,
        learning_rate: float = 0.05,
        max_iter: int = 600,
        max_leaf_nodes: int = 15,
        min_samples_leaf: int = 80,
        l2_regularization: float = 1.0,
        random_state: int = 0,
        **hgb_kwargs,
    ):
        self.calib_fraction = calib_fraction
        self.random_state = random_state
        self.hgb_params = dict(
            learning_rate=learning_rate, max_iter=max_iter, max_leaf_nodes=max_leaf_nodes,
            min_samples_leaf=min_samples_leaf, l2_regularization=l2_regularization,
            random_state=random_state, **hgb_kwargs,
        )
        self.feature_cols_: list[str] = []
        self.calibrated_: "CalibratedClassifierCV | None" = None

    def fit(self, df: pd.DataFrame) -> "GBMOutcomeModel":
        d = df.sort_values("date", kind="stable").reset_index(drop=True)
        self.feature_cols_ = gbm_feature_columns(d)
        X = d[self.feature_cols_].to_numpy(dtype=float)
        y = d["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()

        # Time-based inner split: oldest rows train the booster, newest calibrate it.
        cut = min(max(int(round(len(d) * (1.0 - self.calib_fraction))), 1), len(d) - 1)
        base = HistGradientBoostingClassifier(**self.hgb_params)
        base.fit(X[:cut], y[:cut])
        self.calibrated_ = CalibratedClassifierCV(
            FrozenEstimator(base), method="isotonic"
        ).fit(X[cut:], y[cut:])
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Return an (n, 3) array of P(H/D/A), columns in H,D,A order (matches RESULT_TO_INT)."""
        if self.calibrated_ is None:
            raise RuntimeError("GBMOutcomeModel is not fitted.")
        X = df[self.feature_cols_].to_numpy(dtype=float)
        proba = self.calibrated_.predict_proba(X)
        full = np.zeros((len(df), 3), dtype=float)
        for j, c in enumerate(self.calibrated_.classes_):
            full[:, int(c)] = proba[:, j]
        s = full.sum(axis=1, keepdims=True)
        return np.divide(full, s, out=np.full_like(full, 1.0 / 3.0), where=s > 0)


def walk_forward_gbm_outcome(
    df: pd.DataFrame, years: tuple[int, ...] = DEFAULT_WC_YEARS, **model_kwargs
) -> list[dict]:
    """Fit the GBM outcome model per World Cup (train strictly before) and score normalized RPS.

    Mirrors the other walk_forward_* helpers: time-based via datasets.walk_forward_tournaments,
    scored with metrics.rps. Returns one dict per tournament: ``{"year", "n", "rps"}``.
    """
    rows: list[dict] = []
    for year, train, test in datasets.walk_forward_tournaments(df, years):
        model = GBMOutcomeModel(**model_kwargs).fit(train)
        proba = model.predict_proba(test)
        y_true = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        rows.append({"year": year, "n": int(len(test)), "rps": metrics.rps(proba, y_true)})
    return rows


# --------------------------------------------------------------------------- #
# Ensemble (Dixon-Coles + GBM outcome)
# --------------------------------------------------------------------------- #
def _inner_time_split(df: pd.DataFrame, val_fraction: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a frame into (older inner-train, newer inner-val) by date — time-ordered.

    The validation slice is the most recent `val_fraction` of rows; every inner-train date is
    <= every inner-val date. Used to choose the ensemble weight without touching test data.
    """
    d = df.sort_values("date", kind="stable").reset_index(drop=True)
    cut = int(round(len(d) * (1.0 - val_fraction)))
    return d.iloc[:cut], d.iloc[cut:]


class EnsembleModel:
    """Blend GBM-outcome and Dixon-Coles H/D/A probabilities: ``w·p_gbm + (1-w)·p_dc``.

    The two components fail differently — the GBM reads the full feature table, Dixon-Coles
    reads the goal-scoring structure — so a convex blend is a cheap, better-calibrated win.

    **The mixing weight is chosen WITHOUT touching the evaluation folds.** `fit` carves a
    time-based inner validation window off the *end* of the training set (the most recent
    ``inner_val_fraction``, still strictly before the test tournament): both components are fit
    on the older inner-train slice, predict the held-out inner-val slice, and ``w`` is the grid
    value minimising inner-val RPS. Only then are the components **refit on the full training
    window** with that ``w`` frozen. Tuning the blend on the 2010-2022 test WCs would be
    leakage; this never does.

    Exposes the fitted components (`gbm_`, `dc_`) and `weight_` so an evaluator can read off the
    individual model probabilities (e.g. for a paired bootstrap) without refitting.
    """

    def __init__(
        self,
        inner_val_fraction: float = 0.2,
        weight_grid: "np.ndarray | None" = None,
        gbm_kwargs: "dict | None" = None,
        dc_kwargs: "dict | None" = None,
    ):
        self.inner_val_fraction = inner_val_fraction
        self.weight_grid = np.linspace(0.0, 1.0, 101) if weight_grid is None else np.asarray(weight_grid)
        self.gbm_kwargs = dict(gbm_kwargs or {})
        self.dc_kwargs = dict(dc_kwargs or {})
        self.weight_ = 0.5            # weight on the GBM component
        self.inner_val_rps_: float | None = None
        self.gbm_: "GBMOutcomeModel | None" = None
        self.dc_: "DixonColesModel | None" = None

    def _select_weight(self, df: pd.DataFrame) -> float:
        """Pick w on a time-based inner-val window; fall back to 0.5 if the window is too small."""
        inner_train, inner_val = _inner_time_split(df, self.inner_val_fraction)
        y_val = inner_val["result"].map(datasets.RESULT_TO_INT)
        # Need a usable inner-val window with all three outcomes to score RPS meaningfully.
        if len(inner_train) < 20 or len(inner_val) < 10 or y_val.nunique() < 3:
            self.inner_val_rps_ = None
            return 0.5
        pg = GBMOutcomeModel(**self.gbm_kwargs).fit(inner_train).predict_proba(inner_val)
        pd_ = DixonColesModel(**self.dc_kwargs).fit(inner_train).predict_proba(inner_val)
        y = y_val.astype(int).to_numpy()
        scores = [metrics.rps(w * pg + (1.0 - w) * pd_, y) for w in self.weight_grid]
        best = int(np.argmin(scores))
        self.inner_val_rps_ = float(scores[best])
        return float(self.weight_grid[best])

    def fit(self, df: pd.DataFrame) -> "EnsembleModel":
        self.weight_ = self._select_weight(df)              # inner-val only, no test data
        self.gbm_ = GBMOutcomeModel(**self.gbm_kwargs).fit(df)   # refit components on full train
        self.dc_ = DixonColesModel(**self.dc_kwargs).fit(df)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self.gbm_ is None or self.dc_ is None:
            raise RuntimeError("EnsembleModel is not fitted.")
        p = self.weight_ * self.gbm_.predict_proba(df) + (1.0 - self.weight_) * self.dc_.predict_proba(df)
        return p / p.sum(axis=1, keepdims=True)


def walk_forward_ensemble(
    df: pd.DataFrame, years: tuple[int, ...] = DEFAULT_WC_YEARS, **ensemble_kwargs
) -> list[dict]:
    """Fit the ensemble per World Cup (train strictly before) and score normalized RPS.

    Time-based via datasets.walk_forward_tournaments; the mixing weight is chosen on each
    fold's inner-val window inside `EnsembleModel.fit`. Returns one dict per tournament:
    ``{"year", "n", "rps", "weight"}``.
    """
    rows: list[dict] = []
    for year, train, test in datasets.walk_forward_tournaments(df, years):
        model = EnsembleModel(**ensemble_kwargs).fit(train)
        proba = model.predict_proba(test)
        y_true = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        rows.append({"year": year, "n": int(len(test)),
                     "rps": metrics.rps(proba, y_true), "weight": model.weight_})
    return rows


# --------------------------------------------------------------------------- #
# Confederation calibration
# --------------------------------------------------------------------------- #
_WIN_SHARE = {"H": (1.0, 0.0), "D": (0.5, 0.5), "A": (0.0, 1.0)}   # result -> (home, away) share


class ConfederationCalibrator:
    """A per-confederation outcome offset estimated from inter-confederation matches.

    Cross-confederation strength is anchored only by the (sparse) games between confederations,
    and the models systematically mis-rate some confederations there (the WC backtest shows AFC /
    CONCACAF over-predicted, CONMEBOL / UEFA under-predicted — same shape for the Elo baseline and
    the ensemble). This learns a small, shrinkage-regularised offset per confederation and applies
    it as a win/loss logit tilt on any model's H/D/A — narrowing the calibration gap and (on the
    backtest) improving RPS.

    **Leakage-safe.** `fit` consumes only the rows handed to it: it time-splits them, fits an
    internal Elo-logistic detector on the older slice, and estimates each confederation's mean
    ``actual - predicted`` win-share on the newer (held-out) slice — out-of-sample, so the residual
    reflects a real bias rather than in-sample fit. Per WC fold, pass the pre-tournament training
    set only; nothing peeks at the test data.

    The offset is the shrunk mean ``sum_resid / (count + shrinkage)`` (small confederations are
    pulled toward 0); only confederations with at least ``min_matches`` inter-confederation games
    get a non-zero offset. The tilt magnitude is ``sensitivity`` (Elo-logit units per win-share
    point; the default ~4 is the logistic slope ``1/(p(1-p))`` at a typical win probability).
    """

    def __init__(self, shrinkage: float = 150.0, sensitivity: float = 4.0,
                 cal_fraction: float = 0.3, min_matches: int = 30):
        self.shrinkage = shrinkage
        self.sensitivity = sensitivity
        self.cal_fraction = cal_fraction
        self.min_matches = min_matches
        self.offsets_: dict[str, float] = {}

    def fit(self, df: pd.DataFrame) -> "ConfederationCalibrator":
        d = df.sort_values("date", kind="stable")
        cut = int(round(len(d) * (1.0 - self.cal_fraction)))
        older, hold = d.iloc[:cut], d.iloc[cut:]
        if len(older) < 50 or len(hold) < self.min_matches:
            self.offsets_ = {}                     # too little history -> no adjustment
            return self
        proba = EloLogisticModel().fit(older).predict_proba(hold)   # out-of-sample detector
        self.offsets_ = self._estimate(hold, proba)
        return self

    def _estimate(self, df: pd.DataFrame, proba: np.ndarray) -> dict[str, float]:
        hc = df["home_confed"].to_numpy()
        ac = df["away_confed"].to_numpy()
        res = df["result"].to_numpy()
        sums: dict[str, float] = defaultdict(float)
        counts: dict[str, int] = defaultdict(int)
        for i in range(len(df)):
            if pd.isna(hc[i]) or pd.isna(ac[i]) or hc[i] == ac[i] or res[i] not in _WIN_SHARE:
                continue
            pH, pD, pA = proba[i]
            oh, oa = _WIN_SHARE[res[i]]
            sums[hc[i]] += oh - (pH + 0.5 * pD)
            counts[hc[i]] += 1
            sums[ac[i]] += oa - (pA + 0.5 * pD)
            counts[ac[i]] += 1
        return {c: sums[c] / (counts[c] + self.shrinkage)
                for c in sums if counts[c] >= self.min_matches}

    def adjust(self, proba: np.ndarray, home_confed, away_confed) -> np.ndarray:
        """Tilt each H/D/A row by ``sensitivity * (offset[home_confed] - offset[away_confed])``.

        Non-draw mass is shifted between home and away (the draw probability is preserved), then
        the row is renormalised. Rows whose confederations have no offset are returned unchanged.
        """
        out = np.array(proba, dtype=float).copy()
        hc = np.asarray(home_confed)
        ac = np.asarray(away_confed)
        for i in range(len(out)):
            delta = self.sensitivity * (self.offsets_.get(hc[i], 0.0) - self.offsets_.get(ac[i], 0.0))
            if delta == 0.0:
                continue
            pH, pD, pA = out[i]
            nd = pH + pA
            if nd <= 0:
                continue
            w = 1.0 / (1.0 + np.exp(-(np.log(max(pH, 1e-9) / max(pA, 1e-9)) + delta)))
            out[i] = [nd * w, pD, nd * (1.0 - w)]
        s = out.sum(axis=1, keepdims=True)
        return np.divide(out, s, out=np.full_like(out, 1.0 / 3.0), where=s > 0)


def walk_forward_confed_calibrated(
    df: pd.DataFrame, years: tuple[int, ...] = DEFAULT_WC_YEARS,
    base_factory=None, **calib_kwargs
) -> list[dict]:
    """Per WC, score the base model with and without the confederation calibration.

    `base_factory()` builds the base outcome model (defaults to EnsembleModel). The calibrator is
    fit on each fold's training set ONLY (as-of), then applied to the test predictions. Returns one
    dict per tournament: ``{"year", "n", "rps_base", "rps_cal", "offsets"}``.
    """
    base_factory = base_factory or EnsembleModel
    rows: list[dict] = []
    for year, train, test in datasets.walk_forward_tournaments(df, years):
        calib = ConfederationCalibrator(**calib_kwargs).fit(train)
        base = base_factory().fit(train)
        pb = base.predict_proba(test)
        pc = calib.adjust(pb, test["home_confed"].to_numpy(), test["away_confed"].to_numpy())
        y = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        rows.append({"year": year, "n": int(len(test)),
                     "rps_base": metrics.rps(pb, y), "rps_cal": metrics.rps(pc, y),
                     "offsets": dict(calib.offsets_)})
    return rows
