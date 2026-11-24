@echo off
echo ========================================================
echo Building StockFlow PC Desktop Application
echo ========================================================

echo [1/3] Building frontend production bundle...
cd frontend
call npm run build
if %ERRORLEVEL% neq 0 (
    echo Frontend build failed!
    cd ..
    exit /b %ERRORLEVEL%
)
cd ..

echo [2/3] Compiling standalone Windows executable with PyInstaller...
pyinstaller StockFlow.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo PyInstaller packaging failed!
    exit /b %ERRORLEVEL%
)

echo [3/3] Syncing active database...
copy /Y stockflow.db dist\StockFlow\stockflow.db

echo ========================================================
echo StockFlow Desktop App built successfully!
echo Executable located at: dist\StockFlow\StockFlow.exe
echo ========================================================
