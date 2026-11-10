#!/usr/bin/env python3
"""anaesthesia.ng static site generator.

Stdlib only. Reads content/*.md and writes the static site to docs/.
Each content file starts with front matter (--- ... ---) holding title, type,
path/slug, category, date, excerpt and author; the body is Markdown.
Run: python3 build.py
"""
import html
import json
import os
import posixpath
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
CONTENT = os.path.join(ROOT, "content")

SITE_NAME = "anaesthesia.ng"
TAGLINE = "Advancing Anaesthesia Through Knowledge."
DESCRIPTION = ("The academic and professional knowledge hub for anaesthesia in "
               "Nigeria and Africa: articles, clinical notes, examination guidance "
               "and research resources.")
SITE_URL = "https://anaesthesia.ng"
TODAY = date.today().isoformat()

# ---- OpportunityBoard v0 config ----
# Web3Forms public access key (public by design; submissions go to the
# mailbox the Web3Forms account was created with). No secret lives here.
W3F_ACCESS_KEY = "ed40ec04-304d-434a-a07d-5eeb0e971488"
W3F_ENDPOINT = "https://api.web3forms.com/submit"
OPPORTUNITIES_JSON = os.path.join(ROOT, "data", "opportunities.json")
OPP_BOARD_PATH = "/opportunities/"
OPP_FORM_PATH = "/post-vacancy/"
OPP_THANKS_PATH = "/post-vacancy/thanks/"
OPP_TYPES = ("permanent", "locum", "training/fellowship")
OPP_NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT",
    "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi",
    "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo",
    "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]
OPP_TRUST_NOTE = ("anaesthesia.ng lists vacancies only. We do not employ, place "
                  "or recommend candidates and charge candidates nothing. "
                  "Apply directly to the hospital.")

CATEGORIES = [
    "General Anaesthesia", "Regional Anaesthesia", "Obstetric Anaesthesia",
    "Paediatric Anaesthesia", "Neuroanaesthesia", "Cardiothoracic Anaesthesia",
    "Critical Care", "Pain Medicine", "Anaesthesia Equipment and Technology",
    "Perioperative Medicine", "Patient Safety",
    "Research and Evidence-Based Practice",
]

NAV = [
    ("/", "Home"), ("/resources/", "Resources"), ("/articles/", "Articles"),
    ("/clinical-notes/", "Clinical Notes"), ("/study-resources/", "Study Resources"),
    ("/examinations/", "Examinations"), ("/research/", "Research"),
    ("/news/", "News"), ("/opportunities/", "Opportunities"), ("/about/", "About"),
]

DEMO_NOTE = ("Demonstration content prepared to show the site structure. "
             "Replace or remove it after editorial review before launch.")

CRUMB_LABELS = {
    "examinations": "Examinations", "research": "Research", "articles": "Articles",
    "clinical-notes": "Clinical Notes", "news": "News", "opportunities": "Opportunities", "resources": "Resources",
    "study-resources": "Study Resources", "about": "About", "contact": "Contact",
    "privacy": "Privacy", "disclaimer": "Disclaimer", "category": "Categories",
}


# ---------- helpers ----------

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def link(target, current):
    """Relative href from page at `current` (site-absolute, trailing /) to `target`."""
    r = posixpath.relpath(target, current)
    if r == ".":
        return "./"
    if target.endswith("/") and not r.endswith("/"):
        r += "/"
    return r


def esc(s):
    return html.escape(s or "", quote=True)


def esc_text(s):
    return html.escape(s or "", quote=False)


# ---------- tiny Markdown ----------

def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md(text):
    out, para, items = [], [], None

    def flush_p():
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            del para[:]

    def flush_l():
        nonlocal items
        if items is not None:
            out.append("<ul>" + "".join("<li>" + _inline(i) + "</li>" for i in items) + "</ul>")
            items = None

    for line in text.strip().split("\n"):
        s = line.strip()
        if not s:
            flush_p(); flush_l(); continue
        if s.startswith("### "):
            flush_p(); flush_l(); out.append("<h3>" + _inline(s[4:]) + "</h3>"); continue
        if s.startswith("## "):
            flush_p(); flush_l(); out.append("<h2>" + _inline(s[3:]) + "</h2>"); continue
        if s.startswith("- "):
            flush_p()
            if items is None:
                items = []
            items.append(s[2:]); continue
        para.append(s)
    flush_p(); flush_l()
    return "\n".join(out)


# ---------- content ----------

def load_content():
    items = []
    for fn in sorted(os.listdir(CONTENT)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(CONTENT, fn), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
        if not m:
            raise SystemExit("front matter missing in content/%s" % fn)
        meta = {}
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        meta["body_html"] = md(m.group(2))
        meta["file"] = fn
        items.append(meta)
    return items


def jsonld(objs):
    return "".join('<script type="application/ld+json">%s</script>' % json.dumps(o) for o in objs)


def site_jsonld():
    return jsonld([
        {"@context": "https://schema.org", "@type": "WebSite",
         "name": SITE_NAME, "url": SITE_URL + "/"},
        {"@context": "https://schema.org", "@type": "Organization",
         "name": SITE_NAME, "url": SITE_URL + "/"},
    ])


# ---------- page shell ----------

def shell(path, title, desc, body, active=None, demo=False, extra_head=""):
    cur = active or path
    root = "/" if cur == "/" else "/" + cur.strip("/").split("/")[0] + "/"

    def mark(t):
        return ' aria-current="page"' if t == root else ""

    canonical = SITE_URL + ("" if path == "/" else path)
    demo_html = ('<div class="demo-banner" role="note"><strong>Demonstration content.</strong> '
                 + esc_text(DEMO_NOTE) + "</div>") if demo else ""
    favicon = link("/assets/favicon.svg", path)
    css_link = link("/assets/style.css", path) + "?v=4"
    analytics_link = link("/assets/analytics.js", path)
    home_link = link("/", path)
    search_link = link("/search/", path)
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0F161C">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,600&display=swap" rel="stylesheet">
<link rel="icon" type="image/svg+xml" href="{favicon}">
<link rel="stylesheet" href="{css_link}">
<script src="{analytics_link}"></script>
{site_jsonld()}{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-grid">
    <a class="wordmark" href="{home_link}" aria-label="anaesthesia.ng home">anaesthesia<span>.ng</span></a>

    <form class="search" role="search" action="{search_link}" method="get">
      <label class="sr-only" for="site-search">Search anaesthesia.ng</label>
      <input id="site-search" type="search" name="q" placeholder="Search topics, past questions, syllabus" autocomplete="off" enterkeyhint="search">
      <button type="submit">Search</button>
    </form>

    <nav class="site-nav" aria-label="Primary">
      <ul>
        <li class="nav-search"><a href="{search_link}"{mark("/search/")}>Search</a></li>
        <li><a href="{link("/resources/", path)}"{mark("/resources/")}>Resources</a></li>
        <li><a href="{link("/examinations/", path)}"{mark("/examinations/")}>Exams</a></li>
        <li><a href="{link("/research/", path)}"{mark("/research/")}>Research</a></li>
        <li><a href="{link("/opportunities/", path)}"{mark("/opportunities/")}>Opportunities</a></li>
        <li><a href="{link("/about/", path)}"{mark("/about/")}>About</a></li>
      </ul>
    </nav>
  </div>
</header>
<main id="main">
{demo_html}<div class="wrap page-wrap">{body}</div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="wordmark" href="{home_link}" aria-label="anaesthesia.ng home">anaesthesia<span>.ng</span></a>
        <p class="footer-about">An independent academic knowledge hub for anaesthesia in Nigeria and West Africa.</p>
      </div>

      <nav class="footer-links" aria-label="Footer">
        <a href="{link("/about/", path)}">About</a>
        <a href="{link("/editorial-policy/", path)}">Editorial policy</a>
        <a href="{link("/contact/", path)}">Contact</a>
        <a href="{link("/articles/", path)}">Articles</a>
        <a href="{link("/clinical-notes/", path)}">Clinical notes</a>
        <a href="{link("/news/", path)}">News</a>
        <a href="{link("/study-resources/", path)}">Study resources</a>
        <a href="{link("/privacy/", path)}">Privacy</a>
        <a href="{link("/disclaimer/", path)}">Disclaimer</a>
        <a href="https://github.com/RolandDecker/anaesthesia-ng">Source on GitHub</a>
      </nav>
    </div>

    <p class="footer-note">&copy; 2026 anaesthesia.ng. Independent and not affiliated with WACS or NPMCN. This site is a static build maintained in a GitHub repository; the repository holds the source and change history.</p>
  </div>
</footer>
</body>
</html>
"""
    return out


def crumbs(path, title):
    parts = [p for p in path.strip("/").split("/") if p]
    nav_set = {t for t, _ in NAV}
    out = ['<nav class="breadcrumb" aria-label="Breadcrumb"><ol>',
           '<li><a href="%s">Home</a></li>' % link("/", path)]
    acc = "/"
    for p in parts[:-1]:
        acc += p + "/"
        label = esc_text(CRUMB_LABELS.get(p, p.replace("-", " ").title()))
        if acc in nav_set:
            out.append('<li><a href="%s">%s</a></li>' % (link(acc, path), label))
        else:
            out.append("<li>%s</li>" % label)
    out.append('<li aria-current="page">%s</li>' % esc_text(title))
    out.append("</ol></nav>")
    return "".join(out)


# ---------- page builders ----------

def article_page(item, all_items, base_list, base_label):
    path = item["path"]
    cat = item.get("category", "")
    related = [a for a in all_items if a.get("category") == cat and a["path"] != path][:2]
    related_html = ""
    if related:
        related_html = '<section class="related"><h2>Related reading</h2><ul>' + "".join(
            '<li><a href="%s">%s</a></li>' % (link(a["path"], path), esc_text(a["title"])) for a in related) + "</ul></section>"
    ld = jsonld([{"@context": "https://schema.org", "@type": "Article",
                  "headline": item["title"], "datePublished": item.get("date", TODAY),
                  "author": {"@type": "Person", "name": item.get("author", "anaesthesia.ng editorial")},
                  "publisher": {"@type": "Organization", "name": SITE_NAME},
                  "mainEntityOfPage": SITE_URL + path}])
    byline = ('<div class="byline"><span class="byline-item">%s</span>'
              '<span class="byline-item">Published %s</span>'
              '<span class="byline-item">Last reviewed %s</span>'
              '<a class="tag" href="%s">%s</a></div>') % (
        esc_text(item.get("author", "Editorial team")), esc_text(item.get("date", TODAY)),
        esc_text(item.get("reviewed", item.get("date", TODAY))),
        link("/articles/category/%s/" % slugify(cat), path) if cat else link(base_list, path),
        esc_text(cat or base_label))
    body = (crumbs(path, item["title"]) + '<article class="prose" data-slug="' + item["path"].strip("/").split("/")[-1] + '"><h1>' + esc_text(item["title"]) + "</h1>"
            + byline + item["body_html"] + "</article>" + related_html)
    return shell(path, item["title"] + " | " + SITE_NAME, item.get("excerpt", DESCRIPTION),
                 body, active=base_list, demo=item.get("demo") == "true", extra_head=ld)


def listing_page(path, title, intro_html, groups, active):
    sections = []
    for label, items in groups:
        if not items:
            continue
        rows = "".join(
            '<li class="post-row"><a href="%s">%s</a>'
            '<span class="post-meta">%s%s</span><p>%s</p></li>' % (
                link(i["path"], path), esc_text(i["title"]),
                esc_text(i.get("date", "")), (" &middot; " + esc_text(i.get("category"))) if i.get("category") else "",
                esc_text(i.get("excerpt", ""))) for i in items)
        sections.append('<section class="post-group"><h2>%s</h2><ul class="post-list">%s</ul></section>'
                        % (esc_text(label), rows))
    body = crumbs(path, title) + '<article class="prose"><h1>' + esc_text(title) + "</h1>" + intro_html + "</article>" + "".join(sections)
    return shell(path, title + " | " + SITE_NAME, DESCRIPTION, body, active=active)


def home_html(articles, notes, news):
    path = "/"
    featured = articles[:3]
    cards = [
        ("/resources/", "Academic Resources", "A directory of learning materials across twelve anaesthesia categories."),
        ("/examinations/", "Examinations", "Structured starting points for WACS, NPMCN and Diploma preparation."),
        ("/research/", "Research", "Methodology, writing skills, grants and opportunities for African researchers."),
        ("/news/", "Latest Updates", "Academic and professional updates, announced as they are verified."),
    ]
    cards_html = "".join(
        '<a class="card entry-card" href="%s"><h3>%s</h3><p>%s</p></a>' % (link(t, path), esc_text(h), esc_text(p))
        for t, h, p in cards)
    feat_html = "".join(
        '<a class="card post-card" href="%s"><span class="tag">%s</span><h3>%s</h3>'
        '<p class="post-meta">%s</p><p>%s</p></a>' % (
            link(a["path"], path), esc_text(a.get("category", "")), esc_text(a["title"]),
            esc_text(a.get("date", "")), esc_text(a.get("excerpt", ""))) for a in featured)
    exam_links = "".join('<li><a href="%s">%s</a></li>' % (link(t, path), l)
                         for t, l in [("/examinations/wacs/", "WACS Anaesthesia"),
                                      ("/examinations/npmcn/", "NPMCN Anaesthesia"),
                                      ("/examinations/diploma/", "Diploma in Anaesthesia")])
    body = """
<section class="hero">
  <div class="wrap">
    <h1>""" + esc_text(TAGLINE) + """</h1>
    <p class="hero-sub">""" + esc_text(DESCRIPTION) + """</p>
    <form class="search-form" action="./search/" method="get" role="search">
      <label class="visually-hidden" for="home-q">Search the site</label>
      <input type="search" id="home-q" name="q" placeholder="Search articles, topics and resources" autocomplete="off">
      <button type="submit">Search</button>
    </form>
  </div>
</section>
<section class="section"><div class="wrap">
  <h2>Start here</h2>
  <div class="card-grid">""" + cards_html + """</div>
</div></section>
<section class="section section-alt"><div class="wrap">
  <h2>Featured articles</h2>
  <div class="card-grid">""" + feat_html + """</div>
  <p class="more-link"><a href="./articles/">Browse all articles</a></p>
</div></section>
<section class="section"><div class="wrap split">
  <div>
    <h2>Examination preparation</h2>
    <p>Orientation pages for the three routes most Nigerian anaesthesia trainees take, each with a study-planning framework and pointers to official sources.</p>
    <ul class="plain-list">""" + exam_links + """</ul>
  </div>
  <div>
    <h2>Research and opportunities</h2>
    <p>Skills pages for methodology, biostatistics and scientific writing, plus a curated view of grants, fellowships and calls for papers relevant to anaesthesia in Africa.</p>
    <p><a class="button" href="./research/methodology/">Research skills</a></p>
  </div>
</div></section>
<section class="section section-alt"><div class="wrap">
  <h2>About this site</h2>
  <p>anaesthesia.ng is an independent academic resource for anaesthesia trainees, practitioners and educators in Nigeria and across Africa. Clinical material is reviewed by a qualified human before publication, and demonstration entries are clearly labelled.</p>
  <p><a class="button" href="./about/">About and editorial policy</a></p>
</div></section>
"""
    return shell(path, SITE_NAME + " | " + TAGLINE, DESCRIPTION, body, active="/")


def search_page(idx_rel, prefix):
    js = SEARCH_JS.replace("__IDX__", idx_rel).replace("__PREFIX__", prefix)
    noscript = ('<noscript><p>Search needs JavaScript. You can also browse the '
                '<a href="%s">article index</a>.</p></noscript>' % link("/articles/", "/search/"))
    return ('<section class="section"><div class="wrap search-wrap">'
            '<h1>Search</h1>'
            '<form class="search-form" action="./" method="get" role="search">'
            '<label class="visually-hidden" for="q">Search the site</label>'
            '<input type="search" id="q" name="q" placeholder="Search articles, notes and pages" autocomplete="off">'
            '<button type="submit">Search</button></form>'
            '<div id="results" aria-live="polite"></div>' + noscript + "</div></section>"
            '<script>' + js + "</script>")


SEARCH_JS = """
(function () {
  var input = document.getElementById('q');
  var box = document.getElementById('results');
  var esc = function (s) { var d = document.createElement('span'); d.textContent = s || ''; return d.innerHTML; };
  fetch('__IDX__').then(function (r) { return r.json(); }).then(function (items) {
    var params = new URLSearchParams(location.search);
    var q = (params.get('q') || '').trim();
    if (q) { input.value = q; }
    var ql = q.toLowerCase();
    var hits = items.filter(function (it) {
      if (!ql) { return true; }
      return ((it.title + ' ' + it.category + ' ' + it.excerpt).toLowerCase().indexOf(ql) !== -1);
    });
    if (q && window.Analytics) {
      window.Analytics.track('site_search', { query: q, results_count: hits.length });
    }
    if (hits.length) {
      box.innerHTML = '<ul class="post-list">' + hits.map(function (it) {
        return '<li class="post-row"><a href="__PREFIX__' + it.url + '">' + esc(it.title) + '</a>' +
          '<span class="post-meta">' + esc(it.category) + '</span><p>' + esc(it.excerpt) + '</p></li>';
      }).join('') + '</ul>';
    } else {
      box.innerHTML = '<p>No results' + (q ? ' for &ldquo;' + esc(q) + '&rdquo;' : '') +
        '. Try a shorter word.</p>';
    }
  });
})();
"""


# ---------- opportunity board (OpportunityBoard v0) ----------

def load_opportunities():
    """Read data/opportunities.json. Dev fixtures are included only when the
    OPPORTUNITY_BOARD_DEV env var is set, so production builds never show them.
    Listings whose deadline has passed are hidden (build-time expiry)."""
    try:
        with open(OPPORTUNITIES_JSON, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"listings": [], "fixtures": []}
    listings = list(data.get("listings", []))
    if os.environ.get("OPPORTUNITY_BOARD_DEV") == "1":
        listings += list(data.get("fixtures", []))
    live = []
    today = date.today()
    for o in listings:
        deadline = o.get("deadline", "")
        try:
            if deadline and date.fromisoformat(deadline) < today:
                continue
        except ValueError:
            pass  # malformed date: keep, do not silently drop data
        live.append(o)
    return live


def opp_employment_type(t):
    t = (t or "").lower()
    if t == "permanent":
        return "FULL_TIME"
    if t == "locum":
        return "CONTRACTOR"
    return "FELLOWSHIP"


def trust_note_html(path):
    return '<p class="opp-trust">' + esc_text(OPP_TRUST_NOTE) + "</p>"


def opp_apply_html(o, path):
    am = (o.get("apply_method") or "").strip()
    if not am:
        return ""
    if "@" in am and "://" not in am:
        href, label = "mailto:" + esc(am), esc_text(am)
    else:
        href, label = esc(am), esc_text(am)
    return ('<p class="opp-apply"><a class="button" data-apply href="%s" rel="noopener">Apply to the hospital</a>'
            '<span class="post-meta">&nbsp;%s</span></p>' % (href, label))


def opp_card(o, path):
    href = link("/opportunities/%s/" % o["slug"], path)
    desc = (o.get("description") or "").strip()
    excerpt = desc[:160] + ("…" if len(desc) > 160 else "")
    badge = '<span class="opp-badge">Verified</span> ' if o.get("verified") else ""
    meta = " &middot; ".join(x for x in [
        esc_text(o.get("hospital", "")),
        esc_text("%s, %s" % (o.get("city", ""), o.get("state", "")) if o.get("city") else o.get("state", "")),
        esc_text(o.get("type", "")),
        esc_text(o.get("specialty", "")),
    ] if x)
    return ('<li class="card opp-card" data-state="%s" data-type="%s" data-specialty="%s">'
            '%s<a href="%s"><h3>%s</h3></a>'
            '<p class="post-meta">%s</p><p>%s</p>'
            '<p class="post-meta">Apply by %s</p></li>') % (
        esc(o.get("state", "")), esc(o.get("type", "")), esc(o.get("specialty", "")),
        badge, href, esc_text(o.get("title", "")), meta, esc_text(excerpt),
        esc_text(o.get("deadline", "")))


BOARD_JS = """
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll('.opp-card'));
  var empty = document.getElementById('opp-empty');
  var A = window.Analytics;
  if (A) { A.track('opportunities_viewed', { listings_count: cards.length }); }
  var sel = {};
  ['state', 'type', 'specialty'].forEach(function (k) {
    sel[k] = document.getElementById('opp-filter-' + k);
    if (!sel[k]) { return; }
    sel[k].addEventListener('change', function () {
      if (A) { A.track('filter_used', { filter: k, value: this.value }); }
      apply();
    });
  });
  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('[data-cta]') : null;
    if (el && A) { A.track('post_vacancy_cta_clicked', { location: el.getAttribute('data-cta') }); }
  });
  function apply() {
    var visible = 0, any = false;
    cards.forEach(function (c) {
      any = true;
      var show = true;
      for (var k in sel) {
        if (sel[k] && sel[k].value && c.getAttribute('data-' + k) !== sel[k].value) { show = false; }
      }
      c.style.display = show ? '' : 'none';
      if (show) { visible++; }
    });
    if (empty) { empty.hidden = visible > 0; }
  }
  apply();
})();
"""


def opportunities_board(path, listings):
    states = sorted({o.get("state", "") for o in listings if o.get("state")})
    specialties = sorted({o.get("specialty", "") for o in listings if o.get("specialty")})

    def options(values):
        return "".join('<option value="%s">%s</option>' % (esc(v), esc_text(v)) for v in values)

    filters = ""
    if listings:
        filters = ('<div class="opp-filters" role="group" aria-label="Filter vacancies">'
                   '<label>State <select id="opp-filter-state"><option value="">All states</option>%s</select></label>'
                   '<label>Type <select id="opp-filter-type"><option value="">All types</option>%s</select></label>'
                   '<label>Specialty <select id="opp-filter-specialty"><option value="">All specialties</option>%s</select></label>'
                   '</div>') % (options(states), options(OPP_TYPES), options(specialties))
    cards = "".join(opp_card(o, path) for o in listings)
    empty_state = ('<div id="opp-empty" class="opp-empty"%s>'
                   '<p>No open roles yet. Hospitals: post a vacancy.</p>'
                   '<p><a class="button" data-cta="opportunities_empty_state" href="%s">Post a vacancy</a></p>'
                   '</div>') % (" hidden" if listings else "", link(OPP_FORM_PATH, path))
    body = (crumbs(path, "Opportunities")
            + '<article class="prose"><h1>Opportunities</h1>'
            + '<p>Vacancies in anaesthesia and perioperative medicine in Nigeria, listed by hospitals: '
              'permanent, locum and training/fellowship positions. Apply directly to the hospital for every role.</p>'
            + trust_note_html(path)
            + '<p><a class="button" data-cta="opportunities_board" href="%s">Hospitals: post a vacancy</a></p>'
              '</article>' % link(OPP_FORM_PATH, path)
            + filters
            + ('<ul class="card-grid opp-grid">' + cards + "</ul>" if cards else '<ul class="card-grid opp-grid"></ul>')
            + empty_state
            + '<script>' + BOARD_JS + "</script>")
    return shell(path, "Opportunities | " + SITE_NAME,
                 "Anaesthesia and perioperative vacancies in Nigeria: permanent, locum and training/fellowship positions listed by hospitals.",
                 body, active="/opportunities/")


def opportunity_page(o):
    path = OPP_BOARD_PATH + o["slug"] + "/"
    title = o.get("title", "Vacancy")
    hospital = o.get("hospital", "")
    ld = jsonld([{
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": title,
        "description": o.get("description", ""),
        "datePosted": o.get("posted_date", TODAY),
        "validThrough": o.get("deadline", ""),
        "hiringOrganization": {"@type": "Organization", "name": hospital},
        "jobLocation": {"@type": "Place", "address": {
            "@type": "PostalAddress",
            "addressLocality": o.get("city", ""),
            "addressRegion": o.get("state", ""),
            "addressCountry": "NG"}},
        "employmentType": opp_employment_type(o.get("type")),
    }])
    badge = '<span class="opp-badge">Verified</span>' if o.get("verified") else ""
    rows = []
    if hospital: rows.append(("Hospital", hospital))
    if o.get("state"): rows.append(("Location", ("%s, %s" % (o.get("city"), o.get("state"))).strip(", ")))
    if o.get("type"): rows.append(("Type", o.get("type")))
    if o.get("specialty"): rows.append(("Specialty", o.get("specialty")))
    if o.get("contract_length"): rows.append(("Contract length", o.get("contract_length")))
    if o.get("remuneration"): rows.append(("Remuneration", o.get("remuneration")))
    if o.get("posted_date"): rows.append(("Posted", o.get("posted_date")))
    if o.get("deadline"): rows.append(("Apply by", o.get("deadline")))
    meta_rows = "".join("<li><strong>%s:</strong> %s</li>" % (esc_text(k), esc_text(v)) for k, v in rows)
    body_parts = [p and "<p>" + esc_text(p.strip()) + "</p>" for p in (o.get("description") or "").split("\n\n")]
    desc_html = "".join(x for x in body_parts if x)
    body = (crumbs(path, title)
            + '<article class="prose"><h1>' + esc_text(title) + "</h1>"
            + ('<p>' + badge + "</p>" if badge else "")
            + '<ul class="plain-list opp-meta">' + meta_rows + "</ul>"
            + desc_html
            + opp_apply_html(o, path)
            + "</article>"
            + trust_note_html(path)
            + '<script>(function(){var A=window.Analytics,s=%s;'
              'if(A){A.track("opportunity_viewed",{slug:s});}'
              'document.addEventListener("click",function(e){'
              'var t=e.target&&e.target.closest?e.target.closest("[data-apply]"):null;'
              'if(t&&A){A.track("opportunity_apply_clicked",{slug:s});}});})();'
              '</script>' % json.dumps(o["slug"]))
    return shell(path, title + " | " + SITE_NAME,
                 "Vacancy: %s at %s. Apply directly to the hospital." % (title, hospital),
                 body, active="/opportunities/", extra_head=ld)


VACANCY_FORM_JS = """
(function () {
  var form = document.getElementById('vacancy-form');
  if (!form) { return; }
  var A = window.Analytics;
  var t0 = Date.now();
  var started = false;
  var MIN_MS = 5000; /* minimum time on page before submission is accepted */
  var params = new URLSearchParams(location.search);
  function set(name) {
    var el = form.querySelector('[name="' + name + '"]');
    var v = name === 'referrer' ? (document.referrer || '') : (params.get(name) || '');
    if (el) { el.value = v; }
  }
  ['referrer', 'utm_source', 'utm_medium', 'utm_campaign'].forEach(set);
  form.addEventListener('focusin', function () {
    if (!started && A) { started = true; A.track('vacancy_form_started'); }
  });
  function showErr(m) {
    var el = document.getElementById('vacancy-error');
    if (el) { el.textContent = m; el.hidden = false; }
    var b = form.querySelector('button[type="submit"]');
    if (b) { b.disabled = false; b.textContent = 'Submit for review'; }
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (Date.now() - t0 < MIN_MS) { showErr('Please take a moment to complete the form before submitting.'); return; }
    if (!form.checkValidity()) { form.reportValidity(); return; }
    if (form.querySelector('[name="botcheck"]').value) { window.location.assign('__THANKS__'); return; }
    var b = form.querySelector('button[type="submit"]');
    b.disabled = true; b.textContent = 'Sending...';
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    data.access_key = '__KEY__';
    data.subject = 'New vacancy submission (anaesthesia.ng)';
    data.from_name = 'anaesthesia.ng vacancy board';
    fetch('__ENDPOINT__', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data)
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (res.success) { window.location.assign('__THANKS__'); }
      else { showErr(res.message || 'Submission failed. Please try again.'); }
    }).catch(function () { showErr('Network error. Please try again.'); });
  });
})();
"""


def post_vacancy_page(path):
    states = "".join('<option value="%s">%s</option>' % (esc(s), esc_text(s)) for s in OPP_NIGERIAN_STATES)
    types = "".join('<option value="%s">%s</option>' % (esc(t), esc_text(t)) for t in OPP_TYPES)
    js = (VACANCY_FORM_JS.replace("__KEY__", W3F_ACCESS_KEY)
          .replace("__ENDPOINT__", W3F_ENDPOINT)
          .replace("__THANKS__", link(OPP_THANKS_PATH, path)))
    body = (crumbs(path, "Post a vacancy")
            + '<article class="prose"><h1>Post a vacancy</h1>'
            + '<p>Hospitals and employers: use this form to submit an anaesthesia or perioperative vacancy. '
              'Submissions are reviewed before anything is published; nothing auto-publishes. '
              'Approved listings appear on the <a href="%s">Opportunities board</a>.</p>' % link(OPP_BOARD_PATH, path)
            + trust_note_html(path)
            + "</article>"
            + '<form id="vacancy-form" class="vacancy-form" novalidate action="' + W3F_ENDPOINT + '" method="POST">'
            + '<div class="form-grid">'
            + '<label>Hospital name<input type="text" name="hospital_name" required></label>'
            + '<label>State<select name="state" required><option value="">Select a state</option>' + states + '</select></label>'
            + '<label>Contact name<input type="text" name="contact_name" required></label>'
            + '<label>Work email<input type="email" name="work_email" required></label>'
            + '<label>Role title<input type="text" name="role_title" required></label>'
            + '<label>Type<select name="type" required><option value="">Select a type</option>' + types + '</select></label>'
            + '<label>Contract length (optional)<input type="text" name="contract_length"></label>'
            + '<label>How to apply (email address or URL)<input type="text" name="how_to_apply" required></label>'
            + '<label>Application deadline<input type="date" name="deadline" required></label>'
            + '</div>'
            + '<label>Role description<textarea name="description" rows="8" required></textarea></label>'
            + '<label class="consent"><input type="checkbox" name="consent" required>'
            + '<span>I confirm I am authorised to post this vacancy on behalf of the hospital, and I have read the <a href="%s">privacy policy</a>.</span></label>' % link("/privacy/", path)
            + '<p class="hp-wrap"><label>Leave this field empty<input class="hp-field" type="text" name="botcheck" tabindex="-1" autocomplete="off"></label></p>'
            + '<input type="hidden" name="referrer" value="">'
            + '<input type="hidden" name="utm_source" value="">'
            + '<input type="hidden" name="utm_medium" value="">'
            + '<input type="hidden" name="utm_campaign" value="">'
            + '<p id="vacancy-error" class="form-error" hidden></p>'
            + '<button type="submit">Submit for review</button>'
            + "</form>"
            + '<script>' + js + "</script>")
    return shell(path, "Post a vacancy | " + SITE_NAME,
                 "Hospitals: submit an anaesthesia or perioperative vacancy to the anaesthesia.ng opportunities board. Submissions are reviewed before publishing.",
                 body, active="/opportunities/")


def post_vacancy_thanks_page(path):
    body = (crumbs(path, "Thank you")
            + '<section class="section"><div class="wrap prose">'
            + '<h1>Thank you</h1>'
            + '<p>Your vacancy submission has been received. Every submission is reviewed before it is published; '
              'nothing auto-publishes. If the listing is approved, it will appear on the '
              '<a href="%s">Opportunities board</a> with a link back to your apply method.</p>' % link(OPP_BOARD_PATH, path)
            + trust_note_html(path)
            + "</div></section>"
            + '<script>if(window.Analytics){window.Analytics.track("vacancy_submitted");}</script>')
    return shell(path, "Thank you | " + SITE_NAME, "Vacancy submission received for review.", body, active="/opportunities/")


def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if path.endswith("/"):
        full = os.path.join(full, "index.html")
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))

    items = load_content()
    for it in items:
        t = it.get("type", "page")
        if t == "article":
            it["path"] = "/articles/%s/" % slugify(it["title"])
        elif t == "clinical-note":
            it["path"] = "/clinical-notes/%s/" % slugify(it["title"])
        elif t == "news":
            it["path"] = "/news/%s/" % slugify(it["title"])
        elif t == "page":
            it["path"] = it.get("path", "/%s/" % slugify(it["title"]))
    articles = sorted([i for i in items if i["type"] == "article"], key=lambda x: x.get("date", ""), reverse=True)
    notes = sorted([i for i in items if i["type"] == "clinical-note"], key=lambda x: x.get("date", ""), reverse=True)
    news = sorted([i for i in items if i["type"] == "news"], key=lambda x: x.get("date", ""), reverse=True)
    pages = [i for i in items if i["type"] == "page"]
    page_by_path = {p["path"]: p for p in pages}

    override_home = os.path.join(ROOT, "overrides", "index.html")
    if os.path.exists(override_home):
        shutil.copyfile(override_home, os.path.join(OUT, "index.html"))
        print("homepage: using overrides/index.html verbatim")
    else:
        write("/", home_html(articles, notes, news))

    # article + note + news pages
    for it in articles:
        write(it["path"], article_page(it, articles, "/articles/", "Articles"))
    for it in notes:
        write(it["path"], article_page(it, notes, "/clinical-notes/", "Clinical Notes"))
    for it in news:
        write(it["path"], article_page(it, news, "/news/", "News"))

    # category listings under /articles/category/<slug>/
    for cat in CATEGORIES:
        members = [a for a in articles if a.get("category") == cat]
        cpath = "/articles/category/%s/" % slugify(cat)
        write(cpath, listing_page(cpath, cat, "<p>Articles filed under %s.</p>" % esc_text(cat),
                                  [(cat, members)], "/articles/"))

    # top-level listings
    write("/articles/", listing_page("/articles/", "Articles", "", [
        (c, [a for a in articles if a.get("category") == c]) for c in CATEGORIES], "/articles/"))
    write("/clinical-notes/", listing_page("/clinical-notes/", "Clinical Notes", "", [("Recent notes", notes)], "/clinical-notes/"))
    write("/news/", listing_page("/news/", "News and Updates", "", [("Updates", news)], "/news/"))

    # md-driven pages
    for p in pages:
        path = p["path"]
        body = crumbs(path, p["title"]) + '<article class="prose"><h1>' + esc_text(p["title"]) + "</h1>" + p["body_html"]
        if p.get("categories_grid") == "true":
            body += '<div class="card-grid cat-grid">' + "".join(
                '<a class="card" href="%s"><h3>%s</h3></a>' % (
                    link("/articles/category/%s/" % slugify(c), path), esc_text(c)) for c in CATEGORIES) + "</div>"
        body += "</article>"
        active = "/" + path.strip("/").split("/")[0] + "/" if path.count("/") > 2 else path
        write(path, shell(path, p["title"] + " | " + SITE_NAME, p.get("excerpt", DESCRIPTION), body, active=active, demo=p.get("demo") == "true"))

    # opportunity board (OpportunityBoard v0)
    opps = load_opportunities()
    write(OPP_BOARD_PATH, opportunities_board(OPP_BOARD_PATH, opps))
    for o in opps:
        write("/opportunities/%s/" % o["slug"], opportunity_page(o))
    write(OPP_FORM_PATH, post_vacancy_page(OPP_FORM_PATH))
    write(OPP_THANKS_PATH, post_vacancy_thanks_page(OPP_THANKS_PATH))

    # search
    idx_entries = [{"title": a["title"], "url": a["path"].lstrip("/"), "category": a.get("category", "Article"), "excerpt": a.get("excerpt", "")} for a in articles]
    idx_entries += [{"title": n["title"], "url": n["path"].lstrip("/"), "category": "Clinical note", "excerpt": n.get("excerpt", "")} for n in notes]
    idx_entries += [{"title": p["title"], "url": p["path"].lstrip("/"), "category": "Page", "excerpt": p.get("excerpt", "")} for p in pages if p["path"] != "/"]
    write("/search-index.json", json.dumps(idx_entries))
    write("/search/", shell("/search/", "Search | " + SITE_NAME, "Search anaesthesia.ng.", search_page(link("/search-index.json", "/search/"), (link("/", "/search/") or "") + ("" if link("/", "/search/").endswith("/") else "/")), active="/"))

    # 404
    fix404 = ("<script>(function(){var p=location.pathname;"
              "var prefix=p.indexOf('/anaesthesia-ng')===0?'/anaesthesia-ng/':'/';"
              "var links=document.querySelectorAll('[data-target]');"
              "for(var i=0;i<links.length;i++){links[i].setAttribute('href',prefix+links[i].getAttribute('data-target'));}})();</script>")
    nf = shell("/404/", "Page not found | " + SITE_NAME, "Page not found.",
               '<section class="section"><div class="wrap prose"><h1>Page not found</h1>'
               '<p>The page you asked for does not exist. Try the '
               '<a data-target="" href="/">homepage</a> or the '
               '<a data-target="articles/" href="articles/">article index</a>.</p></div></section>'
               + fix404)
    write("/404/", nf)

    # sitemap + robots
    urls = ["/"] + [a["path"] for a in articles] + [n["path"] for n in notes] + [n["path"] for n in news] + [p["path"] for p in pages] + ["/articles/category/%s/" % slugify(c) for c in CATEGORIES] + ["/search/"] \
          + [OPP_BOARD_PATH, OPP_FORM_PATH, OPP_THANKS_PATH] + ["/opportunities/%s/" % o["slug"] for o in opps]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (SITE_URL + ("" if u == "/" else u), TODAY))
    sm.append("</urlset>")
    write("/sitemap.xml", "\n".join(sm))
    write("/robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)

    # custom domain for GitHub Pages (apex): picked up by the Pages deployment
    write("/CNAME", "anaesthesia.ng\n")

    n_html = len(urls) + 1
    print("built %s pages into docs/" % n_html)


if __name__ == "__main__":
    main()
