# DESIGN.md: anaesthesia.ng

Version 1, November 2026. Owner: J. R. Decker.

## How to use this file

- Read this file in full before any UI change.
- Sections 2 to 4 define design tokens. Implement them once in `src/styles/tokens.css`. Components reference tokens only. No hard-coded colors, font sizes or spacing values.
- Sections 5 to 7 define components and pages. Build only what is listed.
- If a request conflicts with this file, stop and ask.
- Items marked `[CONFIRM]` are open decisions. Use the stated default and flag them in the pull request.

---

## 1. Positioning

**One sentence.** The reference and opportunity platform for anaesthesia in Nigeria.

**Audience, in priority order**
1. Exam candidates and trainees (WACS, NPMCN). Heaviest use. Phone first, short sessions, often on mobile data.
2. Practising anaesthetists. Look for reference material and jobs.
3. Hospitals and departments. Post vacancies.

**Tone.** Clinical authority, calm, fast. Reads like a good medical journal built by a product team. Plain verbs, short sentences, sentence case everywhere. No hype words, no exclamation marks.

**The memorable element.** The Home hero is a live sample exam question the visitor can answer immediately. It is the most characteristic thing in this subject's world. Everything else on the site stays quiet and disciplined around it.

**Principles**
1. Content first. Each screen answers one question quickly.
2. Information is dense and scannable. Ornament must earn its place.
3. One primary action per section.
4. Built for a mid-range Android phone on a slow, costly connection.
5. Trust is visible: author, affiliation, last reviewed date, references.
6. Numbers and doses must be unambiguous. Typography is chosen for character legibility.

**Hard constraints**
- Mobile first. Design at 360 px wide, then scale up.
- HTML, CSS and JS per page: at most 150 KB compressed, excluding fonts and images.
- Zero layout shift. Images carry width and height. Fonts use size-adjusted fallback faces.
- Static site on GitHub Pages. Client JS only where interaction requires it.
- WCAG 2.2 AA minimum.
- Light theme only in v1. Tokens are semantic so dark mode can be added later.

**Ban list.** Never use:
- Gradients, glassmorphism, blur panels, floating blobs.
- Emoji as icons.
- Stock-photo heroes.
- Centered-everything layouts.
- Rows of identical icon cards as the structure of a page.
- Scroll-triggered or fade-and-slide-up entrance animation.
- Tracked-out all-caps labels, eyebrow labels above headings.
- Accenting a single word of a headline in a different color or style.
- Numbered markers (01, 02, 03) on content that is not a real sequence.
- Arrows or symbols appended to button and link text.
- Em dashes anywhere in the interface copy.
- Lorem ipsum, fake testimonials, fake statistics.

**Copy rules**
- Write for the user in plain language. Name things by what they do.
- A button says exactly what happens: "Get the book", "Save changes", "Post vacancy". The same action keeps the same name through the whole flow.
- Errors say what went wrong and how to fix it. They do not apologize.
- Empty states invite an action.
- Sentence case for all headings, labels and buttons.

---

## 2. Typography

**Families.** Self-host, WOFF2, Latin subset, variable fonts, one file per family and style, `font-display: swap`. Fonts total under 150 KB. Define size-adjusted fallback faces to prevent layout shift.

- Sans (UI, h3 and below): **Atkinson Hyperlegible Next**, variable font (weight range 200 800). If unavailable, use Atkinson Hyperlegible. It was designed for distinct characters (0 and O, 1 and l and I), which matters for doses and values.
- Serif (h1, h2, long-form reading): **Literata**, variable font (weight range 200 900), plus italic variable font. It was designed for sustained on-screen reading on modest devices.

**Rule.** Serif for h1, h2 and article body. Sans for everything else: navigation, buttons, forms, tables, cards, labels.

**Scale.** Modular scale, ratio 1.25, base 16 px: $s_n = 16 \cdot 1.25^{n}$ px, rounded.

| Token | n | Size | Use |
|---|---|---|---|
| `--text-xs` | -1 | 13 px (0.8125rem) | meta, captions, badges |
| `--text-base` | 0 | 16 px (1rem) | UI text, body |
| `--text-md` | 1 | 20 px (1.25rem) | lede, h3, list titles |
| `--text-lg` | 2 | 25 px (1.5625rem) | h1 mobile, h2 desktop |
| `--text-xl` | 3 | 31 px (1.953rem) | display mobile |
| `--text-2xl` | 4 | 39 px (2.441rem) | h1 desktop |
| `--text-3xl` | 5 | 49 px (3.052rem) | display desktop |
| `--text-read` | off-scale | 18 px (1.125rem) | article body only |

**Roles**

| Role | Family | Mobile | Desktop | Weight | Line height | Tracking |
|---|---|---|---|---|---|---|
| Display (Home hero only) | Serif | xl | 3xl | 600 | 1.15 | -0.01em |
| h1 | Serif | lg | 2xl | 600 | 1.15 | -0.01em |
| h2 | Serif | md | lg | 600 | 1.2 | 0 |
| h3 | Sans | md | md | 700 | 1.3 | 0 |
| Lede | Sans | md | md | 400 | 1.5 | 0 |
| UI body | Sans | base | base | 400 | 1.6 | 0 |
| Article body | Serif | read | read | 400 | 1.7 | 0 |
| Meta and captions | Sans | xs | xs | 400 | 1.4 | 0 |
| Button | Sans | base | base | 700 | 1 | 0 |

- Use tabular figures (`font-variant-numeric: tabular-nums`) in tables, vacancy rows and quiz progress.
- Article column is 680 px, about 65 characters. UI paragraphs max 65ch.
- Body links: `--action` color, always underlined (1 px, offset 0.15em). Hover uses `--action-hover`.

```css
:root {
  --font-sans: "Atkinson Hyperlegible Next", "Atkinson Hyperlegible", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --font-serif: "Literata", Georgia, "Times New Roman", serif;
  --text-xs: 0.8125rem;
  --text-base: 1rem;
  --text-md: 1.25rem;
  --text-lg: 1.5625rem;
  --text-xl: 1.953rem;
  --text-2xl: 2.441rem;
  --text-3xl: 3.052rem;
  --text-read: 1.125rem;
}
```

---

## 3. Palette

One brand hue (deep teal), a cool neutral ramp, one amber accent, status colors. Teal reads clinical and calm without the default medical blue.

```css
:root {
  /* neutrals */
  --n-0: #FFFFFF;  --n-50: #F7F8F8;  --n-100: #EEF0F1; --n-200: #DDE1E3; --n-300: #C3C9CD;
  --n-400: #9AA3A9; --n-500: #67727A; --n-600: #4F5A62; --n-700: #353E45; --n-800: #1F262B; --n-900: #11161A;
  /* brand */
  --brand-50: #E8F4F3;  --brand-100: #CFE8E6; --brand-300: #7FBFBA; --brand-500: #1F8A85;
  --brand-700: #0B5D5B; --brand-800: #084745; --brand-900: #05302F;
  /* accent */
  --accent-50: #FEF3E2; --accent-700: #B45309;
  /* status */
  --success: #1B7F3B; --success-bg: #EAF6EE;
  --error: #B42318;   --error-bg: #FDECEA;

  /* semantic layer: components use these only */
  --bg: var(--n-0);
  --bg-subtle: var(--n-50);
  --text-strong: var(--n-900);
  --text: var(--n-800);
  --text-secondary: var(--n-600);
  --text-muted: var(--n-500);
  --border: var(--n-200);
  --border-input: var(--n-300);
  --action: var(--brand-700);
  --action-hover: var(--brand-800);
  --action-pressed: var(--brand-900);
  --focus: var(--brand-700);
}
```

**Usage**

| Need | Token |
|---|---|
| Page background | `--bg` |
| Alternate section band, table header | `--bg-subtle` |
| Headings | `--text-strong` |
| Body text | `--text` |
| Secondary text | `--text-secondary` |
| Meta text (minimum allowed for text) | `--text-muted` |
| Dividers, card borders | `--border` |
| Input borders | `--border-input` |
| Primary buttons, links, active nav, selected states | `--action` |
| Tinted callout and selected backgrounds | `--brand-50` |
| Footer background | `--brand-900` |
| New badges, exam tips, warnings | `--accent-700` on `--accent-50` |
| Correct answer, success | `--success` on `--success-bg` |
| Errors, incorrect answer | `--error` on `--error-bg` |

**Rules**
- `--brand-500` and `--n-400` are for decoration and text of 25 px and above only.
- Amber never appears on buttons.
- Color never carries meaning alone. Pair it with text or an icon.
- All text pairs must reach 4.5:1 contrast (3:1 for text of 25 px and above).
- Approximate contrast on white, computed by hand, to be re-verified with a checker in the build: `--text` over 14:1, `--text-secondary` 7:1, `--text-muted` 4.9:1, `--action` 7.7:1, `--accent-700` 5.5:1, `--success` 5.1:1, `--error` 6.6:1.
- On `--brand-900` surfaces, text and focus rings use `--n-0`.

---

## 4. Spacing, shape and motion

**Spacing.** Base unit 4 px: $4k$ px with $k \in \{1, 2, 3, 4, 6, 8, 12, 16\}$.

```css
:root {
  --space-1: 0.25rem; --space-2: 0.5rem; --space-3: 0.75rem; --space-4: 1rem;
  --space-6: 1.5rem;  --space-8: 2rem;   --space-12: 3rem;   --space-16: 4rem;
  --radius-sm: 4px;   --radius: 6px;     --radius-lg: 10px;
  --shadow-pop: 0 4px 16px rgba(17, 22, 26, 0.08);
}
```

- Component padding: `--space-4`, panels `--space-6` on desktop.
- Gap between related elements: `--space-2` to `--space-4`. Between groups: `--space-6` to `--space-8`.
- Section vertical padding: `--space-12` mobile, `--space-16` desktop. Home hero on desktop: `--space-16` plus `--space-8`.

**Layout**
- Breakpoints (min-width): 480, 768, 1120.
- Container: max 1120 px. Gutters 16 px, 24 px from 768 px.
- Reading column: 680 px.
- Grid: 4 columns mobile, 8 at 768 px, 12 at 1120 px. Gap 16 px, 24 px from 768 px.
- Alignment: left-aligned text everywhere. Center only single-purpose blocks such as the 404 page.

**Shape**
- Radius by hierarchy: `--radius-sm` for badges, `--radius` for buttons, inputs and option rows, `--radius-lg` for panels, featured cards and dialogs.
- Surfaces are separated by 1 px borders in `--border`. No shadows on cards.
- `--shadow-pop` for menus and dialogs only.
- Focus: 2 px solid `--focus`, offset 2 px. Always visible, never removed.
- Tap targets at least 44 by 44 px.
- Icons: inline SVG, outline style, 1.5 px stroke, 20 px, one set (Lucide). Icons never carry meaning alone.
- Images: WebP or AVIF, explicit width and height, lazy-load below the fold. Prefer diagrams and screenshots. Use real photographs only when supplied by the author or with permission. No stock photos.

**Motion**
- Interaction feedback only: 150 ms ease-out on color, border-color and a transform of at most 2 px.
- No load or scroll animation. The single exception is the answer reveal in the quiz (section 5.9).
- Respect `prefers-reduced-motion`.

---

## 5. Layout patterns and components

Define each once as a reusable component. Pages compose them.

### 5.1 Site header
- Height 56 px mobile, 64 px desktop. Sticky on desktop only. 1 px bottom border.
- Left: wordmark "anaesthesia.ng" in sans 700, `--text-md`, `--text-strong`. Text only, no logo mark in v1.
- Desktop navigation: Library, Question bank, Opportunities, Community, About. Active item in `--action` with a 2 px bottom border. Right side: "Sign in" as a secondary button.
- Mobile: wordmark and a "Menu" button with text label. The menu opens a full-width panel below the header with 56 px tall links.

### 5.2 Page header
- Optional breadcrumb (meta style), h1, lede (max 60ch), optional meta row.
- Vertical padding `--space-12` mobile, `--space-16` desktop. 1 px bottom border.

### 5.3 Buttons
- Height 44 px, horizontal padding 20 px, `--radius`, sans 700.
- Primary: `--action` background, white text. Hover `--action-hover`. Pressed `--action-pressed`.
- Secondary: white background, 1 px `--action` border, `--action` text. Hover `--brand-50` background.
- Text button: `--action`, underlined.
- One primary button per section. Full width on mobile when alone in a form.
- Loading: label stays, 16 px spinner on the left, button disabled.

### 5.4 Badges
- `--text-xs`, sans 700, padding 2 px 8 px, `--radius-sm`, sentence case.
- Neutral: `--n-100` background, `--n-700` text. Brand: `--brand-50` and `--action`. Accent: `--accent-50` and `--accent-700`.

### 5.5 Content row (articles and notes)
Used in the Library and "Latest" lists. A list with 1 px dividers, no cards.
- Title (sans 700, `--text-md`, `--text-strong`) as the whole-row link. Hover changes title color to `--action`.
- One to two lines of excerpt in `--text-secondary`. Meta line: content type badge, topic, reading time, last reviewed date.
- Vertical padding `--space-4`. Desktop: title and excerpt left, meta right-aligned.

### 5.6 Feature card (book and Anki decks only)
Cards exist for visual products and nowhere else. Maximum two per row.
- `--radius-lg`, 1 px border, `--space-6` padding. Cover image or typographic cover at the top, title, one-sentence description, one button.
- Hover: border color changes to `--brand-300`.

### 5.7 Vacancy row
Dense list, not cards. Whole row is a link.
- Line 1: job title (sans 700, `--text-md`). Line 2: hospital and state. Line 3 (badges): role level, type.
- Right column on desktop: posted date and closing date, tabular figures. On mobile these sit under the badges.
- Vertical padding `--space-4`, 1 px divider. Closing within 7 days gets an accent badge reading "Closes soon".

### 5.8 Article layout
- Single 680 px column. Serif body at `--text-read`, line height 1.7.
- Page header carries the byline: "By J. R. Decker, Aminu Kano Teaching Hospital", published date, last reviewed date.
- Callout blocks with a text label, 3 px left border, `--radius`: "Clinical pearl" (`--brand-50`, `--action` border), "Exam tip" (`--accent-50`, `--accent-700` border), "Warning" (`--error-bg`, `--error` border).
- Tables scroll horizontally inside their own container. Header row `--bg-subtle`, bold, 1 px row dividers.
- End matter: references list, "Educational use only, not clinical advice" line with link to the full disclaimer, then related items as content rows.

### 5.9 Quiz screen
- Top: 4 px progress bar in `--action`, then "Question 12 of 40" in meta style with tabular figures.
- Stem: serif at `--text-read`.
- Options: full-width rows, minimum height 56 px, 1 px `--border-input`, `--radius`, with a letter marker (A to E) at the left. Selected: 2 px `--action` border and `--brand-50` background.
- After answering: correct row shows `--success` border, `--success-bg` and a check icon with the word "Correct". A wrong selection shows `--error` styling, an x icon and the word "Incorrect". The explanation panel (`--bg-subtle`, `--radius-lg`) opens beneath with the explanation and reference. This reveal is the one allowed animation: 150 ms height and opacity.
- Mobile: a fixed bottom action bar holds one primary button, "Check answer", which becomes "Next question" after answering.

### 5.10 Forms
- Single column. Label above field. Helper text in meta style.
- Inputs 44 px tall, 1 px `--border-input`, `--radius`, 16 px text to prevent mobile zoom. Focus uses the standard focus ring.
- Validate on blur. Error text sits under the field in `--error` with an icon. The field border turns `--error`.
- Required fields are marked "(required)" in the label. Optional fields are marked "(optional)".
- On success the form is replaced by a confirmation panel that states what happens next.

### 5.11 Email capture
- Single email field and one button. Inline on desktop, stacked on mobile.
- Button text states the outcome, for example "Get the book".
- Beneath: "Free. Unsubscribe any time." plus a link to the privacy page.
- Success state: "Check your inbox for the download link."

### 5.12 States
- Empty: heading, one sentence, one action. No illustration.
- Loading: skeleton blocks in `--n-100` matching the final layout. Spinners only inside buttons.
- Error: what happened, how to fix it, a retry button.
- Auth gate: when a signed-out visitor reaches a gated page, show what they will get and a "Sign in" and "Create account" pair.

### 5.13 Footer
- Background `--brand-900`, text `--n-0`.
- Up to three columns: Study (Library, Question bank, WACS Update Book), Work (Opportunities, Post a vacancy), Site (About, Privacy, Terms, Medical disclaimer).
- Bottom line: "anaesthesia.ng. Educational content for anaesthetists in Nigeria. Not a substitute for clinical judgment."

---

## 6. References

Open each site before keeping it, because designs change. Treat them as direction for specific qualities. Never copy markup, branding or imagery. `[CONFIRM]` Replace any entry you dislike.

| Site | Copy this | Do not copy |
|---|---|---|
| stripe.com (docs and marketing pages) | Type hierarchy, heading-to-body size ratio, whitespace between sections, restrained color | Gradient heroes, heavy animation |
| nejm.org (article pages) | Long-form reading layout, serif body, how references and figures are handled | Dense journal chrome, paywall patterns |
| linear.app | Restraint, tight type, neutral palette with one accent, crisp borders | Dark hero, motion effects |
| design-system.service.gov.uk | Form patterns, error messaging, accessibility, plain language | Visual identity |
| wellfound.com (job listings) | Scannable vacancy lists and filters | Visual clutter |

**Reference screenshots**
- Capture the specific pages at the viewport sizes listed below and save them locally in `design/refs/`.
- Name each file for what to take from it, for example `stripe-docs-heading-ratio-1280.png`.
- `design/refs/` is listed in `.gitignore`. Never commit, publish or embed these screenshots. They are third-party material used for direction only.
- The agent reads them from the local folder when the prompt names them. If a file is missing, the agent works from the written "Copy this" column and does not guess.

| File | Page | Viewports |
|---|---|---|
| `stripe-docs-heading-ratio-1280.png`, `-360.png` | Any docs article | 1280, 360 |
| `nejm-article-reading-layout-1280.png`, `-360.png` | Any free-access article | 1280, 360 |
| `linear-home-restraint-1280.png` | Home page | 1280 |
| `govuk-form-errors-360.png` | Text input and error message component pages | 360 |
| `wellfound-job-list-1280.png`, `-360.png` | Job list view (or another job board's list) | 1280, 360 |

---

## 7. Page-by-page plan

**Sitemap**

```
/                          Home
/wacs-update-book          Book landing and email capture
/library                   Index of articles, notes, decks
/library/[slug]            Article
/question-bank             Landing and filters
/question-bank/session     Quiz screen (sign-in required)
/community                 Overview
/community/submit          Submit a question
/opportunities             Vacancy board
/opportunities/[id]        Vacancy detail
/opportunities/post        Post a vacancy
/locum                     Placeholder
/equipment                 Placeholder
/about
/sign-in  /sign-up         Auth screens (design only; backend decided separately)
/privacy  /terms  /medical-disclaimer    Article layout, plain text
/404
```

Each page below lists purpose, primary action, sections in order, states and mobile notes.

### Home (/)
- **Purpose:** show what the site is and get the visitor studying within one tap.
- **Primary action:** answer the sample question, then start the question bank.
- **Sections**
  1. Hero. Display headline, lede, and the live sample question on the right at 1120 px and above, directly below the headline on mobile. Two buttons: "Start the question bank" (primary) and "Browse vacancies" (secondary).
  2. Two paths. Two side-by-side text panels separated by a 1 px divider. "Study": question bank, WACS Update Book, library. "Work": vacancies for anaesthetists, posting a vacancy for hospitals. Each panel has a heading, two lines and a text link.
  3. Free book band (`--bg-subtle`). Book cover, one-sentence description, email capture.
  4. Latest from the library: five content rows and a "View the library" text link.
  5. Author line: "By J. R. Decker, Aminu Kano Teaching Hospital." Two sentences on purpose and how content is reviewed. `[CONFIRM wording]`
- **Draft copy**
  - Headline: "The anaesthesia reference for Nigeria."
  - Lede: "Exam preparation, clinical notes and vacancies for Nigerian anaesthetists and trainees."
  - Sample question: `[CONFIRM: supply one real SBA question with five options and an explanation]`
- **States:** sample question is interactive without sign-in and shows the quiz reveal pattern.
- **Mobile:** headline, lede, question, buttons, then the rest in the order above.

```
Desktop hero
+--------------------------------------------------+
| anaesthesia.ng   Library  Question bank ...  Sign in |
+--------------------------------------------------+
| The anaesthesia reference     | Sample question  |
| for Nigeria.                  | stem...          |
| Lede text.                    | ( ) A  ( ) B ... |
| [Start the question bank]     | [Check answer]   |
| [Browse vacancies]            |                  |
+--------------------------------------------------+
```

### WACS Update Book (/wacs-update-book)
- **Purpose:** convert visitors into email subscribers with the free book.
- **Primary action:** "Get the book".
- **Sections:** page header with title "WACS Update Book, 2026 Edition" and a one-sentence description. Email capture directly beneath. Cover image. "What is inside" as a plain list of topic areas. "About the author" line. A short FAQ (what is it, who is it for, how is it delivered).
- **States:** success panel after submit. Error state if the email is invalid or the request fails.
- **Mobile:** email capture appears before the cover image.

### Library (/library)
- **Purpose:** find study material fast.
- **Primary action:** open an item.
- **Sections:** page header. Filter bar with a search field, type filter (Articles, Notes, Decks, Book) and topic filter. Results as content rows. Featured products (Anki decks, book) as up to two feature cards above the list.
- **States:** empty results ("No items match. Clear filters."), loading skeleton rows.
- **Mobile:** filters collapse behind a "Filters" button that opens a full-width panel.

### Article (/library/[slug])
- **Purpose:** read and retain.
- **Primary action:** keep reading; at the end, "Practise questions on this topic".
- **Sections:** article layout from 5.8, then a topic-filtered link into the question bank, then related content rows.
- **Mobile:** same single column. Tables scroll inside their own container.

### Question bank (/question-bank)
- **Purpose:** start practising.
- **Primary action:** "Start a session".
- **Sections:** page header. Session setup: exam, topic and number of questions as three form fields. Progress summary for signed-in users (questions answered, accuracy by topic, as a simple table). Signed-out visitors see the setup and an auth gate on start.
- **States:** auth gate, empty progress ("Answer your first question to see progress").

### Quiz session (/question-bank/session)
- **Purpose:** answer questions one at a time.
- **Primary action:** "Check answer" then "Next question".
- **Sections:** quiz screen from 5.9. End screen with score, topic breakdown and two actions: "Review wrong answers" and "Start another session".
- **Mobile:** this is the primary design target. One-thumb use, fixed bottom action bar.

### Community (/community)
- **Purpose:** invite contribution.
- **Primary action:** "Submit a question".
- **Sections:** page header. Plain-language rules for contributions in five lines or fewer. Recently accepted contributions as content rows. Discussion area: `[CONFIRM: embedded chat or a link to an external group]`.
- **Copy:** "The best questions are included in the next edition of the book."

### Submit a question (/community/submit)
- **Purpose:** collect quality questions.
- **Primary action:** "Submit question".
- **Fields:** stem, options A to E, correct answer, explanation, reference, topic.
- **States:** auth gate if signed out. After submit: confirmation panel with status "Under review". Contribution statuses shown in the user's list: Under review, Accepted, Declined with reason.

### Opportunities (/opportunities)
- **Purpose:** find a vacancy.
- **Primary action:** open a vacancy.
- **Sections:** page header with a line "Free for anaesthetists." and a secondary button "Post a vacancy". Filter bar: state, role level, type, posted date. Results as vacancy rows, newest first.
- **Role levels `[CONFIRM]`:** House officer, Medical officer, Registrar, Senior registrar, Consultant, Other. **Types:** Permanent, Locum, Fellowship, Other.
- **States:** empty results ("No vacancies match. Clear filters or check back soon."), loading skeleton rows.
- **Mobile:** filters collapse behind a "Filters" button.

### Vacancy detail (/opportunities/[id])
- **Purpose:** decide and apply.
- **Primary action:** "How to apply" revealing the hospital's application method.
- **Sections:** page header with title, hospital, state. Summary table: role level, type, posted, closing, pay (if provided). Description in UI body text. How to apply. Link back to the board.
- **States:** closed vacancy shows a "Closed" badge and the apply section is replaced by a link to current vacancies.

### Post a vacancy (/opportunities/post)
- **Purpose:** let hospitals submit vacancies with low friction.
- **Primary action:** "Post vacancy".
- **Fields:** hospital name, contact name, contact email, contact phone, job title, role level, type, state, description, closing date, how to apply, pay (optional).
- **States:** confirmation panel stating that the vacancy is reviewed before it appears and that the contact email receives a copy. `[CONFIRM review turnaround wording]`

### LocumLink and Equipment market (/locum, /equipment)
- **Purpose:** hold the place and collect interest.
- **Primary action:** "Notify me".
- **Sections:** page header, two sentences on what is coming, email capture.

### About (/about)
- **Purpose:** establish credibility.
- **Primary action:** "Contact".
- **Sections:** who runs the site (J. R. Decker, Anaesthesia Registrar, Aminu Kano Teaching Hospital) `[CONFIRM wording]`, what the site offers, how content is written and reviewed, contact line.

### Auth screens (/sign-in, /sign-up)
- **Design only.** Single-column forms in the form pattern. Sign-in: email and password, "Sign in", links to "Create account" and "Reset password". Sign-up: name, email, password, consent line with privacy link, "Create account".
- **States:** invalid credentials ("Email or password is incorrect. Check both and try again."), verification pending panel.

### Legal pages (/privacy, /terms, /medical-disclaimer)
- Use the article layout with sans body at `--text-base`. Plain language.

### 404
- Centered single block: heading "This page does not exist.", one sentence, button "Go to the home page", text link "Search the library".

---

## 8. Build order and acceptance

### 8.1 Build order

Each step is one branch, one pull request and one fresh Claude Code session. Do not start the next step until the current one passes its checks in 8.3.

**Step 0. Audit (read-only)**
- List every current page, route and piece of content that must survive.
- Record the current Lighthouse mobile scores as a baseline.
- List existing functionality that must keep working: vacancy board, post-a-vacancy form, email capture, analytics events.
- Output: `/design/audit.md`. No code changes except adding `design/refs/` to `.gitignore`.

**Step 1. Tokens and base**
- `src/styles/tokens.css` with every token from sections 2 to 4.
- Self-hosted font files, reset, base typography, container, grid, focus styles, skip link.
- A `/styleguide` page (`noindex`) showing every token and every type role.

**Step 2. Components**
- Build on `/styleguide` with all states shown (default, hover, focus, disabled, error, loading, empty).
- Order: buttons, badges, forms, site header, footer, page header, content row, feature card, vacancy row, article layout and callouts, email capture, quiz screen, state patterns.

**Step 3. Pages**
- Order: Home, WACS Update Book, Library and Article template, Question bank and Quiz session, Opportunities (board, detail, post form), Community, About, Legal pages, 404, placeholders.
- Question bank screens use sample data. The backend is decided and built separately.

**Step 4. Audit and cleanup**
- Cross-page consistency review against this file.
- Copy pass against the rules in section 1.
- Performance and accessibility pass.
- Remove dead CSS and unused assets.

### 8.2 Rules while building

- Restyle only. Existing form endpoints, data flow and analytics events stay unchanged.
- Confirm `design/refs/` is in `.gitignore` before the first commit. Third-party screenshots never enter the repository.
- Keep the existing stack. Add no UI framework or component library. Add dependencies only with approval.
- Tokens only. Zero hex colors or hard-coded font sizes outside `tokens.css`.
- Do not invent facts, statistics, testimonials or clinical content. Use a visible `[CONFIRM]` placeholder in code comments and list each one in the pull request.
- Commit after each component or page with a message that names it.
- When a requirement is unclear, ask before building.

### 8.3 Acceptance checks, per page, before merge

**Layout**
- No horizontal scroll at 360, 768, 1120 and 1440 px.
- Tap targets are at least 44 by 44 px.

**Accessibility**
- Every interactive element is reachable by keyboard with a visible focus ring and a logical order.
- Skip link to main content works.
- All text meets the contrast rules in section 3.
- Lighthouse accessibility score of at least 95 and zero critical axe violations.
- Images have alt text. Decorative images have empty alt text.
- `prefers-reduced-motion` is honored.

**Performance (mobile, throttled)**
- Lighthouse performance score of at least 90.
- Largest Contentful Paint under 2.5 s. Cumulative Layout Shift under 0.1.
- HTML, CSS and JS together under 150 KB compressed.
- At most two preloaded font files. Images have width and height.

**Content and design**
- Copy follows section 1: sentence case, no em dashes, no exclamation marks, no ban-list items.
- One h1 per page, a unique title and meta description, semantic landmarks.
- Screenshots at 360 px and 1120 px attached to the pull request.

**Functionality**
- Forms submit, links resolve, analytics events fire, existing features behave as before.

### 8.4 Session discipline (for the person running Claude Code)

- Resolve every `[CONFIRM]` item and collect reference screenshots before the paid month starts. Do that work in free chat.
- Keep `CLAUDE.md` short: one line pointing to this file plus the build and test commands.
- One step per session. Run `/clear` between unrelated tasks.
- Use plan mode (Shift+Tab) for any multi-file step. Approve the plan before code is written.
- Choose the model at the start of a session and stay on it. Switching mid-session forces the whole conversation to be re-read at full price.
- Within one task, use `/compact` with instructions, for example `/compact Focus on tokens.css and the component list`. If the last few turns went the wrong way, use `/rewind`.
- Check `/usage` regularly.
- Commit before each step so a bad run is cheap to revert.
