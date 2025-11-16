@echo off
REM ============================================================
REM SCRIPT DE COMPILACIÓN AUTOMÁTICA CON PYINSTALLER
REM Sistema de Gestión de Parqueadero
REM ============================================================

echo.
echo ============================================================
echo  SISTEMA DE GESTION DE PARQUEADERO
echo  Compilador Automatico con PyInstaller
echo ============================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo [ERROR] No se encontro main.py
    echo Por favor, ejecuta este script desde la raiz del proyecto.
    pause
    exit /b 1
)

REM Verificar que PyInstaller está instalado
echo [1/6] Verificando PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [WARN] PyInstaller no esta instalado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
)
echo      OK - PyInstaller encontrado
echo.

REM Limpiar builds anteriores
echo [2/6] Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo      OK - Directorios limpios
echo.

REM Verificar dependencias críticas
echo [3/6] Verificando dependencias criticas...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo [ERROR] PyQt5 no esta instalado
    echo Instala con: pip install PyQt5
    pause
    exit /b 1
)

python -c "import mysql.connector" 2>nul
if errorlevel 1 (
    echo [ERROR] mysql-connector-python no esta instalado
    echo Instala con: pip install mysql-connector-python==8.0.33
    pause
    exit /b 1
)
echo      OK - Dependencias verificadas
echo.

REM Ejecutar PyInstaller
echo [4/6] Compilando con PyInstaller...
echo      Esto puede tomar varios minutos...
pyinstaller parking_system.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la compilacion
    echo Revisa los errores arriba para mas detalles.
    pause
    exit /b 1
)
echo      OK - Compilacion completada
echo.

REM Verificar que se generó el ejecutable
echo [5/6] Verificando ejecutable generado...
if not exist "dist\SistemaParqueadero\SistemaParqueadero.exe" (
    echo [ERROR] No se genero el ejecutable esperado
    pause
    exit /b 1
)
echo      OK - Ejecutable encontrado
echo.

REM Mostrar tamaño y ubicación
echo [6/6] Detalles del ejecutable:
for %%F in ("dist\SistemaParqueadero\SistemaParqueadero.exe") do (
    echo      Ruta: %%~fF
    echo      Tamaño: %%~zF bytes
)
echo.

echo ============================================================
echo  COMPILACION EXITOSA
echo ============================================================
echo.
echo El ejecutable esta en: dist\SistemaParqueadero\
echo.
echo IMPORTANTE:
echo - Debes distribuir TODA la carpeta dist\SistemaParqueadero\
echo - NO distribuyas solo el archivo .exe
echo.
echo Para probar el ejecutable:
echo   cd dist\SistemaParqueadero
echo   SistemaParqueadero.exe
echo.
echo ============================================================
echo.

pause
