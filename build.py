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
    ("/news/", "News"), ("/about/", "About"),
]

DEMO_NOTE = ("Demonstration content prepared to show the site structure. "
             "Replace or remove it after editorial review before launch.")

CRUMB_LABELS = {
    "examinations": "Examinations", "research": "Research", "articles": "Articles",
    "clinical-notes": "Clinical Notes", "news": "News", "resources": "Resources",
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
    nav_links = []
    for target, label in NAV:
        cls = ' aria-current="page"' if target == (active or path) else ""
        nav_links.append('<a href="%s"%s>%s</a>' % (link(target, path), cls, esc_text(label)))
    nav_html = "".join(nav_links)
    canonical = SITE_URL + ("" if path == "/" else path)
    demo_html = ('<div class="demo-banner" role="note"><strong>Demonstration content.</strong> '
                 + esc_text(DEMO_NOTE) + "</div>") if demo else ""
    explore = "".join('<li><a href="%s">%s</a></li>' % (link(t, path), esc_text(l)) for t, l in NAV)
    legal = "".join('<li><a href="%s">%s</a></li>' % (link(t, path), l)
                    for t, l in [("/privacy/", "Privacy"), ("/disclaimer/", "Disclaimer"), ("/contact/", "Contact")])
    favicon = link("/assets/favicon.svg", path)
    css = link("/assets/style.css", path)
    home_link = link("/", path)
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<link rel="icon" type="image/svg+xml" href="{favicon}">
<link rel="stylesheet" href="{css}">
{site_jsonld()}{extra_head}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="{home_link}">anaesthesia<span class="logo-dot">.ng</span></a>
    <nav class="main-nav" aria-label="Main">{nav_html}</nav>
    <details class="mobile-menu">
      <summary aria-label="Open menu">Menu</summary>
      <nav aria-label="Mobile">{nav_html}</nav>
    </details>
  </div>
</header>
<main id="main">
{demo_html}{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="footer-logo">anaesthesia<span class="logo-dot">.ng</span></p>
      <p class="footer-tag">{esc_text(TAGLINE)}</p>
    </div>
    <div>
      <h3>Explore</h3>
      <ul>{explore}</ul>
    </div>
    <div>
      <h3>Legal</h3>
      <ul>{legal}</ul>
    </div>
  </div>
  <div class="wrap footer-legal">
    <p>&copy; 2026 anaesthesia.ng. Educational information only; it does not replace
    clinical judgement, institutional protocols or specialist consultation.</p>
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
    body = (crumbs(path, item["title"]) + '<article class="prose"><h1>' + esc_text(item["title"]) + "</h1>"
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
    urls = ["/"] + [a["path"] for a in articles] + [n["path"] for n in notes] + [n["path"] for n in news] + [p["path"] for p in pages] + ["/articles/category/%s/" % slugify(c) for c in CATEGORIES] + ["/search/"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (SITE_URL + ("" if u == "/" else u), TODAY))
    sm.append("</urlset>")
    write("/sitemap.xml", "\n".join(sm))
    write("/robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE_URL)

    n_html = len(urls) + 1
    print("built %s pages into docs/" % n_html)


if __name__ == "__main__":
    main()
