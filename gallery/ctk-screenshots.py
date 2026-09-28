"""Screenshots of the real Qt/CTK widgets, taken inside desktop 3D Slicer, for the CTK gallery page.

    /Applications/Slicer-5.9.0-2025-10-16.app/Contents/MacOS/Slicer --no-splash --no-main-window \
        --python-script gallery/ctk-screenshots.py

Each widget is built with the same content the browser replica shows, put in a 340 px wide frame with
Slicer's own style, shown, grabbed and saved to gallery/qt-shots/<name>.png. The application palette,
font and style name go to qt-shots/theme.json so the page's CSS can use the same colours.
"""
import json
import os
import traceback

import ctk
import qt
import slicer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qt-shots")
os.makedirs(OUT, exist_ok=True)
WIDTH = 340
results = []


def snap(name, build, note=""):
    frame = qt.QWidget()
    frame.setObjectName("frame")
    frame.setFixedWidth(WIDTH)
    layout = qt.QVBoxLayout(frame)
    layout.setContentsMargins(8, 8, 8, 8)
    try:
        widget = build()
        if type(widget).__name__.endswith("Layout"):
            layout.addLayout(widget)
        else:
            layout.addWidget(widget)
        frame.show()
        for _ in range(4):
            slicer.app.processEvents()
        frame.adjustSize()
        slicer.app.processEvents()
        pixmap = frame.grab()
        path = os.path.join(OUT, name + ".png")
        pixmap.save(path)
        results.append({"name": name, "file": name + ".png", "width": frame.width, "height": frame.height,
                        "dpr": pixmap.devicePixelRatio(), "note": note})
        print(f"  {name}: {frame.width}x{frame.height} @{pixmap.devicePixelRatio()}")
    except Exception as e:  # noqa: BLE001
        results.append({"name": name, "error": f"{type(e).__name__}: {e}", "note": note})
        print(f"  {name} FAILED: {e}\n{traceback.format_exc()}")
    finally:
        frame.close()
        frame.deleteLater()


# ------------------------------------------------------------------ CTK widgets the browser has
def collapsible():
    b = ctk.ctkCollapsibleButton()
    b.text = "ctkCollapsibleButton"
    f = qt.QFormLayout(b)
    f.addRow("Label:", qt.QLineEdit("a field in a QFormLayout"))
    cb = qt.QCheckBox("checked"); cb.checked = True
    f.addRow("Enabled:", cb)
    inner = ctk.ctkCollapsibleButton()
    inner.text = "Collapsed section"
    inner.collapsed = True
    qt.QVBoxLayout(inner).addWidget(qt.QLabel("hidden"))
    f.addRow(inner)
    return b


def collapsibleGroupBox():
    g = ctk.ctkCollapsibleGroupBox()
    g.title = "ctkCollapsibleGroupBox"
    lay = qt.QVBoxLayout(g)
    lay.addWidget(qt.QLabel("Contents of the group box"))
    lay.addWidget(qt.QPushButton("A button inside"))
    return g


def sliderWidget():
    s = ctk.ctkSliderWidget()
    s.minimum, s.maximum, s.decimals, s.singleStep = -50, 50, 1, 0.5
    s.value = 12.5
    s.suffix = " mm"
    return s


def doubleSlider():
    s = ctk.ctkDoubleSlider()
    s.orientation = qt.Qt.Horizontal
    s.minimum, s.maximum, s.singleStep = 0, 1, 0.01
    s.value = 0.6
    return s


def doubleSpinBox():
    s = ctk.ctkDoubleSpinBox()
    s.minimum, s.maximum, s.decimals, s.singleStep = 0, 1, 2, 0.05
    s.value = 0.25
    s.prefix = "x "
    return s


def rangeWidget():
    r = ctk.ctkRangeWidget()
    r.minimum, r.maximum = 0, 1000
    r.setValues(200, 800)
    return r


def doubleRangeSlider():
    r = ctk.ctkDoubleRangeSlider()
    r.orientation = qt.Qt.Horizontal
    r.minimum, r.maximum, r.singleStep = -1, 1, 0.01
    r.setValues(-0.25, 0.75)
    return r


def pathLineEdit():
    p = ctk.ctkPathLineEdit()
    p.nameFilters = ["Volumes (*.nrrd *.nii *.nii.gz *.mha)", "All files (*)"]
    p.currentPath = "/data/case42/CT-chest.nrrd"
    return p


def directoryButton():
    d = ctk.ctkDirectoryButton()
    d.directory = "/data/case42"
    return d


def comboBox():
    c = ctk.ctkComboBox()
    c.addItems(["one", "two"])
    c.defaultText = "Choose..."
    c.setCurrentIndex(-1)
    return c


def checkableComboBox():
    c = ctk.ctkCheckableComboBox()
    c.addItems(["alpha", "beta", "gamma"])
    model = c.checkableModel()
    c.setCheckState(model.index(0, 0), qt.Qt.Checked)
    c.setCheckState(model.index(2, 0), qt.Qt.Checked)
    return c


def colorPickerButton():
    b = ctk.ctkColorPickerButton()
    b.text = "ctkColorPickerButton"
    b.color = qt.QColor(40, 160, 220)
    b.displayColorName = True
    return b


def pushButton():
    b = ctk.ctkPushButton()
    b.text = "ctkPushButton"
    return b


def checkablePushButton():
    b = ctk.ctkCheckablePushButton()
    b.text = "Apply"
    b.checkBoxUserCheckable = True
    return b


def checkBox():
    c = ctk.ctkCheckBox()
    c.text = "ctkCheckBox"
    c.checked = True
    return c


def menuButton():
    b = ctk.ctkMenuButton()
    b.text = "ctkMenuButton"
    menu = qt.QMenu(b)
    menu.addAction("First action")
    menu.addAction("Second action")
    b.setMenu(menu)
    return b


def searchBox():
    s = ctk.ctkSearchBox()
    s.placeholderText = "Search"
    s.showSearchIcon = True
    return s


def fittedTextBrowser():
    b = ctk.ctkFittedTextBrowser()
    b.setHtml("<b>ctkFittedTextBrowser</b>, read only. It grows to fit its text instead of scrolling.")
    return b


def flowLayout():
    w = qt.QWidget()
    lay = ctk.ctkFlowLayout()
    w.setLayout(lay)
    for i in range(8):
        lay.addWidget(qt.QPushButton(f"Item {i + 1}"))
    return w


def expandableWidget():
    w = ctk.ctkExpandableWidget()
    w.orientations = qt.Qt.Vertical
    lay = qt.QVBoxLayout(w)
    lay.addWidget(qt.QTextEdit("ctkExpandableWidget: drag the grip at the bottom to resize"))
    return w


def coordinatesWidget():
    c = ctk.ctkCoordinatesWidget()
    c.decimals = 1
    c.coordinates = "10.0,-20.5,30.3"
    return c


# ------------------------------------------------------------------ CTK widgets the browser lacks
def matrixWidget():
    m = ctk.ctkMatrixWidget()
    m.rowCount = 4
    m.columnCount = 4
    m.decimals = 2
    for i in range(4):
        m.setValue(i, i, 1.0)
    m.setValue(0, 3, 12.5)
    return m


def expandButton():
    row = qt.QHBoxLayout()
    row.addWidget(qt.QLabel("ctkExpandButton:"))
    b = ctk.ctkExpandButton()
    row.addWidget(b)
    row.addStretch()
    return row


def axesWidget():
    a = ctk.ctkAxesWidget()
    a.setFixedHeight(120)
    a.currentAxis = ctk.ctkAxesWidget.Anterior
    return a


def treeComboBox():
    c = ctk.ctkTreeComboBox()
    model = qt.QStandardItemModel()
    for group, items in (("Volumes", ["CT-chest", "MR-head"]), ("Models", ["Aorta", "Liver"])):
        parent = qt.QStandardItem(group)
        for it in items:
            parent.appendRow(qt.QStandardItem(it))
        model.appendRow(parent)
    c.setModel(model)
    return c


def addRemoveComboBox():
    c = ctk.ctkAddRemoveComboBox()
    c.emptyText = "No presets"
    return c


def menuComboBox():
    c = ctk.ctkMenuComboBox()
    menu = qt.QMenu()
    for name in ("Volumes", "Models", "Markups"):
        sub = menu.addMenu(name)
        sub.addAction(name + " A")
        sub.addAction(name + " B")
    c.setMenu(menu)
    try:
        c.editBehavior = ctk.ctkMenuComboBox.Editable
    except Exception:
        pass
    return c


def fontButton():
    b = ctk.ctkFontButton()
    b.currentFont = qt.QFont("Helvetica", 12)
    return b


def languageComboBox():
    c = ctk.ctkLanguageComboBox()
    c.defaultLanguage = "en"
    return c


def materialPropertyWidget():
    m = ctk.ctkMaterialPropertyWidget()
    return m


def dateRangeWidget():
    return ctk.ctkDateRangeWidget()


def modalityWidget():
    return ctk.ctkModalityWidget()


def pathListWidget():
    w = qt.QWidget()
    lay = qt.QHBoxLayout(w)
    paths = ctk.ctkPathListWidget()
    for path in ("/data/case42", "/data/case43"):
        try:
            paths.addPath(path)
        except Exception:
            pass
    buttons = ctk.ctkPathListButtonsWidget()
    lay.addWidget(paths)
    lay.addWidget(buttons)
    return w


def rangeSlider():
    r = ctk.ctkRangeSlider()
    r.orientation = qt.Qt.Horizontal
    r.minimum, r.maximum = 0, 100
    r.setValues(25, 75)
    return r


def errorLogWidget():
    w = ctk.ctkErrorLogWidget()
    w.setErrorLogModel(slicer.app.errorLogModel())
    w.setFixedHeight(150)
    return w


def actionsWidget():
    w = ctk.ctkActionsWidget()
    a = qt.QAction("Open", w)
    a.shortcut = qt.QKeySequence("Ctrl+O")
    b = qt.QAction("Save", w)
    b.shortcut = qt.QKeySequence("Ctrl+S")
    w.addAction(a)
    w.addAction(b)
    w.setFixedHeight(120)
    return w


def scalarsToColors():
    import vtk
    w = ctk.ctkVTKScalarsToColorsWidget()
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(0, 0, 0, 0)
    ctf.AddRGBPoint(50, 0.9, 0.5, 0.2)
    ctf.AddRGBPoint(100, 1, 1, 1)
    w.view().addColorTransferFunction(ctf)
    w.setFixedHeight(180)
    return w


def transferFunctionView():
    return None


# ------------------------------------------------------------------ core Qt widgets, for the theme
def qtButtons():
    row = qt.QHBoxLayout()
    row.addWidget(qt.QPushButton("QPushButton"))
    c = qt.QPushButton("Checkable")
    c.checkable = True
    c.checked = True
    row.addWidget(c)
    d = qt.QPushButton("Disabled")
    d.enabled = False
    row.addWidget(d)
    return row


def qtToolButton():
    row = qt.QHBoxLayout()
    t = qt.QToolButton()
    t.text = "QToolButton"
    row.addWidget(t)
    row.addStretch()
    return row


def qtCheckRadio():
    col = qt.QVBoxLayout()
    row = qt.QHBoxLayout()
    cb = qt.QCheckBox("QCheckBox"); cb.checked = True
    row.addWidget(cb)
    row.addWidget(qt.QCheckBox("unchecked"))
    col.addLayout(row)
    row2 = qt.QHBoxLayout()
    for i, name in enumerate(("Axial", "Sagittal", "Coronal")):
        r = qt.QRadioButton(name)
        r.checked = i == 0
        row2.addWidget(r)
    col.addLayout(row2)
    return col


def qtLineEdit():
    e = qt.QLineEdit()
    e.placeholderText = "QLineEdit placeholder"
    return e


def qtTextEdit():
    t = qt.QTextEdit()
    t.plainText = "QTextEdit: multi-line text.\nSecond line."
    t.setFixedHeight(70)
    return t


def qtSpinBoxes():
    row = qt.QHBoxLayout()
    s = qt.QSpinBox()
    s.maximum = 100
    s.value = 42
    s.suffix = " %"
    row.addWidget(s)
    d = qt.QDoubleSpinBox()
    d.minimum, d.maximum, d.decimals, d.singleStep = -10, 10, 3, 0.125
    d.value = 1.5
    row.addWidget(d)
    return row


def qtComboBox():
    c = qt.QComboBox()
    c.addItems(["Linear", "Nearest", "B-spline"])
    c.currentIndex = 2
    return c


def qtSlider():
    s = qt.QSlider(qt.Qt.Horizontal)
    s.maximum = 10
    s.value = 3
    return s


def qtProgressBar():
    p = qt.QProgressBar()
    p.value = 45
    return p


def qtGroupBox():
    g = qt.QGroupBox("QGroupBox (checkable)")
    g.checkable = True
    lay = qt.QVBoxLayout(g)
    lay.addWidget(qt.QLabel("Inside a QGroupBox"))
    lay.addWidget(qt.QPushButton("A"))
    return g


def qtTabWidget():
    t = qt.QTabWidget()
    for name in ("Tab A", "Tab B", "Tab C"):
        page = qt.QWidget()
        qt.QVBoxLayout(page).addWidget(qt.QLabel(f"QTabWidget page {name}"))
        t.addTab(page, name)
    return t


def qtListWidget():
    l = qt.QListWidget()
    l.addItems(["QListWidget row 0", "row 1", "row 2", "row 3"])
    l.setCurrentRow(1)
    l.setFixedHeight(90)
    return l


def qtTableWidget():
    t = qt.QTableWidget(3, 3)
    t.setHorizontalHeaderLabels(["Node", "Type", "Voxels"])
    for r, row in enumerate((("CT-chest", "ScalarVolume", "16.7 M"), ("Liver", "Segmentation", "2 segments"), ("Aorta", "Model", "12 k points"))):
        for c, v in enumerate(row):
            t.setItem(r, c, qt.QTableWidgetItem(v))
    t.verticalHeader().visible = False
    t.setFixedHeight(120)
    return t


def qtTreeWidget():
    t = qt.QTreeWidget()
    t.setHeaderLabels(["QTreeWidget"])
    for group, items in (("Volumes", ["CT-chest", "MR-head"]), ("Models", ["Aorta"])):
        parent = qt.QTreeWidgetItem([group])
        for it in items:
            parent.addChild(qt.QTreeWidgetItem([it]))
        t.addTopLevelItem(parent)
    t.expandAll()
    t.setFixedHeight(120)
    return t


def qtFormLayout():
    w = qt.QWidget()
    f = qt.QFormLayout(w)
    f.addRow("Input volume:", qt.QComboBox())
    f.addRow("Threshold:", qt.QDoubleSpinBox())
    f.addRow("Name:", qt.QLineEdit())
    return w


SHOTS = [
    ("ctkCollapsibleButton", collapsible), ("ctkCollapsibleGroupBox", collapsibleGroupBox),
    ("ctkSliderWidget", sliderWidget), ("ctkDoubleSlider", doubleSlider), ("ctkDoubleSpinBox", doubleSpinBox),
    ("ctkRangeWidget", rangeWidget), ("ctkDoubleRangeSlider", doubleRangeSlider),
    ("ctkPathLineEdit", pathLineEdit), ("ctkDirectoryButton", directoryButton),
    ("ctkComboBox", comboBox), ("ctkCheckableComboBox", checkableComboBox),
    ("ctkColorPickerButton", colorPickerButton), ("ctkPushButton", pushButton),
    ("ctkCheckablePushButton", checkablePushButton), ("ctkCheckBox", checkBox), ("ctkMenuButton", menuButton),
    ("ctkSearchBox", searchBox), ("ctkFittedTextBrowser", fittedTextBrowser), ("ctkFlowLayout", flowLayout),
    ("ctkExpandableWidget", expandableWidget), ("ctkCoordinatesWidget", coordinatesWidget),
    ("ctkMatrixWidget", matrixWidget), ("ctkExpandButton", expandButton), ("ctkAxesWidget", axesWidget),
    ("ctkTreeComboBox", treeComboBox), ("ctkAddRemoveComboBox", addRemoveComboBox), ("ctkMenuComboBox", menuComboBox),
    ("ctkFontButton", fontButton), ("ctkLanguageComboBox", languageComboBox),
    ("ctkMaterialPropertyWidget", materialPropertyWidget), ("ctkDateRangeWidget", dateRangeWidget),
    ("ctkModalityWidget", modalityWidget), ("ctkPathListWidget", pathListWidget), ("ctkRangeSlider", rangeSlider),
    ("ctkErrorLogWidget", errorLogWidget), ("ctkActionsWidget", actionsWidget),
    ("ctkVTKScalarsToColorsWidget", scalarsToColors),
    ("QPushButton", qtButtons), ("QToolButton", qtToolButton), ("QCheckBox+QRadioButton", qtCheckRadio),
    ("QLineEdit", qtLineEdit), ("QTextEdit", qtTextEdit), ("QSpinBox+QDoubleSpinBox", qtSpinBoxes),
    ("QComboBox", qtComboBox), ("QSlider", qtSlider), ("QProgressBar", qtProgressBar), ("QGroupBox", qtGroupBox),
    ("QTabWidget", qtTabWidget), ("QListWidget", qtListWidget), ("QTableWidget", qtTableWidget),
    ("QTreeWidget", qtTreeWidget), ("QFormLayout", qtFormLayout),
]

def style_name():
    try:
        return str(qt.QApplication.style().objectName)
    except Exception:
        try:
            return str(slicer.app.settings().value("Styles/Style", "Slicer"))
        except Exception:
            return "?"


try:
    print(f"Slicer {slicer.app.applicationVersion}, style {style_name()}")
    for name, build in SHOTS:
        snap(name, build)

    palette = slicer.app.palette()
    roles = ["Window", "WindowText", "Base", "AlternateBase", "Text", "Button", "ButtonText", "BrightText", "Highlight",
             "HighlightedText", "Light", "Midlight", "Mid", "Dark", "Shadow", "ToolTipBase", "ToolTipText", "PlaceholderText", "Link"]
    theme = {
        "slicerVersion": slicer.app.applicationVersion,
        "style": style_name(),
        "font": {"family": slicer.app.font().family(), "pointSize": slicer.app.font().pointSize(), "pixelSize": slicer.app.font().pixelSize()},
        "palette": {role: palette.color(getattr(qt.QPalette, role)).name() for role in roles if hasattr(qt.QPalette, role)},
        "disabled": {role: palette.color(qt.QPalette.Disabled, getattr(qt.QPalette, role)).name() for role in ("WindowText", "Text", "ButtonText", "Base", "Button")},
        "shots": results,
    }
    with open(os.path.join(OUT, "theme.json"), "w") as f:
        json.dump(theme, f, indent=1)
    print(f"wrote {len(results)} shots, theme.json")
except Exception:
    traceback.print_exc()
finally:
    print("exiting")
    slicer.app.exit(0)
