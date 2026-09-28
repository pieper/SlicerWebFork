# Widget gallery: the qt/ctk compatibility layer, measured and shown

Two demonstrations of `python/slicerweb/qtcompat/`, the layer that lets Python scripted modules
written for desktop Slicer build their Qt/CTK GUIs in the browser, plus the study behind them:

| | |
|---|---|
| [ctk-gallery.html](https://pieper.github.io/SlicerWebFork/ctk-gallery.html) | A page of its own, not part of the application: each real Qt/CTK widget, photographed inside desktop Slicer 5.9 on macOS, beside the same widget built by the browser layer. The replicas are live and print their signals. A checkbox switches them between a CSS theme that follows the macOS Qt palette and SlicerWeb's own dark theme. |
| [gallery.html](https://pieper.github.io/SlicerWebFork/gallery.html) | The application with the **Widget Gallery** scripted module open: twelve sections that exercise every Qt, CTK and MRML widget the layer has, a Designer `.ui` file through `slicer.util.loadUI`, the MRML widgets bound to a small demo scene, dialogs, and a coverage report computed at run time against the toolkits' class lists. |
| [docs/qt-emulation.md](../docs/qt-emulation.md) | How the layer works, what Slicer's Python actually asks of Qt (counted over Slicer's modules, four extensions and 111 `.ui` files), the coverage today, and what a fuller emulation would take, in tiers. |

Both pages are published by [.github/workflows/publish-gallery.yml](../.github/workflows/publish-gallery.yml)
from the `qt-ctk-gallery` branch of pieper/SlicerWebFork. Nothing under `web/` or `python/` is changed
on this branch: the module is packaged as an ordinary extension wheel and installed with
`?extensions=WidgetGallery`; the standalone page loads Pyodide and the `slicerweb` wheel alone.

## What is here

- `WidgetGallery/` - the scripted module (`WidgetGallery.py`, `Resources/UI/WidgetGallery.ui`). Its
  `coverage()` compares the class lists of QtWidgets, QtCore/QtGui, CTK and the MRML widgets with
  what `qt`, `ctk` and `slicer` provide, and classifies each as available, via base, placeholder or
  missing. Widgets that fail to build are caught and listed instead of stopping `setup()`.
- `make-gallery-wheel.py` - packages the module as `slicer_ext_widgetgallery-*.whl` into
  `$SLICERWEB_EXTENSIONS` and adds it to `index.json` there (uses `scripts/make_wheels.py`).
- `ctk-screenshots.py` - run **inside desktop Slicer** to take the Qt screenshots and read the
  palette: `Slicer --no-splash --no-main-window --python-script $PWD/gallery/ctk-screenshots.py`.
  Writes `qt-shots/*.png` and `qt-shots/theme.json`. The widgets get the same content the replicas
  show, in a 340 px frame.
- `ctk-gallery.py` - the replica builders, run in Pyodide by the page; `ctk-gallery.html` and
  `qt-theme.css` - the page and the Qt look. The theme is mostly overrides of the Tailwind colour
  tokens the widgets are built on, plus rules on the widgets' own classes (`.sw-*`), so it applies to
  any module GUI, not only this page.
- `gallery.html` - a wrapper that embeds the application, installs the extension and opens the module
  (the mechanism of `docs/embedding.md`).
- `install-gallery.sh <site dir>` - copies the pages, screenshots and the widgets bundle next to a
  built site.
- `../web/tests/widget-gallery.mjs`, `../web/tests/ctk-gallery.mjs` - headless checks with screenshots.

## Running it locally

```bash
export SLICERWEB_WHEELS=... SLICERWEB_EXTENSIONS=... SLICERWEB_SAMPLE_DATA=...   # as for the app
python3 gallery/make-gallery-wheel.py           # the module, as an extension wheel + index entry
cd web && npm ci && npm run build               # the app and the widgets bundle
cd .. && gallery/install-gallery.sh web/dist/app
cd web && npx vite preview --port 4173          # http://localhost:4173/ctk-gallery.html, /gallery.html
node tests/ctk-gallery.mjs http://localhost:4173/ ctk-gallery.png
node tests/widget-gallery.mjs http://localhost:4173/ widget-gallery.png
```

With the development server (`npm run dev`) the module works through
`http://localhost:5173/?extensions=WidgetGallery`, then "Widget Gallery" in the module finder; the
standalone page needs the built widgets bundle, so it is served from a build.

## What the gallery found

Coverage of the toolkits' listed classes by the layer, measured at run time (2026-09-23, upstream
9cdff5d): Qt widgets 39 of 99 available, CTK 16 of 100, MRML/Slicer widgets 19 of 103; the missing
ones are mostly item views and models, dialogs, and the display-node property widgets. Three bugs
worth fixing regardless of any larger plan:

1. `QAbstractSpinBox.setPrefix` (and the `prefix` property in `.ui` files) throws
   `TypeError: Cannot set property prefix of #<Element> which has only a getter`: the layer writes an
   element property named `prefix`, which the DOM defines read-only on every `Element`. Renaming the
   Vue prop (`prefixText`, say) in `SwSpinBox.vue` and `qtcompat/widgets.py` fixes it.
2. `QTableWidget._render` builds `innerHTML` from unescaped cell text.
3. `QWidget.setFixedHeight` and the other size setters are no-ops, so a `QScrollArea` never scrolls.

The larger picture, with the counts and a suggested order of work, is in
[docs/qt-emulation.md](../docs/qt-emulation.md).
