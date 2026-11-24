@echo off
title StockFlow PC App
setlocal enabledelayedexpansion

if exist "%~dp0dist\StockFlow\StockFlow.exe" (
    echo Launching packaged StockFlow desktop app...
    start "" "%~dp0dist\StockFlow\StockFlow.exe"
) else (
    echo Packaged executable not found, launching from source...
    python "%~dp0desktop_app.py"
)
