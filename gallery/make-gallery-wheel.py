#!/usr/bin/env python3
"""Package the Widget Gallery scripted module as a SlicerWeb extension wheel and list it in the
extension index, so that `?extensions=WidgetGallery` (or the Extensions Manager) installs it.

    python3 gallery/make-gallery-wheel.py

Reads the runtime wheels from $SLICERWEB_WHEELS (for the Slicer version directory) and writes the
wheel and the index entry to $SLICERWEB_EXTENSIONS; both default to the directories the web
application serves (see web/vite.assets.ts). The layout follows scripts/stages/80-extensions.sh:
the module goes to slicer_home/lib/Slicer-<version>/qt-scripted-modules/, the directory the
application's own scripted modules live in, which is how the module manager finds it.
"""
import glob
import json
import os
import sys
import zipfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(here), "scripts"))
from make_wheels import Wheel  # noqa: E402

wheels = os.environ.get("SLICERWEB_WHEELS", "D:/SlicerWeb-build/dist/wheels")
extensions = os.environ.get("SLICERWEB_EXTENSIONS", "D:/SlicerWeb-build/dist/extensions")
version = "0.1.0"

core = glob.glob(os.path.join(wheels, "slicer_core-*.whl"))
if not core:
    sys.exit(f"No slicer_core wheel in {wheels} (set SLICERWEB_WHEELS)")
libdir = sorted({n.split("/")[2] for n in zipfile.ZipFile(core[0]).namelist() if n.startswith("slicer_home/lib/Slicer-")})[0]

wheel = Wheel("slicer-ext-widgetgallery", version, pure=True,
              summary="Widget Gallery: every Qt, CTK and MRML widget of the browser's qt/ctk layer on one panel")
count = wheel.add_tree(os.path.join(here, "WidgetGallery"), f"slicer_home/lib/{libdir}/qt-scripted-modules",
                       exclude=lambda rel: "__pycache__" in rel or rel.endswith(".pyc"))
path = wheel.write(extensions)
print(f"{count} files -> {path}")

index_path = os.path.join(extensions, "index.json")
index = json.load(open(index_path)) if os.path.exists(index_path) else {"extensions": []}
entry = {
    "name": "WidgetGallery",
    "homepage": "https://github.com/pieper/SlicerWebFork/tree/qt-ctk-gallery/gallery",
    "category": "Developer Tools",
    "contributors": ["Steve Pieper (Isomics)"],
    "description": "Every Qt, CTK and MRML widget the browser's qt/ctk compatibility layer provides, on one panel, with a coverage report against the toolkits' class lists.",
    "depends": [],
    "screenshots": [],
    "icon": "",
    "revision": version,
    "modules": ["WidgetGallery"],
    "version": version,
    "wheel": os.path.basename(path),
}
index["extensions"] = [e for e in index["extensions"] if e["name"] != "WidgetGallery"] + [entry]
json.dump(index, open(index_path, "w"), indent=1)
print(f"{index_path}: {[e['name'] for e in index['extensions']]}")
