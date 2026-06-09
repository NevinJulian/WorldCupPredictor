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

`walk_forward_elo_baseline` / `walk_forward_dixon_coles` fit and score each the only way we
evaluate anything here — time-based, training strictly before each World Cup (see
datasets.walk_forward_tournaments) — returning the per-tournament normalized RPS.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.special import gammaln
from sklearn.linear_model import LogisticRegression

from . import datasets, metrics

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
    form a year or two old counts for half. Strengths (base, home_adv, attack, defence) are
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

    def __init__(
        self,
        half_life_days: float = 547.0,   # ~1.5 years
        reg: float = 5.0,                # ridge strength -> cold-start shrinkage
        max_goals: int = 10,
        rho_bounds: tuple[float, float] = (-0.2, 0.2),
        max_iter: int = 1000,
    ):
        self.half_life_days = half_life_days
        self.reg = reg
        self.max_goals = max_goals
        self.rho_bounds = rho_bounds
        self.max_iter = max_iter
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

    def _lambdas(self, home: str, away: str, neutral: bool = True) -> tuple[float, float]:
        ah, dh = self.attack_.get(home, 0.0), self.defence_.get(home, 0.0)
        aa, da = self.attack_.get(away, 0.0), self.defence_.get(away, 0.0)
        adv = 0.0 if neutral else self.home_adv_
        lam = np.exp(self.base_ + adv + ah - da)
        mu = np.exp(self.base_ + aa - dh)
        return float(lam), float(mu)

    def score_matrix(self, home: str, away: str, neutral: bool = True) -> np.ndarray:
        """(max_goals+1) x (max_goals+1) probability matrix P[x, y] = P(home x, away y)."""
        lam, mu = self._lambdas(home, away, neutral)
        P = np.outer(self._pois_pmf(lam), self._pois_pmf(mu))
        rho = self.rho
        P[0, 0] *= 1.0 - lam * mu * rho
        P[0, 1] *= 1.0 + lam * rho
        P[1, 0] *= 1.0 + mu * rho
        P[1, 1] *= 1.0 - rho
        np.clip(P, 0.0, None, out=P)
        total = P.sum()
        if total <= 0:  # degenerate rho guard -> fall back to independent Poisson
            P = np.outer(self._pois_pmf(lam), self._pois_pmf(mu))
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
