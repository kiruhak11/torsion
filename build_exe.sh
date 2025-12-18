#!/usr/bin/env bash
# Сборка дистрибутива лаунчера (Mac/Linux) через PyInstaller
# Требования: python3, pip install pyinstaller

set -e
cd "$(dirname "$0")"

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --windowed \
  --name torsion_lab_launcher \
  launcher.py \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --add-data "torsion_lab.db:." \
  --add-data "torsion_animation.gif:." \
  --hidden-import "PyQt5.sip"

echo "Готово. Бинарник лежит в dist/torsion_lab_launcher"

