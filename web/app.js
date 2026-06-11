/* World Cup 2026 forecast — game mode. Vanilla JS, no framework, no build.
   Loads web/data/model_export.json (served over http — see web/README.md) and renders the
   neutral-venue head-to-head for any two of the 48 teams. */
(function () {
  "use strict";

  var DATA_URL = "data/model_export.json";
  var $ = function (id) { return document.getElementById(id); };

  var state = { pairs: null, confed: {}, teams: [] };

  // ---- boot ---------------------------------------------------------------
  fetch(DATA_URL, { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(init)
    .catch(function (err) {
      showNotice("Couldn't load the forecast data (" + err.message +
        "). Serve this folder over http — see web/README.md.");
      $("foot-meta").textContent = "Model data unavailable";
    });

  function init(data) {
    // index the 1128 unordered neutral pairs by "home|away" for O(1) lookup
    state.pairs = new Map();
    data.game_mode.forEach(function (m) { state.pairs.set(m.home + "|" + m.away, m); });
    state.confed = (data.structure && data.structure.confederations) || {};

    // 48 teams, alphabetical
    var groups = (data.structure && data.structure.groups) || {};
    var teams = [];
    Object.keys(groups).forEach(function (g) { teams = teams.concat(groups[g]); });
    state.teams = teams.sort(function (a, b) { return a.localeCompare(b); });

    populateSelect($("team1"));
    populateSelect($("team2"));
    // sensible defaults: a marquee tie if present
    $("team1").value = state.teams.indexOf("Spain") >= 0 ? "Spain" : state.teams[0];
    $("team2").value = state.teams.indexOf("Argentina") >= 0 ? "Argentina" : state.teams[1];

    $("team1").addEventListener("change", render);
    $("team2").addEventListener("change", render);
    wireModeSwitch();
    footerMeta(data.metadata || {});
    render();
  }

  function populateSelect(sel) {
    var frag = document.createDocumentFragment();
    state.teams.forEach(function (name) {
      var o = document.createElement("option");
      o.value = name;
      o.textContent = name;
      frag.appendChild(o);
    });
    sel.appendChild(frag);
  }

  // ---- matchup lookup with unordered-pair flip ----------------------------
  function parseScore(s) { var p = s.split("-"); return [parseInt(p[0], 10), parseInt(p[1], 10)]; }

  // Returns the head-to-head from t1's perspective, or null if the pair is missing.
  function getMatch(t1, t2) {
    var direct = state.pairs.get(t1 + "|" + t2);
    if (direct) {
      return {
        score: parseScore(direct.modal),
        pWin: direct.p_home, pDraw: direct.p_draw, pLoss: direct.p_away,
        e1: direct.e_home, e2: direct.e_away,
        top: direct.top.map(function (t) { return { score: parseScore(t[0]), p: t[1] }; })
      };
    }
    // stored the other way round: flip scorelines and swap win/loss so t1 reads as "home"
    var rev = state.pairs.get(t2 + "|" + t1);
    if (rev) {
      return {
        score: flip(parseScore(rev.modal)),
        pWin: rev.p_away, pDraw: rev.p_draw, pLoss: rev.p_home,
        e1: rev.e_away, e2: rev.e_home,
        top: rev.top.map(function (t) { return { score: flip(parseScore(t[0])), p: t[1] }; })
      };
    }
    return null;
  }
  function flip(sc) { return [sc[1], sc[0]]; }

  // ---- render -------------------------------------------------------------
  function render() {
    var t1 = $("team1").value, t2 = $("team2").value;
    $("persp-name").textContent = t1;

    if (t1 === t2) {
      return showNotice("Pick two different teams to see the head-to-head.");
    }
    var m = getMatch(t1, t2);
    if (!m) {
      return showNotice("No forecast on file for " + t1 + " vs " + t2 + ".");
    }
    hideNotice();
    $("result").hidden = false;

    // scoreboard
    setTeam("sb-home-name", "sb-home-confed", t1);
    setTeam("sb-away-name", "sb-away-confed", t2);
    $("sb-score").textContent = m.score[0] + "–" + m.score[1];   // en dash

    // win / draw / loss bar (normalise widths so they fill the track)
    var total = m.pWin + m.pDraw + m.pLoss || 1;
    $("wdl-win").style.width = (100 * m.pWin / total) + "%";
    $("wdl-draw").style.width = (100 * m.pDraw / total) + "%";
    $("wdl-loss").style.width = (100 * m.pLoss / total) + "%";
    $("lab-win").textContent = pct(m.pWin);
    $("lab-draw").textContent = pct(m.pDraw);
    $("lab-loss").textContent = pct(m.pLoss);
    $("lab-win-team").textContent = t1;
    $("lab-loss-team").textContent = t2;

    // expected goals
    $("xg-home-name").textContent = t1;
    $("xg-away-name").textContent = t2;
    $("xg-home").textContent = m.e1.toFixed(1);
    $("xg-away").textContent = m.e2.toFixed(1);

    // top-3 scorelines
    renderTop3(m.top);
  }

  function setTeam(nameId, confedId, team) {
    $(nameId).textContent = team;
    var c = state.confed[team];
    $(confedId).textContent = c || "";
    $(confedId).style.display = c ? "" : "none";
  }

  function renderTop3(top) {
    var ol = $("top3");
    ol.textContent = "";
    var maxP = top.reduce(function (a, t) { return Math.max(a, t.p); }, 0) || 1;
    top.forEach(function (t) {
      var li = document.createElement("li");
      li.className = "top3__row";
      var score = document.createElement("span");
      score.className = "top3__score";
      score.textContent = t.score[0] + "–" + t.score[1];
      var track = document.createElement("div");
      track.className = "top3__track";
      var fill = document.createElement("div");
      fill.className = "top3__fill";
      fill.style.width = (100 * t.p / maxP) + "%";
      track.appendChild(fill);
      var p = document.createElement("span");
      p.className = "top3__pct";
      p.textContent = pct(t.p);
      li.appendChild(score); li.appendChild(track); li.appendChild(p);
      ol.appendChild(li);
    });
  }

  function pct(x) { return Math.round(x * 100) + "%"; }

  // ---- notice / result toggling ------------------------------------------
  function showNotice(msg) {
    var n = $("notice");
    n.textContent = msg;
    n.hidden = false;
    var res = $("result"); if (res) res.hidden = true;
  }
  function hideNotice() { $("notice").hidden = true; }

  // ---- mode switch (Tournament is a placeholder this release) -------------
  function wireModeSwitch() {
    var btnGame = $("mode-game"), btnTour = $("mode-tournament");
    function select(which) {
      var game = which === "game";
      btnGame.classList.toggle("is-active", game);
      btnTour.classList.toggle("is-active", !game);
      btnGame.setAttribute("aria-selected", String(game));
      btnTour.setAttribute("aria-selected", String(!game));
      $("view-game").classList.toggle("is-active", game);
      $("view-tournament").classList.toggle("is-active", !game);
      $("view-game").hidden = !game;
      $("view-tournament").hidden = game;
    }
    btnGame.addEventListener("click", function () { select("game"); });
    btnTour.addEventListener("click", function () { select("tournament"); });
  }

  // ---- footer metadata ----------------------------------------------------
  function footerMeta(meta) {
    var bits = [];
    if (meta.model_version) bits.push("Model v" + meta.model_version);
    if (meta.as_of) bits.push("data as-of " + meta.as_of);
    if (meta.confed_calibration) bits.push("confederation-calibrated");
    $("foot-meta").textContent = bits.join(" · ") || "World Cup 2026 forecast";
  }
})();
