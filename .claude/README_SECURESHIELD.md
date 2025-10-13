# 🔐 SecureShield - Agente de Seguridad OWASP

**Versión:** 1.0
**Compatible con:** Python 3.8+
**Estándar:** OWASP Top 10 (2021)
**Última actualización:** 2025-10-13

---

## 📖 Descripción General

**SecureShield** es un agente automatizado de análisis de seguridad diseñado específicamente para el Sistema de Gestión de Parqueadero. Realiza un escaneo exhaustivo del código buscando vulnerabilidades comunes basadas en el estándar **OWASP Top 10 (2021)** y genera un reporte completo con recomendaciones de remediación.

### Objetivo

Blindar el sistema ante vulnerabilidades en base de datos, autenticación y código, proporcionando un análisis automatizado que identifica:

- Credenciales hardcodeadas
- Vulnerabilidades de inyección SQL
- Falta de cifrado en contraseñas
- Conexiones inseguras sin SSL/TLS
- Código inseguro (eval, exec, pickle)
- Falta de validación de entradas
- Ausencia de protección contra fuerza bruta
- Falta de logging de auditoría

---

## 🎯 Características Principales

### 1. Análisis de Código Estático

- **Búsqueda por patrones regex** - Detecta credenciales hardcodeadas, SQL injection, etc.
- **Análisis AST (Abstract Syntax Tree)** - Identifica uso de funciones peligrosas como eval/exec
- **Escaneo multi-archivo** - Analiza todo el proyecto automáticamente

### 2. Verificación de Seguridad en Autenticación

- ✅ Verifica uso de hashing de contraseñas (bcrypt/argon2)
- ✅ Detecta falta de protección contra fuerza bruta
- ✅ Identifica ausencia de logging de auditoría
- ✅ Verifica implementación de rate limiting

### 3. Auditoría de Configuración de Base de Datos

- ✅ Verifica uso de SSL/TLS en conexiones MySQL
- ✅ Detecta contraseñas por defecto o débiles
- ✅ Identifica credenciales no protegidas por variables de entorno
- ✅ Verifica uso de consultas parametrizadas

### 4. Validación de Entradas

- ✅ Verifica sanitización de datos de usuario
- ✅ Detecta falta de escape de caracteres especiales
- ✅ Identifica validaciones insuficientes

### 5. Categorización OWASP y CWE

Cada vulnerabilidad se clasifica según:

- **OWASP Top 10 (2021)** - Ej: A03:2021 – Injection
- **CWE (Common Weakness Enumeration)** - Ej: CWE-89 (SQL Injection)
- **Severidad** - CRITICAL, HIGH, MEDIUM, LOW

---

## 🚀 Instalación y Uso

### Instalación

El agente ya está incluido en el proyecto. No requiere instalación adicional.

```bash
# Verificar que el script existe
ls .claude/secureshield_analyzer.py
```

### Uso con Comando Slash

La forma más fácil de ejecutar el agente es usando el comando slash:

```bash
/secureshield
```

### Uso Directo del Script

También puedes ejecutar el script directamente:

```bash
python .claude/secureshield_analyzer.py
```

### Salida

El agente genera un archivo `SECURITY_AUDIT.md` en la raíz del proyecto con el reporte completo.

---

## 📊 Interpretación del Reporte

### Puntuación de Seguridad

| Score | Nivel de Riesgo | Descripción |
|-------|-----------------|-------------|
| 80-100 | 🟢 BAJO | Buena postura de seguridad |
| 60-79 | 🟡 MEDIO | Vulnerabilidades que deben corregirse |
| 40-59 | 🟠 ALTO | Vulnerabilidades críticas presentes |
| 0-39 | 🔴 CRÍTICO | Sistema altamente vulnerable |

### Severidad de Hallazgos

#### 🔴 CRITICAL (15 puntos de penalización cada uno)

- Contraseñas hardcodeadas
- Falta de hashing de contraseñas
- Vulnerabilidades de SQL Injection
- Uso de eval/exec sin validación

**Acción:** Corrección inmediata requerida

#### 🟠 HIGH (8 puntos de penalización cada uno)

- Conexiones sin SSL/TLS
- Falta de protección contra fuerza bruta
- Variables de entorno no utilizadas
- Imports inseguros (pickle, marshal)

**Acción:** Corregir en 1-2 semanas

#### 🟡 MEDIUM (3 puntos de penalización cada uno)

- Falta de logging de auditoría
- Sanitización insuficiente de entradas
- Validaciones débiles

**Acción:** Corregir en 1 mes

#### 🟢 LOW (1 punto de penalización cada uno)

- Mejoras de código menores
- Optimizaciones recomendadas

**Acción:** Corregir cuando sea posible

---

## 🛠️ Vulnerabilidades Detectadas y Soluciones

### 1. Contraseñas Hardcodeadas

**Problema detectado:**
```python
# ❌ INSEGURO
password = "root"
DB_PASSWORD = "splaza123*"
```

**Solución:**
```python
# ✅ SEGURO
from os import getenv
from dotenv import load_dotenv

load_dotenv()
password = getenv("DB_PASSWORD")
```

**Pasos:**
1. Instalar `python-dotenv`: `pip install python-dotenv`
2. Crear archivo `.env` con credenciales
3. Agregar `.env` a `.gitignore`
4. Usar `getenv()` en el código

---

### 2. SQL Injection

**Problema detectado:**
```python
# ❌ INSEGURO - Concatenación de strings
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# ❌ INSEGURO - String formatting
query = "SELECT * FROM users WHERE id = %d" % user_id
cursor.execute(query)
```

**Solución:**
```python
# ✅ SEGURO - Consulta parametrizada
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))

# ✅ SEGURO - Múltiples parámetros
query = "SELECT * FROM users WHERE username = %s AND active = %s"
cursor.execute(query, (username, True))
```

**Beneficios:**
- MySQL escapa automáticamente los valores
- Previene inyección de SQL malicioso
- Mejora el rendimiento (query caching)

---

### 3. Falta de Hashing de Contraseñas

**Problema detectado:**
```python
# ❌ INSEGURO - Texto plano
cursor.execute("INSERT INTO usuarios (password) VALUES (%s)", (password,))

# ❌ INSEGURO - MD5/SHA1 sin salt
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
```

**Solución con bcrypt:**
```python
# ✅ SEGURO - bcrypt con salt automático
import bcrypt

# Al registrar usuario
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute("INSERT INTO usuarios (password_hash) VALUES (%s)", (password_hash,))

# Al verificar login
stored_hash = cursor.fetchone()[0]
if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
    print("Login exitoso")
```

**Instalación:**
```bash
pip install bcrypt
```

**Ventajas de bcrypt:**
- Salt automático único por contraseña
- Resistente a ataques de fuerza bruta (slow hashing)
- Ampliamente probado y seguro

---

### 4. Conexión MySQL sin SSL

**Problema detectado:**
```python
# ❌ INSEGURO - Sin cifrado
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password123"
)
```

**Solución:**
```python
# ✅ SEGURO - Con SSL/TLS
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getenv("DB_PASSWORD"),
    ssl_ca='/path/to/ca-cert.pem',
    ssl_verify_cert=True,
    ssl_disabled=False
)
```

**Configurar SSL en MySQL Server:**
```sql
-- Verificar SSL habilitado
SHOW VARIABLES LIKE '%ssl%';

-- Crear usuario con SSL obligatorio
CREATE USER 'secure_user'@'localhost' REQUIRE SSL;
GRANT ALL PRIVILEGES ON parking_management.* TO 'secure_user'@'localhost';
```

---

### 5. Protección contra Fuerza Bruta

**Problema detectado:**
```python
# ❌ INSEGURO - Intentos ilimitados
def authenticate(username, password):
    user = get_user(username)
    if user and user.password == password:
        return True
    return False
```

**Solución:**
```python
# ✅ SEGURO - Con límite de intentos y bloqueo temporal
import time
from collections import defaultdict

class AuthManager:
    def __init__(self):
        self.failed_attempts = defaultdict(list)  # {username: [timestamp1, ...]}
        self.lockout_duration = 900  # 15 minutos
        self.max_attempts = 5

    def is_locked_out(self, username: str) -> bool:
        """Verifica si el usuario está bloqueado"""
        now = time.time()
        # Limpiar intentos antiguos
        self.failed_attempts[username] = [
            t for t in self.failed_attempts[username]
            if now - t < self.lockout_duration
        ]
        return len(self.failed_attempts[username]) >= self.max_attempts

    def authenticate(self, username: str, password: str) -> bool:
        """Autentica usuario con protección contra fuerza bruta"""
        # Verificar bloqueo
        if self.is_locked_out(username):
            remaining = self.lockout_duration - (time.time() - self.failed_attempts[username][0])
            raise Exception(f"Cuenta bloqueada. Intente en {int(remaining/60)} minutos")

        # Verificar credenciales
        user = self.get_user(username)
        if user and bcrypt.checkpw(password.encode(), user.password_hash):
            # Login exitoso - limpiar intentos fallidos
            self.failed_attempts[username].clear()
            return True
        else:
            # Login fallido - registrar intento
            self.failed_attempts[username].append(time.time())
            attempts_left = self.max_attempts - len(self.failed_attempts[username])
            raise Exception(f"Credenciales inválidas. Intentos restantes: {attempts_left}")
```

---

### 6. Sistema de Logging de Auditoría

**Problema detectado:**
```python
# ❌ INSEGURO - Sin registro de eventos
def login(username, password):
    if authenticate(username, password):
        return redirect('/dashboard')
```

**Solución:**
```python
# ✅ SEGURO - Con logging completo
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Configurar logger
logger = logging.getLogger('security_audit')
handler = RotatingFileHandler(
    'logs/security.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def login(username, password, ip_address):
    try:
        if authenticate(username, password):
            logger.info(f"LOGIN_SUCCESS | User: {username} | IP: {ip_address}")
            return redirect('/dashboard')
    except Exception as e:
        logger.warning(f"LOGIN_FAILED | User: {username} | IP: {ip_address} | Error: {str(e)}")
        raise

def logout(username):
    logger.info(f"LOGOUT | User: {username}")

def password_change(username):
    logger.info(f"PASSWORD_CHANGE | User: {username}")
```

**Logs generados:**
```
2025-10-13 14:23:45 | INFO | LOGIN_SUCCESS | User: admin | IP: 192.168.1.100
2025-10-13 14:25:12 | WARNING | LOGIN_FAILED | User: admin | IP: 192.168.1.100 | Error: Credenciales inválidas
2025-10-13 14:30:00 | INFO | LOGOUT | User: admin
```

---

## 📋 Plan de Remediación Completo

### Fase 1: CRÍTICO (Días 1-3)

**Prioridad máxima - Corrección inmediata**

- [ ] **Día 1:** Eliminar todas las contraseñas hardcodeadas
  - Crear archivo `.env`
  - Migrar credenciales a variables de entorno
  - Agregar `.env` a `.gitignore`
  - Instalar `python-dotenv`

- [ ] **Día 2:** Implementar hashing de contraseñas
  - Instalar `bcrypt`
  - Migrar tabla `usuarios` para usar `password_hash`
  - Actualizar funciones de registro y login
  - Forzar reset de contraseñas de usuarios existentes

- [ ] **Día 3:** Convertir consultas SQL a parametrizadas
  - Identificar todas las consultas dinámicas
  - Reemplazar concatenación/f-strings por placeholders
  - Probar exhaustivamente

### Fase 2: ALTO (Semana 1-2)

**Prioridad alta - Corrección urgente**

- [ ] **Semana 1:** Configurar SSL/TLS en MySQL
  - Generar certificados SSL
  - Configurar MySQL para requerir SSL
  - Actualizar código de conexión
  - Probar conectividad

- [ ] **Semana 1:** Implementar protección contra fuerza bruta
  - Agregar tracking de intentos fallidos
  - Implementar bloqueo temporal
  - Agregar CAPTCHAs (opcional)

- [ ] **Semana 2:** Implementar logging de auditoría
  - Configurar `logging` module
  - Crear directorio `logs/`
  - Implementar rotación de logs
  - Registrar eventos críticos

### Fase 3: MEDIO (Mes 1)

**Prioridad media - Mejoras importantes**

- [ ] Implementar sanitización robusta de entradas
- [ ] Agregar validación por whitelist de caracteres
- [ ] Implementar rate limiting global
- [ ] Agregar headers de seguridad HTTP

### Fase 4: BAJO (Mes 2-3)

**Prioridad baja - Mejoras recomendadas**

- [ ] Implementar autenticación de dos factores (2FA)
- [ ] Configurar Web Application Firewall (WAF)
- [ ] Realizar penetration testing
- [ ] Implementar monitoreo en tiempo real

---

## 🔍 Ejemplo de Reporte Generado

```markdown
# 🔐 Reporte de Auditoría de Seguridad - SecureShield

**Fecha:** 2025-10-13 18:30:00
**Puntuación de Seguridad:** 45/100
**Nivel de Riesgo:** 🟠 ALTO

## Resumen Ejecutivo

- Archivos escaneados: 31
- Total de hallazgos: 27
- Vulnerabilidades CRÍTICAS: 8 🔴
- Vulnerabilidades ALTAS: 6 🟠
- Vulnerabilidades MEDIAS: 10 🟡
- Vulnerabilidades BAJAS: 3 🟢

## Hallazgos CRÍTICOS

### 1. Contraseña hardcodeada detectada
**Archivo:** `src/config/settings.py:15`
**Categoría OWASP:** A02:2021 – Cryptographic Failures
**CWE ID:** CWE-798
**Código:**
```python
password: str = "root"
```
**Recomendación:** Usar variables de entorno (.env) con python-dotenv...
```

---

## 📚 Referencias y Recursos

### Documentación Oficial

- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [MySQL SSL Documentation](https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html)
- [bcrypt Documentation](https://github.com/pyca/bcrypt/)

### Herramientas Complementarias

```bash
# Bandit - Analizador de seguridad para Python
pip install bandit
bandit -r src/

# Safety - Verificador de dependencias vulnerables
pip install safety
safety check --json

# sqlmap - Testing de SQL Injection
sqlmap -u "http://localhost/api/login" --data="user=admin&pass=admin"
```

### Librerías Recomendadas

```bash
pip install bcrypt              # Hashing de contraseñas
pip install python-dotenv       # Variables de entorno
pip install cryptography        # Cifrado general
pip install pyjwt               # JSON Web Tokens
pip install python-jose         # JWT con más features
```

---

## 🎓 Mejores Prácticas de Seguridad

### 1. Principio de Mínimo Privilegio

```python
# Usuario de DB con privilegios limitados
CREATE USER 'parking_app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE ON parking_management.* TO 'parking_app'@'localhost';
# NO dar privilegios de DROP, DELETE, GRANT
```

### 2. Defensa en Profundidad (Defense in Depth)

- **Capa 1:** Validación en frontend (PyQt5)
- **Capa 2:** Validación en backend (Python)
- **Capa 3:** Restricciones en base de datos (MySQL)
- **Capa 4:** Firewall y seguridad de red

### 3. Fail Securely (Fallar de Forma Segura)

```python
# ✅ BUENO - Denegar por defecto
def check_permission(user, resource):
    if user.is_admin:
        return True
    if user.has_permission(resource):
        return True
    return False  # Por defecto: denegar

# ❌ MALO - Permitir por defecto
def check_permission(user, resource):
    if user.is_banned:
        return False
    return True  # Por defecto: permitir
```

### 4. No Confiar en el Cliente

```python
# ❌ MALO - Confiar en dato del cliente
user_role = request.form.get('role')  # Cliente envía "admin"
create_user(username, password, role=user_role)

# ✅ BUENO - Validar en servidor
user_role = 'user'  # Por defecto
if current_user.is_admin and request.form.get('role') == 'admin':
    user_role = 'admin'
create_user(username, password, role=user_role)
```

---

## ⚙️ Configuración Avanzada

### Personalizar Patrones de Búsqueda

Edita `.claude/secureshield_analyzer.py` para agregar patrones personalizados:

```python
PATTERNS = {
    # Agregar nuevos patrones
    "custom_secrets": [
        r'STRIPE_API_KEY\s*=\s*["\'][^"\']+["\']',
        r'AWS_SECRET\s*=\s*["\'][^"\']+["\']',
    ],
}
```

### Ajustar Severidad de Penalizaciones

```python
# En generate_security_report()
score -= self.stats.get("critical", 0) * 20  # Aumentar penalización
score -= self.stats.get("high", 0) * 10
score -= self.stats.get("medium", 0) * 5
score -= self.stats.get("low", 0) * 2
```

---

## 🤝 Contribuir

Si encuentras una vulnerabilidad no detectada por SecureShield:

1. Documentar el caso
2. Agregar patrón de detección al script
3. Probar con el proyecto
4. Actualizar documentación

---

## 📞 Soporte

Para preguntas o problemas con SecureShield:

- Revisar la documentación completa
- Consultar [OWASP Top 10](https://owasp.org/Top10/)
- Buscar en [CWE Database](https://cwe.mitre.org/)

---

## ⚠️ Disclaimer

**SecureShield es una herramienta automatizada de análisis estático.** No reemplaza:

- Revisión manual de código por expertos
- Penetration testing profesional
- Auditorías de seguridad externas
- Análisis dinámico (runtime)

Para sistemas en producción, se recomienda contratar servicios profesionales de seguridad.

---

**Versión:** 1.0
**Última actualización:** 2025-10-13
**Mantenedor:** Claude Code + SecureShield

© 2025 - Sistema de Gestión de Parqueadero
