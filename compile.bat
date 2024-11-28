@echo off

python -m nuitka ValQ.py --enable-plugin=tk-inter --standalone --onefile

if %errorlevel% neq 0 (
    echo Build failed.
    exit /b %errorlevel%
)

echo Build completed.

if not exist dist (
    mkdir dist
)

copy ValQ.exe dist\

if %errorlevel% equ 0 (
    del ValQ.exe
)

cd dist
powershell Compress-Archive -Path ValQ.exe -DestinationPath ValQ_and_bypass.zip


echo zipped successfully.
