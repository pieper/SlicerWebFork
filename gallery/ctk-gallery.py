"""Replicas for the CTK gallery page: the same widgets ctk-screenshots.py photographs in desktop
Slicer, built here with SlicerWeb's qt/ctk compatibility layer, running in bare Pyodide (no VTK, no
MRML: only the slicerweb wheel). build(name, container_id) puts the replica into the page.
"""
import js
import qt
import ctk


def report(name, text):
    """What a replica just reported, shown under it."""
    el = js.document.getElementById("sig-" + name)
    if el is not None:
        el.textContent = text


def _wrap(layout):
    w = qt.QWidget()
    w.setLayout(layout)
    return w


# ------------------------------------------------------------------ CTK widgets the browser has
def collapsible():
    b = ctk.ctkCollapsibleButton("ctkCollapsibleButton")
    b.contentsCollapsed.connect(lambda c: report("ctkCollapsibleButton", f"contentsCollapsed({c})"))
    f = qt.QFormLayout(b)
    f.addRow("Label:", qt.QLineEdit("a field in a QFormLayout"))
    cb = qt.QCheckBox("checked")
    cb.setChecked(True)
    f.addRow("Enabled:", cb)
    inner = ctk.ctkCollapsibleButton("Collapsed section")
    inner.collapsed = True
    qt.QVBoxLayout(inner).addWidget(qt.QLabel("hidden"))
    f.addRow(inner)
    return b


def collapsibleGroupBox():
    g = ctk.ctkCollapsibleGroupBox()
    g.setTitle("ctkCollapsibleGroupBox")
    lay = qt.QVBoxLayout(g)
    lay.addWidget(qt.QLabel("Contents of the group box"))
    lay.addWidget(qt.QPushButton("A button inside"))
    return g


def sliderWidget():
    s = ctk.ctkSliderWidget()
    s.setRange(-50, 50)
    s.setDecimals(1)
    s.setSingleStep(0.5)
    s.setValue(12.5)
    s.setSuffix(" mm")
    s.valueChanged.connect(lambda v: report("ctkSliderWidget", f"valueChanged({v})"))
    return s


def doubleSlider():
    s = ctk.ctkDoubleSlider()
    s.setRange(0, 1)
    s.setSingleStep(0.01)
    s.setValue(0.6)
    s.valueChanged.connect(lambda v: report("ctkDoubleSlider", f"valueChanged({v})"))
    return s


def doubleSpinBox():
    s = ctk.ctkDoubleSpinBox()
    s.setRange(0, 1)
    s.setDecimals(2)
    s.setSingleStep(0.05)
    s.setValue(0.25)
    s.valueChanged.connect(lambda v: report("ctkDoubleSpinBox", f"valueChanged({v})"))
    return s


def rangeWidget():
    r = ctk.ctkRangeWidget()
    r.setRange(0, 1000)
    r.setValues(200, 800)
    r.valuesChanged.connect(lambda lo, hi: report("ctkRangeWidget", f"valuesChanged({lo}, {hi})"))
    return r


def doubleRangeSlider():
    r = ctk.ctkDoubleRangeSlider()
    r.setRange(-1, 1)
    r.setSingleStep(0.01)
    r.setDecimals(2)
    r.setValues(-0.25, 0.75)
    r.valuesChanged.connect(lambda lo, hi: report("ctkDoubleRangeSlider", f"valuesChanged({lo:.2f}, {hi:.2f})"))
    return r


def pathLineEdit():
    p = ctk.ctkPathLineEdit()
    p.setNameFilters(["Volumes (*.nrrd *.nii *.nii.gz *.mha)", "All files (*)"])
    p.setCurrentPath("/data/case42/CT-chest.nrrd")
    p.currentPathChanged.connect(lambda path: report("ctkPathLineEdit", f"currentPathChanged({path})"))
    return p


def directoryButton():
    d = ctk.ctkDirectoryButton()
    d.directory = "/data/case42"
    d.directoryChanged.connect(lambda path: report("ctkDirectoryButton", f"directoryChanged({path})"))
    return d


def comboBox():
    c = ctk.ctkComboBox()
    c.addItems(["one", "two"])
    c.setDefaultText("Choose...")
    c.currentTextChanged.connect(lambda t: report("ctkComboBox", f"currentTextChanged({t})"))
    return c


def checkableComboBox():
    c = ctk.ctkCheckableComboBox()
    c.addItems(["alpha", "beta", "gamma"])
    c.checkedIndexesChanged.connect(lambda: report("ctkCheckableComboBox", f"checkedIndexes -> {c.checkedIndexes()}"))
    return c


def colorPickerButton():
    b = ctk.ctkColorPickerButton("ctkColorPickerButton")
    b.setColor(qt.QColor(40, 160, 220))
    b.colorChanged.connect(lambda c: report("ctkColorPickerButton", f"colorChanged({c.name()})"))
    return b


def pushButton():
    b = ctk.ctkPushButton("ctkPushButton")
    b.clicked.connect(lambda: report("ctkPushButton", "clicked()"))
    return b


def checkablePushButton():
    b = ctk.ctkCheckablePushButton("Apply")
    b.clicked.connect(lambda *a: report("ctkCheckablePushButton", "clicked()"))
    b.checkBoxToggled.connect(lambda on: report("ctkCheckablePushButton", f"checkBoxToggled({on})"))
    return b


def checkBox():
    c = ctk.ctkCheckBox("ctkCheckBox")
    c.setChecked(True)
    c.toggled.connect(lambda on: report("ctkCheckBox", f"toggled({on})"))
    return c


def menuButton():
    b = ctk.ctkMenuButton("ctkMenuButton")
    menu = qt.QMenu(b)
    for text in ("First action", "Second action"):
        menu.addAction(text).triggered.connect(lambda checked=False, t=text: report("ctkMenuButton", f"QAction '{t}' triggered"))
    b.setMenu(menu)
    b.clicked.connect(lambda: report("ctkMenuButton", "clicked(); the menu does not pop up in the browser"))
    return b


def searchBox():
    s = ctk.ctkSearchBox()
    s.setPlaceholderText("Search")
    s.textChanged.connect(lambda t: report("ctkSearchBox", f"textChanged({t!r})"))
    return s


def fittedTextBrowser():
    b = ctk.ctkFittedTextBrowser()
    b.setHtml("<b>ctkFittedTextBrowser</b>, read only. It grows to fit its text instead of scrolling.")
    return b


def flowLayout():
    w = qt.QWidget()
    lay = ctk.ctkFlowLayout(w)
    for i in range(8):
        b = qt.QPushButton(f"Item {i + 1}")
        b.clicked.connect(lambda checked=False, i=i: report("ctkFlowLayout", f"Item {i + 1} clicked"))
        lay.addWidget(b)
    return w


def expandableWidget():
    w = ctk.ctkExpandableWidget()
    lay = qt.QVBoxLayout(w)
    t = qt.QTextEdit()
    t.setPlainText("ctkExpandableWidget: the size grip is not emulated")
    lay.addWidget(t)
    return w


def coordinatesWidget():
    c = ctk.ctkCoordinatesWidget()
    c.setDecimals(1)
    c.coordinates = "10.0,-20.5,30.3"
    c.coordinatesChanged.connect(lambda *a: report("ctkCoordinatesWidget", f"coordinatesChanged -> {c.coordinates}"))
    return c


# ------------------------------------------------------------------ core Qt widgets
def qtButtons():
    row = qt.QHBoxLayout()
    b = qt.QPushButton("QPushButton")
    b.clicked.connect(lambda: report("QPushButton", "clicked()"))
    row.addWidget(b)
    c = qt.QPushButton("Checkable")
    c.setCheckable(True)
    c.setChecked(True)
    c.toggled.connect(lambda on: report("QPushButton", f"toggled({on})"))
    row.addWidget(c)
    d = qt.QPushButton("Disabled")
    d.setEnabled(False)
    row.addWidget(d)
    return _wrap(row)


def qtToolButton():
    row = qt.QHBoxLayout()
    t = qt.QToolButton()
    t.setText("QToolButton")
    t.clicked.connect(lambda: report("QToolButton", "clicked()"))
    row.addWidget(t)
    row.addStretch()
    return _wrap(row)


def qtCheckRadio():
    col = qt.QVBoxLayout()
    row = qt.QHBoxLayout()
    a = qt.QCheckBox("QCheckBox")
    a.setChecked(True)
    a.toggled.connect(lambda on: report("QCheckBox+QRadioButton", f"QCheckBox toggled({on})"))
    row.addWidget(a)
    row.addWidget(qt.QCheckBox("unchecked"))
    col.addLayout(row)
    row2 = qt.QHBoxLayout()
    group = qt.QButtonGroup()
    for i, name in enumerate(("Axial", "Sagittal", "Coronal")):
        r = qt.QRadioButton(name)
        r.setChecked(i == 0)
        group.addButton(r, i)
        row2.addWidget(r)
    group.idToggled.connect(lambda id, on: on and report("QCheckBox+QRadioButton", f"QButtonGroup idToggled({id})"))
    col.addLayout(row2)
    w = _wrap(col)
    w._group = group
    return w


def qtLineEdit():
    e = qt.QLineEdit()
    e.setPlaceholderText("QLineEdit placeholder")
    e.textChanged.connect(lambda t: report("QLineEdit", f"textChanged({t!r})"))
    return e


def qtTextEdit():
    t = qt.QTextEdit()
    t.setPlainText("QTextEdit: multi-line text.\nSecond line.")
    t.textChanged.connect(lambda: report("QTextEdit", "textChanged()"))
    return t


def qtSpinBoxes():
    row = qt.QHBoxLayout()
    s = qt.QSpinBox()
    s.setRange(0, 100)
    s.setValue(42)
    s.setSuffix(" %")
    s.valueChanged.connect(lambda v: report("QSpinBox+QDoubleSpinBox", f"QSpinBox valueChanged({v})"))
    row.addWidget(s)
    d = qt.QDoubleSpinBox()
    d.setRange(-10, 10)
    d.setDecimals(3)
    d.setSingleStep(0.125)
    d.setValue(1.5)
    d.valueChanged.connect(lambda v: report("QSpinBox+QDoubleSpinBox", f"QDoubleSpinBox valueChanged({v})"))
    row.addWidget(d)
    return _wrap(row)


def qtComboBox():
    c = qt.QComboBox()
    c.addItems(["Linear", "Nearest", "B-spline"])
    c.setCurrentIndex(2)
    c.currentIndexChanged.connect(lambda i: report("QComboBox", f"currentIndexChanged({i})"))
    return c


def qtSlider():
    s = qt.QSlider(qt.Qt.Horizontal)
    s.setRange(0, 10)
    s.setValue(3)
    s.valueChanged.connect(lambda v: report("QSlider", f"valueChanged({v})"))
    return s


def qtProgressBar():
    p = qt.QProgressBar()
    p.setRange(0, 100)
    p.setValue(45)
    return p


def qtGroupBox():
    g = qt.QGroupBox("QGroupBox (checkable)")
    g.setCheckable(True)
    lay = qt.QVBoxLayout(g)
    lay.addWidget(qt.QLabel("Inside a QGroupBox"))
    b = qt.QPushButton("A")
    b.clicked.connect(lambda: report("QGroupBox", "A clicked()"))
    lay.addWidget(b)
    return g


def qtTabWidget():
    t = qt.QTabWidget()
    for name in ("Tab A", "Tab B", "Tab C"):
        page = qt.QWidget()
        qt.QVBoxLayout(page).addWidget(qt.QLabel(f"QTabWidget page {name}"))
        t.addTab(page, name)
    t.currentChanged.connect(lambda i: report("QTabWidget", f"currentChanged({i})"))
    return t


def qtListWidget():
    l = qt.QListWidget()
    l.setObjectName("QListWidget")
    l.addItems(["QListWidget row 0", "row 1", "row 2", "row 3"])
    l.setCurrentRow(1)
    l.currentRowChanged.connect(lambda r: report("QListWidget", f"currentRowChanged({r})"))
    return l


def qtTableWidget():
    t = qt.QTableWidget()
    t.setRowCount(3)
    t.setColumnCount(3)
    t.setHorizontalHeaderLabels(["Node", "Type", "Voxels"])
    for r, row in enumerate((("CT-chest", "ScalarVolume", "16.7 M"), ("Liver", "Segmentation", "2 segments"), ("Aorta", "Model", "12 k points"))):
        for c, v in enumerate(row):
            t.setItem(r, c, qt.QTableWidgetItem(v))
    return t


def qtFormLayout():
    w = qt.QWidget()
    f = qt.QFormLayout(w)
    f.addRow("Input volume:", qt.QComboBox())
    f.addRow("Threshold:", qt.QDoubleSpinBox())
    f.addRow("Name:", qt.QLineEdit())
    return w


BUILDERS = {
    "ctkCollapsibleButton": collapsible, "ctkCollapsibleGroupBox": collapsibleGroupBox,
    "ctkSliderWidget": sliderWidget, "ctkDoubleSlider": doubleSlider, "ctkDoubleSpinBox": doubleSpinBox,
    "ctkRangeWidget": rangeWidget, "ctkDoubleRangeSlider": doubleRangeSlider,
    "ctkPathLineEdit": pathLineEdit, "ctkDirectoryButton": directoryButton,
    "ctkComboBox": comboBox, "ctkCheckableComboBox": checkableComboBox,
    "ctkColorPickerButton": colorPickerButton, "ctkPushButton": pushButton,
    "ctkCheckablePushButton": checkablePushButton, "ctkCheckBox": checkBox, "ctkMenuButton": menuButton,
    "ctkSearchBox": searchBox, "ctkFittedTextBrowser": fittedTextBrowser, "ctkFlowLayout": flowLayout,
    "ctkExpandableWidget": expandableWidget, "ctkCoordinatesWidget": coordinatesWidget,
    "QPushButton": qtButtons, "QToolButton": qtToolButton, "QCheckBox+QRadioButton": qtCheckRadio,
    "QLineEdit": qtLineEdit, "QTextEdit": qtTextEdit, "QSpinBox+QDoubleSpinBox": qtSpinBoxes,
    "QComboBox": qtComboBox, "QSlider": qtSlider, "QProgressBar": qtProgressBar, "QGroupBox": qtGroupBox,
    "QTabWidget": qtTabWidget, "QListWidget": qtListWidget, "QTableWidget": qtTableWidget,
    "QFormLayout": qtFormLayout,
}

# Widgets the compatibility layer does not have (the page shows the Qt screenshot alone)
NOTES = {
    "ctkMatrixWidget": "not in the browser layer (ctk.ctkMatrixWidget is missing)",
    "ctkExpandButton": "not in the browser layer",
    "ctkAxesWidget": "not in the browser layer",
    "ctkTreeComboBox": "not in the browser layer",
    "ctkAddRemoveComboBox": "not in the browser layer",
    "ctkMenuComboBox": "not in the browser layer",
    "ctkFontButton": "not in the browser layer",
    "ctkLanguageComboBox": "not in the browser layer",
    "ctkMaterialPropertyWidget": "not in the browser layer",
    "ctkDateRangeWidget": "not in the browser layer",
    "ctkModalityWidget": "not in the browser layer",
    "ctkPathListWidget": "not in the browser layer",
    "ctkRangeSlider": "not in the browser layer (ctkRangeWidget is; this is the bare slider)",
    "ctkErrorLogWidget": "not in the browser layer (the application has its own log window)",
    "ctkActionsWidget": "not in the browser layer",
    "ctkVTKScalarsToColorsWidget": "not in the browser layer (needs a canvas transfer function editor)",
    "QTreeWidget": "qt.QTreeWidget is missing from the browser layer",
}

_keep = []   # the replicas, kept alive (their DOM listeners hold Python callbacks)


def build(name, container_id):
    """Build the replica of a widget into a page element; returns a status string."""
    container = js.document.getElementById(container_id)
    builder = BUILDERS.get(name)
    if builder is None:
        return NOTES.get(name, "no replica for this widget")
    try:
        widget = builder()
    except Exception as e:  # noqa: BLE001
        return f"failed: {type(e).__name__}: {e}"
    _keep.append(widget)
    container.appendChild(widget.element())
    return "ok"


def names():
    return list(BUILDERS)
