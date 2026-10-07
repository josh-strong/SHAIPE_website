# SHAIPE Logo Package

For how to edit this website using Cursor or Copilot, see:
- CONTRIBUTING: ./CONTRIBUTING.md
- Quickstart for Editors: ./docs/QUICKSTART.md

## Palette
- Oxford Blue (primary): #002147
- Accent Blue: #0f4d92
- Neutral text: #111
- Background: #ffffff

## File List
- logo_mark_primary.svg
- logo_mark_reversed.svg
- logo_lockup_horizontal.svg
- logo_lockup_stacked.svg
- favicon_16.png
- favicon_32.png
- apple_touch_180.png

## Usage Guidelines
- Minimum size: 24 px for symbol, 120 px for lockup
- Clearspace: maintain half the symbol's width as padding around
- Works in 1-colour (black/white)
- Ensure contrast meets WCAG AA

## Do / Don't
- Do use official colour palette
- Do maintain aspect ratio
- Don't distort or rotate the logo
- Don't change colours outside palette

## Keeping the website fast

The site is static: no build, server framework or package installation is needed
to preview or publish it. Pico CSS 2.1.1 and the footer icons are served locally
from `assets/vendor/pico/` and `assets/icons/`, with their upstream licences.
Pico's original source is <https://cdn.jsdelivr.net/npm/@picocss/pico@2.1.1/css/pico.min.css>;
the icons come from <https://github.com/simple-icons/simple-icons>.

Keep original images in `assets/img/`. The pages display smaller WebP copies in
`assets/img/optimised/`, choosing a resolution appropriate to the screen.
Research figures use lossless compression; links still open the original files.
Images have explicit dimensions, and portraits and footer icons load lazily.

After replacing an original, regenerate the display copies:

```bash
python3 -m pip install Pillow
python3 scripts/optimise_images.py
```

When adding a new image, add its source and display widths to the script's
`IMAGES` list, then update the page's `src`, `srcset`, `sizes`, `width` and `height`.
Do not upscale a small source. Use lossless compression for plots and diagrams.
Alison Noble, Joshua Strong and Nick Yeung's current portraits are saved locally;
Paul Greig's portrait still uses its existing remote URL, whose server refused
downloads during optimisation.

In a local desktop cold-cache Chrome check, downloads fell from 2.15 MB to
0.18 MB on Home, 4.39 MB to 0.21 MB on About, 13.06 MB to 0.47 MB on People
(after scrolling through the members), and 2.45 MB to 0.29 MB on the HAIC
publication page. These are transfer measurements from a local preview, not
public-hosting load-time guarantees.
