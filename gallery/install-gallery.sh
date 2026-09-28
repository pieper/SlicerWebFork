#!/usr/bin/env bash
# Put the gallery pages and their assets next to a built site, so that the server that serves the
# application serves them too:
#   /gallery.html        the Widget Gallery module inside the application
#   /ctk-gallery.html    the standalone CTK gallery: Qt screenshots beside the browser replicas
# Usage: gallery/install-gallery.sh <site directory>     (e.g. web/dist/app, after `npm run build`)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
target="${1:?site directory (web/dist/app)}"
widgets="$here/../web/dist/widgets"
[ -f "$widgets/slicerweb-widgets.js" ] || { echo "Build the widgets bundle first: cd web && npm run build:widgets"; exit 1; }
mkdir -p "$target/gallery/qt-shots" "$target/widgets"
cp "$here/gallery.html" "$here/ctk-gallery.html" "$target/"
cp "$here/ctk-gallery.py" "$here/qt-theme.css" "$target/gallery/"
cp "$here/qt-shots/"*.png "$here/qt-shots/theme.json" "$target/gallery/qt-shots/"
cp "$widgets/slicerweb-widgets.js" "$widgets/slicerweb.css" "$target/widgets/"
echo "gallery installed into $target"
