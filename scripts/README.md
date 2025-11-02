# Scripts - Sistema de Gestión de Parqueadero

Este directorio contiene los puntos de entrada y scripts de conveniencia para ejecutar el sistema.

## 📁 Archivos

### Aplicaciones Principales

- **`main_modular.py`** - Aplicación principal sin autenticación (modo desarrollo)
- **`main_with_auth.py`** - Aplicación principal con autenticación (modo producción)

### Scripts de Conveniencia

- **`run.py`** - Script rápido para ejecutar sin autenticación
- **`run_with_auth.py`** - Script rápido para ejecutar con autenticación

---

## 🚀 Formas de Ejecutar el Sistema

### 1. Usando `python -m src` (Recomendado)

```bash
# Sin autenticación (modo desarrollo)
python -m src

# Con autenticación (modo producción)
python -m src --auth

# Mostrar ayuda
python -m src --help

# Mostrar versión
python -m src --version
```

### 2. Usando scripts de conveniencia

```bash
# Sin autenticación
python scripts/run.py

# Con autenticación
python scripts/run_with_auth.py

# Mostrar ayuda
python scripts/run_with_auth.py --help
```

### 3. Ejecutando directamente los main

```bash
# Sin autenticación
python scripts/main_modular.py

# Con autenticación
python scripts/main_with_auth.py
```

---

## 🔐 Credenciales de Prueba

Para el modo con autenticación:
- **Usuario:** `splaza`
- **Contraseña:** `splaza123*`

---

## 📝 Diferencias entre Modos

### Modo Sin Autenticación (`run.py` o `python -m src`)
- ✅ Acceso directo al sistema
- ✅ Ideal para desarrollo y pruebas
- ✅ Sin restricciones de usuario
- ⚠️ No usar en producción

### Modo Con Autenticación (`run_with_auth.py` o `python -m src --auth`)
- ✅ Ventana de login obligatoria
- ✅ Control de acceso por usuario
- ✅ Registro de sesiones
- ✅ Recomendado para producción

---

## 🛠️ Troubleshooting

### Error: "No module named 'src'"
```bash
# Asegurarse de ejecutar desde el directorio raíz del proyecto
cd /ruta/a/parking_system
python -m src
```

### Error: "No se pudo conectar a la base de datos"
1. Verificar que MySQL esté corriendo
2. Verificar credenciales en archivo `.env`
3. Ver documentación en `db/README.md`

### Error: "ModuleNotFoundError: No module named 'PyQt5'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

---

## 📚 Documentación Adicional

- **Configuración completa:** Ver `docs/CLAUDE.md`
- **Base de datos:** Ver `db/README.md`
- **Variables de entorno:** Ver `.env.example` en raíz

---

**Última actualización:** 2025-10-26
**Versión:** 2.0.3
