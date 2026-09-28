# Emulating Qt for Slicer's Python in the browser: how SlicerWeb does it, and what "all of it" would take

Written 2026-09-23 against lassoan/SlicerWeb at 9cdff5d, on a Mac with Slicer at
`~/slicer/latest/Slicer`, CTK at `~/slicer/slicer-skill/slicer-dependencies/CTK`, Qt 5.15 headers at
`~/Qt/5.15.2`. The numbers below come from grepping those trees and from the Widget Gallery module
(`gallery/WidgetGallery/WidgetGallery.py`), which measures the runtime's coverage live, and the
standalone CTK gallery page (`gallery/ctk-gallery.html`), which puts the real Qt widgets, photographed
in desktop Slicer, beside the browser layer's replicas. Both are published from the `qt-ctk-gallery`
branch of pieper/SlicerWebFork: <https://pieper.github.io/SlicerWebFork/ctk-gallery.html> and
<https://pieper.github.io/SlicerWebFork/gallery.html>. `gallery/README.md` says how to run them.

## 1. How the facade in SlicerWeb works

`python/qt`, `python/ctk` and `python/slicerweb/qtcompat/` (about 5,300 lines of Python) plus 17 Vue
components in `web/src/widgets/`.

**Object model.** Every Python `QObject` keeps a parent/children tree, an object name, dynamic
properties and signals, as Qt does. Every `QWidget` additionally creates **one real DOM element at
construction** through Pyodide's `js` module. Leaf controls are Vue components registered as **custom
elements in the light DOM** (`<sw-slider>`, `<sw-combobox>`, `<sw-node-selector>`, ...) whose props
carry Qt property names and whose `CustomEvent`s carry Qt signal names with the arguments in
`event.detail`. Containers and layouts are plain `<div>`/`<fieldset>`/`<section>` with Tailwind classes.
There is no virtual tree and no diffing: Python writes properties straight onto elements, and Vue's
reactivity inside each element coalesces the repaint.

**Properties.** A `QProp` descriptor gives the PythonQt "property as attribute" behaviour
(`w.enabled = False`, `w.text`, `box.collapsed`), optionally forwarding to an element prop and emitting a
change signal. Values that PythonQt lets you both read and call (`combo.currentData` and
`combo.currentData()`) are returned as `str`/`int`/`float` subclasses whose `__call__` returns themselves.

**Signals.** `Signal` descriptors produce per-instance `BoundSignal`s supporting all three PythonQt
forms: `b.clicked.connect(f)`, `b.connect("clicked(bool)", f)` and
`b.connect("currentNodeChanged(bool)", other, "setEnabled(bool)")`. The C++ signature string is parsed
for its argument count so that `connect("clicked()", lambda: ...)` never receives the bool, and slot
arity is trimmed with `inspect.signature`, as Qt would. Unknown signal names are silently created so
`connect` never fails. `blockSignals` works. A `disconnectReceiver` walk reproduces Qt's "deleting the
receiver drops the connection", which module reload depends on.

**Layouts.** `QVBoxLayout`/`QHBoxLayout` are flex columns/rows, `QFormLayout` a two-column CSS grid that
collapses to one column under a container query, `QGridLayout` a CSS grid with `grid-row`/`grid-column`
per child, `ctkFlowLayout` a wrapping flex row, `addStretch` a `flex-1` spacer. Stretch factors, spacing,
margins and alignment are accepted and ignored. Parenting is Python-only: a widget not placed in a layout
is not in the document.

**Designer files.** `slicer.util.loadUI` is upstream's, unchanged; it lands in a 186-line `QUiLoader`
that parses the XML with `ElementTree`, resolves classes through the `qt`, `ctk` and `slicer` namespaces,
applies `<property>`s by calling `set<Name>()` or setting the attribute, keeps `stdset="0"` dynamic
properties (`SlicerParameterName`) reachable through `widget.property()`, and rebuilds the four layout
types. It drops `<connections>`, `<buttongroups>`, `<action>`s and item contents of views.

**Application services.** `slicer.app` is a plain Python class with the module manager, a Qt-free
`LayoutManager` driving the real `vtkMRMLLayoutNode`, an IO manager, a JSON settings store persisted to
IndexedDB (behind `QSettings`), `startupCompleted` and the other application signals, and version/path
properties. `mainWindow()` returns `None`, so everything in `slicer.util` that reaches into the main
window (menus, toolbars, status bar, module selector) is unavailable. Dialogs map to the browser's
`alert`/`confirm`/`prompt`; `QDialog.exec_()` returns `Rejected` at once; `QFileDialog` returns nothing;
`QProcess.start()` raises.

**Module hosting.** `ScriptedModuleHost.vue` mounts an empty `<div>` and asks Python to build the widget
into it: `<Name>Widget(parent).setup()` runs unchanged and the elements it made are appended. Reload
tears the tree down through `disconnectReceiver` and destroys the Pyodide proxies so nothing of the old
module survives.

**Adding a widget** is three edits: a Vue component with Qt-named props/emits, a line in the tag map, and
a Python class declaring `_tag`, `QProp(..., el=...)`, `Signal(...)` and `_events`.

## 2. What Slicer's Python actually asks of Qt

Grepped over Slicer's 160 module Python files, 19 segment editor effects, 111 `.ui` files, and four
large scripted extensions (SlicerHeart, SlicerMorph, SegmentEditorExtraEffects, SlicerDMRI).

| | distinct classes | carry 90% of uses |
|---|---|---|
| `qt.*` | 119 | QPushButton, QFormLayout, QLabel, `qt.Qt` enums, QCheckBox, QLineEdit, QWidget, QRadioButton, QSizePolicy, QHBoxLayout, QIcon, QApplication, QMessageBox, QSettings, QComboBox, QVBoxLayout, QGridLayout, QColor, QSpinBox, QTimer, QFileDialog, QProcess, QAction, QDir, QDoubleSpinBox, QDialogButtonBox, QTextEdit, QDialog |
| `ctk.*` | 36 | ctkPathLineEdit, ctkCollapsibleButton, ctkSliderWidget, ctkDoubleSpinBox, ctkCollapsibleGroupBox, ctkDirectoryButton, ctkSettingsPanel, ctkRangeWidget, ctkColorPickerButton |
| `slicer.q*` | 45 | qMRMLNodeComboBox, qMRMLSubjectHierarchyTreeView, qMRMLSpinBox, qSlicerMarkupsPlaceWidget, qMRMLSegmentEditorWidget, qMRMLTransformSliders, qMRMLCoordinatesWidget, qMRMLSliderWidget (qMRMLScreenShotDialog's 305 hits are all the test boilerplate) |

Three idioms dominate and any emulation must treat them as first class:

- **Property assignment beats setters.** `enabled` 752, `text` 326, `toolTip` 273, `value` 259,
  `checked` 230, `title` 200 assignments, versus `setEnabled` 143 and `setText` 109 calls.
- **String-form connect is the norm.** 1,092 `connect("signal(args)", slot)` against about 165
  `signal.connect(slot)`. About 45 distinct signals; `clicked(bool)`, `clicked()`, `valueChanged(double)`,
  `currentNodeChanged(vtkMRMLNode*)`, `validInputChanged(bool)` and `toggled(bool)` are most of them.
- **`.ui` files use four layouts and about 20 widget classes.** QLabel 725, QCheckBox 231, QPushButton
  184, ctkCollapsibleButton 137, qMRMLNodeComboBox 114, ctkSliderWidget 109. 278 Designer
  `<connection>`s exist, 85% of them `mrmlSceneChanged -> setMRMLScene` and enable/show gating. Only 18
  modules use `loadUI`; 140 build their GUI imperatively in `setup()`.

The hard parts are not widgets:

| idiom | sites | why it hurts in a page |
|---|---|---|
| blocking `exec_()` on dialogs, menus, message boxes | 29 direct, plus every `slicer.util.messageBox`/`confirm*Display`/`delayDisplay` | JavaScript cannot block a synchronous Python call and hand back the button pressed |
| `slicer.app.processEvents()` | 123 | re-entrant event pumping inside loops; the page has one event loop and no nested pumping |
| `QProcess`, `QSocketNotifier` | 34 + 6 | no subprocesses |
| native file dialogs, `ctkPathLineEdit` paths | 38 + 229 | only `<input type=file>`; no directory or save-path pickers, no real paths |
| `QMenu`/`QAction` popups, context menus | 17 / 33 | need reimplementing; `menu.exec_(pos)` blocks |
| `QShortcut`, key events, event filters | 8 / 3 / 3 | scoping and browser-reserved keys |
| `QIcon`/`QPixmap`/`ctkWidgetsUtils.grabWidget` | ~155 | screenshots need canvas capture |

Drag and drop, `keyPressEvent` overrides, `QClipboard`, `QNetworkAccessManager` are essentially unused
from Python and can be skipped.

## 3. The size of the real API

- Qt 5.15 QtWidgets has 219 public headers, about 90 of them instantiable widgets. `QWidget` alone
  declares about 272 methods and 59 `Q_PROPERTY`s; `QComboBox` 91 methods, `QAbstractItemView` 130,
  `QTableWidget` 110, `QTreeWidget` 118. What PythonQt exposes is narrower than the headers: only
  `Q_PROPERTY`s, public slots, `Q_INVOKABLE` methods, signals and the decorator-added helpers, which is
  why Slicer and CTK mark so much `Q_INVOKABLE`. That metadata is exactly what a generator can read.
- CTK `Libs/Widgets` has about 100 exported classes and `Libs/Visualization/VTK/Widgets` 30 more (the
  transfer-function and scalars-to-colors editors, the VTK views, matrix and threshold widgets).
- Slicer has 77 `qMRML*` widgets in `Libs/MRML/Widgets`, about 55 more in the loadable modules'
  `Widgets/` directories, and 67 `qSlicer*` headers in `Base/QTGUI` (application, module framework, IO
  dialogs, settings panels, extensions manager).

## 4. Coverage today, measured by the gallery at runtime

"available" means the class has members of its own; "via base" a bare subclass of a working class;
"placeholder" exists so `setup()` does not fail but does nothing; "missing" is an `AttributeError`.

| namespace | listed | available | via base | placeholder | missing |
|---|---|---|---|---|---|
| Qt Widgets (99 widget classes) | 99 | 39 | 4 | 2 | 54 |
| Qt Core/Gui (78 commonly used) | 78 | 23 | 0 | 1 | 54 |
| CTK widgets | 100 | 16 | 5 | 2 | 77 |
| MRML / Slicer widgets | 103 | 19 | 2 | 4 | 78 |

That is the right shape for what is there: the widgets scripted modules use most are in, and the missing
ones are largely view/model classes, dialogs, and the display-node property widgets. Notable missing
classes that shipped modules do hit: `QTreeWidget`, `QTableView`, `QListWidgetItem`, `QStandardItemModel`,
`QProgressDialog` (used by `slicer.util.createProgressDialog`), `QDialogButtonBox`, `QMenuBar`,
`QToolBar`, `QIntValidator`/`QDoubleValidator`, `QRegExp`, `QThread`; `ctkMatrixWidget`, `ctkExpandButton`,
`ctkDynamicSpacer`, `ctkSettingsPanel`, `ctkPopupWidget`, the `ctkVTK*` editors; `qMRMLDisplayNodeWidget`
and friends, `qMRMLMatrixWidget`, `qMRMLCoordinatesWidget`, `qMRMLPlotWidget`, `qMRMLTableWidget`,
`qMRMLSegmentationGeometryWidget`, `qMRMLSequenceBrowser*Widget`.

Behaviour gaps the gallery shows even where a class exists: `QDialog.exec_()` returns at once,
`QMenu` never pops up, `QShortcut` never fires, `QSplitter` does not split, `QScrollArea` ignores its
height, `QRadioButton` is a checkbox unless grouped, `QTableWidget` is read-only, stylesheets are
stored and ignored, `qMRMLSubjectHierarchyTreeView` draws nothing, `qMRMLSegmentEditorWidget` is a
label pointing at the Segment Editor panel, the volume-rendering property widget has no transfer
function editor.

Bugs found while building the gallery, worth sending upstream:

1. `QAbstractSpinBox.setPrefix` (and the `prefix` `.ui` property) throws
   `TypeError: Cannot set property prefix of #<Element> which has only a getter`: the facade writes an
   element property named `prefix`, which the DOM defines read-only on every `Element` (the namespace
   prefix). Renaming the Vue prop (e.g. `prefixText`) fixes it.
2. `QTableWidget._render` builds `innerHTML` from unescaped cell text.
3. `QWidget.setFixedHeight`/`setMinimumWidth` etc. are no-ops, so a `QScrollArea` never scrolls.

## 5. What "emulate the full Qt API that Slicer exposes" would take

Three tiers, in increasing cost.

### Tier A: every shipped scripted module and extension GUI builds and works (months, one engineer)

The 80/20 point measured above. Concretely:

- **Item views with models.** `QListWidget`/`QTableWidget`/`QTreeWidget` with item objects, selection,
  editing and signals; `QTableView`/`QTreeView` over `QStandardItemModel`, `QSortFilterProxyModel`,
  `QAbstractItemModel` and `QItemSelectionModel`; `QHeaderView`. One generic Vue table/tree component
  driven by a Python-side model would cover all of these.
- **Dialogs that block.** See §6; this is the one architectural decision. With it, `QDialog`,
  `QDialogButtonBox`, `QProgressDialog`, `QMessageBox` with custom buttons, `QInputDialog.getItem`,
  `ctkMessageBox` with "don't show again", `QMenu.exec_`, `slicer.util.delayDisplay` and the
  `confirm*Display` family all become faithful.
- **Menus, actions, shortcuts.** `QMenu` popups on `QToolButton`/`ctkMenuButton`, `Qt.CustomContextMenu`
  with `customContextMenuRequested`, `QActionGroup`, `QShortcut`/`setShortcut` bound to `keydown` with
  Qt's context scoping.
- **Geometry and style.** Honour fixed/minimum/maximum sizes, `QSizePolicy` (map to flex-grow),
  `QSplitter` with a drag handle, `QScrollArea` as an overflow box, `QFrame` shapes, a stylesheet subset
  (`color`, `background`, `font-weight`, `border`, `padding`, selectors by object name and class).
- **`.ui` completeness.** `<connections>` (generic signal-to-slot by name, which the `connect` machinery
  already supports), `<buttongroups>`, `<action>`/`<addaction>`, view `<item>`s, `<spacer>` sizes.
- **The CTK short list.** `ctkMatrixWidget`, `ctkExpandButton`, `ctkExpandableWidget` (real),
  `ctkDynamicSpacer`, `ctkSettingsPanel`/`ctkSettingsDialog` (backed by the settings store),
  `ctkPopupWidget`, `ctkCheckableComboBox` (real multi-select), `ctkComboBox` default text,
  `ctkTreeComboBox`, `ctkFileDialog`, `ctkColorDialog`.
- **The MRML short list.** `qMRMLSubjectHierarchyTreeView` (the page already has `ShTree.vue`),
  `qMRMLSegmentEditorWidget` (embed `SegmentEditorPanel.vue`), `qMRMLSegmentsTableView`,
  `qMRMLDisplayNodeWidget`/`qMRMLModelDisplayNodeWidget`/`qMRMLMarkupsDisplayNodeWidget`,
  `qMRMLMatrixWidget`, `qMRMLCoordinatesWidget`, `qMRMLVolumeInfoWidget`, `qMRMLWindowLevelWidget` and
  `qMRMLVolumeThresholdWidget` (real), `qMRMLPlotWidget`/`qMRMLTableWidget` (`PlotView.vue` and
  `TableView.vue` exist), `qMRMLSequenceBrowserPlay/SeekWidget`, `qMRMLLayoutWidget` and the view widgets
  attaching canvases from the existing `LayoutManager`, `qMRMLVolumePropertyNodeWidget` with a
  canvas-drawn transfer function editor (`ctkVTKScalarsToColorsWidget`).
- **`slicer.util` and `slicer.app` chrome.** A `mainWindow()` object with `statusBar()`, a module
  selector (`selectModule`, `moduleSelector`), the `set*Visible` toggles talking to the Vue shell,
  `createProgressDialog`, `pythonShell()` returning the console.

Rough size: 3,000 to 6,000 more lines of Python and 15 to 20 more Vue components, on top of the 5,300
lines and 17 components that exist.

### Tier B: the PythonQt surface of every widget Slicer exposes (many months, generated skeletons)

"Everything exposed" is bounded and machine-readable: every `Q_PROPERTY`, public slot, `Q_INVOKABLE`
method, signal and enum of ~90 Qt widgets, ~130 CTK classes and ~200 Slicer widget classes. A generator
over the headers (the same information PythonQt's wrapper generator consumes; `moc`'s JSON output or a
libclang script would do) can emit the Python classes with the correct property names and types, signal
signatures and slot arities, so that no module ever hits an `AttributeError` and every property round
trips. That is weeks of work and gives complete *shape*.

Behaviour is the cost. Roughly in order of effort: item views and delegates; Qt's event system (event
filters, key/mouse events, focus, tab order); painting (`QPainter` on a canvas for the few custom-painted
widgets); `QGraphicsView`/`QGraphicsScene` (CTK's transfer-function editors are graphics scenes);
docking, MDI, toolbars and menubars; the DICOM browser and database (`ctkDICOM*`, needs SQLite in wasm
and a real DICOM stack); `qSlicerIOManager`'s add-data and save-data dialogs with their option widgets;
settings panels; extensions manager. Each of those is a component in its own right; the MRML widgets are
the bulk, because their C++ logic (scene observation, node filtering, display-property mapping) is not
compiled to WebAssembly (it is Qt code) and has to be rewritten in Python or Vue against the MRML nodes,
which *are* compiled.

### Tier C: things a page cannot do

`QProcess` and `QThread` (no subprocesses; Python threads exist in Pyodide only with cross-origin
isolation); native directory and save-path pickers (the File System Access API is Chromium-only);
`file://` URLs; `QDesktopServices` beyond `window.open`; `QSystemTrayIcon`; real modal application-level
event loops nested arbitrarily deep. These need explicit "not on the web" behaviour, which is what the
facade does today.

## 6. The blocking-dialog decision

Everything in `slicer.util`'s dialog family, `QDialog.exec_()`, `QMenu.exec_()`, `delayDisplay` and the
123 `processEvents()` sites assume a synchronous call that returns when the user is done. Options:

1. **WebAssembly JavaScript Promise Integration (JSPI).** Pyodide's `pyodide.ffi.run_sync(awaitable)`
   suspends the WebAssembly stack until a JavaScript promise settles, with no worker and no
   SharedArrayBuffer. `exec_()` becomes `return run_sync(show_dialog_and_wait())`, `processEvents()`
   becomes `run_sync(sleep(0))`, and unchanged module code just works. JSPI is on by default in
   Chromium-based browsers; Firefox and Safari are behind flags or in progress, so the facade would keep
   the non-blocking fallback for them. This is the path I would take, and it fits SlicerWeb's decision to
   avoid cross-origin isolation.
2. **Pyodide in a Web Worker with `Atomics.wait`.** Truly blocking, works in every browser, but needs
   COOP/COEP headers, moves every DOM touch across a message channel (the whole facade is built on
   synchronous DOM access), and the WebGL views would have to move to `OffscreenCanvas`. A rewrite.
3. **Make call sites async.** Faithful and portable, but it means editing every module, which defeats
   "runs unchanged".

## 7. Alternative: Qt itself in WebAssembly

Qt for WebAssembly exists (Qt 5.15 has a `wasm_32` kit installed here, Qt 6 is better), and one could
build Slicer's Qt layer, CTK and PythonQt for it, getting the full API for free. The costs are why
SlicerWeb went the other way: a 30 to 60 MB Qt runtime on top of the current 70 MB, Qt drawing its own
pixels into a canvas (no HTML text, accessibility, phone layout or CSS theming), PythonQt and CTK's
Python bindings ported to Emscripten dynamic linking, and the same blocking-dialog problem, since Qt
for wasm also forbids `exec()`. It would give the desktop GUI, not a web GUI.

## 8. Suggested order of work

1. Send the three bugs in §4 upstream; small and unambiguous.
2. Land JSPI-backed `exec_()`/`processEvents()` behind a capability check; it unlocks `slicer.util`
   wholesale.
3. Generate property/signal/slot skeletons for the qt, ctk and qMRML classes from the headers, so the
   gallery's "missing" column goes to zero and every module at least builds; keep the gallery as the
   regression test for what is real versus placeholder.
4. Item views over a Python-side model, then menus/shortcuts, then the MRML display widgets by reusing
   the Vue panels the application already has.
5. Transfer-function editor and the view widgets last; they are the only ones that need new rendering.
