@echo off
REM Script para ejecutar tests del Parking Management System

echo ========================================
echo PARKING SYSTEM - TEST RUNNER
echo ========================================
echo.

if "%1"=="" goto help
if "%1"=="all" goto all
if "%1"=="security" goto security
if "%1"=="unit" goto unit
if "%1"=="integration" goto integration
if "%1"=="coverage" goto coverage
if "%1"=="critical" goto critical
goto help

:all
echo Ejecutando TODOS los tests...
pytest -v
goto end

:security
echo Ejecutando tests de SEGURIDAD...
pytest -v -m security
goto end

:unit
echo Ejecutando tests UNITARIOS...
pytest -v -m unit
goto end

:integration
echo Ejecutando tests de INTEGRACION...
pytest -v -m integration
goto end

:coverage
echo Ejecutando tests con COVERAGE...
pytest --cov=src --cov-report=html --cov-report=term-missing
start htmlcov\index.html
goto end

:critical
echo Ejecutando solo tests CRITICOS...
pytest -v -m critical
goto end

:help
echo Uso: run_tests.bat [opcion]
echo.
echo Opciones:
echo   all          - Todos los tests
echo   security     - Solo tests de seguridad
echo   unit         - Solo tests unitarios
echo   integration  - Solo tests de integracion
echo   coverage     - Tests con reporte de cobertura
echo   critical     - Solo tests criticos
echo.
goto end

:end
