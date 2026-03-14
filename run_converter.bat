@echo off
echo Installing requirements and starting the Image Converter...
python -m pip install Pillow --quiet
python converter.py
pause
