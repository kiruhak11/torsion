@echo off
REM Сборка Windows-EXE для лаунчера (PyInstaller)
REM Требования: Python 3.10+, установленный pyinstaller (pip install pyinstaller)

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name torsion_lab_launcher ^
  launcher.py ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "torsion_lab.db;." ^
  --add-data "torsion_animation.gif;." ^
  --hidden-import "PyQt5.sip"

echo.
echo Готово. EXE лежит в папке dist\torsion_lab_launcher.exe

