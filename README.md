# anaesthesia.ng

Static academic site for anaesthesia in Nigeria and Africa. Plain HTML/CSS output,
built by `build.py` (Python standard library only) from Markdown files in `content/`.
Hosted free on GitHub Pages; pushes to `main` rebuild and deploy automatically.

## Add or edit content

1. Add or edit a file in `content/`. Every file needs front matter at the top:

   ```
   ---
   title: My article title
   type: article        # article | clinical-note | news | page
   category: General Anaesthesia   # for articles and clinical notes
   date: 2026-11-05
   excerpt: One sentence shown in listings and search.
   author: Name, credentials
   ---
   Then write the body in Markdown (## headings, **bold**, - lists, [links](url)).
   ```

2. `page` files also take `path: /about/` (any URL) and, for the resources page,
   `categories_grid: true`.
3. Commit and push. GitHub Actions runs `build.py` and deploys within a minute or two.

Types map to URLs: article -> /articles/<title-slug>/, clinical-note ->
/clinical-notes/<slug>/, news -> /news/<slug>/, page -> its `path`.

## Build locally

```
python3 build.py     # writes the site into docs/
```

## Deployment

- Hosting: GitHub Pages (free) via the included GitHub Actions workflow.
- Canonical domain: https://anaesthesia.ng (to be connected after DNS is set by the owner).
- Secondary domain anesthesia.ng 301-redirects to anaesthesia.ng (registrar-level or
  Cloudflare free redirect; see the deployment guide).
- No database, no server code, no accounts, no analytics.

## Known limitations (v1)

- Canonical URLs and sitemap use https://anaesthesia.ng; on the preview URL they
  point at the future production domain. Harmless for preview, correct after launch.
- Search is a client-side index over published content only.
- Examination pages deliberately avoid specific dates/fees until verified against
  official college publications; each carries a last-verified note.
- Demonstration articles and notes are labelled with a banner and must be replaced
  or removed after editorial review.
- Lighthouse scores were not measured in this build; the site is static, has no
  JavaScript on content pages, and inlines no large assets.
