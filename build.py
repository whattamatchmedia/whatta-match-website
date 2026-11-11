#!/usr/bin/env python3
"""Builds the Whatta Match Media static site into ./site
Edit the CONTENT below, then run:  python3 build.py
"""
import json, os, re, html

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
DOMAIN = "https://whattamatchmedia.com"           # live domain (Netlify primary)
EMAIL = "hello@whattamatch.com"                 # change to the real inbox
FORM_ENDPOINT = "https://formspree.io/f/YOUR_FORM_ID"   # see README: paste your Formspree form URL
BOOKING_URL = "https://cal.com/whattamatch"     # change to your booking link
SOCIAL = [("LinkedIn", "https://www.linkedin.com/company/whatta-match-media"),
          ("Instagram", "https://www.instagram.com/whattamatchmedia")]
THREE_JS = "assets/js/vendor/three.min.js"   # three.js r128, self-hosted (MIT)

def logo(name, label="Whatta Match", cls=""):
    s = open(os.path.join(SITE, "assets/logo", name)).read()
    s = re.sub(r'\s(width|height)="[^"]*"', "", s, count=2)
    s = re.sub(r"<title>.*?</title>", "", s)
    uid = re.sub(r"\W", "", name)
    s = s.replace('id="wm-wave"', f'id="g-{uid}"').replace("url(#wm-wave)", f"url(#g-{uid})")
    return s.replace("<svg ", f'<svg role="img" aria-label="{label}" class="{cls}" ', 1)

WAVE_PATH = "M0,0 C20,0 20,120 40,120 C60,120 60,0 80,0 C100,0 100,120 120,120 C140,120 140,0 160,0 C180,0 180,120 200,120 C220,120 220,0 240,0 C260,0 260,120 280,120"
def wave_mark(cls="wave-mark", gid="wm"):
    return (f'<svg class="{cls}" viewBox="-20 -20 320 160" aria-hidden="true"><defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="-16" y1="60" x2="296" y2="60">'
            f'<stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#FF5F1F"/></linearGradient></defs>'
            f'<path d="{WAVE_PATH}" fill="none" stroke="url(#{gid})" stroke-width="32" stroke-linecap="round"/></svg>')


# ---------- Service icons (the same symbols the 3D line draws on the homepage) ----------
SVC_ICON = {
    "consulting": '<circle cx="32" cy="32" r="25"/><path d="M40 20 L36 34 L24 44 L28 30 Z"/>',
    "strategy": '<circle cx="32" cy="32" r="25"/><circle cx="32" cy="32" r="14"/><circle cx="32" cy="32" r="3.5" class="fill"/>',
    "identity": '<path d="M32 6 C34 24 40 30 58 32 C40 34 34 40 32 58 C30 40 24 34 6 32 C24 30 30 24 32 6 Z"/>',
    "content": '<path d="M22 13 L51 32 L22 51 Z"/>',
    "social": '<path d="M14 12 H50 A6 6 0 0 1 56 18 V38 A6 6 0 0 1 50 44 H28 L18 54 V44 H14 A6 6 0 0 1 8 38 V18 A6 6 0 0 1 14 12 Z"/>',
    "performance": '<path d="M7 50 L24 33 L34 42 L55 19"/><path d="M41 18 H56 V33"/>',
    "media": '<rect x="12" y="12" width="40" height="28" rx="4"/><path d="M6 50 H58"/>',
    "match": '<path d="M6 22 C14 22 14 44 22 44 C30 44 30 22 38 22 C46 22 46 44 54 44 C58 44 60 40 60 36"/>',
}
def svc_icon(kind, gid):
    return (f'<svg class="svc-ico" viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="4" y1="32" x2="60" y2="32">'
            f'<stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#FF5F1F"/></linearGradient></defs>'
            f'<g fill="none" stroke="url(#{gid})" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" style="--g:url(#{gid})">{SVC_ICON[kind]}</g></svg>')

# ---------- Pillar line-art (placeholders for case cards and service heroes) ----------
def art(kind, gid):
    g = (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FF8A3D"/>'
         f'<stop offset="1" stop-color="#FF5F1F"/></linearGradient></defs>')
    st = f'fill="none" stroke="url(#{gid})" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    shapes = {
        "strategy": f'<circle cx="100" cy="100" r="70" {st}/><path d="M100 20 L112 100 L100 180 L88 100 Z" {st}/>',
        "identity": f'<path d="M100 22 L160 62 L160 138 L100 178 L40 138 L40 62 Z M40 62 L100 100 L160 62 M100 100 L100 178" {st}/>',
        "content": f'<path d="M100 100 m0 -8 a8 8 0 1 1 -1 0 M100 100 m0 -30 a30 30 0 1 1 -1 0 M100 100 m0 -54 a54 54 0 1 1 -1 0 M100 100 m0 -78 a78 78 0 1 1 -1 0" {st}/>',
        "social": f'<path d="M30 80 L70 40 L105 75 L140 35 L172 72 L150 120 L170 160 L118 150 L80 168 L45 140 Z" {st}/>'
                  + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="url(#{gid})"/>' for x, y in [(30,80),(70,40),(105,75),(140,35),(172,72),(150,120),(170,160),(118,150),(80,168),(45,140)]),
        "performance": f'<path d="M30 40 Q100 70 170 40 M48 72 Q100 96 152 72 M66 104 Q100 120 134 104 M84 134 Q100 142 116 134 M100 150 Q140 160 175 30" {st}/>',
        "media": f'<circle cx="100" cy="100" r="72" {st}/><ellipse cx="100" cy="100" rx="30" ry="72" {st}/><path d="M28 100 H172 M40 62 Q100 76 160 62 M40 138 Q100 124 160 138" {st}/>',
    }
    return f'<svg viewBox="0 0 200 200" aria-hidden="true">{g}{shapes[kind]}</svg>'

SILHOUETTE = ('<svg viewBox="0 0 120 150" aria-hidden="true"><defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#FF5F1F"/></linearGradient></defs>'
              '<path d="M60 22 C76 22 84 34 84 50 C84 68 74 80 60 80 C46 80 36 68 36 50 C36 34 44 22 60 22 Z M14 150 C16 112 36 94 60 94 C84 94 104 112 106 150" fill="none" stroke="url(#{g})" stroke-width="5" stroke-linecap="round"/></svg>')

# ---------- Content ----------
SERVICES = [
    dict(slug="consulting", name="Consulting", art="consulting", match="Ambition to direction",
         short="Senior advice on brand, marketing and growth, from a single session to an embedded partnership.",
         promise="Clear answers to your biggest marketing questions, from people who build brands for a living.",
         who="Founders and leadership teams facing a launch, a new market, a rebrand or a marketing function that isn't delivering, who want an expert outside view before they spend.",
         deliverables=[("Brand and marketing audit", "An honest read of where your brand, channels and spend stand today, and what is holding growth back."),
                       ("Growth roadmap", "A prioritised twelve-month plan: what to do, in what order, and what it should cost."),
                       ("Market entry advisory", "What it takes to launch in a new country or category, before you commit budget."),
                       ("Team and agency structure", "Which skills to hire, which to outsource, and how to brief and measure partners."),
                       ("Fractional CMO", "Senior marketing leadership, part-time, for teams that need direction before a full hire."),
                       ("Workshops and training", "Hands-on sessions that get your leadership and marketing teams aligned and moving.")],
         steps=[("Diagnose", "We review your numbers, brand and team, and talk to the people closest to the customer."), ("Advise", "Straight answers on what to keep, what to change and what to stop."),
                ("Plan", "A roadmap with owners, budgets and measures of success."), ("Stay close", "Regular check-ins, or an embedded role, to keep the plan on track.")],
         faqs=[("How is consulting different from your other services?", "Consulting is advice and direction. If you then want the work done, the same team can deliver it."),
               ("Can we book a one-off session?", "Yes. Many clients start with a single strategy session or an audit and decide from there."),
               ("Do you offer retainers?", "Yes. Monthly advisory and fractional CMO retainers are available."),
               ("Who will we work with?", "Our founders and senior leads. Consulting is never handed to juniors."),
               ("Do you work with businesses outside India?", "Yes. We advise brands across markets and time zones, in person and remotely.")]),
    dict(slug="brand-strategy", name="Brand Strategy", art="strategy", match="Brand to purpose",
         short="Research, positioning and a plan that tells everyone where the brand is going.",
         promise="Know exactly who you are for, and why they should choose you.",
         who="Founders launching something new, businesses entering a new market, and established brands that have drifted from what made them matter.",
         deliverables=[("Audience and market research", "Interviews, category mapping and competitor audits that show where the opening is."),
                       ("Positioning", "One clear sentence on who you serve, what you offer and why it beats the alternatives."),
                       ("Brand architecture", "How your products, sub-brands and offers fit together without confusing anyone."),
                       ("Naming", "Names that are ownable, pronounceable across markets and checked for availability."),
                       ("Messaging framework", "The story, proof points and tone that every team can use."),
                       ("Go-to-market plan", "Channels, sequence and budget split for the launch or relaunch.")],
         steps=[("Listen", "Workshops with your team and research with your customers."), ("Find the gap", "We map the category and locate the position only you can own."),
                ("Define", "Positioning, story and architecture, written and tested."), ("Hand over", "A strategy your team can act on the next morning.")],
         faqs=[("How long does a strategy project take?", "Most run four to eight weeks, depending on how much research is needed."),
               ("Do we need strategy before design?", "If you are launching or changing direction, yes. Design without a position looks good and says nothing."),
               ("Can you work with our existing research?", "Yes. We start from what you already know and fill only the gaps."),
               ("What do we get at the end?", "A strategy document, a messaging framework and a working session with your team."),
               ("Do you work with businesses outside India?", "Yes. We work with brands across markets and time zones.")]),
    dict(slug="brand-identity-design", name="Brand Identity & Design", art="identity", match="Purpose to look",
         short="Logo systems, visual identity, packaging and guidelines built to scale.",
         promise="A look people recognise in half a second, everywhere you show up.",
         who="New brands that need an identity, and growing brands whose look no longer matches who they have become.",
         deliverables=[("Logo system", "Primary, secondary and symbol versions that work from a billboard to a favicon."),
                       ("Visual identity", "Colour, typography, layout and image style that hold together."),
                       ("Packaging", "Pack design that sells on the shelf and on screen."),
                       ("Motion and 3D identity", "How the brand moves, for video, web and social."),
                       ("Brand guidelines", "A clear rulebook your team and partners can follow."),
                       ("Templates", "Decks, social posts and documents ready to use on day one.")],
         steps=[("Brief", "We translate the strategy into a creative brief."), ("Explore", "Distinct directions, each built on a clear idea."),
                ("Refine", "One direction, developed across real applications."), ("System", "Files, guidelines and templates delivered.")],
         faqs=[("Do you only design logos?", "No. We design complete identity systems, of which the logo is one part."),
               ("How many concepts will we see?", "Usually two or three distinct directions, each tested on real applications."),
               ("Will we own the files?", "Yes. On final payment you own the identity and all master files."),
               ("Can you refresh rather than replace our brand?", "Yes. Often an evolution keeps the equity you have built."),
               ("Do you design packaging?", "Yes, from structure and graphics to print-ready files.")]),
    dict(slug="content-creative", name="Content & Creative", art="content", match="Look to story",
         short="Campaigns, film, photography, copy, motion and 3D that people stop for.",
         promise="Work people stop scrolling for, and remember.",
         who="Brands launching campaigns or products, and teams that need a steady flow of content that still feels made with care.",
         deliverables=[("Campaign ideas", "Big ideas that work across film, social, outdoor and retail."),
                       ("Film and photography", "Production from script to final grade."),
                       ("Copywriting", "Headlines, scripts, product copy and long-form writing."),
                       ("Motion design", "Animation for social, web and broadcast."),
                       ("3D and CGI", "Product renders and 3D scenes without a physical shoot."),
                       ("Content systems", "Monthly content built on repeatable formats.")],
         steps=[("Insight", "Find the truth about your audience the idea will stand on."), ("Idea", "One clear idea that can travel across formats."),
                ("Make", "Production in-house and with trusted partners."), ("Launch", "Assets cut for every channel and placement.")],
         faqs=[("Do you handle production?", "Yes. We produce film, photo, motion and 3D, from pre-production to delivery."),
               ("Can you make content every month?", "Yes. We set up content systems with monthly output."),
               ("Do you write in languages other than English?", "We produce work for global audiences and partner with native writers where needed."),
               ("Who owns the content?", "You do, subject to any third-party licences, which we always flag up front."),
               ("Can you work with our in-house team?", "Yes. We often plug into existing marketing teams.")]),
    dict(slug="social-influence", name="Social & Influence", art="social", match="Story to community",
         short="Social strategy, community management and creator programmes.",
         promise="A community that talks about you when you are not in the room.",
         who="Brands that want social to drive real business, and teams ready to work with creators properly.",
         deliverables=[("Social strategy", "Which platforms, what to say there and how to measure it."),
                       ("Content calendars", "Planned, produced and published every month."),
                       ("Community management", "Replies, conversation and care that build loyalty."),
                       ("Creator and influencer programmes", "Finding, briefing and managing the right creators."),
                       ("Social listening", "What people say about you and your category, in real time."),
                       ("Reporting", "Monthly reports tied to business results, not vanity metrics.")],
         steps=[("Audit", "Where you are today, and what is working."), ("Plan", "Platforms, pillars and a calendar."),
                ("Run", "Daily publishing, community care and creator work."), ("Grow", "Monthly reviews and constant testing.")],
         faqs=[("Which platforms do you cover?", "Instagram, LinkedIn, YouTube, X and emerging platforms where your audience is."),
               ("Do you manage influencers end to end?", "Yes: selection, contracts, briefs, approvals and reporting."),
               ("How do you measure success?", "Against business goals like leads, sales and retention, alongside reach and engagement."),
               ("Can we approve every post?", "Yes. You approve the calendar before anything goes live."),
               ("Is there a minimum term?", "We recommend three months to see real results.")]),
    dict(slug="performance-growth", name="Performance & Growth", art="performance", match="Attention to action",
         short="Paid media, SEO, conversion, analytics and automation.",
         promise="Turn attention into revenue you can measure.",
         who="Brands that need predictable growth and clear numbers behind every rupee, dollar or dirham spent.",
         deliverables=[("Paid search and social", "Google, Meta, LinkedIn and more, managed daily."),
                       ("SEO", "Technical, content and authority work that compounds."),
                       ("Conversion optimisation", "Testing pages and funnels to convert more of your traffic."),
                       ("Analytics and tracking", "Clean data you can trust, set up properly."),
                       ("Marketing automation", "Email and CRM journeys that sell while you sleep."),
                       ("Growth reporting", "Dashboards that show what is working and what to do next.")],
         steps=[("Measure", "Fix tracking and set a clear baseline."), ("Plan", "Channels, budgets and targets agreed."),
                ("Launch", "Campaigns live, tested from day one."), ("Optimise", "Weekly changes, monthly reviews.")],
         faqs=[("What budget do we need?", "It depends on your market and goals. We recommend a starting budget in the first call."),
               ("How soon will we see results?", "Paid media shows signal within weeks; SEO builds over months."),
               ("Do you guarantee results?", "We commit to targets we agree together, and report against them openly."),
               ("Who owns the ad accounts?", "You do. We work inside accounts you own."),
               ("Can you fix our tracking?", "Yes. It is usually the first thing we do.")]),
    dict(slug="media-digital", name="Media & Digital Experiences", art="media", match="Action to everywhere",
         short="Media planning and buying, websites, apps and e-commerce.",
         promise="Be in the right places, with experiences worth arriving at.",
         who="Brands planning media across markets, and businesses that need a website, app or store that performs.",
         deliverables=[("Media planning", "Where to spend, across digital, outdoor, print and broadcast."),
                       ("Media buying", "Negotiated rates and placements, managed and verified."),
                       ("Websites", "Fast, accessible sites designed to convert."),
                       ("Apps", "Product design and build for iOS, Android and web."),
                       ("E-commerce", "Stores built to sell, on Shopify and custom platforms."),
                       ("Maintenance", "Ongoing care, updates and improvements.")],
         steps=[("Discover", "Goals, audience and technical needs."), ("Design", "Plans and prototypes you can click through."),
                ("Build", "Development, content and testing."), ("Launch and care", "Go live, measure, improve.")],
         faqs=[("Do you buy media in multiple countries?", "Yes. We plan and buy across markets through trusted partners."),
               ("What platforms do you build websites on?", "Custom code, Webflow, WordPress and Shopify, chosen for your needs."),
               ("Will our site be accessible?", "Yes. We build to WCAG 2.2 AA."),
               ("Can you take over an existing site?", "Yes. We audit it first and recommend what to keep."),
               ("Do you offer hosting?", "We set up and manage hosting on reliable global providers.")]),
]

CASES = [("Case study coming soon", "Brand Strategy", "strategy", "strategy"),
         ("Case study coming soon", "Brand Identity & Design", "identity", "identity"),
         ("Case study coming soon", "Content & Creative", "content", "content"),
         ("Case study coming soon", "Social & Influence", "social", "social"),
         ("Case study coming soon", "Performance & Growth", "performance", "performance"),
         ("Case study coming soon", "Media & Digital", "media", "media")]

FOUNDERS = [("Nainee Sohane", "Co-founder"), ("Srushti Gadekar", "Co-founder")]

ARTICLES = [
    dict(slug="brand-is-a-match", title="Your brand is a match, not a monologue", tag="Brand", date="October 2026", read="4 min",
         lede="The brands people love are not the loudest. They are the best matched to the people they serve.",
         body=["Most brands talk about themselves. Their founding story, their values, their features. Then they wonder why nobody is listening.",
               "A brand only works when it meets someone who needed it. That meeting is the match. It is the moment a person sees a product, a message or a promise and thinks, that is for me.",
               "Strategy is how you find that person. Identity is how they recognise you. Content is what makes them stay. Media is how you show up in the right place at the right time. When these work as one, the match happens again and again.",
               "When they work apart, you get beautiful logos nobody remembers, campaigns that reach the wrong people and websites that look good and convert badly.",
               "That is why we built Whatta Match Media as one team. Not because holistic is a fashionable word, but because the match breaks wherever the handover between agencies happens.",
               "Start with one question: who is this brand perfectly matched to? Everything else follows from the answer."]),
    dict(slug="one-team-or-five", title="One team or five agencies?", tag="Strategy", date="October 2026", read="5 min",
         lede="Specialist agencies are excellent at their part. The cost is everything that falls between them.",
         body=["Many brands run a branding studio, a creative agency, a social agency, a performance agency and a web developer at the same time.",
               "Each one is good at its job. But every handover loses something. The strategy deck never reaches the person writing ads. The identity looks different on the website. The social team does not know what the media plan is buying.",
               "A single team carries one idea from the first workshop to the last ad. Decisions get made faster, budgets stop being split by politics, and results are easier to read because one team owns them.",
               "This does not mean one team does everything alone. It means one team is accountable for the whole match, and brings in specialists where they add something real.",
               "If you are managing five agencies today, ask how much of your week goes into keeping them aligned. That time is the hidden cost of the model."]),
    dict(slug="global-from-day-one", title="Building a brand for every market from day one", tag="Global", date="October 2026", read="4 min",
         lede="A brand that only works at home has to be rebuilt the day it travels. Build it to travel instead.",
         body=["Names that are hard to pronounce, colours with the wrong meaning, copy full of local idioms: these are small decisions that become expensive the moment a brand crosses a border.",
               "Building for global markets from the start is mostly discipline. Test names in several languages. Choose colours and symbols that read well across cultures. Write in clear, simple English that translates cleanly.",
               "Design systems matter too. Layouts must hold longer words in German and right-to-left text in Arabic. Typography needs the character sets you will need later.",
               "None of this makes a brand bland. The strongest global brands have a sharp point of view. They simply express it in ways people everywhere can understand.",
               "Ask early: would this work in London, Dubai and Singapore? If the answer is yes, you are ready to grow."]),
]

NAV = [("Work", "work.html"), ("Services", "services.html"), ("About", "about.html"), ("Insights", "insights.html"), ("Careers", "careers.html")]

# ---------- Layout ----------
def head(title, desc, path, depth, schema=None, extra=""):
    p = "../" * depth
    canon = DOMAIN + "/" + ("" if path == "index.html" else path)
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Whatta Match Media", "url": DOMAIN,
           "logo": DOMAIN + "/assets/logo/WM-stacked-fullcolour-for-light-bg.svg", "email": EMAIL,
           "sameAs": [s[1] for s in SOCIAL],
           "founder": [{"@type": "Person", "name": n} for n, _ in FOUNDERS],
           "description": "A global, holistic marketing and branding agency: consulting, strategy, identity, content, social, performance, media and digital under one team."}
    schemas = [org] + (schema or [])
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s)}</script>' for s in schemas)
    t = html.escape(title)
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#14284A">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Whatta Match Media">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{p}assets/logo/WM-favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}assets/logo/WM-app-icon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Red+Hat+Display:wght@700;800;900&family=Red+Hat+Mono:wght@400;500&family=Red+Hat+Text:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{p}assets/css/main.css">
{ld}{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def header(active, depth, dark=True):
    p = "../" * depth
    cur = ' aria-current="page"'
    items = "".join(f'<li><a href="{p}{h}"{cur if active == h else ""}>{n}</a></li>' for n, h in NAV)
    return f"""<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{p}index.html" aria-label="Whatta Match Media, home">{logo("WM-horizontal-fullcolour-for-dark-bg.svg", "Whatta Match Media")}</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links">Menu</button>
    <ul class="nav-links" id="nav-links">{items}<li><a class="btn btn-primary" href="{p}contact.html">Start a project <span class="arrow" aria-hidden="true">→</span></a></li></ul>
  </div>
</header>
"""

def footer(depth, scripts=""):
    p = "../" * depth
    svc = "".join(f'<li><a href="{p}services/{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)
    soc = "".join(f'<li><a href="{u}" rel="noopener" target="_blank">{n}</a></li>' for n, u in SOCIAL)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div>
        <div class="footer-logo">{logo("WM-stacked-fullcolour-for-dark-bg.svg", "Whatta Match Media")}</div>
        <p class="muted">Brands, perfectly matched. Consulting, consulting, strategy, identity, content, social, performance, media and digital under one team.</p>
        <form class="newsletter" data-endpoint="{FORM_ENDPOINT}" data-next="{p}thank-you.html">
          <label class="sr-only" for="nl-email">Email for our newsletter</label>
          <input id="nl-email" name="email" type="email" placeholder="Your email for our insights" required>
          <input type="hidden" name="form" value="newsletter">
          <button class="btn btn-ghost" type="submit">Subscribe</button>
        </form>
      </div>
      <div><h4>Services</h4><ul>{svc}</ul></div>
      <div><h4>Company</h4><ul><li><a href="{p}about.html">About</a></li><li><a href="{p}work.html">Work</a></li><li><a href="{p}insights.html">Insights</a></li><li><a href="{p}careers.html">Careers</a></li><li><a href="{p}contact.html">Contact</a></li></ul></div>
      <div><h4>Connect</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li>{soc}</ul></div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>2026</span> Whatta Match Media</span>
      <span><a href="{p}privacy.html">Privacy</a> · <a href="{p}terms.html">Terms</a> · <a href="{p}cookies.html">Cookies</a></span>
    </div>
  </div>
</footer>
<div class="cookie" hidden role="region" aria-label="Cookie notice">
  <p>We use essential cookies to run this site and, with your permission, analytics to improve it. <a class="link" href="{p}cookies.html">Cookie policy</a></p>
  <div class="btn-row"><button class="btn btn-ghost" type="button" data-choice="essential">Essential only</button><button class="btn btn-primary" type="button" data-choice="all">Accept all</button></div>
</div>
<script src="{p}assets/js/main.js"></script>
{scripts}
</body>
</html>
"""

def contact_block(depth, title="Let's find your <span class=\"serif\">match.</span>"):
    p = "../" * depth
    return f"""<section class="sec">
  <div class="wrap grid-2">
    <div class="reveal"><p class="eyebrow">Start a project</p><h2 class="h2">{title}</h2></div>
    <div class="reveal" style="align-self:end;display:grid;gap:22px">
      <p class="lede">Tell us where you want to go. We reply to every brief within one working day.</p>
      <div class="btn-row"><a class="btn btn-primary" href="{p}contact.html">Start a project <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="mailto:{EMAIL}">{EMAIL}</a></div>
    </div>
  </div>
</section>
"""

def hero_line(gid):
    # The Match Line runs through every page header, entering from the right edge
    return (f'<svg class="ph-line" viewBox="-20 -20 600 160" aria-hidden="true" preserveAspectRatio="xMinYMid meet"><defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="-16" y1="60" x2="580" y2="60">'
            f'<stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#FF5F1F"/></linearGradient></defs>'
            f'<path pathLength="1" d="{WAVE_PATH} C300,120 300,0 320,0 C340,0 340,120 360,120 C380,120 380,0 400,0 C420,0 420,120 440,120 C460,120 460,0 480,0 C500,0 500,120 520,120 C540,120 540,0 560,0" fill="none" stroke="url(#{gid})" stroke-width="32" stroke-linecap="round"/></svg>')

def page_hero(eyebrow, title, lede, gid="wm-ph"):
    return f"""<section class="page-hero">
  {hero_line(gid)}
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1 class="h1">{title}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>
"""

def write(path, content):
    full = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

# ---------- Home ----------
def home():
    d = 0
    svc_list = "".join(f'<li{" class=\"on\"" if i == 0 else ""}><a href="services/{s["slug"]}.html">{s["name"]}</a></li>' for i, s in enumerate(SERVICES))
    svc_panels = "".join(f"""<div class="svc-panel{" on" if i == 0 else ""}"><span class="match-tag">{s["match"]}</span><h3>{s["name"]}</h3><p>{s["short"]}</p>
        <a class="link" href="services/{s["slug"]}.html">Explore</a></div>""" for i, s in enumerate(SERVICES))
    cards = "".join(f"""<a class="work-card reveal" href="work/case-study.html">
        <span class="tag">{c[1]}</span><div class="art">{wave_mark("", "wk" + str(i))}</div>
        <div><h3>{c[0]}</h3><span class="soon">In production</span></div></a>""" for i, c in enumerate(CASES[:3]))
    body = f"""{header("index.html", d)}
<canvas id="gl" aria-hidden="true"></canvas>
<main id="main">
<section class="hero" id="hero">
  <div class="hero-art" aria-hidden="true">{wave_mark("wave-fallback", "wm-fb")}</div>
  <div class="wrap hero-inner">
    <p class="eyebrow">Global marketing and branding</p>
    <h1 class="display">Brands, <span class="serif">perfectly matched.</span></h1>
    <div class="hero-foot">
      <div style="display:grid;gap:26px">
        <p class="lede">We find the people your brand is meant for, then build everything that reaches them.</p>
        <div class="btn-row"><a class="btn btn-primary" href="contact.html">Start a project <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="#services">What we do</a></div>
      </div>
      <div class="scroll-cue"><span></span>Scroll</div>
    </div>
  </div>
</section>

<section class="sec match" id="match">
  <div class="wrap match-inner">
    <div class="match-labels" aria-hidden="true"><span>Your brand</span><span>Your people</span></div>
    <h2 class="h2 reveal">That moment is <span class="serif">the match.</span></h2>
    <p class="lede reveal">Strategy finds it. Design makes it recognisable. Content makes it felt. Media makes it happen everywhere.</p>
  </div>
</section>

<section id="services" class="svc-track">
  <div class="svc-stage">
    <div class="wrap">
      <div class="svc-side">
        <p class="eyebrow">What we do</p>
        <h2 class="h2">Seven disciplines. <span class="serif">One team.</span></h2>
        <ol class="svc-list">{svc_list}</ol>
        <div class="svc-panels">{svc_panels}</div>
        <p class="svc-count" aria-hidden="true">01 / 07</p>
      </div>
    </div>
  </div>
</section>

<section class="sec" id="approach">
  <div class="wrap">
    <div class="sec-head reveal"><p class="eyebrow">How we work</p><h2 class="h2">One line from brief <span class="serif">to growth.</span></h2></div>
    <ol class="process">
      <li><span class="dot">01</span><h3>Discover</h3><p class="muted">Your business, audience and market.</p></li>
      <li><span class="dot">02</span><h3>Define</h3><p class="muted">The position only you can own.</p></li>
      <li><span class="dot">03</span><h3>Design</h3><p class="muted">Identity, content and experiences.</p></li>
      <li><span class="dot">04</span><h3>Deploy</h3><p class="muted">Launched across every channel.</p></li>
      <li><span class="dot">05</span><h3>Develop</h3><p class="muted">Measured, improved, grown.</p></li>
    </ol>
  </div>
</section>

<section class="sec" id="work">
  <div class="wrap">
    <div class="sec-head sec-head--row reveal"><div><p class="eyebrow">Selected work</p><h2 class="h2">Work that <span class="serif">found its people.</span></h2></div>
      <a class="link" href="work.html">All work</a></div>
    <div class="work-grid">{cards}</div>
  </div>
</section>

<section class="sec finale" id="contact">
  <div class="wrap" style="display:grid;gap:30px">
    <p class="eyebrow">Start a project</p>
    <h2 class="display" style="max-width:9ch">Let's find <span class="serif">your match.</span></h2>
    <p class="lede">Tell us where you want to go. We reply within one working day.</p>
    <div class="btn-row"><a class="btn btn-primary" href="contact.html">Start a project <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="mailto:{EMAIL}">{EMAIL}</a></div>
  </div>
</section>
</main>
"""
    scripts = f'<script src="{THREE_JS}"></script>\n<script src="assets/js/matchline.js"></script>'
    write("index.html", head("Whatta Match Media | Brands, perfectly matched",
                             "Whatta Match Media is a global marketing and branding agency. Consulting, consulting, strategy, identity, content, social, performance, media and digital under one team.",
                             "index.html", d) + body + footer(d, scripts))

# ---------- Services ----------
def services_hub():
    d = 0
    cards = "".join(f"""<a class="card svc-tile reveal" href="services/{s["slug"]}.html" style="text-decoration:none">
      <span class="mono" style="color:var(--sky)">{s["match"]}</span><h3>{s["name"]}</h3><p>{s["short"]}</p><span class="link" style="justify-self:start">Explore</span>{svc_icon(s["art"], "si" + str(i))}</a>""" for i, s in enumerate(SERVICES))
    body = header("services.html", d) + f"""<main id="main">
{page_hero("Services", 'Seven disciplines. <span class="serif">One team.</span>', "From the first workshop to the last ad, one team carries the idea. Choose a discipline, or let us bring them together.")}
<section class="sec" style="padding-top:0"><div class="wrap"><div class="grid-3 svc-hub">{cards}
  <a class="card svc-tile svc-tile--cta reveal" href="contact.html#brief" style="text-decoration:none"><span class="mono" style="color:var(--amber)">Not sure where to start?</span><h3>Find your match</h3><p>Answer four quick questions and we'll suggest the right mix of disciplines.</p><span class="link" style="justify-self:start">Start</span>{svc_icon("match", "si-m")}</a>
</div></div></section>
{contact_block(d)}
</main>
"""
    write("services.html", head("Services | Whatta Match Media", "Consulting, brand strategy, identity, content, social, performance and media under one team.", "services.html", d) + body + footer(d))

def service_page(i, s):
    d = 1
    dl = "".join(f'<div class="card reveal"><h3>{t}</h3><p>{x}</p></div>' for t, x in s["deliverables"])
    steps = "".join(f"<li><h3 class=\"h3\">{t}</h3><p class=\"muted\">{x}</p></li>" for t, x in s["steps"])
    faqs = "".join(f"<details><summary>{q}</summary><p class=\"muted\">{a}</p></details>" for q, a in s["faqs"])
    nxt = SERVICES[(i + 1) % len(SERVICES)]
    schema = [{"@context": "https://schema.org", "@type": "Service", "name": s["name"], "provider": {"@type": "Organization", "name": "Whatta Match Media"},
               "description": s["promise"], "areaServed": "Worldwide", "url": f"{DOMAIN}/services/{s['slug']}.html"},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faqs"]]}]
    body = header("services.html", d) + f"""<main id="main">
{page_hero(s["match"], s["name"], s["promise"] + " " + s["who"], "sp" + str(i))}
<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head reveal"><p class="eyebrow">What's included</p><h2 class="h2">Everything you need, <span class="serif">nothing you don't.</span></h2></div>
  <div class="grid-3">{dl}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head reveal"><p class="eyebrow">Our approach</p><h2 class="h2">How we get there</h2></div>
  <ol class="steps">{steps}</ol>
</div></section>
<section class="sec"><div class="wrap grid-2">
  <div><p class="eyebrow">Questions</p><h2 class="h2">Frequently <span class="serif">asked.</span></h2>
    <p style="margin-top:28px"><span class="muted">Next: </span><a class="link" href="{nxt["slug"]}.html">{nxt["name"]}</a></p></div>
  <div class="faq">{faqs}</div>
</div></section>
{contact_block(d)}
</main>
"""
    write(f"services/{s['slug']}.html", head(f"{s['name']} | Whatta Match Media", s["promise"] + " " + s["short"], f"services/{s['slug']}.html", d, schema) + body + footer(d))

# ---------- About ----------
def about():
    d = 0
    founders = "".join(f"""<div class="card reveal" style="grid-template-columns:120px minmax(0,1fr);align-items:center;gap:24px">
      <div class="portrait">{SILHOUETTE.replace("{g}", "af" + str(i))}</div>
      <div style="display:grid;gap:10px"><h3 class="h3">{n}</h3><p class="mono" style="color:var(--sky)">{r}</p>
      <p>{n.split()[0]} leads Whatta Match Media alongside {FOUNDERS[1 - i][0].split()[0]}. Full bio coming soon.</p>
      <a class="link" href="https://www.linkedin.com" rel="noopener" target="_blank">LinkedIn</a></div></div>""" for i, (n, r) in enumerate(FOUNDERS))
    values = [("Proof over promises", "Every claim we make sits next to a number, a result or a piece of work."),
              ("One team, one idea", "The people who write the strategy stay until the last ad goes live."),
              ("Clear beats clever", "We say things plainly, to clients and to their customers."),
              ("Built to travel", "Every brand we make is ready for more than one market.")]
    vals = "".join(f'<div class="card reveal"><h3>{t}</h3><p>{x}</p></div>' for t, x in values)
    schema = [{"@context": "https://schema.org", "@type": "Person", "name": n, "jobTitle": r, "worksFor": {"@type": "Organization", "name": "Whatta Match Media"}} for n, r in FOUNDERS]
    body = header("about.html", d) + f"""<main id="main">
{page_hero("About us", 'We exist to make <span class="serif">the match.</span>', "Whatta Match Media is a global marketing and branding agency. We bring consulting, strategy, identity, content, social, performance, media and digital together in one team, so nothing gets lost between them.")}
<section class="sec"><div class="wrap grid-2">
  <div><p class="eyebrow">Our story</p><h2 class="h2">Why we started <span class="serif">Whatta Match.</span></h2></div>
  <div class="prose">
    <p>Too many good brands never reach the people they were made for. The strategy sits in a deck. The identity looks different on every channel. The campaign reaches the wrong audience. Each agency did its part, and the match still never happened.</p>
    <p>We built Whatta Match Media to close those gaps. One team carries a brand from the first question to the last result, with every discipline working from the same idea.</p>
    <p>We are based in India and work with brands that want to be understood everywhere. Our job is simple to say and hard to do: find the people your brand is meant for, and make sure they can't look away.</p>
  </div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head reveal"><p class="eyebrow">Founders</p><h2 class="h2">The people <span class="serif">behind the match.</span></h2></div>
  <div class="grid-2">{founders}</div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head reveal"><p class="eyebrow">What we value</p><h2 class="h2">How we work, <span class="serif">every time.</span></h2></div>
  <div class="grid-2">{vals}</div>
</div></section>
{contact_block(d)}
</main>
"""
    write("about.html", head("About | Whatta Match Media", "Whatta Match Media is a global marketing and branding agency founded by Nainee Sohane and Srushti Gadekar.", "about.html", d, schema) + body + footer(d))

# ---------- Work ----------
def work():
    d = 0
    cats = [("all", "All")] + [(s["art"], s["name"]) for s in SERVICES]
    filt = "".join(f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{n}</button>' for k, n in cats)
    cards = "".join(f"""<a class="work-card reveal" data-cat="{c[3]}" href="work/case-study.html"><span class="tag">{c[1]}</span>
      <div class="art">{wave_mark("", "wp" + str(i))}</div><div><h3>{c[0]}</h3><span class="soon">In production</span></div></a>""" for i, c in enumerate(CASES))
    body = header("work.html", d) + f"""<main id="main">
{page_hero("Work", 'Work that <span class="serif">found its people.</span>', "Our first case studies are being written up now. Ask us for the full portfolio on a call and we'll walk you through it.")}
<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="filter" role="group" aria-label="Filter work by discipline">{filt}</div>
  <div class="work-grid">{cards}</div>
</div></section>
{contact_block(d)}
</main>
"""
    write("work.html", head("Work | Whatta Match Media", "Selected brand, content, social, performance and digital work by Whatta Match Media.", "work.html", d) + body + footer(d))

def case_study():
    d = 1
    body = header("work.html", d) + f"""<main id="main">
<section class="page-hero">{hero_line("wm-cs")}<div class="wrap">
  <p class="eyebrow">Case study · Template</p>
  <h1 class="h1">Client name: the headline <span class="serif">result.</span></h1>
  <p class="lede">One sentence on what changed for the client because of this work.</p>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="placeholder" style="aspect-ratio:16/8;display:grid;place-items:center;max-width:100%"><span class="mono">Hero image or film · 1920 × 960</span></div>
  <div class="meta-row" style="margin-top:36px">
    <div><span class="mono muted">Client</span><strong>Client name</strong></div>
    <div><span class="mono muted">Market</span><strong>Country or region</strong></div>
    <div><span class="mono muted">Services</span><strong>Strategy, Identity, Content</strong></div>
    <div><span class="mono muted">Year</span><strong>2026</strong></div>
  </div>
</div></section>
<section class="sec"><div class="wrap grid-2">
  <div><p class="eyebrow">The challenge</p><h2 class="h2">What stood in the way</h2></div>
  <p class="lede" style="align-self:end">Two or three sentences on the business problem, in the client's terms.</p>
</div></section>
<section class="sec"><div class="wrap grid-2">
  <div><p class="eyebrow">The insight</p><h2 class="h2">The match <span class="serif">we found.</span></h2></div>
  <p class="lede" style="align-self:end">The truth about the audience that unlocked the work.</p>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">The work</p><h2 class="h2">What we made</h2></div>
  <div class="grid-3"><div class="placeholder" style="aspect-ratio:4/5">Image 1</div><div class="placeholder" style="aspect-ratio:4/5">Image 2</div><div class="placeholder" style="aspect-ratio:4/5">Image 3</div></div>
</div></section>
<section class="sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">Results</p><h2 class="h2">What changed</h2></div>
  <div class="numbers"><div class="num"><b>00%</b><span>Headline metric</span></div><div class="num"><b>0x</b><span>Second metric</span></div><div class="num"><b>00k</b><span>Third metric</span></div></div>
  <blockquote class="quote" style="margin-top:72px">“Client testimonial goes here, approved in writing.”</blockquote>
  <p class="mono muted">Name, title, company</p>
</div></section>
{contact_block(d)}
</main>
"""
    write("work/case-study.html", head("Case study | Whatta Match Media", "Case study template.", "work/case-study.html", d, extra='<meta name="robots" content="noindex">') + body + footer(d))

# ---------- Insights ----------
def insights():
    d = 0
    rows = "".join(f"""<a href="insights/{a["slug"]}.html" class="reveal"><span class="mono muted">{a["tag"]} · {a["date"]}</span>
      <div style="display:grid;gap:8px"><h3 class="h3">{a["title"]}</h3><p class="muted">{a["lede"]}</p></div><span class="mono muted">{a["read"]}</span></a>""" for a in ARTICLES)
    body = header("insights.html", d) + f"""<main id="main">
{page_hero("Insights", 'Thinking out <span class="serif">loud.</span>', "Points of view on brands, growth and building for global markets, from the Whatta Match Media team.")}
<section class="sec" style="padding-top:0"><div class="wrap"><div class="article-list">{rows}</div></div></section>
{contact_block(d)}
</main>
"""
    write("insights.html", head("Insights | Whatta Match Media", "Points of view on brands, growth and global marketing.", "insights.html", d) + body + footer(d))

def article(a):
    d = 1
    paras = "".join(f"<p>{p}</p>" for p in a["body"])
    schema = [{"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["lede"],
               "author": {"@type": "Organization", "name": "Whatta Match Media"}, "publisher": {"@type": "Organization", "name": "Whatta Match Media"},
               "url": f"{DOMAIN}/insights/{a['slug']}.html"}]
    body = header("insights.html", d) + f"""<main id="main">
<section class="page-hero">{hero_line("wm-ar")}<div class="wrap">
  <p class="eyebrow">{a["tag"]} · {a["date"]} · {a["read"]} read</p>
  <h1 class="h1" style="max-width:18ch">{a["title"]}</h1>
  <p class="lede" style="font-family:var(--f-serif);font-style:italic;font-size:clamp(22px,2.2vw,30px);color:var(--cream)">{a["lede"]}</p>
</div></section>
<section class="sec"><div class="wrap"><article class="prose" style="font-size:19px">{paras}
  <p class="mono" style="margin-top:20px">Written by the Whatta Match Media team</p>
  <p><a class="link" href="../insights.html">More insights</a></p>
</article></div></section>
{contact_block(d)}
</main>
"""
    write(f"insights/{a['slug']}.html", head(f"{a['title']} | Whatta Match Media", a["lede"], f"insights/{a['slug']}.html", d, schema) + body + footer(d))

# ---------- Careers ----------
def careers():
    d = 0
    perks = [("Real responsibility", "Work directly with founders and clients from your first week."),
             ("Every discipline", "Learn how strategy, design, content and growth fit together."),
             ("Global clients", "Build work for brands in more than one market."),
             ("Room to grow", "We're early, so the people who join now help shape what we become.")]
    pk = "".join(f'<div class="card reveal"><h3>{t}</h3><p>{x}</p></div>' for t, x in perks)
    body = header("careers.html", d) + f"""<main id="main">
{page_hero("Careers", 'Do the best work <span class="serif">of your life.</span>', "We're building a team that can carry a brand from first idea to measurable growth. If that sounds like you, we'd like to meet.")}
<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head reveal"><p class="eyebrow">Why join</p><h2 class="h2">What you'll get</h2></div>
  <div class="grid-2">{pk}</div>
</div></section>
<section class="sec"><div class="wrap grid-2">
  <div><p class="eyebrow">Open roles</p><h2 class="h2">No open roles <span class="serif">right now.</span></h2>
    <p class="lede" style="margin-top:22px">We're always meeting strategists, designers, writers, producers and growth marketers. Send us your work and we'll be in touch when the right role opens.</p></div>
  <form class="form" data-endpoint="{FORM_ENDPOINT}" data-next="thank-you.html">
    <input type="hidden" name="form" value="careers">
    <div class="field"><label for="c-name">Full name</label><input id="c-name" name="name" autocomplete="name" required></div>
    <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="c-role">Your discipline</label><select id="c-role" name="discipline"><option>Strategy</option><option>Design</option><option>Copy and content</option><option>Social</option><option>Performance and growth</option><option>Media</option><option>Development</option><option>Other</option></select></div>
    <div class="field"><label for="c-link">Portfolio or LinkedIn link</label><input id="c-link" name="portfolio" type="url" placeholder="https://"></div>
    <div class="field"><label for="c-msg">Tell us about yourself</label><textarea id="c-msg" name="message"></textarea></div>
    <div class="hp" aria-hidden="true"><input tabindex="-1" name="_gotcha" autocomplete="off"></div>
    <button class="btn btn-primary" type="submit">Send application <span class="arrow" aria-hidden="true">→</span></button>
    <p class="form-status" role="status"></p>
  </form>
</div></section>
</main>
"""
    write("careers.html", head("Careers | Whatta Match Media", "Join Whatta Match Media, a global marketing and branding agency.", "careers.html", d) + body + footer(d))

# ---------- Contact ----------
def contact():
    d = 0
    def q(name, title, opts):
        o = "".join(f'<label class="chip"><input type="radio" name="{name}" value="{v}"><span>{t}</span></label>' for v, t in opts)
        return f"""<div class="brief-step"><fieldset class="field chips" style="display:grid;gap:14px"><legend class="h3" style="font-family:var(--f-display);text-transform:none;letter-spacing:-0.01em;font-size:clamp(22px,2.2vw,30px);color:var(--cream);margin-bottom:14px">{title}</legend>
          <div class="chips">{o}</div></fieldset><p class="brief-hint muted" hidden>Pick one to continue.</p></div>"""
    steps = (q("b_goal", "What do you need most?", [("launch", "Launch a new brand"), ("rebrand", "Refresh our brand"), ("grow", "Grow sales and leads"), ("awareness", "Get known")]) +
             q("b_stage", "Where is the business today?", [("early", "Pre-launch or early"), ("growing", "Growing"), ("established", "Established")]) +
             q("b_where", "Where are your customers?", [("local", "One country"), ("regional", "A few countries"), ("global", "Worldwide")]) +
             q("b_when", "When do you want to start?", [("now", "Within a month"), ("soon", "In 1 to 3 months"), ("later", "Just exploring")]))
    svc = "".join(f'<label class="chip"><input type="checkbox" name="services" value="{s["name"]}"><span>{s["name"]}</span></label>' for s in SERVICES)
    body = header("contact.html", d) + f"""<main id="main">
{page_hero("Contact", 'Let\'s find <span class="serif">your match.</span>', "Tell us where you want to go. We reply to every brief within one working day.")}
<section class="sec" style="padding-top:0"><div class="wrap grid-2">
  <div style="display:grid;gap:22px;align-content:start">
    <p class="eyebrow">Find your match</p>
    <h2 class="h2">Not sure where to start?</h2>
    <p class="muted">Answer four questions and we'll suggest the right mix of services.</p>
    <div class="brief" id="brief" data-brief>
      <div class="brief-progress" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
      {steps}
      <div class="brief-result" hidden>
        <p class="eyebrow">Your match</p>
        <h3 class="h3" style="margin-bottom:16px">We'd start with these three.</h3>
        <ul></ul>
        <p class="muted" data-summary style="margin-top:16px"></p>
        <div class="btn-row" style="margin-top:20px"><a class="btn btn-primary" href="{BOOKING_URL}" target="_blank" rel="noopener">Book a call <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="#brief-form">Send a brief</a></div>
      </div>
      <div class="brief-nav"><button class="btn btn-ghost" type="button" data-back hidden>Back</button><button class="btn btn-primary" type="button" data-next>Next</button></div>
    </div>
  </div>
  <div style="display:grid;gap:22px;align-content:start" id="brief-form">
    <p class="eyebrow">Send a brief</p>
    <form class="form" data-endpoint="{FORM_ENDPOINT}" data-next="thank-you.html">
      <input type="hidden" name="form" value="project brief">
      <input type="hidden" id="services-suggested" name="suggested_services" value="">
      <div class="field"><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization" required></div>
      <div class="field"><label for="f-email">Work email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="f-site">Website</label><input id="f-site" name="website" type="url" placeholder="https://"></div>
      <fieldset class="field" style="border:0;padding:0;margin:0"><legend>Services you need</legend><div class="chips" style="margin-top:8px">{svc}</div></fieldset>
      <div class="field"><label for="f-budget">Budget range (USD)</label><select id="f-budget" name="budget"><option>Under 10,000</option><option>10,000 to 25,000</option><option>25,000 to 75,000</option><option>75,000 to 150,000</option><option>150,000+</option><option>Not sure yet</option></select></div>
      <div class="field"><label for="f-time">Timeline</label><select id="f-time" name="timeline"><option>Within a month</option><option>1 to 3 months</option><option>3 to 6 months</option><option>Just exploring</option></select></div>
      <div class="field"><label for="f-msg">Tell us about the project</label><textarea id="f-msg" name="message" required></textarea></div>
      <div class="hp" aria-hidden="true"><input tabindex="-1" name="_gotcha" autocomplete="off"></div>
      <button class="btn btn-primary" type="submit">Send brief <span class="arrow" aria-hidden="true">→</span></button>
      <p class="form-status" role="status"></p>
      <p class="form-note">By sending this form you agree to our <a class="link" href="privacy.html">privacy policy</a>.</p>
    </form>
    <div class="meta-row" style="margin-top:24px">
      <div><span class="mono muted">Email</span><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></div>
      <div><span class="mono muted">Book a call</span><a class="link" href="{BOOKING_URL}" target="_blank" rel="noopener">Pick a time</a></div>
      <div><span class="mono muted">Based in</span><strong>India · Working worldwide</strong></div>
    </div>
  </div>
</div></section>
</main>
"""
    write("contact.html", head("Contact | Whatta Match Media", "Start a project with Whatta Match Media. We reply to every brief within one working day.", "contact.html", d) + body + footer(d))

# ---------- Utility ----------
LEGAL = {
    "privacy.html": ("Privacy policy", [
        ("Who we are", f"Whatta Match Media (\"we\", \"us\") runs this website. Contact us at {EMAIL} about anything in this policy."),
        ("What we collect", "When you send a form, we collect the details you enter: usually your name, email, company and message. If you accept analytics cookies, we collect anonymous usage data such as pages visited and device type."),
        ("Why we collect it", "To reply to your enquiry, to send our newsletter if you subscribed, and to improve this website. We do not sell your data."),
        ("Legal basis", "We process your data with your consent, or because we have a legitimate interest in replying to business enquiries. This policy is written to meet India's Digital Personal Data Protection Act 2023 and the EU and UK GDPR."),
        ("Who we share it with", "Trusted providers who help us run the site, such as our form, email and analytics providers. They process data only on our instructions."),
        ("How long we keep it", "Enquiries for up to two years, newsletter details until you unsubscribe."),
        ("Your rights", f"You can ask to access, correct or delete your data, or withdraw consent, at any time by emailing {EMAIL}."),
        ("Changes", "We may update this policy. The date below shows the latest version. Last updated: October 2026.")]),
    "terms.html": ("Terms of use", [
        ("Using this site", "By using this website you agree to these terms. If you don't agree, please don't use the site."),
        ("Content", "All content on this site, including the Whatta Match Media name, logo and wave symbol, belongs to Whatta Match Media unless stated otherwise. You may not copy or reuse it without written permission."),
        ("Accuracy", "We work to keep information on this site accurate, but it is provided for general information and may change without notice."),
        ("Links", "Links to other websites are provided for convenience. We are not responsible for their content."),
        ("Liability", "To the extent the law allows, we are not liable for any loss arising from use of this site."),
        ("Governing law", "These terms are governed by the laws of India."),
        ("Contact", f"Questions about these terms: {EMAIL}. Last updated: October 2026.")]),
    "cookies.html": ("Cookie policy", [
        ("What cookies are", "Cookies are small files stored in your browser. They help websites work and help owners understand how sites are used."),
        ("Essential cookies", "We store your cookie choice in your browser so we don't ask again. This is needed for the site to work."),
        ("Analytics cookies", "If you choose Accept all, we may use privacy-friendly analytics to understand which pages are useful. These are off unless you accept them."),
        ("Managing cookies", "You can clear cookies at any time in your browser settings, which will also reset your choice here."),
        ("Contact", f"Questions: {EMAIL}. Last updated: October 2026.")]),
}
def legal(path, title, sections):
    d = 0
    body = "".join(f"<h2>{h}</h2><p>{t}</p>" for h, t in sections)
    page = header("", d) + f"""<main id="main">
{page_hero("Legal", title, "Plain-language summary of how this website works.")}
<section class="sec"><div class="wrap"><div class="prose">{body}</div></div></section>
</main>
"""
    write(path, head(f"{title} | Whatta Match Media", f"{title} for whattamatch.com.", path, d) + page + footer(d))

def simple(path, eyebrow, title, lede, cta, robots=True):
    d = 0
    extra = '' if robots else '<meta name="robots" content="noindex">'
    page = header("", d) + f"""<main id="main">
<section class="page-hero page-hero--full">{hero_line("wm-s")}<div class="wrap">
  <p class="eyebrow">{eyebrow}</p><h1 class="h1">{title}</h1><p class="lede">{lede}</p>
  <div class="btn-row" style="margin-top:32px">{cta}</div>
</div></section>
</main>
"""
    write(path, head(f"{eyebrow} | Whatta Match Media", lede, path, d, extra=extra) + page + footer(d))

def knot404():
    # The line ties itself in a knot
    knot = ('<svg class="wave-mark" viewBox="0 0 320 200" aria-hidden="true" style="width:clamp(160px,20vw,260px)"><defs><linearGradient id="k404" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#FF5F1F"/></linearGradient></defs>'
            '<path d="M10,150 C60,150 80,40 150,40 C230,40 240,160 170,160 C100,160 110,60 170,70 C230,80 250,150 310,150" fill="none" stroke="url(#k404)" stroke-width="26" stroke-linecap="round"/></svg>')
    d = 0
    page = header("", d) + f"""<main id="main">
<section class="page-hero" style="min-height:85vh;display:flex;align-items:center"><div class="wrap">
  {knot}<p class="eyebrow">Error 404</p><h1 class="h1">No match <span class="serif">found.</span></h1>
  <p class="lede">The page you're looking for has moved or never existed. Let's get you back on the line.</p>
  <div class="btn-row" style="margin-top:32px"><a class="btn btn-primary" href="/index.html">Back to home <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="/contact.html">Contact us</a></div>
</div></section>
</main>
"""
    # 404 is served from any path, so it uses root-absolute links
    out = head("Page not found | Whatta Match Media", "Page not found.", "404.html", d, extra='<meta name="robots" content="noindex">') + page + footer(d)
    out = out.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    for n, h in NAV + [("", "contact.html"), ("", "index.html"), ("", "about.html"), ("", "privacy.html"), ("", "terms.html"), ("", "cookies.html"), ("", "thank-you.html")]:
        out = out.replace(f'href="{h}"', f'href="/{h}"')
    out = out.replace('href="services/', 'href="/services/')
    write("404.html", out)

def seo_files():
    pages = ["index.html", "about.html", "services.html", "work.html", "insights.html", "careers.html", "contact.html", "privacy.html", "terms.html", "cookies.html"]
    pages += [f"services/{s['slug']}.html" for s in SERVICES] + [f"insights/{a['slug']}.html" for a in ARTICLES]
    urls = "".join(f"<url><loc>{DOMAIN}/{'' if p == 'index.html' else p}</loc><changefreq>monthly</changefreq></url>" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /thank-you.html\nDisallow: /work/case-study.html\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    svc = "\n".join(f"- [{s['name']}]({DOMAIN}/services/{s['slug']}.html): {s['short']}" for s in SERVICES)
    write("llms.txt", f"""# Whatta Match Media

> A global, holistic marketing and branding agency based in India. One team covers consulting, brand strategy, identity and design, content and creative, social and influence, performance and growth, and media and digital experiences. Founded by Nainee Sohane and Srushti Gadekar.

## Services
{svc}

## Company
- [About]({DOMAIN}/about.html)
- [Insights]({DOMAIN}/insights.html)
- [Contact]({DOMAIN}/contact.html): {EMAIL}
""")
    # netlify.toml lives at the repo root (publishes site/), not inside site/
    write("_redirects", "/*    /404.html   404\n")

if __name__ == "__main__":
    home(); services_hub()
    for i, s in enumerate(SERVICES): service_page(i, s)
    about(); work(); case_study(); insights()
    for a in ARTICLES: article(a)
    careers(); contact()
    for p, (t, s) in LEGAL.items(): legal(p, t, s)
    simple("thank-you.html", "Thank you", 'Brief <span class="serif">received.</span>', "Thanks for getting in touch. We reply to every message within one working day.",
           '<a class="btn btn-primary" href="index.html">Back to home <span class="arrow" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="insights.html">Read our insights</a>', robots=False)
    knot404(); seo_files()
    print("Built:", sum(len(f) for _, _, f in os.walk(SITE)), "files")
