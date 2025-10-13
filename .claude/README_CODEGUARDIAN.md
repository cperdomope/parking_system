# 🛡️ CodeGuardian - Agente de Refactorización y Estilo

## Descripción

**CodeGuardian** es un agente especializado para mantener la calidad del código del Sistema de Gestión de Parqueadero. Analiza automáticamente el código, detecta problemas, sugiere mejoras y genera reportes de salud del código.

## Características Principales

✅ **Análisis Automático** - Escanea todo el repositorio en busca de problemas
✅ **Verificación Python 3.13.2** - Asegura compatibilidad con la versión exacta
✅ **Detección de Código Duplicado** - Identifica patrones repetitivos
✅ **Refactorización Inteligente** - Sugiere mejoras en funciones y clases
✅ **Reportes Detallados** - Genera `code_health_report.md` con métricas completas
✅ **Integración con Herramientas** - Soporta ruff, flake8, black, isort, pylint

## Uso con Claude Code

### Opción 1: Comando Slash (Recomendado)

```bash
/codeguardian
```

Este comando invoca al agente y ejecuta automáticamente todas las tareas de análisis.

### Opción 2: Script Manual

```bash
python .claude/codeguardian_analyzer.py
```

Ejecuta el analizador directamente y genera el reporte.

## Herramientas Opcionales (Recomendadas)

Para obtener análisis más completo, instala estas herramientas:

```bash
# Instalar todas las herramientas de análisis
pip install ruff flake8 black isort pylint

# O instalarlas individualmente
pip install ruff      # Linter rápido y moderno
pip install flake8    # Verificador de estilo PEP 8
pip install black     # Formateador automático
pip install isort     # Organizador de imports
pip install pylint    # Análisis estático avanzado
```

## Qué Analiza CodeGuardian

### 1. Compatibilidad Python
- ✅ Verifica versión exacta (3.13.2)
- ✅ Detecta sintaxis deprecated
- ✅ Valida codificación UTF-8

### 2. Calidad de Código
- 📏 Funciones largas (>100 líneas)
- 🔄 Código duplicado
- 📊 Complejidad ciclomática
- 🎯 Profundidad de anidación

### 3. Documentación
- 📝 Funciones sin docstring
- 📚 Clases sin documentación
- 💬 Comentarios faltantes

### 4. Estilo
- 🎨 Cumplimiento PEP 8
- 🔤 Nombres de variables
- 📦 Organización de imports
- 🔡 Formateo consistente

### 5. Arquitectura
- 🏗️ Patrones de diseño correctos
- 🔗 Acoplamiento entre módulos
- 📦 Separación de responsabilidades

## Archivos Prioritarios

CodeGuardian presta especial atención a:

1. `src/ui/reportes_tab.py` - Archivo más grande (~950 líneas)
2. `src/ui/asignaciones_tab.py` - Lógica compleja de asignaciones
3. `src/database/manager.py` - Patrón Singleton crítico
4. `src/database/eliminacion_cascada.py` - Transacciones sensibles
5. `main_modular.py` - Punto de entrada principal

## Reporte Generado

El comando genera `code_health_report.md` en la raíz del proyecto con:

- 📊 **Métricas Generales** - Archivos, líneas, funciones, clases
- ✅ **Compatibilidad Python** - Verificación de versión
- 🛠️ **Herramientas** - Estado de instalación
- 📝 **Documentación** - Funciones/clases sin docstring
- 📏 **Funciones Largas** - Top 10 funciones que necesitan refactorización
- 🎯 **Archivos Prioritarios** - Top 5 archivos para revisar
- 💡 **Recomendaciones** - Lista de mejoras sugeridas
- 🏆 **Puntuación** - Score de 0-100 de salud del código

## Ejemplo de Uso

```bash
# 1. Ejecutar análisis
python .claude/codeguardian_analyzer.py

# 2. Revisar el reporte generado
cat code_health_report.md

# 3. Aplicar formateo automático (si black está instalado)
black src/

# 4. Organizar imports (si isort está instalado)
isort src/

# 5. Verificar mejoras
ruff check .
```

## Integración con Claude Code

CodeGuardian está diseñado para trabajar con Claude Code:

```
User: /codeguardian
Claude: 🛡️ Iniciando análisis CodeGuardian...

        🔍 Analizando 30 archivos Python...
        📊 Generando reporte de salud del código...
        ✅ Análisis completado!

        🏆 Puntuación: 78/100

        📄 Reporte completo en: code_health_report.md
```

## Configuración

### Personalizar Umbrales

Edita `.claude/codeguardian_analyzer.py` para ajustar:

```python
# Línea 175 - Umbral de funciones largas
if func_lines > 100:  # Cambiar este valor

# Línea 287 - Penalizaciones de score
if len(self.metrics["long_functions"]) > 10:  # Ajustar umbral
    score -= 15
```

### Excluir Archivos

Modifica la función `analyze_project()` para excluir archivos:

```python
# Línea 216
if "__pycache__" in str(file_path) or "test_" in str(file_path):
    continue
```

## Recomendaciones del Proyecto

Según CLAUDE.md, el proyecto actualmente:

- ✅ Tiene código limpio (limpieza realizada 2025-01-05)
- ✅ Sin imports sin usar
- ✅ Sin archivos obsoletos
- ⚠️ Sin tests unitarios (pendiente v2.0)
- ⚠️ Algunas funciones largas en reportes_tab.py

## Roadmap de CodeGuardian

### v1.0 (Actual)
- ✅ Análisis básico de métricas
- ✅ Detección de funciones largas
- ✅ Verificación de versión Python
- ✅ Reporte en Markdown

### v2.0 (Futuro)
- 🔄 Integración con ruff/flake8
- 🔄 Análisis de complejidad ciclomática
- 🔄 Detección automática de código duplicado
- 🔄 Sugerencias de type hints
- 🔄 Integración con pre-commit hooks

### v3.0 (Futuro)
- 🔄 Refactorización automática con confirmación
- 🔄 Generación automática de tests
- 🔄 Análisis de seguridad (bandit)
- 🔄 Dashboard interactivo de métricas

## Soporte

Para problemas o sugerencias:

1. Revisa el reporte generado en `code_health_report.md`
2. Consulta los logs del script
3. Verifica que Python 3.13.2 esté instalado correctamente

## Licencia

Parte del Sistema de Gestión de Parqueadero v1.1
© 2025 - Carlos Ivan Perdomo

---

**¡CodeGuardian mantiene tu código limpio y saludable! 🛡️**
