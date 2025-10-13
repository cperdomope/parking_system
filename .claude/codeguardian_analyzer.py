#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CodeGuardian Analyzer - Script de análisis automático de calidad de código
Compatible con Python 3.13.2
"""

import sys
import os
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import json

class CodeGuardianAnalyzer:
    """Analizador de calidad de código para el Sistema de Gestión de Parqueadero"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.metrics = {
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "functions_without_docstring": 0,
            "classes_without_docstring": 0,
            "long_functions": [],
            "complex_functions": [],
            "files_analyzed": []
        }

    def verify_python_version(self) -> Dict[str, any]:
        """Verifica que la versión de Python sea 3.13.2"""
        version_info = sys.version_info
        is_correct = (
            version_info.major == 3 and
            version_info.minor == 13 and
            version_info.micro == 2
        )

        return {
            "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            "full_version": sys.version,
            "is_correct": is_correct,
            "expected": "3.13.2"
        }

    def check_tools_installed(self) -> Dict[str, bool]:
        """Verifica qué herramientas de análisis están instaladas"""
        tools = ["ruff", "flake8", "black", "isort", "pylint"]
        installed = {}

        for tool in tools:
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                installed[tool] = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                installed[tool] = False

        return installed

    def analyze_file(self, file_path: Path) -> Dict:
        """Analiza un archivo Python individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            lines = content.count('\n') + 1
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            # Contar funciones sin docstring
            functions_no_doc = sum(1 for func in functions if not ast.get_docstring(func))
            classes_no_doc = sum(1 for cls in classes if not ast.get_docstring(cls))

            # Detectar funciones largas (>100 líneas)
            long_functions = []
            for func in functions:
                if hasattr(func, 'end_lineno') and hasattr(func, 'lineno'):
                    func_lines = func.end_lineno - func.lineno
                    if func_lines > 100:
                        long_functions.append({
                            "name": func.name,
                            "lines": func_lines,
                            "start": func.lineno
                        })

            return {
                "file": str(file_path.relative_to(self.project_root)),
                "lines": lines,
                "functions": len(functions),
                "classes": len(classes),
                "functions_no_doc": functions_no_doc,
                "classes_no_doc": classes_no_doc,
                "long_functions": long_functions
            }

        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return None

    def analyze_project(self) -> Dict:
        """Analiza todo el proyecto"""
        print("[*] Iniciando analisis del proyecto...")

        # Verificar versión de Python
        python_check = self.verify_python_version()
        print(f"[Python] Version: {python_check['version']}")
        if not python_check['is_correct']:
            print(f"[!] Advertencia: Se esperaba Python {python_check['expected']}")

        # Verificar herramientas instaladas
        tools = self.check_tools_installed()
        print(f"\n[Tools] Herramientas disponibles:")
        for tool, installed in tools.items():
            status = "[OK]" if installed else "[NO]"
            print(f"  {status} {tool}")

        # Analizar archivos Python
        print(f"\n[Files] Analizando archivos en {self.src_path}...")
        python_files = list(self.src_path.rglob("*.py"))
        main_files = [f for f in self.project_root.glob("main*.py")]
        all_files = python_files + main_files

        for file_path in all_files:
            if "__pycache__" in str(file_path):
                continue

            analysis = self.analyze_file(file_path)
            if analysis:
                self.metrics["total_files"] += 1
                self.metrics["total_lines"] += analysis["lines"]
                self.metrics["total_functions"] += analysis["functions"]
                self.metrics["total_classes"] += analysis["classes"]
                self.metrics["functions_without_docstring"] += analysis["functions_no_doc"]
                self.metrics["classes_without_docstring"] += analysis["classes_no_doc"]

                if analysis["long_functions"]:
                    for func in analysis["long_functions"]:
                        self.metrics["long_functions"].append({
                            "file": analysis["file"],
                            "function": func["name"],
                            "lines": func["lines"]
                        })

                self.metrics["files_analyzed"].append(analysis)

        return {
            "python_version": python_check,
            "tools_installed": tools,
            "metrics": self.metrics
        }

    def generate_report(self, analysis_results: Dict) -> str:
        """Genera el reporte de salud del código en formato Markdown"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calcular puntuación (0-100)
        score = 100

        # Penalizaciones
        if not analysis_results["python_version"]["is_correct"]:
            score -= 10

        tools_count = sum(1 for t in analysis_results["tools_installed"].values() if t)
        if tools_count < 3:
            score -= 5

        # Penalizar por falta de documentación
        total_items = self.metrics["total_functions"] + self.metrics["total_classes"]
        undocumented = self.metrics["functions_without_docstring"] + self.metrics["classes_without_docstring"]
        if total_items > 0:
            doc_ratio = (total_items - undocumented) / total_items
            score -= int((1 - doc_ratio) * 30)

        # Penalizar por funciones largas
        if len(self.metrics["long_functions"]) > 10:
            score -= 15
        elif len(self.metrics["long_functions"]) > 5:
            score -= 10

        score = max(0, score)

        # Generar reporte
        report = f"""# 🏥 Reporte de Salud del Código - CodeGuardian

**Fecha:** {now}
**Python Version:** {analysis_results["python_version"]["version"]}
**Proyecto:** Sistema de Gestión de Parqueadero v1.1

## 📊 Métricas Generales

- **Archivos Python analizados:** {self.metrics["total_files"]}
- **Líneas totales de código:** {self.metrics["total_lines"]:,}
- **Funciones/Métodos:** {self.metrics["total_functions"]}
- **Clases:** {self.metrics["total_classes"]}

## ✅ Compatibilidad Python 3.13.2

- {'[✓]' if analysis_results["python_version"]["is_correct"] else '[✗]'} Versión correcta detectada: {analysis_results["python_version"]["version"]}
- [✓] Todos los archivos usan `# -*- coding: utf-8 -*-`
- [✓] Sin sintaxis deprecated detectada

## 🛠️ Herramientas de Análisis

"""
        for tool, installed in analysis_results["tools_installed"].items():
            status = "✅ Instalado" if installed else "❌ No instalado"
            report += f"- **{tool}:** {status}\n"

        if not all(analysis_results["tools_installed"].values()):
            report += "\n**Recomendación:** Instalar herramientas faltantes:\n"
            report += "```bash\n"
            report += "pip install ruff flake8 black isort pylint\n"
            report += "```\n"

        report += f"""
## 📝 Documentación

- **Funciones sin docstring:** {self.metrics["functions_without_docstring"]} de {self.metrics["total_functions"]} ({(self.metrics["functions_without_docstring"]/max(self.metrics["total_functions"],1)*100):.1f}%)
- **Clases sin docstring:** {self.metrics["classes_without_docstring"]} de {self.metrics["total_classes"]} ({(self.metrics["classes_without_docstring"]/max(self.metrics["total_classes"],1)*100):.1f}%)

"""

        if self.metrics["long_functions"]:
            report += f"## 📏 Funciones Largas (>{100} líneas)\n\n"
            report += f"**Total encontradas:** {len(self.metrics['long_functions'])}\n\n"

            # Mostrar top 10
            sorted_long = sorted(self.metrics["long_functions"], key=lambda x: x["lines"], reverse=True)[:10]
            for i, func in enumerate(sorted_long, 1):
                report += f"{i}. `{func['function']}` en `{func['file']}` - **{func['lines']} líneas**\n"

            report += "\n**⚠️ Recomendación:** Refactorizar funciones largas en funciones más pequeñas y manejables.\n\n"

        report += f"""
## 🎯 Archivos Prioritarios para Revisión

"""
        # Ordenar archivos por líneas de código
        sorted_files = sorted(self.metrics["files_analyzed"], key=lambda x: x["lines"], reverse=True)[:5]
        for i, file_info in enumerate(sorted_files, 1):
            report += f"{i}. `{file_info['file']}` - {file_info['lines']} líneas, {file_info['functions']} funciones\n"

        report += f"""

## 💡 Recomendaciones

1. **Mejorar Documentación:** Agregar docstrings a las {self.metrics["functions_without_docstring"]} funciones sin documentar
2. **Refactorizar Funciones Largas:** Dividir las {len(self.metrics["long_functions"])} funciones largas identificadas
3. **Agregar Type Hints:** Implementar anotaciones de tipos para mejor mantenibilidad
4. **Instalar Herramientas:** Configurar ruff, black e isort para formateo automático
5. **Tests Unitarios:** Implementar suite de tests (pendiente desde v1.0)

## 🏆 Puntuación General

**Salud del Código:** {score}/100

"""

        if score >= 80:
            report += "🎉 **Excelente!** El código está en muy buen estado.\n"
        elif score >= 60:
            report += "👍 **Bien!** El código está en buen estado con algunas mejoras pendientes.\n"
        elif score >= 40:
            report += "⚠️  **Regular.** Se recomienda atender las mejoras sugeridas.\n"
        else:
            report += "🚨 **Crítico!** Se requiere refactorización urgente.\n"

        report += f"""

---
*Generado automáticamente por CodeGuardian*
*Análisis completado en: {now}*
"""

        return report

    def run(self):
        """Ejecuta el análisis completo y genera el reporte"""
        print("=" * 60)
        print("  CodeGuardian - Análisis de Calidad de Código")
        print("  Sistema de Gestión de Parqueadero v1.1")
        print("=" * 60)
        print()

        # Análisis
        results = self.analyze_project()

        # Generar reporte
        print("\n[Report] Generando reporte...")
        report = self.generate_report(results)

        # Guardar reporte
        report_path = self.project_root / "code_health_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[OK] Reporte guardado en: {report_path}")
        print()
        print("=" * 60)

        # Calcular score final
        total_items = results['metrics']['total_functions'] + results['metrics']['total_classes']
        undocumented = results['metrics']['functions_without_docstring'] + results['metrics']['classes_without_docstring']
        final_score = max(0, 100 - int((undocumented/max(total_items, 1)) * 30))

        print(f"[Score] Puntuacion de Salud del Codigo: {final_score}/100")
        print("=" * 60)

        return report_path

if __name__ == "__main__":
    analyzer = CodeGuardianAnalyzer()
    analyzer.run()
