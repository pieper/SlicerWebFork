"""Widget Gallery: every Qt, CTK and MRML widget the browser's qt/ctk layer offers, on one panel.

A scripted module in the ordinary sense (ScriptedLoadableModule + Widget, a .ui file, slicer.util),
so what it shows is exactly what a module written for desktop Slicer gets when it runs here. Each
section is a ctkCollapsibleButton; every signal it wires up writes a line to the event log at the
top, so what a widget reports can be seen as it is used.

The first section is a coverage report: the classes of Qt Widgets, CTK and the MRML widgets as
their headers list them, against what this runtime provides (available, a bare placeholder, or
missing). It is computed at run time, so it stays true as the compatibility layer grows.
"""

import logging
import os
import traceback

import qt
import ctk
import vtk

import slicer
from slicer.ScriptedLoadableModule import (
    ScriptedLoadableModule,
    ScriptedLoadableModuleLogic,
    ScriptedLoadableModuleTest,
    ScriptedLoadableModuleWidget,
)

logger = logging.getLogger("WidgetGallery")


# ------------------------------------------------------------------------------------ class lists
# QtWidgets 5.15, as listed by its public headers (QStyle*, QGraphics*, QGesture*, accessibility and
# platform classes left out: a module GUI does not touch those).
QT_WIDGET_CLASSES = """
QAbstractButton QAbstractItemDelegate QAbstractItemView QAbstractScrollArea QAbstractSlider
QAbstractSpinBox QAction QActionGroup QApplication QBoxLayout QButtonGroup QCalendarWidget QCheckBox
QColorDialog QColumnView QComboBox QCommandLinkButton QCompleter QDataWidgetMapper QDateEdit
QDateTimeEdit QDial QDialog QDialogButtonBox QDockWidget QDoubleSpinBox QErrorMessage QFileDialog
QFileSystemModel QFocusFrame QFontComboBox QFontDialog QFormLayout QFrame QGridLayout QGroupBox
QHBoxLayout QHeaderView QInputDialog QItemDelegate QKeySequenceEdit QLCDNumber QLabel QLayout
QLayoutItem QLineEdit QListView QListWidget QListWidgetItem QMainWindow QMdiArea QMdiSubWindow QMenu
QMenuBar QMessageBox QOpenGLWidget QPlainTextEdit QProgressBar QProgressDialog QPushButton
QRadioButton QRubberBand QScrollArea QScrollBar QShortcut QSizeGrip QSizePolicy QSlider QSpacerItem
QSpinBox QSplashScreen QSplitter QStackedLayout QStackedWidget QStatusBar QStyledItemDelegate
QSystemTrayIcon QTabBar QTabWidget QTableView QTableWidget QTableWidgetItem QTextBrowser QTextEdit
QTimeEdit QToolBar QToolBox QToolButton QToolTip QTreeView QTreeWidget QTreeWidgetItem QUndoStack
QVBoxLayout QWhatsThis QWidget QWidgetAction QWizard QWizardPage
""".split()

# QtCore and QtGui classes a scripted module reaches for (not widgets, but part of the same facade).
QT_CORE_CLASSES = """
QObject QTimer QSettings QEvent QEventLoop QThread QProcess QVariant QSize QSizeF QPoint QPointF
QRect QRectF QUrl QDir QFile QFileInfo QTemporaryDir QTemporaryFile QStandardPaths QDateTime QDate
QTime QLocale QTranslator QByteArray QIODevice QTextStream QDataStream QBuffer QUuid QSignalMapper
QAbstractItemModel QStandardItemModel QStandardItem QSortFilterProxyModel QModelIndex
QItemSelectionModel QItemSelection QRegExp QRegularExpression QCryptographicHash QMimeData
QNetworkAccessManager QNetworkRequest QNetworkReply
QColor QIcon QPixmap QImage QFont QFontMetrics QCursor QKeySequence QPalette QPainter QPen QBrush
QClipboard QDrag QDesktopServices QTextDocument QTextCursor QTextCharFormat QValidator
QIntValidator QDoubleValidator QRegExpValidator QKeyEvent QMouseEvent QWheelEvent QShowEvent
QCloseEvent QResizeEvent QGuiApplication QScreen QWindow
""".split()

# CTK/Libs/Widgets and CTK/Libs/Visualization/VTK/Widgets, as their headers list them (private,
# plugin, testing and event-player classes left out).
CTK_WIDGET_CLASSES = """
ctkActionsWidget ctkAddRemoveComboBox ctkAxesWidget ctkBasePopupWidget ctkButtonGroup ctkCheckBox
ctkCheckBoxPixmaps ctkCheckableComboBox ctkCheckableHeaderView ctkCheckableModelHelper
ctkCheckablePushButton ctkCollapsibleButton ctkCollapsibleGroupBox ctkColorDialog
ctkColorPickerButton ctkComboBox ctkCompleter ctkConsole ctkCoordinatesWidget ctkCrosshairLabel
ctkDateRangeWidget ctkDirectoryButton ctkDoubleRangeSlider ctkDoubleSlider ctkDoubleSpinBox
ctkDynamicSpacer ctkErrorLogModel ctkErrorLogWidget ctkExpandButton ctkExpandableWidget
ctkFileDialog ctkFittedTextBrowser ctkFlatProxyModel ctkFlowLayout ctkFontButton ctkHistogram
ctkLanguageComboBox ctkLayoutManager ctkMaterialPropertyPreviewLabel ctkMaterialPropertyWidget
ctkMatrixWidget ctkMenuButton ctkMenuComboBox ctkMessageBox ctkModalityWidget ctkPathLineEdit
ctkPathListButtonsWidget ctkPathListWidget ctkPopupWidget ctkProxyStyle ctkPushButton ctkQImageView
ctkRangeSlider ctkRangeWidget ctkScreenshotDialog ctkSearchBox ctkSettings ctkSettingsDialog
ctkSettingsPanel ctkSignalMapper ctkSizeGrip ctkSliderWidget ctkSplitter ctkThumbnailLabel
ctkThumbnailListWidget ctkToolTipTrapper ctkTransferFunction ctkTransferFunctionView
ctkTreeComboBox ctkWorkflowButtonBoxWidget ctkWorkflowGroupBox ctkWorkflowStackedWidget
ctkWorkflowTabWidget ctkWorkflowWidget ctkWorkflowWidgetStep
ctkVTKAbstractView ctkVTKChartView ctkVTKColorTransferFunction ctkVTKCompositeFunction
ctkVTKDataSetArrayComboBox ctkVTKDataSetModel ctkVTKDiscretizableColorTransferWidget ctkVTKHistogram
ctkVTKLookupTable ctkVTKMagnifyView ctkVTKMatrixWidget ctkVTKOpenGLNativeWidget ctkVTKPiecewiseFunction
ctkVTKPropertyWidget ctkVTKRenderView ctkVTKScalarBarWidget ctkVTKScalarsToColorsComboBox
ctkVTKScalarsToColorsView ctkVTKScalarsToColorsWidget ctkVTKSliceView ctkVTKSurfaceMaterialPropertyWidget
ctkVTKTextPropertyWidget ctkVTKThresholdWidget ctkVTKThumbnailView ctkVTKVolumePropertyWidget
""".split()

# Slicer/Libs/MRML/Widgets, Base/QTGUI and the widgets of the loadable modules that Python reaches
# through the slicer namespace (event players, delegates and models left out).
MRML_WIDGET_CLASSES = """
qMRMLWidget qMRMLAbstractViewWidget qMRMLCheckableNodeComboBox qMRMLClipNodeDisplayWidget
qMRMLClipNodeWidget qMRMLCollapsibleButton qMRMLColorTableComboBox qMRMLCoordinatesWidget
qMRMLDisplayNodeViewComboBox qMRMLDisplayNodeWidget qMRMLEventBrokerWidget qMRMLExpandingWebView
qMRMLLabelComboBox qMRMLLayoutManager qMRMLLayoutWidget qMRMLLinearTransformSlider qMRMLListWidget
qMRMLMatrixWidget qMRMLModelInfoWidget qMRMLNavigationView qMRMLNodeAttributeTableView
qMRMLNodeAttributeTableWidget qMRMLNodeComboBox qMRMLPlotView qMRMLPlotViewControllerWidget
qMRMLPlotWidget qMRMLROIWidget qMRMLRangeWidget qMRMLScalarInvariantComboBox
qMRMLScalarsDisplayWidget qMRMLSceneModel qMRMLSortFilterProxyModel qMRMLScreenShotDialog
qMRMLSegmentSelectorWidget qMRMLSliceControllerWidget qMRMLSliceInformationWidget
qMRMLSliceVerticalControllerWidget qMRMLSliceView qMRMLSliceWidget qMRMLSliderWidget qMRMLSpinBox
qMRMLTableModel qMRMLTableView qMRMLTableViewControllerWidget qMRMLTableWidget qMRMLThreeDView
qMRMLThreeDViewControllerWidget qMRMLThreeDViewInformationWidget qMRMLThreeDWidget
qMRMLTransformSliders qMRMLTreeView qMRMLViewControllerBar qMRMLVolumeInfoWidget
qMRMLVolumeThresholdWidget qMRMLVolumeWidget qMRMLWindowLevelWidget
qMRMLSubjectHierarchyTreeView qMRMLSubjectHierarchyComboBox qMRMLSubjectHierarchyModel
qMRMLSegmentsTableView qMRMLSegmentEditorWidget qMRMLSegmentationConversionParametersWidget
qMRMLSegmentationDisplayNodeWidget qMRMLSegmentationFileExportWidget qMRMLSegmentationGeometryWidget
qMRMLMarkupsDisplayNodeWidget qMRMLMarkupsROIWidget qMRMLMarkupsPlaneWidget
qMRMLMarkupsInteractionHandleWidget qMRMLModelDisplayNodeWidget qMRMLColorPickerWidget
qMRMLColorLegendDisplayNodeWidget qMRMLPlotChartPropertiesWidget qMRMLPlotSeriesPropertiesWidget
qMRMLSequenceBrowserPlayWidget qMRMLSequenceBrowserSeekWidget qMRMLSequenceEditWidget qMRMLTextWidget
qMRMLTransformDisplayNodeWidget qMRMLTransformInfoWidget qMRMLUnitWidget qMRMLVolumePropertyNodeWidget
qSlicerWidget qSlicerAbstractModuleWidget qSlicerScriptedLoadableModuleWidget qSlicerModuleWidget
qSlicerSimpleMarkupsWidget qSlicerMarkupsPlaceWidget qSlicerTerminologyNavigatorWidget
qSlicerTerminologyEditorWidget qSlicerVolumeRenderingPresetComboBox
qSlicerVolumeRenderingPropertiesWidget qSlicerGPURayCastVolumeRenderingPropertiesWidget
qSlicerScalarVolumeDisplayWidget qSlicerLabelMapVolumeDisplayWidget qSlicerVolumeDisplayWidget
qSlicerDTISliceDisplayWidget qSlicerTableColumnPropertiesWidget qSlicerWebWidget
qSlicerIOOptionsWidget qSlicerFileWriterOptionsWidget qSlicerNodeWriterOptionsWidget
qSlicerExtensionsManagerWidget
""".split()


def _class_status(cls):
    """How much of a class is there: 'available', 'via base' (a bare subclass of a working
    class), 'placeholder' (a bare subclass of QWidget/QObject) or 'missing'."""
    if cls is None:
        return "missing"
    if not isinstance(cls, type):
        return "available"
    own = [k for k in vars(cls) if not k.startswith("_") and k not in ("Signal",)]
    if own:
        return "available"
    bases = [b.__name__ for b in cls.__mro__[1:]]
    if bases and bases[0] in ("QWidget", "QObject", "qMRMLWidget", "object", "_ElementWidget"):
        return "placeholder"
    return "via base"


def coverage():
    """[(group, class name, status)] for every class the lists above name."""
    rows = []
    for name in QT_WIDGET_CLASSES:
        rows.append(("Qt Widgets", name, _class_status(getattr(qt, name, None))))
    for name in QT_CORE_CLASSES:
        rows.append(("Qt Core/Gui", name, _class_status(getattr(qt, name, None))))
    for name in CTK_WIDGET_CLASSES:
        rows.append(("CTK", name, _class_status(getattr(ctk, name, None))))
    for name in MRML_WIDGET_CLASSES:
        rows.append(("MRML/Slicer", name, _class_status(getattr(slicer, name, None))))
    return rows


# ------------------------------------------------------------------------------------ the module
class WidgetGallery(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Widget Gallery"
        self.parent.categories = ["Developer Tools"]
        self.parent.dependencies = []
        self.parent.contributors = ["Steve Pieper (Isomics, Inc.)"]
        self.parent.helpText = (
            "Every Qt, CTK and MRML widget the browser's qt/ctk compatibility layer provides, on one "
            "panel, with a coverage report against the real toolkits' class lists. Each control writes "
            "what it reports to the event log at the top."
        )
        self.parent.acknowledgementText = "Built to study SlicerWeb's Qt emulation (lassoan/SlicerWeb)."


class WidgetGalleryWidget(ScriptedLoadableModuleWidget):
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.logic = None
        self.demoNodes = {}
        self.failures = []   # [(section, widget, error)]
        self._timer = None
        self._sections = []

    # --- helpers ------------------------------------------------------------------------------
    def log(self, text):
        self.eventLog.appendPlainText(str(text))

    def safely(self, label, fn):
        """A click handler: what it returns, or the exception it raised, goes to the log."""
        def run(*args):
            try:
                result = fn()
                self.log(f"{label} -> {result!r}")
            except Exception as e:  # noqa: BLE001
                self.log(f"{label} raised {type(e).__name__}: {e}")
        return run

    def section(self, title, form=False, collapsed=False):
        button = ctk.ctkCollapsibleButton()
        button.text = title
        button.collapsed = collapsed
        self.layout.addWidget(button)
        layout = qt.QFormLayout(button) if form else qt.QVBoxLayout(button)
        self._sections.append((title, button))
        return button, layout

    def guarded(self, section, name, factory):
        """Run a widget's factory; a failure becomes a red note instead of stopping setup()."""
        try:
            return factory()
        except Exception as e:  # noqa: BLE001 - shown to the user
            self.failures.append((section, name, f"{type(e).__name__}: {e}"))
            logger.warning("Widget Gallery: %s in %s failed: %s", name, section, traceback.format_exc())
            note = qt.QLabel(f"{name}: {type(e).__name__}: {e}")
            note.setStyleSheet("color: #ff8080")
            return note

    # --- setup --------------------------------------------------------------------------------
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.logic = WidgetGalleryLogic()

        # Event log first, so every section below can write to it
        logBox, logLayout = self.section("Event log", collapsed=False)
        self.eventLog = qt.QPlainTextEdit()
        self.eventLog.setReadOnly(True)
        self.eventLog.setMaximumBlockCount(60)
        self.eventLog.placeholderText = "Signals from the widgets below appear here"
        logLayout.addWidget(self.eventLog)
        row = qt.QHBoxLayout()
        clearButton = qt.QPushButton("Clear log")
        clearButton.clicked.connect(lambda: self.eventLog.clear())
        row.addWidget(clearButton)
        self.disableAll = qt.QCheckBox("Disable every section (QWidget.setEnabled on containers)")
        self.disableAll.toggled.connect(self.onDisableAll)
        row.addWidget(self.disableAll)
        row.addStretch()
        logLayout.addLayout(row)

        self.setupCoverage()
        self.setupButtons()
        self.setupInputs()
        self.setupSliders()
        self.setupContainers()
        self.setupItemViews()
        self.setupUiFile()
        self.setupMRMLWidgets()
        self.setupDialogs()
        self.setupApplication()
        self.setupFailures()
        self.layout.addStretch(1)
        self.log(f"Widget Gallery ready: {len(self._sections)} sections, {len(self.failures)} widgets failed to build")

    def onDisableAll(self, disabled):
        for title, button in self._sections:
            if title not in ("Event log",):
                button.setEnabled(not disabled)
        self.log(f"setEnabled({not disabled}) on {len(self._sections) - 1} sections")

    # --- coverage -----------------------------------------------------------------------------
    def setupCoverage(self):
        box, layout = self.section("Coverage: the toolkits' classes against this runtime", collapsed=True)
        rows = coverage()
        groups = {}
        for group, name, status in rows:
            groups.setdefault(group, []).append((name, status))
        summary = []
        for group, items in groups.items():
            counts = {}
            for _, status in items:
                counts[status] = counts.get(status, 0) + 1
            summary.append(f"{group}: {counts.get('available', 0)} available, {counts.get('via base', 0)} via base, "
                           f"{counts.get('placeholder', 0)} placeholders, {counts.get('missing', 0)} missing of {len(items)}")
        label = qt.QLabel("\n".join(summary))
        label.setWordWrap(True)
        layout.addWidget(label)
        note = qt.QLabel("'available' = the class has members of its own here; 'via base' = a bare subclass of a working "
                         "class (usually fine); 'placeholder' = exists so that setup() does not fail, does nothing; "
                         "'missing' = AttributeError on use.")
        note.setWordWrap(True)
        layout.addWidget(note)
        tabs = qt.QTabWidget()
        for group, items in groups.items():
            table = qt.QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Class", "Status"])
            table.setRowCount(len(items))
            for i, (name, status) in enumerate(sorted(items, key=lambda x: ({"missing": 0, "placeholder": 1, "via base": 2, "available": 3}[x[1]], x[0]))):
                table.setItem(i, 0, qt.QTableWidgetItem(name))
                table.setItem(i, 1, qt.QTableWidgetItem(status))
            tabs.addTab(table, group)
        layout.addWidget(tabs)
        self.coverageRows = rows

    # --- buttons ------------------------------------------------------------------------------
    def setupButtons(self):
        box, layout = self.section("Buttons: QPushButton, QToolButton, QCheckBox, QRadioButton, QButtonGroup, CTK buttons", form=True)
        S = "Buttons"

        def pushButtons():
            row = qt.QHBoxLayout()
            b = qt.QPushButton("QPushButton")
            b.setToolTip("clicked() goes to the log")
            b.clicked.connect(lambda: self.log("QPushButton clicked"))
            row.addWidget(b)
            c = qt.QPushButton("Checkable")
            c.setCheckable(True)
            c.toggled.connect(lambda on: self.log(f"checkable QPushButton toggled -> {on}"))
            row.addWidget(c)
            d = qt.QPushButton("Disabled")
            d.setEnabled(False)
            row.addWidget(d)
            t = qt.QToolButton()
            t.setText("QToolButton")
            t.clicked.connect(lambda: self.log("QToolButton clicked"))
            row.addWidget(t)
            row.addStretch()
            return row
        layout.addRow("Push buttons", self.guarded(S, "QPushButton", pushButtons))

        def checkBoxes():
            row = qt.QHBoxLayout()
            a = qt.QCheckBox("QCheckBox")
            a.setChecked(True)
            a.toggled.connect(lambda on: self.log(f"QCheckBox toggled -> {on}"))
            row.addWidget(a)
            b = ctk.ctkCheckBox("ctkCheckBox")
            b.stateChanged.connect(lambda state: self.log(f"ctkCheckBox stateChanged -> {state}"))
            row.addWidget(b)
            row.addStretch()
            return row
        layout.addRow("Check boxes", self.guarded(S, "QCheckBox", checkBoxes))

        def radios():
            row = qt.QHBoxLayout()
            group = qt.QButtonGroup(box)
            for i, name in enumerate(("Axial", "Sagittal", "Coronal")):
                r = qt.QRadioButton(name)
                if i == 0:
                    r.setChecked(True)
                group.addButton(r, i)
                row.addWidget(r)
            group.idToggled.connect(lambda id, on: on and self.log(f"QButtonGroup idToggled -> {id}"))
            row.addStretch()
            self.radioGroup = group
            return row
        layout.addRow("Radio buttons", self.guarded(S, "QRadioButton/QButtonGroup", radios))

        def ctkButtons():
            row = qt.QHBoxLayout()
            apply = ctk.ctkCheckablePushButton("Apply")
            apply.setToolTip("The check box is 'auto-update'; the button is the action")
            apply.clicked.connect(lambda *a: self.log("ctkCheckablePushButton clicked (run once)"))
            apply.checkBoxToggled.connect(lambda on: self.log(f"ctkCheckablePushButton checkBoxToggled -> {on}"))
            row.addWidget(apply)
            p = ctk.ctkPushButton("ctkPushButton")
            p.clicked.connect(lambda: self.log("ctkPushButton clicked"))
            row.addWidget(p)
            m = ctk.ctkMenuButton("ctkMenuButton")
            menu = qt.QMenu(m)
            for text in ("First action", "Second action"):
                action = menu.addAction(text)
                action.triggered.connect(lambda checked=False, t=text: self.log(f"QAction '{t}' triggered"))
            m.setMenu(menu)
            m.clicked.connect(lambda: [a.trigger() for a in menu.actions()[:1]] and self.log("ctkMenuButton: menu popups are not emulated; first QAction triggered instead"))
            row.addWidget(m)
            row.addStretch()
            return row
        layout.addRow("CTK buttons", self.guarded(S, "ctk buttons", ctkButtons))

        def actions():
            row = qt.QHBoxLayout()
            action = qt.QAction("QAction (checkable)", box)
            action.setCheckable(True)
            action.toggled.connect(lambda on: self.log(f"QAction toggled -> {on}"))
            b = qt.QPushButton("Trigger the QAction")
            b.clicked.connect(action.trigger)
            row.addWidget(b)
            s = qt.QShortcut(qt.QKeySequence("Ctrl+G"), box)
            s.activated.connect(lambda: self.log("QShortcut activated"))
            row.addWidget(qt.QLabel("QShortcut Ctrl+G exists (keyboard shortcuts are not delivered here)"))
            row.addStretch()
            return row
        layout.addRow("Actions", self.guarded(S, "QAction/QShortcut", actions))

    # --- inputs -------------------------------------------------------------------------------
    def setupInputs(self):
        box, layout = self.section("Text, numbers, choices: QLineEdit, QTextEdit, spin boxes, combo boxes, paths, colors", form=True)
        S = "Inputs"

        def lineEdit():
            e = qt.QLineEdit()
            e.setPlaceholderText("QLineEdit: textChanged / editingFinished")
            e.textChanged.connect(lambda t: self.log(f"QLineEdit textChanged -> {t!r}"))
            e.editingFinished.connect(lambda: self.log("QLineEdit editingFinished"))
            return e
        layout.addRow("QLineEdit", self.guarded(S, "QLineEdit", lineEdit))

        def search():
            e = ctk.ctkSearchBox()
            e.setPlaceholderText("ctkSearchBox")
            e.textChanged.connect(lambda t: self.log(f"ctkSearchBox -> {t!r}"))
            return e
        layout.addRow("ctkSearchBox", self.guarded(S, "ctkSearchBox", search))

        def textEdit():
            e = qt.QTextEdit()
            e.setPlainText("QTextEdit: multi-line text.\nEdit me; textChanged is logged.")
            e.textChanged.connect(lambda: self.log(f"QTextEdit textChanged ({len(e.toPlainText())} chars)"))
            return e
        layout.addRow("QTextEdit", self.guarded(S, "QTextEdit", textEdit))

        def browser():
            b = ctk.ctkFittedTextBrowser()
            b.setHtml("<b>ctkFittedTextBrowser</b>, read only. Rich text arrives as its text here.")
            return b
        layout.addRow("Text browser", self.guarded(S, "ctkFittedTextBrowser", browser))

        def spins():
            row = qt.QHBoxLayout()
            s = qt.QSpinBox()
            s.setRange(0, 100)
            s.setValue(42)
            s.setSuffix(" %")
            s.valueChanged.connect(lambda v: self.log(f"QSpinBox -> {v}"))
            row.addWidget(s)
            d = qt.QDoubleSpinBox()
            d.setRange(-10, 10)
            d.setDecimals(3)
            d.setSingleStep(0.125)
            d.setValue(1.5)
            d.valueChanged.connect(lambda v: self.log(f"QDoubleSpinBox -> {v}"))
            row.addWidget(d)
            c = ctk.ctkDoubleSpinBox()
            c.setRange(0, 1)
            c.setDecimals(2)
            c.setSingleStep(0.05)
            c.setValue(0.25)
            # setPrefix is left out: the facade maps it to the element's "prefix" property, which the
            # DOM defines read-only on every Element (its namespace prefix) - a bug to report upstream
            c.valueChanged.connect(lambda v: self.log(f"ctkDoubleSpinBox -> {v}"))
            row.addWidget(c)
            return row
        layout.addRow("Spin boxes", self.guarded(S, "spin boxes", spins))

        def combos():
            row = qt.QHBoxLayout()
            c = qt.QComboBox()
            for text, data in (("Linear", 1), ("Nearest", 0), ("B-spline", 3)):
                c.addItem(text, data)
            c.setCurrentIndex(2)
            c.currentIndexChanged.connect(lambda i: self.log(f"QComboBox currentIndexChanged -> {i} ({c.currentText}, data={c.currentData})"))
            row.addWidget(c)
            k = ctk.ctkComboBox()
            k.addItems(["ctkComboBox", "one", "two"])
            k.setDefaultText("Choose…")
            k.currentTextChanged.connect(lambda t: self.log(f"ctkComboBox -> {t}"))
            row.addWidget(k)
            x = ctk.ctkCheckableComboBox()
            x.addItems(["ctkCheckableComboBox", "alpha", "beta"])
            x.checkedIndexesChanged.connect(lambda: self.log(f"ctkCheckableComboBox checked -> {x.checkedIndexes()}"))
            row.addWidget(x)
            return row
        layout.addRow("Combo boxes", self.guarded(S, "combo boxes", combos))

        def paths():
            col = qt.QVBoxLayout()
            p = ctk.ctkPathLineEdit()
            p.setNameFilters(["Volumes (*.nrrd *.nii *.nii.gz *.mha)", "All files (*)"])
            p.currentPathChanged.connect(lambda path: self.log(f"ctkPathLineEdit currentPathChanged -> {path}"))
            col.addWidget(p)
            d = ctk.ctkDirectoryButton()
            d.directoryChanged.connect(lambda path: self.log(f"ctkDirectoryButton directoryChanged -> {path}"))
            col.addWidget(d)
            return col
        layout.addRow("Paths", self.guarded(S, "ctkPathLineEdit", paths))

        def colors():
            row = qt.QHBoxLayout()
            c = ctk.ctkColorPickerButton("ctkColorPickerButton")
            c.setColor(qt.QColor(40, 160, 220))
            c.colorChanged.connect(lambda color: self.log(f"ctkColorPickerButton colorChanged -> {color.name()} rgb={color.red()},{color.green()},{color.blue()}"))
            row.addWidget(c)
            row.addStretch()
            return row
        layout.addRow("Color", self.guarded(S, "ctkColorPickerButton", colors))

        def coords():
            c = ctk.ctkCoordinatesWidget()
            c.setDecimals(1)
            c.coordinates = "10.0,-20.5,30.25"
            c.coordinatesChanged.connect(lambda *a: self.log(f"ctkCoordinatesWidget -> {c.coordinates}"))
            return c
        layout.addRow("Coordinates", self.guarded(S, "ctkCoordinatesWidget", coords))

    # --- sliders ------------------------------------------------------------------------------
    def setupSliders(self):
        box, layout = self.section("Sliders and progress: QSlider, ctkSliderWidget, ctkRangeWidget, QProgressBar + QTimer", form=True)
        S = "Sliders"

        def qslider():
            s = qt.QSlider(qt.Qt.Horizontal)
            s.setRange(0, 10)
            s.setValue(3)
            s.valueChanged.connect(lambda v: self.log(f"QSlider -> {v}"))
            return s
        layout.addRow("QSlider", self.guarded(S, "QSlider", qslider))

        def ctkslider():
            s = ctk.ctkSliderWidget()
            s.setRange(-50, 50)
            s.setDecimals(1)
            s.setSingleStep(0.5)
            s.setValue(12.5)
            s.setSuffix(" mm")
            s.valueChanged.connect(lambda v: self.log(f"ctkSliderWidget -> {v}"))
            return s
        layout.addRow("ctkSliderWidget", self.guarded(S, "ctkSliderWidget", ctkslider))

        def dslider():
            s = ctk.ctkDoubleSlider()
            s.setRange(0, 1)
            s.setSingleStep(0.01)
            s.setValue(0.6)
            s.valueChanged.connect(lambda v: self.log(f"ctkDoubleSlider -> {v}"))
            return s
        layout.addRow("ctkDoubleSlider", self.guarded(S, "ctkDoubleSlider", dslider))

        def rng():
            r = ctk.ctkRangeWidget()
            r.setRange(0, 1000)
            r.setValues(200, 800)
            r.valuesChanged.connect(lambda lo, hi: self.log(f"ctkRangeWidget valuesChanged -> {lo}, {hi}"))
            return r
        layout.addRow("ctkRangeWidget", self.guarded(S, "ctkRangeWidget", rng))

        def drng():
            r = ctk.ctkDoubleRangeSlider()
            r.setRange(-1, 1)
            r.setSingleStep(0.01)
            r.setDecimals(2)
            r.setValues(-0.25, 0.75)
            r.valuesChanged.connect(lambda lo, hi: self.log(f"ctkDoubleRangeSlider -> {lo:.2f}, {hi:.2f}"))
            return r
        layout.addRow("ctkDoubleRangeSlider", self.guarded(S, "ctkDoubleRangeSlider", drng))

        def progress():
            col = qt.QVBoxLayout()
            bar = qt.QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            col.addWidget(bar)
            row = qt.QHBoxLayout()
            start = qt.QPushButton("Start a QTimer (100 ms)")
            stop = qt.QPushButton("Stop")
            timer = qt.QTimer()
            timer.setInterval(100)

            def tick():
                bar.setValue((bar.value + 5) % 101)
                if bar.value == 100:
                    self.log("QProgressBar reached 100 (QTimer.timeout)")
            timer.timeout.connect(tick)
            start.clicked.connect(lambda: (timer.start(), self.log(f"QTimer started, isActive={timer.isActive()}")))
            stop.clicked.connect(lambda: (timer.stop(), self.log("QTimer stopped")))
            once = qt.QPushButton("QTimer.singleShot(1500)")
            once.clicked.connect(lambda: qt.QTimer.singleShot(1500, lambda: self.log("QTimer.singleShot fired after 1.5 s")))
            row.addWidget(start)
            row.addWidget(stop)
            row.addWidget(once)
            row.addStretch()
            col.addLayout(row)
            self._timer = timer
            return col
        layout.addRow("QProgressBar", self.guarded(S, "QProgressBar/QTimer", progress))

    # --- containers ---------------------------------------------------------------------------
    def setupContainers(self):
        box, layout = self.section("Containers and layouts: QGroupBox, collapsibles, QTabWidget, QStackedWidget, QGridLayout, ctkFlowLayout, QSplitter, QScrollArea")
        S = "Containers"

        def groupBox():
            g = qt.QGroupBox("QGroupBox (checkable)")
            g.setCheckable(True)
            g.toggled.connect(lambda on: self.log(f"QGroupBox toggled -> {on}"))
            l = qt.QVBoxLayout(g)
            l.addWidget(qt.QLabel("Inside a QGroupBox with a QVBoxLayout"))
            inner = qt.QHBoxLayout()
            inner.addWidget(qt.QPushButton("A"))
            inner.addWidget(qt.QPushButton("B"))
            inner.addStretch(1)
            inner.addWidget(qt.QPushButton("C (after addStretch)"))
            l.addLayout(inner)
            return g
        layout.addWidget(self.guarded(S, "QGroupBox", groupBox))

        def collapsibleGroup():
            g = ctk.ctkCollapsibleGroupBox()
            g.setTitle("ctkCollapsibleGroupBox")
            g.collapsed = False
            l = qt.QVBoxLayout(g)
            l.addWidget(qt.QLabel("Rendered as a QGroupBox: collapsing is kept as a property only"))
            return g
        layout.addWidget(self.guarded(S, "ctkCollapsibleGroupBox", collapsibleGroup))

        def nested():
            outer = ctk.ctkCollapsibleButton("Nested ctkCollapsibleButton (collapsed by default)")
            outer.collapsed = True
            outer.contentsCollapsed.connect(lambda c: self.log(f"nested ctkCollapsibleButton contentsCollapsed -> {c}"))
            l = qt.QFormLayout(outer)
            l.addRow("A row", qt.QLineEdit("in a QFormLayout"))
            inner = ctk.ctkCollapsibleButton("Inner")
            qt.QVBoxLayout(inner).addWidget(qt.QLabel("Two levels down"))
            l.addRow(inner)
            return outer
        layout.addWidget(self.guarded(S, "ctkCollapsibleButton", nested))

        def tabs():
            t = qt.QTabWidget()
            for name in ("Tab A", "Tab B", "Tab C"):
                page = qt.QWidget()
                qt.QVBoxLayout(page).addWidget(qt.QLabel(f"QTabWidget page {name}"))
                t.addTab(page, name)
            t.currentChanged.connect(lambda i: self.log(f"QTabWidget currentChanged -> {i} ({t.tabText(i)})"))
            return t
        layout.addWidget(self.guarded(S, "QTabWidget", tabs))

        def stacked():
            col = qt.QVBoxLayout()
            chooser = qt.QComboBox()
            stack = qt.QStackedWidget()
            for name in ("Page one", "Page two", "Page three"):
                chooser.addItem(name)
                page = qt.QWidget()
                qt.QVBoxLayout(page).addWidget(qt.QLabel(f"QStackedWidget shows: {name}"))
                stack.addWidget(page)
            chooser.currentIndexChanged.connect(stack.setCurrentIndex)
            stack.currentChanged.connect(lambda i: self.log(f"QStackedWidget currentChanged -> {i}"))
            col.addWidget(chooser)
            col.addWidget(stack)
            return col
        layout.addLayout(self.guarded(S, "QStackedWidget", stacked))

        def grid():
            g = qt.QGroupBox("QGridLayout 3x3 with a 2-column span")
            l = qt.QGridLayout(g)
            for r in range(3):
                for c in range(3):
                    if (r, c) == (2, 1):
                        continue
                    b = qt.QPushButton(f"({r},{c})")
                    b.clicked.connect(lambda checked=False, r=r, c=c: self.log(f"grid cell ({r},{c}) clicked"))
                    l.addWidget(b, r, c, 1, 2 if (r, c) == (2, 0) else 1)
            return g
        layout.addWidget(self.guarded(S, "QGridLayout", grid))

        def flow():
            g = qt.QGroupBox("ctkFlowLayout: wraps to the panel width")
            l = ctk.ctkFlowLayout(g)
            for i in range(14):
                l.addWidget(qt.QPushButton(f"Item {i + 1}"))
            return g
        layout.addWidget(self.guarded(S, "ctkFlowLayout", flow))

        def splitter():
            s = qt.QSplitter()
            s.setOrientation(qt.Qt.Horizontal)
            for name in ("QSplitter left", "QSplitter right"):
                w = qt.QTextEdit()
                w.setPlainText(name)
                s.addWidget(w)
            return s
        layout.addWidget(self.guarded(S, "QSplitter", splitter))

        def scroll():
            area = qt.QScrollArea()
            area.setWidgetResizable(True)
            area.setFixedHeight(90)
            content = qt.QWidget()
            l = qt.QVBoxLayout(content)
            for i in range(8):
                l.addWidget(qt.QLabel(f"QScrollArea line {i + 1} (the area is 90 px high)"))
            area.setWidget(content)
            return area
        layout.addWidget(self.guarded(S, "QScrollArea", scroll))

        def frame():
            f = qt.QFrame()
            f.setFrameShape(getattr(qt.QFrame, "StyledPanel", 6))
            f.setStyleSheet("border: 1px solid #5a7; padding: 4px")
            qt.QVBoxLayout(f).addWidget(qt.QLabel("QFrame with a stylesheet border"))
            return f
        layout.addWidget(self.guarded(S, "QFrame", frame))

    # --- item views ---------------------------------------------------------------------------
    def setupItemViews(self):
        box, layout = self.section("Item views: QListWidget, QTableWidget", form=True)
        S = "Item views"

        def listWidget():
            l = qt.QListWidget()
            l.addItems(["QListWidget row 0", "row 1", "row 2", "row 3"])
            l.currentRowChanged.connect(lambda r: self.log(f"QListWidget currentRowChanged -> {r}"))
            return l
        layout.addRow("QListWidget", self.guarded(S, "QListWidget", listWidget))

        def table():
            t = qt.QTableWidget()
            t.setRowCount(3)
            t.setColumnCount(3)
            t.setHorizontalHeaderLabels(["Node", "Type", "Voxels"])
            for r, (name, kind, n) in enumerate((("CT-chest", "ScalarVolume", "16.7 M"), ("Liver", "Segmentation", "2 segments"), ("Aorta", "Model", "12 k points"))):
                for c, v in enumerate((name, kind, n)):
                    t.setItem(r, c, qt.QTableWidgetItem(v))
            t.cellClicked.connect(lambda r, c: self.log(f"QTableWidget cellClicked -> {r},{c}"))
            return t
        layout.addRow("QTableWidget", self.guarded(S, "QTableWidget", table))

        def tree():
            t = qt.QTreeWidget()
            t.setHeaderLabels(["QTreeWidget"])
            return t
        layout.addRow("QTreeWidget", self.guarded(S, "QTreeWidget", tree))

    # --- .ui file -----------------------------------------------------------------------------
    def setupUiFile(self):
        box, layout = self.section("Qt Designer .ui file through slicer.util.loadUI + childWidgetVariables")
        S = ".ui file"

        def load():
            path = self.resourcePath("UI/WidgetGallery.ui")
            uiWidget = slicer.util.loadUI(path)
            layout.addWidget(uiWidget)
            self.ui = slicer.util.childWidgetVariables(uiWidget)
            uiWidget.setMRMLScene(slicer.mrmlScene)
            self.ui.inputSelector.setMRMLScene(slicer.mrmlScene)
            self.ui.inputSelector.currentNodeChanged.connect(lambda node: self.log(f".ui inputSelector -> {node.GetName() if node else None}"))
            self.ui.thresholdSlider.valueChanged.connect(lambda v: self.log(f".ui thresholdSlider -> {v}"))
            self.ui.rangeWidget.valuesChanged.connect(lambda lo, hi: self.log(f".ui rangeWidget -> {lo}, {hi}"))
            self.ui.nameEdit.textChanged.connect(lambda t: self.log(f".ui nameEdit -> {t!r}"))
            self.ui.colorButton.colorChanged.connect(lambda c: self.log(f".ui colorButton -> {c.name()}"))
            self.ui.invertCheckBox.toggled.connect(lambda on: self.log(f".ui invertCheckBox -> {on}"))
            self.ui.applyButton.clicked.connect(lambda *a: self.log(f".ui applyButton clicked; auto-update={self.ui.applyButton.checked}"))
            self.ui.tabWidget.currentChanged.connect(lambda i: self.log(f".ui tabWidget -> {i}"))
            self.ui.tabSpinBox.valueChanged.connect(lambda v: self.log(f".ui tabSpinBox -> {v}"))
            names = sorted(k for k in vars(self.ui) if not k.startswith("_"))
            note = qt.QLabel(f"childWidgetVariables found {len(names)} named widgets: {', '.join(names)}")
            note.setWordWrap(True)
            layout.addWidget(note)
            param = self.ui.inputSelector.property("SlicerParameterName")
            layout.addWidget(qt.QLabel(f"Dynamic property SlicerParameterName on inputSelector: {param!r}"))
            return uiWidget
        self.guarded(S, "loadUI", load)

    # --- MRML widgets -------------------------------------------------------------------------
    def setupMRMLWidgets(self):
        box, layout = self.section("MRML widgets: node selectors, subject hierarchy, markups, segments, transforms, volume rendering", form=True)
        S = "MRML"
        makeButton = qt.QPushButton("Create demo nodes (volume, model, markups, transform, segmentation)")
        makeButton.clicked.connect(self.createDemoNodes)
        layout.addRow(makeButton)

        def nodeCombo():
            c = slicer.qMRMLNodeComboBox()
            c.nodeTypes = ["vtkMRMLScalarVolumeNode"]
            c.addEnabled = True
            c.removeEnabled = True
            c.renameEnabled = True
            c.noneEnabled = True
            c.setMRMLScene(slicer.mrmlScene)
            c.currentNodeChanged.connect(lambda node: self.log(f"qMRMLNodeComboBox currentNodeChanged -> {node.GetName() if node else None}"))
            c.nodeAddedByUser.connect(lambda node: self.log(f"qMRMLNodeComboBox nodeAddedByUser -> {node.GetName() if node else None}"))
            self.volumeSelector = c
            return c
        layout.addRow("qMRMLNodeComboBox", self.guarded(S, "qMRMLNodeComboBox", nodeCombo))

        def multiCombo():
            c = slicer.qMRMLNodeComboBox()
            c.nodeTypes = ["vtkMRMLModelNode", "vtkMRMLMarkupsFiducialNode"]
            c.noneEnabled = True
            c.setMRMLScene(slicer.mrmlScene)
            c.currentNodeChanged.connect(lambda node: self.log(f"models/markups selector -> {node.GetName() if node else None}"))
            return c
        layout.addRow("Two node types", self.guarded(S, "qMRMLNodeComboBox(2 types)", multiCombo))

        def checkable():
            c = slicer.qMRMLCheckableNodeComboBox()
            c.nodeTypes = ["vtkMRMLModelNode"]
            c.setMRMLScene(slicer.mrmlScene)
            c.checkedNodesChanged.connect(lambda: self.log(f"qMRMLCheckableNodeComboBox checked -> {[n.GetName() for n in c.checkedNodes()]}"))
            return c
        layout.addRow("qMRMLCheckableNodeComboBox", self.guarded(S, "qMRMLCheckableNodeComboBox", checkable))

        def shCombo():
            c = slicer.qMRMLSubjectHierarchyComboBox()
            c.setMRMLScene(slicer.mrmlScene)
            c.currentItemChanged.connect(lambda item: self.log(f"qMRMLSubjectHierarchyComboBox currentItemChanged -> {item}"))
            return c
        layout.addRow("qMRMLSubjectHierarchyComboBox", self.guarded(S, "qMRMLSubjectHierarchyComboBox", shCombo))

        def colorCombo():
            c = slicer.qMRMLColorTableComboBox()
            c.setMRMLScene(slicer.mrmlScene)
            c.currentNodeChanged.connect(lambda node: self.log(f"qMRMLColorTableComboBox -> {node.GetName() if node else None}"))
            return c
        layout.addRow("qMRMLColorTableComboBox", self.guarded(S, "qMRMLColorTableComboBox", colorCombo))

        def mrmlSlider():
            s = slicer.qMRMLSliderWidget()
            s.setMRMLScene(slicer.mrmlScene)
            s.setQuantity("length")
            s.setRange(0, 100)
            s.setValue(25)
            s.valueChanged.connect(lambda v: self.log(f"qMRMLSliderWidget -> {v}"))
            return s
        layout.addRow("qMRMLSliderWidget", self.guarded(S, "qMRMLSliderWidget", mrmlSlider))

        def mrmlSpin():
            s = slicer.qMRMLSpinBox()
            s.setMRMLScene(slicer.mrmlScene)
            s.setQuantity("length")
            s.setValue(7)
            s.valueChanged.connect(lambda v: self.log(f"qMRMLSpinBox -> {v}"))
            return s
        layout.addRow("qMRMLSpinBox", self.guarded(S, "qMRMLSpinBox", mrmlSpin))

        def mrmlRange():
            r = slicer.qMRMLRangeWidget()
            r.setMRMLScene(slicer.mrmlScene)
            r.setQuantity("length")
            r.setRange(-100, 100)
            r.setValues(-30, 40)
            r.valuesChanged.connect(lambda lo, hi: self.log(f"qMRMLRangeWidget -> {lo}, {hi}"))
            return r
        layout.addRow("qMRMLRangeWidget", self.guarded(S, "qMRMLRangeWidget", mrmlRange))

        def transformSliders():
            t = slicer.qMRMLTransformSliders()
            t.setMRMLScene(slicer.mrmlScene)
            t.setTitle("qMRMLTransformSliders (translation)")
            t.setTypeOfTransform(slicer.qMRMLTransformSliders.TRANSLATION if hasattr(slicer.qMRMLTransformSliders, "TRANSLATION") else 0)
            t.setRange(-100, 100)
            t.valuesChanged.connect(lambda: self.log("qMRMLTransformSliders valuesChanged"))
            self.transformSliders = t
            return t
        layout.addRow(self.guarded(S, "qMRMLTransformSliders", transformSliders))

        def segmentSelector():
            s = slicer.qMRMLSegmentSelectorWidget()
            s.setMRMLScene(slicer.mrmlScene)
            s.currentSegmentChanged.connect(lambda id: self.log(f"qMRMLSegmentSelectorWidget currentSegmentChanged -> {id}"))
            s.currentNodeChanged.connect(lambda node: self.log(f"qMRMLSegmentSelectorWidget node -> {node.GetName() if node else None}"))
            self.segmentSelector = s
            return s
        layout.addRow("qMRMLSegmentSelectorWidget", self.guarded(S, "qMRMLSegmentSelectorWidget", segmentSelector))

        def segmentsTable():
            t = slicer.qMRMLSegmentsTableView()
            self.segmentsTable = t
            return t
        layout.addRow("qMRMLSegmentsTableView", self.guarded(S, "qMRMLSegmentsTableView", segmentsTable))

        def markups():
            m = slicer.qSlicerSimpleMarkupsWidget()
            m.setMRMLScene(slicer.mrmlScene)
            m.setNodeBaseName("GalleryPoints")
            m.markupsNodeChanged.connect(lambda: self.log("qSlicerSimpleMarkupsWidget markupsNodeChanged"))
            m.activeMarkupsFiducialPlaceModeChanged.connect(lambda on: self.log(f"place mode -> {on}"))
            self.markupsWidget = m
            return m
        layout.addRow(self.guarded(S, "qSlicerSimpleMarkupsWidget", markups))

        def placeWidget():
            p = slicer.qSlicerMarkupsPlaceWidget()
            p.setMRMLScene(slicer.mrmlScene)
            p.setPlaceModePersistency(True)
            p.activeMarkupsPlaceModeChanged.connect(lambda on: self.log(f"qSlicerMarkupsPlaceWidget place mode -> {on}"))
            self.placeWidget = p
            return p
        layout.addRow("qSlicerMarkupsPlaceWidget", self.guarded(S, "qSlicerMarkupsPlaceWidget", placeWidget))

        def shTree():
            t = slicer.qMRMLSubjectHierarchyTreeView()
            t.setMRMLScene(slicer.mrmlScene)
            t.setFixedHeight(160)
            t.currentItemChanged.connect(lambda item: self.log(f"qMRMLSubjectHierarchyTreeView currentItemChanged -> {item}"))
            return t
        layout.addRow(self.guarded(S, "qMRMLSubjectHierarchyTreeView", shTree))

        def vrPreset():
            c = slicer.qSlicerVolumeRenderingPresetComboBox()
            c.setMRMLScene(slicer.mrmlScene)
            c.currentNodeChanged.connect(lambda node: self.log(f"qSlicerVolumeRenderingPresetComboBox -> {node.GetName() if node else None}"))
            return c
        layout.addRow("VR presets", self.guarded(S, "qSlicerVolumeRenderingPresetComboBox", vrPreset))

        def vrProperty():
            w = slicer.qMRMLVolumePropertyNodeWidget()
            w.setMRMLScene(slicer.mrmlScene)
            w.volumePropertyNodeChanged.connect(lambda: self.log("qMRMLVolumePropertyNodeWidget volumePropertyNodeChanged"))
            self.vrPropertyWidget = w
            return w
        layout.addRow("qMRMLVolumePropertyNodeWidget", self.guarded(S, "qMRMLVolumePropertyNodeWidget", vrProperty))

        def windowLevel():
            w = slicer.qMRMLWindowLevelWidget()
            w.setMRMLScene(slicer.mrmlScene)
            self.windowLevelWidget = w
            return w
        layout.addRow("qMRMLWindowLevelWidget", self.guarded(S, "qMRMLWindowLevelWidget", windowLevel))

        def threshold():
            w = slicer.qMRMLVolumeThresholdWidget()
            w.setMRMLScene(slicer.mrmlScene)
            self.thresholdWidget = w
            return w
        layout.addRow("qMRMLVolumeThresholdWidget", self.guarded(S, "qMRMLVolumeThresholdWidget", threshold))

        def views():
            row = qt.QHBoxLayout()
            for name in ("qMRMLSliceWidget", "qMRMLThreeDWidget", "qMRMLTableView", "qMRMLPlotView"):
                cls = getattr(slicer, name, None)
                w = cls() if cls else qt.QLabel(f"{name}: missing")
                if cls:
                    w.setFixedHeight(40)
                    w.setStyleSheet("border: 1px dashed #888")
                    inner = qt.QVBoxLayout(w)
                    inner.addWidget(qt.QLabel(f"{name}: placeholder (views live in the layout, not in a panel)"))
                row.addWidget(w)
            return row
        layout.addRow("View widgets", self.guarded(S, "view widgets", views))

    def createDemoNodes(self):
        try:
            self.demoNodes = self.logic.createDemoNodes()
        except Exception as e:  # noqa: BLE001
            self.log(f"createDemoNodes failed: {type(e).__name__}: {e}")
            logger.exception("createDemoNodes failed")
            return
        n = self.demoNodes
        self.log("Demo nodes: " + ", ".join(f"{k}={v.GetName()}" for k, v in n.items()))
        for attr, key, setter in (("transformSliders", "transform", "setMRMLTransformNode"),
                                  ("segmentSelector", "segmentation", "setCurrentNode"),
                                  ("segmentsTable", "segmentation", "setSegmentationNode"),
                                  ("markupsWidget", "markups", "setCurrentNode"),
                                  ("placeWidget", "markups", "setCurrentNode"),
                                  ("windowLevelWidget", "volume", "setMRMLVolumeNode"),
                                  ("thresholdWidget", "volume", "setMRMLVolumeNode"),
                                  ("volumeSelector", "volume", "setCurrentNode")):
            widget = getattr(self, attr, None)
            if widget is not None and key in n:
                try:
                    getattr(widget, setter)(n[key])
                except Exception as e:  # noqa: BLE001
                    self.log(f"{attr}.{setter} failed: {e}")
        if hasattr(self, "vrPropertyWidget") and "volumeProperty" in n:
            try:
                self.vrPropertyWidget.setMRMLVolumePropertyNode(n["volumeProperty"])
            except Exception as e:  # noqa: BLE001
                self.log(f"vrPropertyWidget failed: {e}")
        if hasattr(self, "ui") and "volume" in n:
            self.ui.inputSelector.setCurrentNode(n["volume"])
        try:
            slicer.util.setSliceViewerLayers(background=n.get("volume"), fit=True)
        except Exception as e:  # noqa: BLE001
            self.log(f"setSliceViewerLayers failed: {e}")

    # --- dialogs ------------------------------------------------------------------------------
    def setupDialogs(self):
        box, layout = self.section("Dialogs and messages: QMessageBox, QInputDialog, ctkMessageBox, QFileDialog, QDialog, slicer.util.*")
        S = "Dialogs"
        flow = ctk.ctkFlowLayout()
        layout.addLayout(flow)

        def button(text, callback):
            b = qt.QPushButton(text)
            def run():
                try:
                    result = callback()
                    self.log(f"{text} -> {result!r}")
                except Exception as e:  # noqa: BLE001
                    self.log(f"{text} raised {type(e).__name__}: {e}")
            b.clicked.connect(run)
            flow.addWidget(b)

        button("QMessageBox.information", lambda: qt.QMessageBox.information(None, "Title", "QMessageBox.information: the browser's alert()"))
        button("QMessageBox.question", lambda: "Yes" if qt.QMessageBox.question(None, "Question", "QMessageBox.question: confirm()?") == qt.QMessageBox.Yes else "No")
        button("QInputDialog.getText", lambda: qt.QInputDialog.getText(None, "Input", "QInputDialog.getText: prompt()", qt.QLineEdit.Normal if hasattr(qt.QLineEdit, "Normal") else 0, "default"))
        button("ctkMessageBox (Ok/Cancel)", lambda: self._ctkMessageBox())
        button("slicer.util.messageBox", lambda: slicer.util.messageBox("slicer.util.messageBox"))
        button("slicer.util.confirmYesNoDisplay", lambda: slicer.util.confirmYesNoDisplay("slicer.util.confirmYesNoDisplay?"))
        button("slicer.util.confirmOkCancelDisplay", lambda: slicer.util.confirmOkCancelDisplay("slicer.util.confirmOkCancelDisplay?"))
        button("slicer.util.delayDisplay", lambda: slicer.util.delayDisplay("slicer.util.delayDisplay (500 ms)", 500))
        button("slicer.util.infoDisplay", lambda: slicer.util.infoDisplay("slicer.util.infoDisplay"))
        button("slicer.util.warningDisplay", lambda: slicer.util.warningDisplay("slicer.util.warningDisplay"))
        button("slicer.util.errorDisplay", lambda: slicer.util.errorDisplay("slicer.util.errorDisplay"))
        button("QFileDialog.getOpenFileName", lambda: qt.QFileDialog.getOpenFileName(None, "Open", "", "Images (*.nrrd)"))
        button("QDialog().exec_()", lambda: self._dialog())
        button("qt.QApplication.setOverrideCursor(Wait) 1 s", lambda: self._waitCursor())

    def _ctkMessageBox(self):
        box = ctk.ctkMessageBox()
        box.setWindowTitle("ctkMessageBox")
        box.text = "A ctkMessageBox with Ok and Cancel"
        box.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
        box.setDontShowAgainVisible(True)
        result = box.exec_()
        return "Ok" if result == qt.QMessageBox.Ok else "Cancel"

    def _dialog(self):
        d = qt.QDialog()
        d.setWindowTitle("A QDialog")
        l = qt.QVBoxLayout(d)
        l.addWidget(qt.QLabel("QDialog.exec_() cannot block in the browser"))
        d.accepted.connect(lambda: self.log("QDialog accepted"))
        d.rejected.connect(lambda: self.log("QDialog rejected"))
        return d.exec_()

    def _waitCursor(self):
        qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
        qt.QTimer.singleShot(1000, lambda: (qt.QApplication.restoreOverrideCursor(), self.log("cursor restored")))
        return qt.QApplication.overrideCursor().shape()

    # --- application services -----------------------------------------------------------------
    def setupApplication(self):
        box, layout = self.section("Application: slicer.app, layout manager, settings, status bar, modules", form=True)
        S = "Application"

        def layoutCombo():
            c = qt.QComboBox()
            layouts = [("Four-up", slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView),
                       ("Conventional", slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView),
                       ("One-up red slice", slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView),
                       ("One-up 3D", slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView),
                       ("3D only + table", slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpTableView)]
            for name, id in layouts:
                c.addItem(name, id)

            def change(index):
                id = layouts[index][1]
                slicer.app.layoutManager().setLayout(id)
                self.log(f"layoutManager().setLayout({id}) -> layout is now {slicer.app.layoutManager().layout}")
            c.currentIndexChanged.connect(lambda i: self.safely("setLayout", lambda: change(i))())
            return c
        layout.addRow("Layout", self.guarded(S, "layoutManager", layoutCombo))

        def settings():
            row = qt.QHBoxLayout()
            edit = qt.QLineEdit("hello")
            save = qt.QPushButton("QSettings.setValue")
            load = qt.QPushButton("QSettings.value")

            def doSave():
                s = qt.QSettings()
                s.setValue("WidgetGallery/text", edit.text)
                self.log(f"QSettings saved WidgetGallery/text={edit.text!r}")

            def doLoad():
                self.log(f"QSettings.value -> {qt.QSettings().value('WidgetGallery/text', 'unset')!r}")
            save.clicked.connect(doSave)
            load.clicked.connect(doLoad)
            row.addWidget(edit)
            row.addWidget(save)
            row.addWidget(load)
            return row
        layout.addRow("QSettings", self.guarded(S, "QSettings", settings))

        def status():
            b = qt.QPushButton("slicer.util.showStatusMessage(...)")
            b.clicked.connect(self.safely("showStatusMessage", lambda: slicer.util.showStatusMessage("Hello from the Widget Gallery", 3000)))
            return b
        layout.addRow("Status bar", self.guarded(S, "showStatusMessage", status))

        def info():
            lines = []
            try:
                lines.append(f"slicer.app.applicationName = {slicer.app.applicationName}")
                lines.append(f"slicer.app.applicationVersion = {slicer.app.applicationVersion}")
                lines.append(f"slicer.app.majorVersion.minorVersion = {slicer.app.majorVersion}.{slicer.app.minorVersion}")
                lines.append(f"qt.QT_VERSION_STR = {qt.QT_VERSION_STR}")
                lines.append(f"slicer.util.mainWindow() = {type(slicer.util.mainWindow()).__name__}")
                lines.append(f"modules loaded = {len(slicer.app.moduleManager().loadedModulesNames())}")
                lines.append(f"slicer.app.temporaryPath = {slicer.app.temporaryPath}")
                lines.append(f"slicer.app.slicerHome = {slicer.app.slicerHome}")
            except Exception as e:  # noqa: BLE001
                lines.append(f"(reading application info failed: {e})")
            label = qt.QLabel("\n".join(lines))
            label.setWordWrap(True)
            return label
        layout.addRow("slicer.app", self.guarded(S, "slicer.app", info))

        def python():
            row = qt.QHBoxLayout()
            b = qt.QPushButton("slicer.util.selectModule('Data')")
            b.clicked.connect(self.safely("slicer.util.selectModule('Data')", lambda: slicer.util.selectModule("Data")))
            row.addWidget(b)
            c = qt.QPushButton("slicer.util.pythonShell()")
            c.clicked.connect(self.safely("slicer.util.pythonShell()", lambda: slicer.util.pythonShell()))
            row.addWidget(c)
            d = qt.QPushButton("slicer.app.processEvents()")
            d.clicked.connect(self.safely("slicer.app.processEvents()", lambda: slicer.app.processEvents()))
            row.addWidget(d)
            return row
        layout.addRow("Navigation", self.guarded(S, "selectModule", python))

    # --- failures -----------------------------------------------------------------------------
    def setupFailures(self):
        box, layout = self.section(f"Widgets that failed to build here: {len(self.failures)}", collapsed=not self.failures)
        if not self.failures:
            layout.addWidget(qt.QLabel("Every widget of this gallery was built without an exception."))
            return
        table = qt.QTableWidget()
        table.setRowCount(len(self.failures))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Section", "Widget", "Error"])
        for i, (section, name, error) in enumerate(self.failures):
            for c, v in enumerate((section, name, error)):
                table.setItem(i, c, qt.QTableWidgetItem(v))
        layout.addWidget(table)

    def cleanup(self):
        if self._timer is not None:
            self._timer.stop()


class WidgetGalleryLogic(ScriptedLoadableModuleLogic):
    def createDemoNodes(self):
        """A small scene for the MRML widgets: a volume, a model, markups, a transform, a segmentation."""
        import numpy as np

        scene = slicer.mrmlScene
        nodes = {}
        existing = scene.GetFirstNodeByName("GalleryVolume")
        if existing:
            nodes["volume"] = existing
        else:
            size = 48
            z, y, x = np.mgrid[0:size, 0:size, 0:size]
            r = np.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2 + (z - size / 2) ** 2)
            array = (200 * np.exp(-(r / 14.0) ** 2) + 40 * (r < 20)).astype(np.int16)
            volume = slicer.util.addVolumeFromArray(array, ijkToRAS=np.diag([2.0, 2.0, 2.0, 1.0]), name="GalleryVolume")
            nodes["volume"] = volume
        model = scene.GetFirstNodeByName("GallerySphere")
        if not model:
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(30)
            sphere.SetThetaResolution(32)
            sphere.SetPhiResolution(32)
            sphere.Update()
            model = scene.AddNewNodeByClass("vtkMRMLModelNode", "GallerySphere")
            model.SetAndObservePolyData(sphere.GetOutput())
            model.CreateDefaultDisplayNodes()
        nodes["model"] = model
        markups = scene.GetFirstNodeByName("GalleryPoints")
        if not markups:
            markups = scene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "GalleryPoints")
            for p in ((10, 0, 0), (0, 20, 0), (0, 0, 30)):
                markups.AddControlPoint(vtk.vtkVector3d(*p))
        nodes["markups"] = markups
        transform = scene.GetFirstNodeByName("GalleryTransform")
        if not transform:
            transform = scene.AddNewNodeByClass("vtkMRMLLinearTransformNode", "GalleryTransform")
            model.SetAndObserveTransformNodeID(transform.GetID())
        nodes["transform"] = transform
        segmentation = scene.GetFirstNodeByName("GallerySegmentation")
        if not segmentation:
            segmentation = scene.AddNewNodeByClass("vtkMRMLSegmentationNode", "GallerySegmentation")
            segmentation.CreateDefaultDisplayNodes()
            segmentation.SetReferenceImageGeometryParameterFromVolumeNode(nodes["volume"])
            for name, radius, color in (("Core", 12, (0.9, 0.3, 0.2)), ("Shell", 20, (0.2, 0.6, 0.9))):
                s = vtk.vtkSphereSource()
                s.SetRadius(radius)
                s.SetCenter(48, 48, 48)
                s.Update()
                segmentation.AddSegmentFromClosedSurfaceRepresentation(s.GetOutput(), name, color)
        nodes["segmentation"] = segmentation
        try:
            vrLogic = slicer.modules.volumerendering.logic()
            display = vrLogic.GetFirstVolumeRenderingDisplayNode(nodes["volume"])
            if not display:
                display = vrLogic.CreateDefaultVolumeRenderingNodes(nodes["volume"])
            if display and display.GetVolumePropertyNode():
                nodes["volumeProperty"] = display.GetVolumePropertyNode()
        except Exception:  # noqa: BLE001
            logger.debug("No volume rendering logic", exc_info=True)
        return nodes


class WidgetGalleryTest(ScriptedLoadableModuleTest):
    def runTest(self):
        self.setUp()
        self.test_gallery()

    def test_gallery(self):
        self.delayDisplay("Building the gallery's demo nodes")
        widget = slicer.modules.WidgetGalleryWidget
        widget.createDemoNodes()
        self.assertIn("volume", widget.demoNodes)
        rows = coverage()
        missing = [name for _, name, status in rows if status == "missing"]
        self.delayDisplay(f"Coverage: {len(rows) - len(missing)} of {len(rows)} classes present; {len(widget.failures)} widgets failed")
        self.assertEqual(widget.failures, [], f"widgets failed to build: {widget.failures}")
        self.delayDisplay("Test passed")
