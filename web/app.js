/* World Cup 2026 forecast — game mode + tournament view. Vanilla JS, no framework, no build.
   Loads web/data/model_export.json (+ web/flags/flags.json) over http — see web/README.md. */
(function () {
  "use strict";

  var EXPORT_URL = "data/model_export.json";
  var FLAGS_URL = "flags/flags.json";
  var FLAG_DIR = "flags/";
  var TITLE_TOP = 8;            // contenders shown in the title-odds row

  var $ = function (id) { return document.getElementById(id); };
  var state = { data: null, pairs: new Map(), confed: {}, teams: [], flags: {}, n: "50000" };

  // 3-letter FIFA codes for the compact bracket cards (fallback: first 3 letters).
  var CODE3 = {
    "Mexico": "MEX", "South Africa": "RSA", "South Korea": "KOR", "Czechia": "CZE",
    "Canada": "CAN", "Switzerland": "SUI", "Bosnia and Herzegovina": "BIH", "Qatar": "QAT",
    "Brazil": "BRA", "Morocco": "MAR", "Scotland": "SCO", "Haiti": "HAI", "United States": "USA",
    "Paraguay": "PAR", "Australia": "AUS", "Türkiye": "TUR", "Germany": "GER", "Ecuador": "ECU",
    "Ivory Coast": "CIV", "Curaçao": "CUW", "Netherlands": "NED", "Japan": "JPN", "Sweden": "SWE",
    "Tunisia": "TUN", "Belgium": "BEL", "Egypt": "EGY", "Iran": "IRN", "New Zealand": "NZL",
    "Spain": "ESP", "Uruguay": "URU", "Cape Verde": "CPV", "Saudi Arabia": "KSA", "France": "FRA",
    "Senegal": "SEN", "Norway": "NOR", "Iraq": "IRQ", "Argentina": "ARG", "Austria": "AUT",
    "Algeria": "ALG", "Jordan": "JOR", "Portugal": "POR", "Colombia": "COL", "DR Congo": "COD",
    "Uzbekistan": "UZB", "England": "ENG", "Croatia": "CRO", "Ghana": "GHA", "Panama": "PAN"
  };
  function code3(team) { return CODE3[team] || team.slice(0, 3).toUpperCase(); }
  var ROUND_NAME = { R32: "Round of 32", R16: "Round of 16", QF: "Quarter-finals", SF: "Semi-finals", Final: "Final" };

  // ---- boot ---------------------------------------------------------------
  Promise.all([
    fetch(EXPORT_URL, { cache: "no-cache" }).then(okJson),
    fetch(FLAGS_URL, { cache: "no-cache" }).then(okJson).catch(function () { return {}; })
  ]).then(function (r) { init(r[0], r[1]); }).catch(boot_fail);

  function okJson(r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }
  function boot_fail(err) {
    var n = $("game-notice");
    n.textContent = "Couldn't load the forecast data (" + err.message +
      "). Serve this folder over http — see web/README.md.";
    n.hidden = false;
    $("foot-meta").textContent = "Model data unavailable";
  }

  function init(data, flags) {
    state.data = data;
    state.flags = flags || {};
    data.game_mode.forEach(function (m) { state.pairs.set(m.home + "|" + m.away, m); });
    state.confed = (data.structure && data.structure.confederations) || {};
    var groups = (data.structure && data.structure.groups) || {};
    var teams = [];
    Object.keys(groups).forEach(function (g) { teams = teams.concat(groups[g]); });
    state.teams = teams.slice().sort(function (a, b) { return a.localeCompare(b); });

    var levels = (data.tournament && data.tournament.levels) || [1000, 10000, 50000, 100000];
    state.n = String(levels.indexOf(50000) >= 0 ? 50000 : levels[levels.length - 1]);

    setupGame();
    setupTournament(levels);
    setupModal();
    wireModeSwitch();
    footerMeta(data.metadata || {});
    renderGame();
    renderTournament();
  }

  // ---- tiny DOM helpers ---------------------------------------------------
  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function pct(x) { return Math.round(x * 100) + "%"; }
  function commas(n) { return Number(n).toLocaleString("en-US"); }
  function scoreText(modal) { return modal.replace("-", "–"); }   // en dash

  // ---- flags --------------------------------------------------------------
  function flagEl(team, cls) {
    var iso = state.flags[team];
    var img = document.createElement("img");
    img.className = "flag" + (cls ? " " + cls : "");
    img.src = FLAG_DIR + (iso ? iso : "_placeholder") + ".svg";
    img.alt = team;            // country name for screen readers
    img.title = team;
    img.width = 20; img.height = 15; img.loading = "lazy";
    img.onerror = function () {
      if (this.src.indexOf("_placeholder") < 0) { this.onerror = null; this.src = FLAG_DIR + "_placeholder.svg"; }
    };
    return img;
  }
  // flag + visible name (name is never dropped — the flag is supplementary)
  function teamLabel(team, cls) {
    var w = el("span", "team" + (cls ? " " + cls : ""));
    w.appendChild(flagEl(team));
    w.appendChild(el("span", "team__name", team));
    return w;
  }

  // ---- matchup maths ------------------------------------------------------
  function parseScore(s) { var p = s.split("-"); return [parseInt(p[0], 10), parseInt(p[1], 10)]; }
  function flip(sc) { return [sc[1], sc[0]]; }

  // Neutral head-to-head from t1's perspective (the 1128-pair lookup + unordered flip).
  function neutralMatch(t1, t2) {
    // total-goals fields (pOver25, goalTotals) are perspective-symmetric, so they copy as-is
    var d = state.pairs.get(t1 + "|" + t2);
    if (d) return {
      score: parseScore(d.modal), pWin: d.p_home, pDraw: d.p_draw, pLoss: d.p_away,
      e1: d.e_home, e2: d.e_away, top: d.top.map(function (t) { return { score: parseScore(t[0]), p: t[1] }; }),
      pOver25: d.p_over25, goalTotals: d.goal_totals
    };
    var r = state.pairs.get(t2 + "|" + t1);
    if (r) return {
      score: flip(parseScore(r.modal)), pWin: r.p_away, pDraw: r.p_draw, pLoss: r.p_home,
      e1: r.e_away, e2: r.e_home, top: r.top.map(function (t) { return { score: flip(parseScore(t[0])), p: t[1] }; }),
      pOver25: r.p_over25, goalTotals: r.goal_totals
    };
    return null;
  }
  // A group fixture reads its OWN fields (real venue), from the home team's perspective.
  function fixtureMatch(fx) {
    return {
      score: parseScore(fx.modal), pWin: fx.p_home, pDraw: fx.p_draw, pLoss: fx.p_away,
      e1: fx.e_home, e2: fx.e_away, top: fx.top.map(function (t) { return { score: parseScore(t[0]), p: t[1] }; }),
      pOver25: fx.p_over25, goalTotals: fx.goal_totals
    };
  }

  // ---- shared match panel (game result + detail modal) --------------------
  function buildMatchPanel(home, away, m) {
    var frag = document.createDocumentFragment();
    var sb = el("div", "scoreboard");
    sb.appendChild(scoreTeam(home, "home"));
    var sc = el("div", "scoreboard__score");
    var p1 = (m.top && m.top[0]) ? m.top[0].p : null;       // top-1 scoreline probability
    sc.appendChild(el("span", "scoreboard__label", p1 != null ? "most likely · " + pct(p1) : "most likely"));
    sc.appendChild(el("span", "scoreboard__digits", m.score[0] + "–" + m.score[1]));
    sc.appendChild(el("span", "scoreboard__xg", "xG " + m.e1.toFixed(1) + " – " + m.e2.toFixed(1)));
    sb.appendChild(sc);
    sb.appendChild(scoreTeam(away, "away"));
    frag.appendChild(sb);
    frag.appendChild(buildWDL(home, away, m));
    var cards = el("div", "cards");
    cards.appendChild(buildXG(home, away, m));
    cards.appendChild(buildTop3(m.top));
    if (m.goalTotals) cards.appendChild(buildTotals(m));
    frag.appendChild(cards);
    return frag;
  }
  // Total-goals card: P(over 2.5) headline + a P(0,1,2,3,4,5+) bar (over-2.5 buckets tinted).
  function buildTotals(m) {
    var card = el("div", "card card--totals");
    card.appendChild(el("h3", "card__title", "Total goals"));
    if (m.pOver25 != null) {
      var over = el("div", "totals__over");
      over.appendChild(el("b", null, pct(m.pOver25)));
      over.appendChild(document.createTextNode(" over 2.5 goals"));
      card.appendChild(over);
    }
    var labels = ["0", "1", "2", "3", "4", "5+"];
    var maxP = m.goalTotals.reduce(function (a, x) { return Math.max(a, x); }, 0) || 1;
    var chart = el("div", "gt");
    m.goalTotals.forEach(function (p, i) {
      var row = el("div", "gt__row");
      row.appendChild(el("span", "gt__k", labels[i]));
      var track = el("div", "gt__track");
      var fill = el("div", "gt__fill" + (i >= 3 ? " gt__fill--over" : ""));
      fill.style.width = (100 * p / maxP) + "%";
      track.appendChild(fill);
      row.appendChild(track);
      row.appendChild(el("span", "gt__pct", pct(p)));
      chart.appendChild(row);
    });
    card.appendChild(chart);
    return card;
  }
  function scoreTeam(team, side) {
    var t = el("div", "scoreboard__team scoreboard__team--" + side);
    var id = el("span", "scoreboard__id");
    id.appendChild(flagEl(team, "flag--lg"));
    id.appendChild(el("span", "scoreboard__name", team));
    t.appendChild(id);
    var c = state.confed[team];
    if (c) t.appendChild(el("span", "confed-tag", c));
    return t;
  }
  function buildWDL(home, away, m) {
    var wrap = el("div", "wdl");
    var total = (m.pWin + m.pDraw + m.pLoss) || 1;
    var bar = el("div", "wdl__bar");
    bar.setAttribute("role", "img");
    bar.setAttribute("aria-label", home + " win " + pct(m.pWin) + ", draw " + pct(m.pDraw) +
      ", " + away + " win " + pct(m.pLoss));
    bar.appendChild(seg("win", 100 * m.pWin / total));
    bar.appendChild(seg("draw", 100 * m.pDraw / total));
    bar.appendChild(seg("loss", 100 * m.pLoss / total));
    wrap.appendChild(bar);
    var leg = el("div", "wdl__legend");
    leg.appendChild(legKey("win", m.pWin, home));
    leg.appendChild(legKey("draw", m.pDraw, "draw"));
    leg.appendChild(legKey("loss", m.pLoss, away));
    wrap.appendChild(leg);
    return wrap;
  }
  function seg(kind, w) { var s = el("span", "wdl__seg wdl__seg--" + kind); s.style.width = w + "%"; return s; }
  function legKey(kind, p, label) {
    var k = el("span", "wdl__key");
    k.appendChild(el("i", "dot dot--" + kind));
    k.appendChild(el("b", null, pct(p)));
    k.appendChild(document.createTextNode(" " + label));
    return k;
  }
  function buildXG(home, away, m) {
    var card = el("div", "card card--xg");
    card.appendChild(el("h3", "card__title", "Expected goals"));
    var box = el("div", "xg");
    box.appendChild(xgRow(home, m.e1));
    box.appendChild(xgRow(away, m.e2));
    card.appendChild(box);
    return card;
  }
  function xgRow(team, v) {
    var r = el("div", "xg__row");
    r.appendChild(teamLabel(team, "xg__team"));
    r.appendChild(el("span", "xg__val", v.toFixed(1)));
    return r;
  }
  function buildTop3(top) {
    var card = el("div", "card card--top");
    card.appendChild(el("h3", "card__title", "Most-likely scorelines"));
    var ol = el("ol", "top3");
    var maxP = top.reduce(function (a, t) { return Math.max(a, t.p); }, 0) || 1;
    top.forEach(function (t) {
      var li = el("li", "top3__row");
      li.appendChild(el("span", "top3__score", t.score[0] + "–" + t.score[1]));
      var track = el("div", "top3__track");
      var fill = el("div", "top3__fill"); fill.style.width = (100 * t.p / maxP) + "%";
      track.appendChild(fill);
      li.appendChild(track);
      li.appendChild(el("span", "top3__pct", pct(t.p)));
      ol.appendChild(li);
    });
    card.appendChild(ol);
    return card;
  }

  // ---- game mode ----------------------------------------------------------
  function setupGame() {
    populate($("team1")); populate($("team2"));
    $("team1").value = state.teams.indexOf("Spain") >= 0 ? "Spain" : state.teams[0];
    $("team2").value = state.teams.indexOf("Argentina") >= 0 ? "Argentina" : state.teams[1];
    $("team1").addEventListener("change", renderGame);
    $("team2").addEventListener("change", renderGame);
  }
  function populate(sel) {
    var frag = document.createDocumentFragment();
    state.teams.forEach(function (name) {
      var o = document.createElement("option");
      o.value = name; o.textContent = name;
      frag.appendChild(o);
    });
    sel.appendChild(frag);
  }
  function renderGame() {
    var t1 = $("team1").value, t2 = $("team2").value;
    $("persp-name").textContent = t1;
    var res = $("game-result"), notice = $("game-notice");
    if (t1 === t2) { notice.textContent = "Pick two different teams to see the head-to-head."; notice.hidden = false; res.hidden = true; return; }
    var m = neutralMatch(t1, t2);
    if (!m) { notice.textContent = "No forecast on file for " + t1 + " vs " + t2 + "."; notice.hidden = false; res.hidden = true; return; }
    notice.hidden = true; res.hidden = false;
    res.textContent = "";
    res.appendChild(buildMatchPanel(t1, t2, m));
  }

  // ---- tournament ---------------------------------------------------------
  function setupTournament(levels) {
    var box = $("nsel-btns"); box.textContent = "";
    levels.forEach(function (L) {
      var b = el("button", "nsel__btn" + (String(L) === state.n ? " is-active" : ""), fmtN(L));
      b.setAttribute("data-n", String(L));
      b.setAttribute("aria-pressed", String(String(L) === state.n));
      b.addEventListener("click", function () { setN(String(L)); });
      box.appendChild(b);
    });
  }
  function fmtN(L) { return L >= 1000 ? (L / 1000) + "k" : String(L); }
  function setN(n) {
    state.n = n;
    Array.prototype.forEach.call($("nsel-btns").children, function (b) {
      var on = b.getAttribute("data-n") === n;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", String(on));
    });
    renderTournament();
  }
  function renderTournament() {
    var tour = state.data && state.data.tournament;
    if (!tour || !tour.by_n) return;
    var sec = tour.by_n[state.n];
    if (!sec) return;
    $("title-n").textContent = "N = " + commas(state.n);
    renderTitleOdds(sec.teams);
    renderGroups(sec.groups);
    renderBracket(tour.chalk);
  }
  function renderTitleOdds(teams) {
    var box = $("title-odds"); box.textContent = "";
    teams.slice(0, TITLE_TOP).forEach(function (t, i) {
      var card = el("div", "metric");
      var head = el("div", "metric__head");
      head.appendChild(el("span", "metric__rank", "#" + (i + 1)));
      head.appendChild(teamLabel(t.team));
      card.appendChild(head);
      card.appendChild(el("div", "metric__big", pct(t.title)));
      card.appendChild(el("div", "metric__sub", "advance " + pct(t.advance)));
      box.appendChild(card);
    });
  }
  function groupFixtures() {
    var by = {};
    (state.data.group_stage || []).forEach(function (fx) { (by[fx.group] = by[fx.group] || []).push(fx); });
    return by;
  }
  function renderGroups(groupsObj) {
    var grid = $("groups-grid"); grid.textContent = "";
    var fbg = groupFixtures();
    Object.keys(groupsObj).sort().forEach(function (g) {
      var card = el("article", "gcard");
      card.appendChild(el("h3", "gcard__title", "Group " + g));

      var tbl = el("div", "gtable");
      var head = el("div", "gtable__row gtable__row--head");
      ["Team", "Adv", "Win", "RU", "3rd"].forEach(function (h, i) {
        head.appendChild(el("span", "gcell" + (i ? " gcell--num" : ""), h));
      });
      tbl.appendChild(head);
      groupsObj[g].forEach(function (r) {
        var row = el("div", "gtable__row");
        row.appendChild(teamLabel(r.team, "gcell gcell--team"));
        row.appendChild(el("span", "gcell gcell--num gcell--adv", pct(r.advance)));
        row.appendChild(el("span", "gcell gcell--num", pct(r.win)));
        row.appendChild(el("span", "gcell gcell--num", pct(r.runner_up)));
        row.appendChild(el("span", "gcell gcell--num", pct(r.third)));
        tbl.appendChild(row);
      });
      card.appendChild(tbl);

      var fl = el("div", "gfix");
      (fbg[g] || []).forEach(function (fx) {
        var row = el("button", "gfix__row");
        var scoreCell = el("div", "gfix__sc");
        scoreCell.appendChild(el("span", "gfix__score", scoreText(fx.modal)));
        scoreCell.appendChild(el("span", "gfix__xg", "xG " + fx.e_home.toFixed(1) + "–" + fx.e_away.toFixed(1)));
        row.appendChild(miniTeam(fx.home, false));
        row.appendChild(scoreCell);
        row.appendChild(miniTeam(fx.away, true));
        row.addEventListener("click", function () { openDetail(fixtureMatch(fx), fx.home, fx.away, "Group " + g); });
        fl.appendChild(row);
      });
      card.appendChild(fl);
      grid.appendChild(card);
    });
  }
  function miniTeam(team, reverse) {
    var w = el("span", "miniteam" + (reverse ? " miniteam--rev" : ""));
    w.appendChild(flagEl(team));
    w.appendChild(el("span", "team__name", team));
    return w;
  }
  // The bracket renders two layouts from the same data: a mirrored center-final tree (wide,
  // ≥1024px) and a vertical round-stacked tree (narrow). CSS shows exactly one; neither scrolls
  // sideways. The chalk bracket is stored in fold order, so the first half of each round is the
  // left side of the tree and the second half is the right side.
  function byRound(bracket) {
    var by = { R32: [], R16: [], QF: [], SF: [], Final: [] };
    bracket.forEach(function (t) { if (by[t.round]) by[t.round].push(t); });
    return by;
  }
  function renderBracket(chalk) {
    var wrap = $("bracket"); wrap.textContent = "";
    if (!chalk) return;
    var by = byRound(chalk.bracket);
    wrap.appendChild(buildWideBracket(by, chalk.champion));
    wrap.appendChild(buildTallBracket(by, chalk.champion));
  }

  // --- shared compact tie card (flag + 3-letter code + per-team goals; winner highlighted) ---
  function bracketTie(t) {
    var sc = parseScore(t.modal);
    var m = neutralMatch(t.home, t.away);   // neutral tie: source of xG + the detail panel
    var tie = el("button", "bx-tie");
    tie.appendChild(bxRow(t, t.home, sc[0]));
    tie.appendChild(bxRow(t, t.away, sc[1]));
    if (m) tie.appendChild(el("div", "bx-xg", "xG " + m.e1.toFixed(1) + "–" + m.e2.toFixed(1)));
    tie.setAttribute("aria-label",
      t.home + " " + sc[0] + "–" + sc[1] + " " + t.away + "; " + t.winner + " advance");
    tie.addEventListener("click", function () { if (m) openDetail(m, t.home, t.away, ROUND_NAME[t.round] || t.round); });
    return tie;
  }
  function bxRow(t, team, goals) {
    var r = el("div", "bx-row" + (t.winner === team ? " is-winner" : ""));
    r.appendChild(flagEl(team));
    r.appendChild(el("span", "bx-code", code3(team)));
    r.appendChild(el("span", "bx-goals", String(goals)));
    return r;
  }
  function championCard(champion, cls) {
    var ch = el("div", "bx-champ" + (cls ? " " + cls : ""));
    ch.appendChild(el("span", "bx-champ__trophy", "🏆"));   // 🏆
    ch.appendChild(flagEl(champion, "flag--lg"));
    ch.appendChild(el("span", "bx-champ__name", champion));
    return ch;
  }

  // --- wide: mirrored center-final tree (9 flex columns) ---
  function buildWideBracket(by, champion) {
    var wide = el("div", "bx-wide");
    // left half feeds rightward; "first" = the R32 leaves (no incoming connector)
    wide.appendChild(wideCol("R32", by.R32.slice(0, 8), "l", "first"));
    wide.appendChild(wideCol("R16", by.R16.slice(0, 4), "l", ""));
    wide.appendChild(wideCol("QF", by.QF.slice(0, 2), "l", ""));
    wide.appendChild(wideCol("SF", by.SF.slice(0, 1), "l", "single"));
    wide.appendChild(finalCol(by.Final[0], champion));
    wide.appendChild(wideCol("SF", by.SF.slice(1, 2), "r", "single"));
    wide.appendChild(wideCol("QF", by.QF.slice(2, 4), "r", ""));
    wide.appendChild(wideCol("R16", by.R16.slice(4, 8), "r", ""));
    wide.appendChild(wideCol("R32", by.R32.slice(8, 16), "r", "first"));
    return wide;
  }
  function wideCol(label, ties, side, mod) {
    var col = el("div", "bx-col bx-col--" + side + (mod ? " bx-col--" + mod : ""));
    col.appendChild(el("div", "bx-col__title", label));
    var body = el("div", "bx-col__body");
    ties.forEach(function (t) {
      var slot = el("div", "bx-slot");
      slot.appendChild(bracketTie(t));
      body.appendChild(slot);
    });
    col.appendChild(body);
    return col;
  }
  function finalCol(t, champion) {
    var col = el("div", "bx-col bx-col--final");
    col.appendChild(el("div", "bx-col__title", "Final"));
    var body = el("div", "bx-col__body");
    if (t) { var slot = el("div", "bx-slot"); slot.appendChild(bracketTie(t)); body.appendChild(slot); }
    body.appendChild(championCard(champion));
    col.appendChild(body);
    return col;
  }

  // --- tall: rounds stacked top→bottom, full-width cards, vertical scroll only ---
  function buildTallBracket(by, champion) {
    var tall = el("div", "bx-tall");
    ["R32", "R16", "QF", "SF", "Final"].forEach(function (r) {
      var sec = el("section", "bx-sec");
      sec.appendChild(el("h4", "bx-sec__title", ROUND_NAME[r]));
      var list = el("div", "bx-sec__list");
      by[r].forEach(function (t) { list.appendChild(bracketTie(t)); });
      sec.appendChild(list);
      tall.appendChild(sec);
    });
    tall.appendChild(championCard(champion, "bx-champ--tall"));
    return tall;
  }

  // ---- shared detail modal ------------------------------------------------
  function setupModal() {
    $("detail-close").addEventListener("click", closeDetail);
    $("detail-backdrop").addEventListener("click", closeDetail);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !$("detail-modal").hidden) closeDetail();
    });
  }
  function openDetail(m, home, away, kicker) {
    $("detail-title").textContent = kicker + " · " + home + " vs " + away;
    var body = $("detail-body"); body.textContent = "";
    body.appendChild(buildMatchPanel(home, away, m));
    $("detail-modal").hidden = false;
    document.body.classList.add("modal-open");
    $("detail-close").focus();
  }
  function closeDetail() {
    $("detail-modal").hidden = true;
    document.body.classList.remove("modal-open");
  }

  // ---- mode switch --------------------------------------------------------
  function wireModeSwitch() {
    var btnGame = $("mode-game"), btnTour = $("mode-tournament");
    function select(which, push) {
      var game = which === "game";
      btnGame.classList.toggle("is-active", game);
      btnTour.classList.toggle("is-active", !game);
      btnGame.setAttribute("aria-selected", String(game));
      btnTour.setAttribute("aria-selected", String(!game));
      $("view-game").classList.toggle("is-active", game);
      $("view-tournament").classList.toggle("is-active", !game);
      $("view-game").hidden = !game;
      $("view-tournament").hidden = game;
      if (push !== false) { try { history.replaceState(null, "", game ? "#game" : "#tournament"); } catch (e) {} }
    }
    btnGame.addEventListener("click", function () { select("game"); });
    btnTour.addEventListener("click", function () { select("tournament"); });
    if (location.hash === "#tournament") select("tournament", false);   // deep-link to the bracket
  }

  // ---- footer -------------------------------------------------------------
  function footerMeta(meta) {
    var bits = [];
    if (meta.model_version) bits.push("Model v" + meta.model_version);
    if (meta.as_of) bits.push("data as-of " + meta.as_of);
    if (meta.confed_calibration) bits.push("confederation-calibrated");
    $("foot-meta").textContent = bits.join(" · ") || "World Cup 2026 forecast";
  }
})();
