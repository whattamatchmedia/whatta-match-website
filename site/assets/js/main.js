/* Whatta Match Media — shared site behaviour (no dependencies) */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var WM = (window.WM = window.WM || {});

  /* Header: solid background after scrolling */
  var header = document.querySelector(".site-header");
  function onScrollHeader() { if (header) header.classList.toggle("is-solid", window.scrollY > 40); }
  window.addEventListener("scroll", onScrollHeader, { passive: true });
  onScrollHeader();

  /* Mobile menu */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "Close" : "Menu";
      document.body.style.overflow = open ? "hidden" : "";
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A" && links.classList.contains("is-open")) toggle.click();
    });
  }

  /* Reveal on scroll */
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }) : null;
  document.querySelectorAll(".reveal").forEach(function (el) {
    if (io && !reduce) io.observe(el); else el.classList.add("in");
  });

  /* Manifesto: words light up as you read */
  var manifesto = document.querySelector(".manifesto");
  if (manifesto) {
    manifesto.querySelectorAll("p").forEach(function (p) {
      var out = [];
      p.childNodes.forEach(function (n) {
        if (n.nodeType === 3) {
          n.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) out.push(document.createTextNode(w));
            else { var s = document.createElement("span"); s.className = "word"; s.textContent = w; out.push(s); }
          });
        } else { n.classList.add("word"); out.push(n); }
      });
      p.textContent = "";
      out.forEach(function (n) { p.appendChild(n); });
    });
    var words = manifesto.querySelectorAll(".word");
    var lightWords = function () {
      var r = manifesto.getBoundingClientRect();
      var vh = window.innerHeight;
      var prog = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height * 0.75)));
      var n = Math.round(prog * words.length);
      words.forEach(function (w, i) { w.classList.toggle("on", i < n); });
    };
    if (!reduce) { window.addEventListener("scroll", lightWords, { passive: true }); lightWords(); }
  }

  /* Services chapter: which pillar is active */
  var track = document.querySelector(".svc-track");
  WM.svcIndex = 0; WM.svcProgress = 0;
  if (track) {
    var items = document.querySelectorAll(".svc-list li");
    var panels = document.querySelectorAll(".svc-stage .svc-panel");
    var count = document.querySelector(".svc-count");
    var setSvc = function () {
      var r = track.getBoundingClientRect();
      var span = r.height - window.innerHeight;
      var p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
      WM.svcProgress = p;
      var N = items.length || 6, idx = Math.min(N - 1, Math.floor(p * N));
      if (idx !== WM.svcIndex || !items[idx].classList.contains("on")) {
        WM.svcIndex = idx;
        items.forEach(function (li, i) { li.classList.toggle("on", i === idx); });
        panels.forEach(function (pn, i) { pn.classList.toggle("on", i === idx); pn.setAttribute("aria-hidden", i === idx ? "false" : "true"); });
        if (count) count.textContent = "0" + (idx + 1) + " / 0" + N;
      }
    };
    window.addEventListener("scroll", setSvc, { passive: true });
    window.addEventListener("resize", setSvc);
    setSvc();
  }

  /* Counters */
  var counters = document.querySelectorAll("[data-count]");
  var runCount = function (el) {
    var target = parseFloat(el.getAttribute("data-count"));
    if (reduce) { el.textContent = target; return; }
    var start = performance.now(), dur = 1600;
    (function tick(t) {
      var k = Math.min(1, (t - start) / dur);
      el.textContent = Math.round(target * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(tick);
    })(start);
  };
  if (io) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { runCount(e.target); cio.unobserve(e.target); } });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  } else counters.forEach(runCount);

  /* Process line draws in */
  document.querySelectorAll(".process").forEach(function (p) {
    if (!io || reduce) { p.style.setProperty("--p", 1); return; }
    var pio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { p.style.setProperty("--p", 1); pio.disconnect(); } });
    }, { threshold: 0.4 });
    pio.observe(p);
  });

  /* Magnetic buttons + cursor node (pointer devices only) */
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (fine && !reduce) {
    var cursor = document.createElement("div");
    cursor.className = "cursor"; cursor.setAttribute("aria-hidden", "true");
    document.body.appendChild(cursor);
    var cx = 0, cy = 0, tx = 0, ty = 0;
    window.addEventListener("mousemove", function (e) { tx = e.clientX; ty = e.clientY; cursor.classList.add("is-on"); });
    document.addEventListener("mouseleave", function () { cursor.classList.remove("is-on"); });
    (function loop() {
      cx += (tx - cx) * 0.22; cy += (ty - cy) * 0.22;
      cursor.style.transform = "translate(" + cx + "px," + cy + "px)";
      requestAnimationFrame(loop);
    })();
    document.querySelectorAll("a, button, summary, .chip").forEach(function (el) {
      el.addEventListener("mouseenter", function () { cursor.classList.add("is-hover"); });
      el.addEventListener("mouseleave", function () { cursor.classList.remove("is-hover"); });
    });
    document.querySelectorAll(".btn").forEach(function (b) {
      b.addEventListener("mousemove", function (e) {
        var r = b.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.25, y = (e.clientY - r.top - r.height / 2) * 0.35;
        b.style.transform = "translate(" + x + "px," + y + "px)";
      });
      b.addEventListener("mouseleave", function () { b.style.transform = ""; });
    });
    document.querySelectorAll(".work-card").forEach(function (c) {
      c.addEventListener("mousemove", function (e) {
        var r = c.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        c.style.transform = "perspective(900px) rotateY(" + x * 8 + "deg) rotateX(" + -y * 8 + "deg)";
      });
      c.addEventListener("mouseleave", function () { c.style.transform = ""; });
    });
  }

  /* Work filter */
  var filter = document.querySelector(".filter");
  if (filter) {
    filter.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      filter.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var f = b.getAttribute("data-filter");
      document.querySelectorAll("[data-cat]").forEach(function (c) {
        c.hidden = !(f === "all" || c.getAttribute("data-cat").indexOf(f) > -1);
      });
    });
  }

  /* Forms: posts to the endpoint in data-endpoint (e.g. Formspree). Until one is set, goes to the thank-you page. */
  document.querySelectorAll("form[data-endpoint]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".form-status");
      if (form.querySelector(".hp input") && form.querySelector(".hp input").value) return;
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var ep = form.getAttribute("data-endpoint");
      var next = form.getAttribute("data-next") || "/thank-you";
      if (!ep || ep.indexOf("YOUR_") > -1) { window.location.href = next; return; }
      if (status) status.textContent = "Sending…";
      fetch(ep, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (r.ok) window.location.href = next;
          else if (status) status.textContent = "That didn't send. Please email hello@whattamatch.com instead.";
        })
        .catch(function () { if (status) status.textContent = "That didn't send. Check your connection, or email hello@whattamatch.com."; });
    });
  });

  /* Find your match: brief builder */
  var brief = document.querySelector("[data-brief]");
  if (brief) {
    var steps = brief.querySelectorAll(".brief-step");
    var bars = brief.querySelectorAll(".brief-progress i");
    var back = brief.querySelector("[data-back]");
    var nextBtn = brief.querySelector("[data-next]");
    var result = brief.querySelector(".brief-result");
    var cur = 0;
    var show = function (i) {
      cur = i;
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      bars.forEach(function (b, k) { b.classList.toggle("on", k <= i); });
      back.hidden = i === 0;
      result.hidden = true;
      nextBtn.hidden = false;
      nextBtn.textContent = i === steps.length - 1 ? "See my match" : "Next";
    };
    var val = function (name) {
      var c = brief.querySelector('input[name="' + name + '"]:checked');
      return c ? c.value : "";
    };
    var recommend = function () {
      var goal = val("b_goal"), stage = val("b_stage"), where = val("b_where"), when = val("b_when");
      var map = {
        launch: ["Brand Strategy", "Brand Identity & Design", "Media & Digital Experiences"],
        rebrand: ["Brand Strategy", "Brand Identity & Design", "Content & Creative"],
        grow: ["Performance & Growth", "Social & Influence", "Consulting"],
        awareness: ["Content & Creative", "Social & Influence", "Media & Digital Experiences"]
      };
      var why = {
        "Consulting": "An expert outside view and a clear roadmap before you spend.",
        "Brand Strategy": "Positioning and a clear plan before anything is made.",
        "Brand Identity & Design": "A look that carries the strategy everywhere.",
        "Content & Creative": "Campaigns and content people stop for.",
        "Social & Influence": "Community and creators who carry the story.",
        "Performance & Growth": "Paid, search and conversion work that turns attention into revenue.",
        "Media & Digital Experiences": "The site, the media plan and the channels that reach people."
      };
      var list = (map[goal] || map.launch).slice();
      if (where === "global" && list.indexOf("Media & Digital Experiences") < 0) list[2] = "Media & Digital Experiences";
      if (stage === "early" && list.indexOf("Brand Strategy") < 0) list[0] = "Brand Strategy";
      var ul = result.querySelector("ul"); ul.textContent = "";
      list.forEach(function (s) {
        var li = document.createElement("li");
        var b = document.createElement("strong"); b.textContent = s;
        var sp = document.createElement("span"); sp.className = "muted"; sp.textContent = why[s];
        li.appendChild(b); li.appendChild(sp); ul.appendChild(li);
      });
      var summary = result.querySelector("[data-summary]");
      summary.textContent = when === "now" ? "You want to move fast. Book a call and we'll come back within one working day." : "Book a call and we'll shape a plan around your timing.";
      var field = document.getElementById("services-suggested");
      if (field) field.value = list.join(", ");
    };
    nextBtn.addEventListener("click", function () {
      var step = steps[cur];
      if (!step.querySelector("input:checked")) { step.querySelector(".brief-hint").hidden = false; return; }
      step.querySelector(".brief-hint").hidden = true;
      if (cur < steps.length - 1) show(cur + 1);
      else {
        recommend();
        steps.forEach(function (s) { s.hidden = true; });
        result.hidden = false; nextBtn.hidden = true;
        bars.forEach(function (b) { b.classList.add("on"); });
      }
    });
    back.addEventListener("click", function () { show(Math.max(0, result.hidden ? cur - 1 : cur)); });
    show(0);
  }

  /* Cookie notice (stores the choice in this browser only) */
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
                set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var bar = document.querySelector(".cookie");
  if (bar && !store.get("wm-cookies")) {
    bar.hidden = false;
    bar.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () { store.set("wm-cookies", b.getAttribute("data-choice")); bar.hidden = true; });
    });
  }

  /* Footer year */
  var y = document.querySelector("[data-year]"); if (y) y.textContent = new Date().getFullYear();
})();
