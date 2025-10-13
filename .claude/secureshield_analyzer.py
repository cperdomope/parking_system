#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SecureShield Analyzer - Agente de Seguridad y Cumplimiento OWASP
Compatible con Python 3.13.2
Versión: 1.0
"""

import sys
import os
import re
import ast
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class SecurityIssue:
    """Representa un problema de seguridad encontrado"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # OWASP Category
    file: str
    line: int
    code: str
    description: str
    recommendation: str
    cwe_id: str = ""  # Common Weakness Enumeration ID


class SecureShieldAnalyzer:
    """Analizador de seguridad para el Sistema de Gestión de Parqueadero"""

    # Patrones de seguridad
    PATTERNS = {
        # Credenciales en texto plano
        "hardcoded_password": [
            r'password\s*=\s*["\'](?!.*\{|\$|%)[^"\']{3,}["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
            r'passwd\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ],
        # Claves de base de datos hardcodeadas
        "db_credentials": [
            r'mysql\.connector\.connect\([^)]*password\s*=\s*["\'][^"\']+["\']',
            r'pymysql\.connect\([^)]*password\s*=\s*["\'][^"\']+["\']',
            r'psycopg2\.connect\([^)]*password\s*=\s*["\'][^"\']+["\']',
        ],
        # SQL Injection potencial
        "sql_injection": [
            r'execute\s*\(\s*["\'].*%s.*["\'].*%\s*\(',  # String formatting en SQL
            r'execute\s*\(\s*["\'].*\+.*["\']',  # Concatenación en SQL
            r'execute\s*\(\s*f["\']',  # F-strings en SQL (potencialmente inseguro)
            r'\.format\s*\([^)]*\)\s*\)',  # .format() en consultas SQL
        ],
        # Imports inseguros
        "insecure_imports": [
            r'import\s+pickle(?!\s+#\s*SAFE)',
            r'from\s+pickle\s+import',
            r'import\s+marshal',
            r'eval\s*\(',
            r'exec\s*\(',
        ],
        # Manejo inseguro de archivos
        "file_operations": [
            r'open\s*\([^)]*["\']w["\'][^)]*\)',  # Escritura de archivos sin validación
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(',
            r'subprocess\.Popen\s*\(',
        ],
    }

    # Configuraciones inseguras conocidas
    INSECURE_CONFIGS = {
        "default_passwords": ["root", "admin", "password", "123456", "splaza123*"],
        "default_users": ["root", "admin", "sa"],
        "weak_ports": [3306, 5432, 27017],  # Puertos DB sin SSL
    }

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.issues: List[SecurityIssue] = []
        self.scanned_files: List[str] = []
        self.stats = {
            "total_files": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "categories": {}
        }

    def scan_file_for_patterns(self, file_path: Path) -> List[SecurityIssue]:
        """Escanea un archivo buscando patrones de seguridad"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Escanear cada patrón
            for category, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    for line_num, line in enumerate(lines, 1):
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            issue = self._create_issue_from_pattern(
                                category, file_path, line_num, line, match
                            )
                            if issue:
                                issues.append(issue)

            # Análisis AST para problemas más complejos
            ast_issues = self._analyze_ast_security(file_path, content)
            issues.extend(ast_issues)

        except Exception as e:
            print(f"[!] Error escaneando {file_path}: {e}")

        return issues

    def _create_issue_from_pattern(
        self, category: str, file_path: Path, line_num: int, line: str, match: re.Match
    ) -> SecurityIssue:
        """Crea un SecurityIssue desde un patrón encontrado"""

        severity_map = {
            "hardcoded_password": ("CRITICAL", "A02:2021 – Cryptographic Failures", "CWE-798"),
            "db_credentials": ("CRITICAL", "A02:2021 – Cryptographic Failures", "CWE-798"),
            "sql_injection": ("CRITICAL", "A03:2021 – Injection", "CWE-89"),
            "insecure_imports": ("HIGH", "A08:2021 – Software and Data Integrity Failures", "CWE-502"),
            "file_operations": ("MEDIUM", "A01:2021 – Broken Access Control", "CWE-73"),
        }

        severity, owasp_cat, cwe = severity_map.get(category, ("LOW", "Security Issue", ""))

        recommendations = {
            "hardcoded_password": "Usar variables de entorno (.env) con python-dotenv. Nunca hardcodear contraseñas.",
            "db_credentials": "Mover credenciales a archivo .env y usar os.getenv(). Agregar .env al .gitignore.",
            "sql_injection": "Usar consultas parametrizadas con placeholders (%s) en lugar de concatenación o f-strings.",
            "insecure_imports": "Evitar pickle/eval/exec. Si es necesario, validar y sanitizar todas las entradas.",
            "file_operations": "Validar y sanitizar nombres de archivos. Usar pathlib y validar permisos.",
        }

        return SecurityIssue(
            severity=severity,
            category=owasp_cat,
            file=str(file_path.relative_to(self.project_root)),
            line=line_num,
            code=line.strip(),
            description=f"{category.replace('_', ' ').title()} detectado",
            recommendation=recommendations.get(category, "Revisar y corregir este código."),
            cwe_id=cwe
        )

    def _analyze_ast_security(self, file_path: Path, content: str) -> List[SecurityIssue]:
        """Analiza el AST buscando problemas de seguridad"""
        issues = []

        try:
            tree = ast.parse(content)

            # Buscar funciones sin manejo de excepciones en operaciones críticas
            for node in ast.walk(tree):
                # Detectar uso de exec/eval
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec']:
                            issues.append(SecurityIssue(
                                severity="CRITICAL",
                                category="A03:2021 – Injection",
                                file=str(file_path.relative_to(self.project_root)),
                                line=node.lineno,
                                code=f"Uso de {node.func.id}()",
                                description=f"Uso peligroso de {node.func.id}() detectado",
                                recommendation="Eliminar eval/exec o validar exhaustivamente la entrada.",
                                cwe_id="CWE-95"
                            ))

        except SyntaxError:
            pass  # Archivo no parseable
        except Exception as e:
            print(f"[!] Error en análisis AST de {file_path}: {e}")

        return issues

    def check_auth_security(self) -> List[SecurityIssue]:
        """Verifica seguridad en el sistema de autenticación"""
        issues = []
        auth_files = [
            self.src_path / "auth" / "auth_manager.py",
            self.src_path / "auth" / "login_window.py",
        ]

        for auth_file in auth_files:
            if not auth_file.exists():
                continue

            try:
                with open(auth_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Verificar si usa hashing de contraseñas
                if 'bcrypt' not in content and 'argon2' not in content and 'hashlib' not in content:
                    issues.append(SecurityIssue(
                        severity="CRITICAL",
                        category="A02:2021 – Cryptographic Failures",
                        file=str(auth_file.relative_to(self.project_root)),
                        line=1,
                        code="Sistema de autenticación",
                        description="No se detectó hashing de contraseñas (bcrypt/argon2)",
                        recommendation="Implementar bcrypt o argon2 para hashear contraseñas. Nunca almacenar en texto plano.",
                        cwe_id="CWE-759"
                    ))

                # Verificar protección contra fuerza bruta
                if 'login_attempts' not in content and 'failed_attempts' not in content:
                    issues.append(SecurityIssue(
                        severity="HIGH",
                        category="A07:2021 – Identification and Authentication Failures",
                        file=str(auth_file.relative_to(self.project_root)),
                        line=1,
                        code="Sistema de autenticación",
                        description="No se detectó protección contra intentos de fuerza bruta",
                        recommendation="Implementar bloqueo temporal tras X intentos fallidos (ej: 5 intentos = 15 min bloqueado).",
                        cwe_id="CWE-307"
                    ))

                # Verificar logging de auditoría
                if 'logging' not in content or 'logger' not in content:
                    issues.append(SecurityIssue(
                        severity="MEDIUM",
                        category="A09:2021 – Security Logging and Monitoring Failures",
                        file=str(auth_file.relative_to(self.project_root)),
                        line=1,
                        code="Sistema de autenticación",
                        description="No se detectó sistema de logging para auditoría",
                        recommendation="Implementar logging de intentos de acceso (exitosos y fallidos) con timestamps.",
                        cwe_id="CWE-778"
                    ))

            except Exception as e:
                print(f"[!] Error verificando {auth_file}: {e}")

        return issues

    def check_database_security(self) -> List[SecurityIssue]:
        """Verifica seguridad en configuración de base de datos"""
        issues = []
        config_file = self.src_path / "config" / "settings.py"

        if not config_file.exists():
            return issues

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verificar uso de SSL/TLS
            if 'ssl' not in content.lower() and 'tls' not in content.lower():
                issues.append(SecurityIssue(
                    severity="HIGH",
                    category="A02:2021 – Cryptographic Failures",
                    file=str(config_file.relative_to(self.project_root)),
                    line=1,
                    code="Configuración de base de datos",
                    description="No se detectó configuración SSL/TLS para conexión a base de datos",
                    recommendation="Habilitar SSL en MySQL y configurar 'ssl_ca', 'ssl_cert', 'ssl_key' en la conexión.",
                    cwe_id="CWE-319"
                ))

            # Verificar credenciales por defecto
            for line_num, line in enumerate(content.split('\n'), 1):
                for default_pwd in self.INSECURE_CONFIGS["default_passwords"]:
                    if default_pwd in line and 'password' in line.lower():
                        issues.append(SecurityIssue(
                            severity="CRITICAL",
                            category="A07:2021 – Identification and Authentication Failures",
                            file=str(config_file.relative_to(self.project_root)),
                            line=line_num,
                            code=line.strip(),
                            description=f"Contraseña por defecto/débil detectada: '{default_pwd}'",
                            recommendation="Usar contraseñas fuertes y almacenarlas en .env, no en el código.",
                            cwe_id="CWE-798"
                        ))

            # Verificar si usa variables de entorno
            if 'getenv' not in content and 'environ' not in content:
                issues.append(SecurityIssue(
                    severity="HIGH",
                    category="A05:2021 – Security Misconfiguration",
                    file=str(config_file.relative_to(self.project_root)),
                    line=1,
                    code="Configuración de base de datos",
                    description="No se usa variables de entorno para credenciales",
                    recommendation="Usar os.getenv() o python-dotenv para cargar credenciales desde .env",
                    cwe_id="CWE-526"
                ))

        except Exception as e:
            print(f"[!] Error verificando configuración DB: {e}")

        return issues

    def check_input_validation(self) -> List[SecurityIssue]:
        """Verifica sanitización de entradas de usuario"""
        issues = []
        validation_files = list(self.src_path.rglob("*validacion*.py"))

        for val_file in validation_files:
            try:
                with open(val_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Verificar sanitización básica
                sanitization_keywords = ['strip', 'sanitize', 'escape', 'validate']
                if not any(keyword in content for keyword in sanitization_keywords):
                    issues.append(SecurityIssue(
                        severity="MEDIUM",
                        category="A03:2021 – Injection",
                        file=str(val_file.relative_to(self.project_root)),
                        line=1,
                        code="Validación de entradas",
                        description="Falta sanitización robusta de entradas de usuario",
                        recommendation="Implementar sanitización exhaustiva: strip, validación de tipo, whitelist de caracteres.",
                        cwe_id="CWE-20"
                    ))

            except Exception as e:
                print(f"[!] Error verificando {val_file}: {e}")

        return issues

    def analyze_project(self) -> Dict:
        """Ejecuta análisis de seguridad completo del proyecto"""
        print("[*] Iniciando análisis de seguridad SecureShield...")
        print(f"[*] Escaneando directorio: {self.src_path}")

        # Escanear todos los archivos Python
        python_files = list(self.src_path.rglob("*.py"))
        main_files = [f for f in self.project_root.glob("main*.py")]
        config_files = [f for f in self.project_root.glob("*.sql")]
        all_files = python_files + main_files

        print(f"[*] Archivos a escanear: {len(all_files)}")

        for file_path in all_files:
            if "__pycache__" in str(file_path):
                continue

            print(f"[>] Escaneando: {file_path.name}")
            file_issues = self.scan_file_for_patterns(file_path)
            self.issues.extend(file_issues)
            self.scanned_files.append(str(file_path.relative_to(self.project_root)))
            self.stats["total_files"] += 1

        # Análisis específicos de seguridad
        print("[*] Verificando sistema de autenticación...")
        auth_issues = self.check_auth_security()
        self.issues.extend(auth_issues)

        print("[*] Verificando configuración de base de datos...")
        db_issues = self.check_database_security()
        self.issues.extend(db_issues)

        print("[*] Verificando validación de entradas...")
        input_issues = self.check_input_validation()
        self.issues.extend(input_issues)

        # Calcular estadísticas
        for issue in self.issues:
            severity_lower = issue.severity.lower()
            self.stats[severity_lower] = self.stats.get(severity_lower, 0) + 1

            category = issue.category
            self.stats["categories"][category] = self.stats["categories"].get(category, 0) + 1

        return {
            "issues": self.issues,
            "stats": self.stats,
            "scanned_files": self.scanned_files
        }

    def generate_security_report(self, analysis_results: Dict) -> str:
        """Genera el reporte de auditoría de seguridad en formato Markdown"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calcular score de seguridad (0-100)
        total_issues = len(self.issues)
        score = 100

        # Penalizaciones por severidad
        score -= self.stats.get("critical", 0) * 15
        score -= self.stats.get("high", 0) * 8
        score -= self.stats.get("medium", 0) * 3
        score -= self.stats.get("low", 0) * 1

        score = max(0, score)

        # Nivel de riesgo
        if score >= 80:
            risk_level = "🟢 BAJO"
            risk_desc = "El sistema tiene buena seguridad con pocas vulnerabilidades."
        elif score >= 60:
            risk_level = "🟡 MEDIO"
            risk_desc = "Se detectaron vulnerabilidades que deben ser corregidas."
        elif score >= 40:
            risk_level = "🟠 ALTO"
            risk_desc = "Existen vulnerabilidades críticas que requieren atención inmediata."
        else:
            risk_level = "🔴 CRÍTICO"
            risk_desc = "Sistema altamente vulnerable. Corrección urgente requerida."

        report = f"""# 🔐 Reporte de Auditoría de Seguridad - SecureShield

**Fecha:** {now}
**Python Version:** {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
**Proyecto:** Sistema de Gestión de Parqueadero v1.1
**Estándar:** OWASP Top 10 (2021)

---

## 📊 Resumen Ejecutivo

### Puntuación de Seguridad: {score}/100

**Nivel de Riesgo:** {risk_level}

{risk_desc}

### Estadísticas Generales

- **Archivos escaneados:** {self.stats['total_files']}
- **Total de hallazgos:** {total_issues}
- **Vulnerabilidades CRÍTICAS:** {self.stats.get('critical', 0)} 🔴
- **Vulnerabilidades ALTAS:** {self.stats.get('high', 0)} 🟠
- **Vulnerabilidades MEDIAS:** {self.stats.get('medium', 0)} 🟡
- **Vulnerabilidades BAJAS:** {self.stats.get('low', 0)} 🟢

---

## 🎯 Vulnerabilidades por Categoría OWASP

"""

        # Mostrar vulnerabilidades por categoría
        for category, count in sorted(self.stats["categories"].items(), key=lambda x: x[1], reverse=True):
            report += f"- **{category}:** {count} hallazgos\n"

        report += "\n---\n\n## 🚨 Hallazgos Detallados\n\n"

        # Agrupar por severidad
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            severity_issues = [i for i in self.issues if i.severity == severity]

            if not severity_issues:
                continue

            icon_map = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
            report += f"### {icon_map[severity]} {severity} ({len(severity_issues)} hallazgos)\n\n"

            for idx, issue in enumerate(severity_issues, 1):
                report += f"""#### {idx}. {issue.description}

**Archivo:** `{issue.file}:{issue.line}`
**Categoría OWASP:** {issue.category}
"""
                if issue.cwe_id:
                    report += f"**CWE ID:** {issue.cwe_id}\n"

                report += f"""**Código:**
```python
{issue.code}
```

**Recomendación:**
{issue.recommendation}

---

"""

        # Sección de recomendaciones prioritarias
        report += """## 🛠️ Plan de Remediación Prioritario

### Fase 1: Correcciones CRÍTICAS (Inmediato)

"""

        critical_issues = [i for i in self.issues if i.severity == "CRITICAL"]
        if critical_issues:
            # Agrupar recomendaciones similares
            unique_recommendations = {}
            for issue in critical_issues:
                if issue.description not in unique_recommendations:
                    unique_recommendations[issue.description] = []
                unique_recommendations[issue.description].append(issue.file)

            for idx, (desc, files) in enumerate(unique_recommendations.items(), 1):
                report += f"{idx}. **{desc}**\n"
                report += f"   - Archivos afectados: {len(files)}\n"
                report += f"   - Acción: {critical_issues[0].recommendation}\n\n"
        else:
            report += "✅ No se detectaron vulnerabilidades críticas.\n\n"

        report += """### Fase 2: Implementaciones de Seguridad Recomendadas

#### 1. Sistema de Hash de Contraseñas con bcrypt

```bash
pip install bcrypt
```

```python
import bcrypt

# Al registrar/actualizar contraseña
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Al verificar login
if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
    # Login exitoso
    pass
```

#### 2. Variables de Entorno con python-dotenv

```bash
pip install python-dotenv
```

**Crear archivo `.env`:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_seguro_aqui
DB_NAME=parking_management
DB_SSL_CA=/path/to/ca-cert.pem
```

**Modificar `src/config/settings.py`:**
```python
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = getenv("DB_HOST", "localhost")
    port: int = int(getenv("DB_PORT", "3306"))
    user: str = getenv("DB_USER", "root")
    password: str = getenv("DB_PASSWORD")
    database: str = getenv("DB_NAME", "parking_management")
    ssl_ca: str = getenv("DB_SSL_CA", None)
```

**⚠️ IMPORTANTE:** Agregar `.env` a `.gitignore`

#### 3. Protección contra Fuerza Bruta

```python
# En auth_manager.py
class AuthManager:
    def __init__(self):
        self.failed_attempts = {}  # {username: [timestamp1, timestamp2, ...]}
        self.lockout_duration = 900  # 15 minutos en segundos
        self.max_attempts = 5

    def check_lockout(self, username: str) -> bool:
        if username not in self.failed_attempts:
            return False

        # Limpiar intentos antiguos
        current_time = time.time()
        recent_attempts = [
            t for t in self.failed_attempts[username]
            if current_time - t < self.lockout_duration
        ]
        self.failed_attempts[username] = recent_attempts

        return len(recent_attempts) >= self.max_attempts
```

#### 4. Sistema de Logging con Cifrado

```python
import logging
from logging.handlers import RotatingFileHandler
from cryptography.fernet import Fernet

# Configurar logging
logger = logging.getLogger('security_audit')
handler = RotatingFileHandler('logs/security.log', maxBytes=10485760, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Registrar eventos
logger.info(f"Login exitoso: {username} desde {ip_address}")
logger.warning(f"Intento fallido: {username} desde {ip_address}")
```

#### 5. Consultas Parametrizadas (Prevención SQL Injection)

**❌ INCORRECTO:**
```python
# NO HACER ESTO
query = f"SELECT * FROM usuarios WHERE username = '{username}'"
cursor.execute(query)
```

**✅ CORRECTO:**
```python
# HACER ESTO
query = "SELECT * FROM usuarios WHERE username = %s"
cursor.execute(query, (username,))
```

#### 6. Habilitar SSL en MySQL

**En el servidor MySQL:**
```sql
-- Verificar SSL
SHOW VARIABLES LIKE '%ssl%';

-- Crear usuario con SSL requerido
CREATE USER 'parking_user'@'localhost' REQUIRE SSL;
GRANT ALL PRIVILEGES ON parking_management.* TO 'parking_user'@'localhost';
```

**En la conexión Python:**
```python
connection = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database,
    ssl_ca='/path/to/ca-cert.pem',
    ssl_verify_cert=True
)
```

---

## 📋 Checklist de Seguridad

### Inmediato (Crítico)
- [ ] Eliminar contraseñas hardcodeadas del código
- [ ] Implementar hashing de contraseñas con bcrypt
- [ ] Mover credenciales a archivo .env
- [ ] Agregar .env a .gitignore

### Corto Plazo (1-2 semanas)
- [ ] Implementar protección contra fuerza bruta
- [ ] Configurar SSL/TLS para MySQL
- [ ] Implementar sistema de logging de auditoría
- [ ] Convertir todas las consultas SQL a parametrizadas

### Mediano Plazo (1 mes)
- [ ] Implementar sanitización robusta de entradas
- [ ] Agregar validación de permisos por rol
- [ ] Implementar rate limiting en endpoints críticos
- [ ] Crear tests de seguridad automatizados

### Largo Plazo (3 meses)
- [ ] Implementar autenticación de dos factores (2FA)
- [ ] Configurar WAF (Web Application Firewall)
- [ ] Realizar penetration testing externo
- [ ] Implementar monitoreo de seguridad en tiempo real

---

## 📚 Referencias y Recursos

### OWASP Top 10 (2021)
- A01:2021 – Broken Access Control
- A02:2021 – Cryptographic Failures
- A03:2021 – Injection
- A05:2021 – Security Misconfiguration
- A07:2021 – Identification and Authentication Failures
- A08:2021 – Software and Data Integrity Failures
- A09:2021 – Security Logging and Monitoring Failures

### CWE (Common Weakness Enumeration)
- CWE-89: SQL Injection
- CWE-798: Use of Hard-coded Credentials
- CWE-759: Use of a One-Way Hash without a Salt
- CWE-307: Improper Restriction of Excessive Authentication Attempts
- CWE-319: Cleartext Transmission of Sensitive Information

### Herramientas Recomendadas
- **Bandit:** Analizador de seguridad para Python
- **Safety:** Verificador de dependencias vulnerables
- **sqlmap:** Testing de SQL Injection
- **OWASP ZAP:** Scanner de vulnerabilidades web

```bash
# Instalar herramientas
pip install bandit safety
```

---

## 🎓 Conclusión

"""

        if score >= 80:
            report += """✅ **Buena postura de seguridad.** El sistema tiene pocas vulnerabilidades. Continuar con las mejores prácticas."""
        elif score >= 60:
            report += """⚠️ **Seguridad mejorable.** Se detectaron vulnerabilidades que deben corregirse siguiendo el plan de remediación."""
        elif score >= 40:
            report += """🚨 **Acción requerida.** Existen vulnerabilidades críticas que comprometen la seguridad del sistema."""
        else:
            report += """🔴 **CRÍTICO: Acción inmediata requerida.** El sistema es altamente vulnerable y no debe estar en producción."""

        report += f"""

**Total de hallazgos:** {total_issues}
**Archivos escaneados:** {self.stats['total_files']}
**Tiempo de escaneo:** {now}

---

*Generado automáticamente por SecureShield - Agente de Seguridad OWASP*
*Versión 1.0 | Compatible con Python 3.13.2*

**⚠️ NOTA:** Este reporte es solo una auditoría automatizada. Se recomienda una revisión manual adicional por un experto en seguridad para producción.
"""

        return report

    def run(self):
        """Ejecuta el análisis de seguridad completo"""
        print("=" * 60)
        print("  SecureShield - Analisis de Seguridad OWASP")
        print("  Sistema de Gestion de Parqueadero v1.1")
        print("=" * 60)
        print()

        # Análisis
        results = self.analyze_project()

        # Generar reporte
        print("\n[*] Generando reporte de auditoría de seguridad...")
        report = self.generate_security_report(results)

        # Guardar reporte
        report_path = self.project_root / "SECURITY_AUDIT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[OK] Reporte guardado en: {report_path}")
        print()
        print("=" * 60)

        # Calcular score final
        total_issues = len(self.issues)
        score = max(0, 100 - (
            self.stats.get("critical", 0) * 15 +
            self.stats.get("high", 0) * 8 +
            self.stats.get("medium", 0) * 3 +
            self.stats.get("low", 0) * 1
        ))

        print(f"[Score] Puntuacion de Seguridad: {score}/100")
        print(f"[Issues] Total de hallazgos: {total_issues}")
        print(f"  - CRITICOS: {self.stats.get('critical', 0)}")
        print(f"  - ALTOS: {self.stats.get('high', 0)}")
        print(f"  - MEDIOS: {self.stats.get('medium', 0)}")
        print(f"  - BAJOS: {self.stats.get('low', 0)}")
        print("=" * 60)

        return report_path


if __name__ == "__main__":
    analyzer = SecureShieldAnalyzer()
    analyzer.run()
