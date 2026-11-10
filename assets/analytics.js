/* anaesthesia.ng analytics: PostHog, consent-gated.
   Loaded by every page. Nothing is captured until the visitor accepts the
   consent banner; the choice is stored in localStorage and re-read on every
   visit. The project key below is PostHog's public client-side ingest token
   (designed to ship in browser code). No secret credentials live in this file. */
(function () {
  "use strict";

  /* Configuration: project key and host in ONE constant. */
  var ANALYTICS_CONFIG = {
    key: "phc_p2cf8wmLFmKqtQERQ3RQNtt7AaamrWQj3zJ7gQJBkRM4",
    host: "https://us.i.posthog.com"
  };

  var CONSENT_KEY = "anaesthesia.ng.analytics_consent";

  var consented = null; /* "" = not chosen yet, "granted", "denied" */
  var inited = false;

  function readConsent() {
    if (consented === null) {
      try { consented = window.localStorage.getItem(CONSENT_KEY) || ""; }
      catch (e) { consented = ""; }
    }
    return consented;
  }

  function writeConsent(v) {
    consented = v;
    try { window.localStorage.setItem(CONSENT_KEY, v); } catch (e) { /* storage blocked: nothing persists, nothing captures */ }
  }

  /* Privacy guard: emails and names never reach event properties. */
  var PII_KEY = /^(e-?mail|mail|first_?name|last_?name|full_?name|middle_?name|user_?name|username|display_?name|nick_?name|phone|mobile)$/i;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function cleanProps(props) {
    var out = {}, k, v;
    for (k in props) {
      if (!Object.prototype.hasOwnProperty.call(props, k)) { continue; }
      if (PII_KEY.test(k)) { continue; }
      v = props[k];
      if (typeof v === "string" && EMAIL_RE.test(v)) { continue; }
      out[k] = v;
    }
    return out;
  }

  function isEmail(s) { return typeof s === "string" && EMAIL_RE.test(s); }

  /* Pageviews: initial load, plus history-API route changes. */
  function capturePageview() {
    if (inited && window.posthog && window.posthog.capture) {
      window.posthog.capture("$pageview", { $current_url: window.location.href });
    }
  }

  function watchHistory() {
    function fire() { capturePageview(); }
    var push = window.history.pushState, replace = window.history.replaceState;
    if (push) {
      window.history.pushState = function () { var r = push.apply(this, arguments); fire(); return r; };
    }
    if (replace) {
      window.history.replaceState = function () { var r = replace.apply(this, arguments); fire(); return r; };
    }
    window.addEventListener("popstate", fire);
  }

  /* PostHog loads from the CDN only after consent is granted. */
  function init() {
    if (inited || readConsent() !== "granted") { return; }
    inited = true;

    (function (t, e) {
      var o, n, p, r;
      e.__SV || (window.posthog = e, e._i = [], e.init = function (i, s, a) {
        function g(t, e) { var o = e.split("."); 2 == o.length && (t = t[o[0]], e = o[1]); t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))); }; }
        p = t.createElement("script"), p.type = "text/javascript", p.async = !0,
        p.src = s.api_host.replace(".i.posthog.com", "-assets.i.posthog.com") + "/static/array.js",
        r = t.getElementsByTagName("script")[0], r.parentNode.insertBefore(p, r);
        var u = e;
        for (void 0 !== a ? u = e[a] = [] : a = "posthog",
        u.people = u.people || [],
        u.toString = function (t) { var e = "posthog"; return "posthog" !== a && (e += "." + a), t || (e += " (stub)"), e; },
        u.people.toString = function () { return u.toString(1) + ".people (stub)"; },
        o = "capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset".split(" "),
        n = 0; n < o.length; n++) g(u, o[n]);
        e._i.push([i, s, a]);
      }, e.__SV = 1);
    })(document, window.posthog || []);

    window.posthog.init(ANALYTICS_CONFIG.key, {
      api_host: ANALYTICS_CONFIG.host,
      capture_pageview: false, /* captured explicitly: initial load + route changes */
      capture_pageleave: true,
      autocapture: false
    });

    capturePageview();
    watchHistory();
  }

  /* Public wrapper: no-ops unless consent is granted and PostHog is live. */
  function track(event, props) {
    if (!inited || !window.posthog || !window.posthog.capture) { return; }
    window.posthog.capture(event, cleanProps(props));
  }

  /* Identity: internal ids only. Email-shaped ids are refused. */
  function identify(internalUserId) {
    if (!inited || !window.posthog) { return; }
    if (isEmail(internalUserId)) { return; }
    window.posthog.identify(String(internalUserId));
  }

  function reset() {
    if (inited && window.posthog && window.posthog.reset) { window.posthog.reset(); }
  }

  /* ---- named events (called from site code as they come online) ---- */
  function signupCompleted(internalUserId) { track("signup_completed"); identify(internalUserId); }
  function loginCompleted(internalUserId) { track("login_completed"); identify(internalUserId); }
  function logout() { reset(); }
  function quizStarted(quizId) { track("quiz_started", { quiz_id: quizId }); }
  function quizCompleted(quizId, score, nQuestions) { track("quiz_completed", { quiz_id: quizId, score: score, n_questions: nQuestions }); }
  function bookDownloaded(title) { track("book_downloaded", { title: title }); }
  function emailSubscribed(source) { track("email_subscribed", { source: source }); }
  function questionContributed() { track("question_contributed"); }

  /* ---- auto-wired behaviours for pages that exist today ---- */

  function closest(el, sel) {
    while (el && el.nodeType === 1) {
      if (el.matches && el.matches(sel)) { return el; }
      el = el.parentNode;
    }
    return null;
  }

  /* article_read at 75% scroll depth, once per page view. */
  function wireArticleRead() {
    var el = document.querySelector("article.prose[data-slug]");
    if (!el) { return; }
    var slug = el.getAttribute("data-slug");
    var fired = false;
    function check() {
      if (fired) { return; }
      var doc = document.documentElement;
      var depth = (window.pageYOffset || doc.scrollTop || 0) + window.innerHeight;
      if (doc.scrollHeight > 0 && depth / doc.scrollHeight >= 0.75) {
        fired = true;
        track("article_read", { slug: slug });
        window.removeEventListener("scroll", check);
      }
    }
    window.addEventListener("scroll", check, { passive: true });
    check();
  }

  /* book_downloaded on PDF / download links, whenever they appear. */
  function wireClicks() {
    document.addEventListener("click", function (e) {
      var dl = e.target && closest(e.target, 'a[href$=".pdf"], a[download]');
      if (dl) {
        var title = (dl.textContent || "").trim() || (dl.getAttribute("href") || "").split("/").pop();
        bookDownloaded(title);
        return;
      }
      if (closest(e.target, "[data-logout]")) { reset(); }
    });
  }

  /* ---- consent banner (choice stored in localStorage) ---- */
  var BANNER_CSS = "#ana-consent{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#0F161C;color:#EBEFF2;padding:16px 24px;font:400 14px/22px system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:center;box-shadow:0 -4px 16px rgba(0,0,0,.35);margin:0}"
    + "#ana-consent p{margin:0;max-width:640px}"
    + "#ana-consent a{color:#EBEFF2;text-decoration:underline}"
    + "#ana-consent button{font:600 14px/22px system-ui,sans-serif;padding:10px 20px;border:2px solid #EBEFF2;border-radius:0;cursor:pointer}"
    + "#ana-consent .ana-accept{background:#EBEFF2;color:#0F161C}"
    + "#ana-consent .ana-decline{background:transparent;color:#EBEFF2}";

  function wireBanner() {
    if (readConsent()) { return; }
    var style = document.createElement("style");
    style.textContent = BANNER_CSS;
    document.head.appendChild(style);
    var b = document.createElement("div");
    b.id = "ana-consent";
    b.setAttribute("role", "region");
    b.setAttribute("aria-label", "Analytics consent");
    b.innerHTML = '<p>We use privacy-friendly, anonymous analytics to see which pages are useful. No emails, names or personal details are collected. See the <a href="/privacy/">privacy policy</a>.</p>'
      + '<button type="button" class="ana-accept">Accept</button>'
      + '<button type="button" class="ana-decline">Decline</button>';
    document.body.appendChild(b);
    b.querySelector(".ana-accept").addEventListener("click", function () {
      writeConsent("granted");
      b.parentNode.removeChild(b);
      init();
    });
    b.querySelector(".ana-decline").addEventListener("click", function () {
      writeConsent("denied");
      b.parentNode.removeChild(b);
    });
  }

  function boot() {
    if (readConsent() === "granted") { init(); }
    else { wireBanner(); }
    wireArticleRead();
    wireClicks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  /* Public API for site code and future pages. */
  window.Analytics = {
    track: track,
    identify: identify,
    reset: reset,
    signupCompleted: signupCompleted,
    loginCompleted: loginCompleted,
    logout: logout,
    quizStarted: quizStarted,
    quizCompleted: quizCompleted,
    bookDownloaded: bookDownloaded,
    emailSubscribed: emailSubscribed,
    questionContributed: questionContributed
  };
})();
