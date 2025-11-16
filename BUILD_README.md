# 🚀 Guía de Compilación con PyInstaller

## Sistema de Gestión de Parqueadero - Ssalud Plaza Claro

---

## 📋 Tabla de Contenidos

1. [Preparación del Entorno](#1-preparación-del-entorno)
2. [Limpieza Pre-Compilación](#2-limpieza-pre-compilación)
3. [Compilación Automática](#3-compilación-automática)
4. [Compilación Manual](#4-compilación-manual)
5. [Verificación y Pruebas](#5-verificación-y-pruebas)
6. [Distribución](#6-distribución)
7. [Resolución de Problemas](#7-resolución-de-problemas)

---

## 1. Preparación del Entorno

### Requisitos Previos

- **Python 3.8 o superior** (Recomendado: 3.10 o 3.11)
- **MySQL Server** instalado y corriendo
- **Git** (para control de versiones)

### Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias críticas
pip install PyQt5==5.15.11
pip install mysql-connector-python==8.0.33

# Instalar PyInstaller
pip install pyinstaller

# Instalar dependencias adicionales
pip install -r requirements.txt
```

### Verificar Instalación

```bash
# Verificar PyQt5
python -c "import PyQt5; print('PyQt5 OK')"

# Verificar MySQL Connector
python -c "import mysql.connector; print('MySQL Connector OK')"

# Verificar PyInstaller
pyinstaller --version
```

---

## 2. Limpieza Pre-Compilación

### Archivos Eliminados Automáticamente

Durante la auditoría, se eliminaron los siguientes archivos redundantes:

```
✓ scripts/run.py (redundante)
✓ scripts/run_with_auth.py (redundante)
✓ scripts/verify_installation.py (obsoleto)
✓ scripts/verify_simple.py (obsoleto)
✓ requirements-dev.txt (innecesario para producción)
✓ .claude/ (configuración de desarrollo)
```

### Archivos Archivados

Documentación movida a `docs/archive/`:

```
✓ docs/CONTRIBUTING.md
✓ docs/SECURITY.md
✓ docs/features/*.md
```

### Estructura Final Limpia

```
parking_system/
├── main.py                     ← ÚNICO punto de entrada
├── parking_system.spec         ← Configuración PyInstaller
├── build_exe.bat               ← Script automatizado de compilación
├── BUILD_README.md             ← Esta guía
├── .env                        ← Configuración de BD
├── requirements.txt            ← Dependencias
├── db/                         ← Esquemas SQL
│   ├── schema/
│   └── migrations/
├── src/                        ← Código fuente
│   ├── auth/
│   ├── config/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── ui/
│   └── utils/
│       └── resource_path.py    ← Utilidad para PyInstaller ¡NUEVA!
├── scripts/                    ← Scripts auxiliares
│   ├── main_modular.py
│   └── main_with_auth.py
└── docs/                       ← Documentación
```

---

## 3. Compilación Automática (RECOMENDADO)

### Opción A: Script Batch (Windows)

```batch
# Doble clic en:
build_exe.bat

# O desde la terminal:
.\build_exe.bat
```

Este script automáticamente:
1. ✅ Verifica PyInstaller
2. ✅ Limpia builds anteriores
3. ✅ Verifica dependencias
4. ✅ Compila con PyInstaller
5. ✅ Valida el ejecutable generado

### Opción B: Comando Único

```bash
pyinstaller parking_system.spec --clean --noconfirm
```

---

## 4. Compilación Manual (Paso a Paso)

### Paso 1: Limpiar Builds Anteriores

```bash
# Windows
rmdir /s /q build dist
del /q *.spec

# Linux/Mac
rm -rf build dist
rm -f *.spec
```

### Paso 2: Generar Archivo .spec (Opcional)

Si quieres regenerar el .spec desde cero:

```bash
pyi-makespec --name=SistemaParqueadero ^
             --onedir ^
             --windowed ^
             --add-data "src;src" ^
             --add-data "db/schema;db/schema" ^
             --add-data ".env;." ^
             --hidden-import=mysql.connector ^
             --hidden-import=PyQt5.QtCore ^
             --hidden-import=PyQt5.QtGui ^
             --hidden-import=PyQt5.QtWidgets ^
             main.py
```

Luego edita `SistemaParqueadero.spec` manualmente.

### Paso 3: Compilar

```bash
pyinstaller parking_system.spec --clean
```

Banderas útiles:
- `--clean`: Limpia caché antes de compilar
- `--noconfirm`: No pide confirmación para sobrescribir
- `--debug all`: Modo debug completo (solo para troubleshooting)

---

## 5. Verificación y Pruebas

### Verificar Estructura Generada

```bash
cd dist/SistemaParqueadero/
dir  # Windows
ls   # Linux/Mac
```

Debe contener:
```
SistemaParqueadero/
├── SistemaParqueadero.exe      ← El ejecutable
├── _internal/                  ← Dependencias (PyQt5, MySQL, etc.)
├── src/                        ← Código fuente empaquetado
├── db/                         ← Esquemas SQL
└── .env                        ← Configuración
```

### Probar el Ejecutable

#### Prueba 1: Ejecución Directa

```bash
cd dist\SistemaParqueadero
SistemaParqueadero.exe
```

**Resultado esperado:**
- ✅ Ventana de login futurista aparece
- ✅ Conexión a BD exitosa
- ✅ No errores en consola

#### Prueba 2: Verificar Logs

Si falla, revisar:
```
dist/SistemaParqueadero/error_log.txt
```

#### Prueba 3: Prueba Completa

1. Ingresar credenciales: `splaza` / `splaza123*`
2. Verificar que carguen todas las pestañas
3. Crear un funcionario de prueba
4. Crear un vehículo de prueba
5. Hacer una asignación
6. Generar un reporte

---

## 6. Distribución

### Opción A: Carpeta Portable (SIN INSTALADOR)

1. Comprimir `dist/SistemaParqueadero/` en ZIP
2. Distribuir el ZIP
3. Usuario descomprime y ejecuta `SistemaParqueadero.exe`

**Ventajas:**
- No requiere instalación
- No requiere permisos de administrador
- Fácil de actualizar

**Desventajas:**
- Usuario debe tener MySQL instalado y configurado

### Opción B: Instalador con NSIS (Recomendado para Producción)

#### Instalar NSIS

1. Descargar desde: https://nsis.sourceforge.io/
2. Instalar NSIS

#### Crear Script NSIS

Crear archivo `installer.nsi`:

```nsis
!define APP_NAME "Sistema de Parqueadero"
!define APP_VERSION "2.1.0"
!define PUBLISHER "Ssalud Plaza Claro"
!define EXE_NAME "SistemaParqueadero.exe"

OutFile "SistemaParqueadero_Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Section "Instalar"
    SetOutPath "$INSTDIR"
    File /r "dist\SistemaParqueadero\*.*"

    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
SectionEnd
```

#### Compilar Instalador

```bash
makensis installer.nsi
```

### Opción C: Instalador con Inno Setup

Similar a NSIS, pero con interfaz gráfica para crear el script.

---

## 7. Resolución de Problemas

### Problema 1: "Segmentation Fault" al Ejecutar

**Causa:** Versión incorrecta de `mysql-connector-python`

**Solución:**
```bash
pip uninstall mysql-connector-python
pip install mysql-connector-python==8.0.33
```

Luego recompilar.

### Problema 2: "ModuleNotFoundError: No module named 'src'"

**Causa:** Rutas no configuradas correctamente

**Solución:**
Verificar en `parking_system.spec`:

```python
datas=[
    ('src', 'src'),  # ← Debe estar presente
    # ...
],
```

Recompilar con `--clean`:
```bash
pyinstaller parking_system.spec --clean
```

### Problema 3: "FileNotFoundError: .env not found"

**Causa:** Archivo `.env` no incluido en el empaquetado

**Solución 1:** Agregar a `parking_system.spec`:
```python
datas=[
    ('.env', '.'),  # ← Agregar esta línea
],
```

**Solución 2:** Crear `.env` manualmente en `dist/SistemaParqueadero/`

### Problema 4: Ejecutable muy grande (>500 MB)

**Causas comunes:**
- Inclusión innecesaria de numpy/pandas/matplotlib

**Solución:**
Editar `parking_system.spec`, sección `excludes`:

```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tkinter',
    'PIL',
    'pytest',
],
```

### Problema 5: Aplicación se cierra inmediatamente

**Diagnóstico:**
1. Ejecutar desde terminal para ver errores:
   ```bash
   cd dist\SistemaParqueadero
   .\SistemaParqueadero.exe
   ```

2. Revisar `error_log.txt`

3. Editar `parking_system.spec` y cambiar:
   ```python
   console=True,  # ← Cambiar a True para ver errores
   ```

4. Recompilar y ejecutar de nuevo

### Problema 6: Error de conexión a MySQL

**Solución:**
1. Verificar que MySQL esté corriendo
2. Editar `.env` en `dist/SistemaParqueadero/`
3. Verificar credenciales correctas

---

## 📚 Recursos Adicionales

### Documentación Oficial

- **PyInstaller:** https://pyinstaller.org/
- **PyQt5:** https://www.riverbankcomputing.com/software/pyqt/
- **MySQL Connector/Python:** https://dev.mysql.com/doc/connector-python/en/

### Archivos de Ayuda en Este Proyecto

- `docs/README.md` - Documentación general del sistema
- `docs/INSTALLATION.md` - Guía de instalación para desarrollo
- `docs/OPTIMIZATION_REPORT.md` - Informe de optimizaciones realizadas

### Comandos Útiles de PyInstaller

```bash
# Ver opciones disponibles
pyinstaller --help

# Generar .spec sin compilar
pyi-makespec main.py

# Compilar con debug
pyinstaller parking_system.spec --debug all

# Limpiar todo (incluso caché)
pyinstaller parking_system.spec --clean --noconfirm

# Modo verbose (ver todos los imports)
pyinstaller parking_system.spec --log-level DEBUG
```

---

## ✅ Checklist de Compilación

Antes de distribuir, verifica:

- [ ] Todas las dependencias instaladas correctamente
- [ ] `.env` configurado (sin credenciales sensibles si es público)
- [ ] Base de datos creada con `db/schema/parking_database_schema.sql`
- [ ] Ejecutable probado en máquina limpia (sin Python instalado)
- [ ] Login funciona correctamente
- [ ] Todas las pestañas cargan sin errores
- [ ] CRUD de funcionarios funciona
- [ ] CRUD de vehículos funciona
- [ ] Asignaciones de parqueaderos funcionan
- [ ] Reportes se generan correctamente
- [ ] `error_log.txt` no contiene errores críticos
- [ ] Documentación incluida (`README.md`, etc.)

---

## 🎯 Resumen Rápido

### Para Compilar:

```bash
# Opción fácil (Windows)
build_exe.bat

# Opción manual
pyinstaller parking_system.spec --clean
```

### Para Distribuir:

```bash
# Comprimir carpeta
cd dist
tar -czf SistemaParqueadero.zip SistemaParqueadero/
```

### Para Ejecutar:

```bash
cd dist/SistemaParqueadero
./SistemaParqueadero.exe
```

---

**¡Éxito con la compilación! 🎉**

Si encuentras problemas, revisa la sección de [Resolución de Problemas](#7-resolución-de-problemas) o crea un issue en el repositorio.
