# Repository Audit: anaesthesia.ng

**Date:** 17 November 2026  
**Status:** Step 0 Baseline Audit (Read-only)  
**Specification:** `DESIGN.md` Section 8.1 Step 0  

---

## 1. Overview and Architecture

`anaesthesia.ng` is a static academic knowledge hub and vacancy platform for anaesthesia in Nigeria and West Africa. The site is generated using a custom static site generator (`build.py`) written entirely with the Python standard library. It outputs plain HTML, CSS, and minimal vanilla JavaScript to the `docs/` directory, which is deployed to GitHub Pages.

---

## 2. Pages and Routes

The current build compiles 43 distinct URL paths into `docs/`. All must be preserved through redesign and refactoring.

### 2.1 Core & Landing Pages
- `/` — Homepage (currently rendered via `overrides/index.html` or `home_html()`).
- `/about/` — Mission, scope, and editorial governance (`content/about.md`).
- `/contact/` — Contact information for the editorial team (`content/contact.md`).
- `/disclaimer/` — Educational disclaimer (`content/disclaimer.md`).
- `/editorial-policy/` — Clinical content review and correction policy (`content/editorial-policy.md`).
- `/privacy/` — Privacy policy and data handling (`content/privacy.md`).
- `/thanks/` — Email subscription confirmation landing page (`content/thanks.md`).
- `/404/` — 404 error page (`build.py` with path prefix normalization).

### 2.2 Examination Preparation Pages
- `/examinations/` — Examination preparation overview (`content/examinations.md`).
- `/examinations/wacs/` — West African College of Surgeons preparation guide (`content/examinations-wacs.md`).
- `/examinations/npmcn/` — National Postgraduate Medical College of Nigeria guide (`content/examinations-npmcn.md`).
- `/examinations/diploma/` — Diploma in Anaesthesia framework (`content/examinations-diploma.md`).

### 2.3 Research & Study Resources Pages
- `/resources/` — Directory of learning materials across 12 categories (`content/resources.md`).
- `/study-resources/` — Reading lists, study guides, and downloadable aids (`content/study-resources.md`).
- `/research/` — Research skills and opportunities overview (`content/research.md`).
- `/research/africa/` — Regional research landscape for Africa (`content/research-africa.md`).
- `/research/methodology/` — Study design, statistics, appraisal, and writing (`content/research-methodology.md`).
- `/research/opportunities/` — Grants, fellowships, and calls for papers (`content/research-opportunities.md`).

### 2.4 Articles (6 items)
- `/articles/how-to-build-a-study-plan-for-the-wacs-primary-examination/` (`content/wacs-primary-study-plan.md`)
- `/articles/writing-your-first-case-report-a-structure-that-works/` (`content/first-case-report.md`)
- `/articles/pre-oxygenation-before-induction-the-core-idea/` (`content/preoxygenation-basics.md`)
- `/articles/choosing-an-anaesthetic-technique-for-caesarean-delivery-how-the-decision-is-framed/` (`content/caesarean-decision-framing.md`)
- `/articles/perioperative-sepsis-a-reading-map/` (`content/perioperative-sepsis-reading-map.md`)
- `/articles/understanding-evidence-hierarchies-from-case-report-to-systematic-review/` (`content/evidence-hierarchy.md`)

### 2.5 Clinical Notes (2 items)
- `/clinical-notes/the-anaesthesia-machine-check-a-structure-for-the-daily-check/` (`content/machine-check-structure.md`)
- `/clinical-notes/the-pre-anaesthetic-assessment-a-structure-to-present-in-vivas/` (`content/preop-assessment-structure.md`)

### 2.6 News & Announcements (1 item)
- `/news/site-structure-published-demonstration-post/` (`content/site-launch-demo.md`)

### 2.7 Category Listings (12 categories)
- `/articles/category/general-anaesthesia/`
- `/articles/category/regional-anaesthesia/`
- `/articles/category/obstetric-anaesthesia/`
- `/articles/category/paediatric-anaesthesia/`
- `/articles/category/neuroanaesthesia/`
- `/articles/category/cardiothoracic-anaesthesia/`
- `/articles/category/critical-care/`
- `/articles/category/pain-medicine/`
- `/articles/category/anaesthesia-equipment-and-technology/`
- `/articles/category/perioperative-medicine/`
- `/articles/category/patient-safety/`
- `/articles/category/research-and-evidence-based-practice/`

### 2.8 Top-Level Indexes & Search
- `/articles/` — Full index of published articles grouped by category.
- `/clinical-notes/` — Index of clinical notes.
- `/news/` — Updates and announcements index.
- `/search/` — Client-side search interface querying `/search-index.json`.

### 2.9 Opportunities & Vacancy Board (OpportunityBoard v0)
- `/opportunities/` — Vacancy board with client-side filters (State, Type, Specialty).
- `/opportunities/[slug]/` — Individual vacancy listing detail pages (generated from `data/opportunities.json`).
- `/post-vacancy/` — Hospital vacancy submission form.
- `/post-vacancy/thanks/` — Post-vacancy submission confirmation page.

### 2.10 Static Feeds & Meta Files
- `/sitemap.xml` — XML sitemap listing all published content URLs.
- `/robots.txt` — Robots exclusion protocol pointing to sitemap.
- `/search-index.json` — Client-side search index.
- `/CNAME` — Custom apex domain declaration (`anaesthesia.ng`).

---

## 3. Content and Assets That Must Survive

1. **Content Source Files (`content/*.md`)**: 23 Markdown files containing structured frontmatter (`title`, `type`, `category`, `date`, `excerpt`, `author`, `reviewed`, `demo`, `path`) and Markdown body.
2. **Opportunities Data (`data/opportunities.json`)**: Live vacancy records under `listings` and test fixtures under `fixtures`.
3. **Brand & Asset Files**:
   - `assets/favicon.svg` — Site favicon.
   - `assets/analytics.js` — Client analytics and consent layer.
   - `assets/style.css` — Existing production styles (untouched during Step 1).
4. **Override Template**: `overrides/index.html` (homepage production override).

---

## 4. Stack and Build System

- **Language / Runtime**: Python 3 standard library only (`html`, `json`, `os`, `posixpath`, `re`, `shutil`, `datetime`). Zero third-party packages or virtual environment dependencies.
- **Build Script**: `build.py`.
- **Local Build Command**:
  ```bash
  python build.py
  # or
  python3 build.py
  ```
- **Deployment**: Managed by GitHub Actions via `.github/workflows/deploy.yml`:
  - Triggers on push to `main` branch.
  - Runs on `ubuntu-latest` with Python 3.12.
  - Executes `python3 build.py`.
  - Publishes `docs/` using `actions/deploy-pages@v4`.

---

## 5. Existing Functionality, Forms and Endpoints

### 5.1 Post a Vacancy Form (`/post-vacancy/`)
- **Endpoint**: `https://api.web3forms.com/submit`
- **Method**: `POST` (JSON payload with `Content-Type: application/json` and `Accept: application/json`)
- **Access Key**: Configured in `build.py` via `W3F_ACCESS_KEY` constant (value omitted from audit).
- **Form Fields**:
  - `hospital_name` (text, required)
  - `state` (select, required, 37 Nigerian states / FCT)
  - `contact_name` (text, required)
  - `work_email` (email, required)
  - `role_title` (text, required)
  - `type` (select, required: `permanent`, `locum`, `training/fellowship`)
  - `contract_length` (text, optional)
  - `how_to_apply` (text, required, email or URL)
  - `deadline` (date, required)
  - `description` (textarea, required)
  - `consent` (checkbox, required)
  - `botcheck` (honeypot field, hidden from users)
  - Tracking metadata: `referrer`, `utm_source`, `utm_medium`, `utm_campaign`
- **Anti-spam & Validation**:
  - Honeypot check: If `botcheck` is filled, immediately redirects to thanks page without submitting.
  - Interaction duration: Requires at least 5000 ms on page before submission is allowed.
  - Client validation using HTML5 validity API.
- **Success Handling**: Redirects visitor to `/post-vacancy/thanks/`.

### 5.2 Kit Newsletter Signup (Embedded on `/`)
- **Script**: `<script async data-uid="09cc83679c" src="https://anaesthesia-ng.kit.com/09cc83679c/index.js"></script>`
- **Double Opt-In Redirect**: Post-confirmation landing target is `/thanks/`.

### 5.3 Opportunities Filter & Board (`/opportunities/`)
- Dynamic filtering by `state`, `type`, and `specialty` without page reload.
- Empty state indicator toggles when no vacancies match active filter combination.

### 5.4 Client Search (`/search/`)
- Fetches `/search-index.json`.
- Filters articles, notes, and pages by title, category, and excerpt based on the `q` query parameter.

---

## 6. Analytics Events and Data Flow

Analytics are managed client-side in `assets/analytics.js` using PostHog, gated by an explicit consent banner.

- **Configuration**: PostHog API host `https://us.i.posthog.com` (project key omitted from audit).
- **Consent Mechanism**:
  - Stored in `localStorage` under `anaesthesia.ng.analytics_consent` (`"granted"` or `"denied"`).
  - Fixed consent banner (`#ana-consent`) displays on first visit.
  - If undecided, early events are queued (up to 10 events) and flushed upon consent.
- **Privacy Guard**: Automatically strips PII keys (email, name, phone, etc.) and email-shaped string values from event properties.
- **Captured Events**:
  - `$pageview` — Fired on initial page load and on History API state changes (`pushState`, `replaceState`, `popstate`).
  - `article_read` — Triggered when user scrolls to 75% depth on `article.prose[data-slug]`. Includes `{ slug }`.
  - `book_downloaded` — Fired on clicks of links targeting `.pdf` or elements with `download` attribute. Includes `{ title }`.
  - `opportunities_viewed` — Fired on `/opportunities/` load. Includes `{ listings_count }`.
  - `filter_used` — Fired when vacancy board filter selects change. Includes `{ filter, value }`.
  - `post_vacancy_cta_clicked` — Fired on click of `[data-cta]`. Includes `{ location }`.
  - `opportunity_viewed` — Fired on `/opportunities/[slug]/` load. Includes `{ slug }`.
  - `opportunity_apply_clicked` — Fired on click of `[data-apply]`. Includes `{ slug }`.
  - `vacancy_form_started` — Fired on first `focusin` within `#vacancy-form`.
  - `vacancy_submitted` — Fired upon loading `/post-vacancy/thanks/`.
  - `site_search` — Fired when query runs on `/search/`. Includes `{ query, results_count }`.
  - `signup_completed`, `login_completed`, `logout` — Prepared methods on `window.Analytics`.
  - `quiz_started`, `quiz_completed` — Prepared methods on `window.Analytics`.
  - `email_subscribed` — Prepared method on `window.Analytics`.
  - `question_contributed` — Prepared method on `window.Analytics`.
  - Session reset via `[data-logout]` click.

---

## 7. Baseline Lighthouse Scores

- **Lighthouse mobile scores**: not measured.
- Baseline characteristics: Static zero-server-overhead build, zero runtime dependencies on content pages, minimal CSS/JS footprint.
