# 🏥 Reporte de Salud del Código - CodeGuardian

**Fecha:** 2025-10-13 18:11:47
**Python Version:** 3.13.2
**Proyecto:** Sistema de Gestión de Parqueadero v1.1

## 📊 Métricas Generales

- **Archivos Python analizados:** 31
- **Líneas totales de código:** 11,847
- **Funciones/Métodos:** 278
- **Clases:** 33

## ✅ Compatibilidad Python 3.13.2

- [✓] Versión correcta detectada: 3.13.2
- [✓] Todos los archivos usan `# -*- coding: utf-8 -*-`
- [✓] Sin sintaxis deprecated detectada

## 🛠️ Herramientas de Análisis

- **ruff:** ✅ Instalado
- **flake8:** ✅ Instalado
- **black:** ✅ Instalado
- **isort:** ✅ Instalado
- **pylint:** ✅ Instalado

## 📝 Documentación

- **Funciones sin docstring:** 27 de 278 (9.7%)
- **Clases sin docstring:** 0 de 33 (0.0%)

## 📏 Funciones Largas (>100 líneas)

**Total encontradas:** 22

1. `setup_ui` en `src\ui\asignaciones_tab.py` - **520 líneas**
2. `setup_ui` en `src\ui\asignaciones_tab.py` - **333 líneas**
3. `setup_ui` en `src\ui\reportes_tab.py` - **265 líneas**
4. `setup_ui` en `src\ui\funcionarios_tab.py` - **255 líneas**
5. `apply_styles` en `src\auth\login_window.py` - **172 líneas**
6. `obtener_todos` en `src\models\parqueadero.py` - **168 líneas**
7. `cargar_funcionarios` en `src\ui\funcionarios_tab.py` - **148 líneas**
8. `cargar_vehiculos` en `src\ui\vehiculos_tab.py` - **146 líneas**
9. `asignar_vehiculo` en `src\models\parqueadero.py` - **145 líneas**
10. `mostrar_asignaciones` en `src\ui\asignaciones_tab.py` - **142 líneas**

**⚠️ Recomendación:** Refactorizar funciones largas en funciones más pequeñas y manejables.


## 🎯 Archivos Prioritarios para Revisión

1. `src\ui\asignaciones_tab.py` - 1807 líneas, 26 funciones
2. `src\ui\reportes_tab.py` - 1596 líneas, 28 funciones
3. `src\ui\funcionarios_tab.py` - 1229 líneas, 24 funciones
4. `src\ui\modal_detalle_parqueadero.py` - 817 líneas, 11 funciones
5. `src\ui\modales_vehiculos.py` - 631 líneas, 16 funciones


## 💡 Recomendaciones

1. **Mejorar Documentación:** Agregar docstrings a las 27 funciones sin documentar
2. **Refactorizar Funciones Largas:** Dividir las 22 funciones largas identificadas
3. **Agregar Type Hints:** Implementar anotaciones de tipos para mejor mantenibilidad
4. **Instalar Herramientas:** Configurar ruff, black e isort para formateo automático
5. **Tests Unitarios:** Implementar suite de tests (pendiente desde v1.0)

## 🏆 Puntuación General

**Salud del Código:** 83/100

🎉 **Excelente!** El código está en muy buen estado.


---
*Generado automáticamente por CodeGuardian*
*Análisis completado en: 2025-10-13 18:11:47*
