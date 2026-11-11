# Whatta Match Media website

The complete website, ready to put online. No installs needed to publish it.

```
site/            ← the website itself. This folder is what goes online.
build.py         ← the copy and settings for every page (for edits, see below)
README.md        ← this guide
```

## Put it online in 2 minutes (Netlify Drop)

1. Go to **app.netlify.com/drop** on a computer.
2. Drag the **`site`** folder onto the page.
3. Netlify gives you a live link straight away (something like `whatta-match.netlify.app`). Open it on your phone and laptop to review.
4. Create a free Netlify account when asked, so the site stays up permanently.
5. To use your own domain: in Netlify go to **Domain management → Add a domain** and follow the steps. HTTPS is set up for you.

Any static host works the same way (Vercel, Cloudflare Pages, GitHub Pages): upload the contents of `site/`.

## Before you launch: 5 things to set

Open `build.py` in any text editor. The settings are at the top:

| Setting | What to put |
| --- | --- |
| `DOMAIN` | Your real web address, e.g. `https://www.whattamatch.com` |
| `EMAIL` | The inbox that should receive enquiries |
| `FORM_ENDPOINT` | Your Formspree link (see below). Until set, forms go straight to the thank-you page and **no message is sent** |
| `BOOKING_URL` | Your Calendly or Cal.com link |
| `SOCIAL` | Your LinkedIn and Instagram URLs |

**Making the forms send to your inbox (free):** sign up at formspree.io, create a form, and copy its URL (looks like `https://formspree.io/f/abcdwxyz`). Paste it as `FORM_ENDPOINT`.

After editing `build.py`, rebuild the pages by running `python3 build.py` in this folder (Python 3 comes with every Mac), then drag `site` onto Netlify again. If you'd rather not touch code, send the changes to Claude and get an updated zip back.

## Placeholder content to check

These are written as sensible defaults. Confirm or change them before launch:

- **"We reply to every brief within one working day"** and the **24-hour** counter on the homepage. Remove if you can't commit to this.
- **Cities on the globe section** (Mumbai, Dubai, London, Singapore, New York). Change to the markets you actually serve.
- **Budget ranges** on the contact form are in USD.
- **Founder bios** say "Full bio coming soon". Send your LinkedIn PDFs to have them written.
- **Founder LinkedIn links** on the About page point to linkedin.com. Add your profile URLs.
- **Case studies** show "Case study coming soon" cards. The template for a real case study is at `site/work/case-study.html`.
- **Legal pages** (privacy, terms, cookies) are plain-language starting points. Have them reviewed by a lawyer.

## What's inside

- **Home** (6 sections: hero, the match moment, services, how we work, work, contact) with the live 3D Match Line, built on the wave from your logo. It draws itself on load and flows gently like a ribbon. At **"That moment is the match"** it breaks into a W (your brand) and an M (your people) that drift apart and then lock back together into the wave. In the pinned **Services** chapter it redraws itself, like a pen, into a symbol for each of the seven disciplines: a compass (Consulting), a target (Brand Strategy), a four-point star (Brand Identity & Design), a play button (Content & Creative), a speech bubble (Social & Influence), a rising arrow (Performance & Growth) and a laptop (Media & Digital Experiences). It then travels down the right-hand margin and returns full-size at the contact finale.
- **Page headers**: on every inner page the Match Line sweeps in from the right edge and draws itself, instead of a small mark above the title.
- **Background**: one ink-blue gradient across the site, with a perspective grid receding to the horizon and fine film grain for depth.
- **About, Services hub (each tile carries its discipline's orange symbol) + 7 service pages, including Consulting, Work, case study template, Insights + 3 articles, Careers, Contact** with the "Find your match" brief builder, **Privacy, Terms, Cookies, 404** ("No match found") and **Thank you**.
- **Mobile**: a lighter 3D scene and a full-screen menu.
- **Accessibility**: WCAG 2.2 AA colour pairings from your guidelines, keyboard navigation, skip link, and a reduced-motion mode that freezes the 3D.
- **Fallback**: devices without WebGL see your static wave instead.
- **SEO**: page titles and descriptions, Open Graph share image, structured data (Organization, Service, FAQ, Article, Person), `sitemap.xml`, `robots.txt` and `llms.txt` for AI search.
- **Performance**: three.js is self-hosted (`assets/js/vendor/`), no other dependencies. Fonts come from Google Fonts.

## Tech notes for a developer

- Plain HTML, CSS and JavaScript. No framework or build step required to host.
- `assets/js/matchline.js`: the 3D scene (three.js r128). Scroll poses are the `KEYS` list: each entry pins a pose (position, rotation, scale, fade) to a point on the page, joined by a Catmull-Rom spline for one continuous path; the fourth item overrides values on mobile. The ribbon flow runs in the vertex shader (`uFlow`, `uTime`). The service shapes are the `SHAPES` list (each one continuous line, resampled to the same number of points so they morph cleanly).
- `assets/js/main.js`: navigation, reveals, counters, cursor, forms, brief builder, cookie notice.
- `assets/css/main.css`: the full design system, with brand tokens at the top.
- `build.py`: generates every HTML page from shared header, footer and content data.
