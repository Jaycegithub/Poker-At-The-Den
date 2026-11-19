# The Den Poker Lounge — website redesign

Black-and-gold redesign of [pokerattheden.com](https://pokerattheden.com/). It keeps all the existing copy, URLs, navigation, forms and tools.

**Status:** the homepage is complete and reviewed at desktop, tablet and phone widths. The inner pages are next. Drafts of About, Our Team, Club Values and Poker exist but haven't been reviewed yet. The remaining inner pages haven't been built.

## Build

```bash
pip install jinja2 pillow beautifulsoup4
python3 build.py            # renders src/ -> dist/
python3 build.py --serve    # http://localhost:8000
```

`dist/` mirrors the live permalinks (`/about-us/` → `dist/about-us/index.html`), so it can be deployed to the existing domain without changing any URLs.

## Layout

| Path | Purpose |
|---|---|
| `src/assets/css/den.css` | Design system: tokens, type scale, buttons, cards, sections, responsive rules |
| `src/assets/js/den.js` | Sticky header, dropdowns, mobile drawer, scroll reveals, Elementor form submit (5 KB, no dependencies) |
| `src/templates/base.html` | `<head>` SEO, header/mega-nav, drawer, footer |
| `src/templates/pages/*.html` | One template per page, using the original copy verbatim |
| `src/widgets/*.html` | Original HTML widgets (ICM calculator, games, membership applications), extracted unchanged |
| `src/data/seo.json` | Live titles / meta descriptions / dates, preserved per URL |
| `tools_images.py` | Builds responsive WebP sizes plus the light logo variant from the original uploads |
| `tools/make_preview.py` | Packages the homepage as a labelled design preview (relative assets, static map, forms in preview mode) |
| `tools/content_check.py` | Confirms every text string from the live page is present in the rebuilt page |
| `docs/AUDIT.md` | Audit findings and issues needing a client decision |

## Design system

- **Colour:** deep black `#0B0B0B`, charcoal `#151515`, card `#1D1D1D`, metallic gold `#C6A15B`, champagne `#D9BD83`, warm white `#F5F3EF`, muted `#A5A5A5`. The old green and cream are gone, and gold is reserved for calls to action, accents and icons.
- **Type:** Cinzel for headings (an engraved, casino-style serif; emphasis in gold foil) and Manrope for body text, on a fluid `clamp()` scale.
- **Motion:** fade-up on scroll, a slow hero zoom, image zoom on hover and button lift. All of it is disabled under `prefers-reduced-motion`.
- **Mobile:** an off-canvas menu with accordions, plus a sticky Call / Become a Member bar that appears after the hero. There's no horizontal scroll from 360px up.

## Homepage QA (current)

- Content: 124/124 strings from the live homepage are present (`tools/content_check.py`).
- Links: 36 checked. Internal links all resolve; external links return 200. PokerAtlas has no URL yet (see audit).
- Forms: the same field names, form ID (`142fbcb`) and Elementor endpoint as the live form. Submissions only work when served from pokerattheden.com; anywhere else it falls back to phone/email.
- Performance (local): initial load 296 KB on mobile and 472 KB on desktop, CLS 0, preloaded hero image, lazy-loaded images below the fold, WebP `srcset`.

## Getting this into WordPress

There was no WordPress admin access, so this is built as static files that mirror the live structure. There are two ways to apply it:

1. **Rebuild in Elementor** (keeps the current workflow). Set the Kit globals to the tokens above, then rebuild the Header (#2298) and Footer (#2323) templates and each page with containers and native widgets, using `dist/` as the visual spec. The HTML widgets and forms stay as they are; `den.css` maps Elementor's `--e-global-*` variables, so the widgets pick up the new palette automatically.
2. **Deploy `dist/` as the front end** on the same domain, keeping WordPress at `/wp-admin/` for the `admin-ajax.php` form handlers.
