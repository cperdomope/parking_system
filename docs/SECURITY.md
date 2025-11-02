# Política de Seguridad

## Versiones Soportadas

Las siguientes versiones del Sistema de Gestión de Parqueaderos reciben actualizaciones de seguridad:

| Versión | Soportada          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

---

## Reportar una Vulnerabilidad

La seguridad de nuestros usuarios es nuestra máxima prioridad. Si descubres una vulnerabilidad de seguridad, por favor repórtala de manera responsable.

### Proceso de Reporte

**POR FAVOR, NO CREES UN ISSUE PÚBLICO** para vulnerabilidades de seguridad.

En su lugar:

1. **Envía un email a**: security@example.com
2. **Incluye la siguiente información**:
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir el problema
   - Versión afectada
   - Impacto potencial
   - Solución propuesta (si tienes una)
   - Tu información de contacto para seguimiento

3. **Tiempo de respuesta esperado**:
   - Acuse de recibo: Dentro de 48 horas
   - Evaluación inicial: Dentro de 7 días
   - Resolución y parche: Según severidad (ver tabla abajo)

### Niveles de Severidad y Tiempo de Respuesta

| Severidad | Descripción | Tiempo de Parche |
|-----------|-------------|------------------|
| **Crítica** | Explotación remota sin autenticación, pérdida de datos | 24-48 horas |
| **Alta** | Escalación de privilegios, inyección SQL | 7 días |
| **Media** | Bypass de autenticación, XSS | 30 días |
| **Baja** | Divulgación de información menor | 90 días |

---

## Prácticas de Seguridad Implementadas

### 1. Autenticación y Autorización

- **Hashing de contraseñas**: bcrypt con salt automático
- **Control de intentos fallidos**: Máximo 5 intentos antes de bloqueo
- **Bloqueo temporal**: 30 minutos después de exceder intentos
- **Timeout de sesión**: 8 horas (configurable)
- **Contraseñas por defecto**: DEBEN cambiarse en producción

```python
# Ejemplo de configuración en .env
SECRET_KEY=genera_una_clave_segura_aqui_32_caracteres
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_TIME=30
SESSION_TIMEOUT=480
```

### 2. Prevención de Inyección SQL

- **Queries parametrizadas**: Uso exclusivo de placeholders `%s`
- **Sanitización de entrada**: Módulo `sanitizacion.py` valida toda entrada
- **Validaciones**: Regex y whitelist para todos los campos

```python
# BUENO: Query parametrizada
query = "SELECT * FROM funcionarios WHERE id = %s"
db.fetch_one(query, (funcionario_id,))

# MALO: Concatenación directa (NUNCA HACER)
query = f"SELECT * FROM funcionarios WHERE id = {funcionario_id}"
```

### 3. Validación de Entrada

Todas las entradas del usuario pasan por validadores centralizados:

```python
from src.utils.validaciones import ValidadorCampos

# Validar cédula
valido, mensaje = ValidadorCampos.validar_cedula(cedula)
if not valido:
    return (False, mensaje)

# Validar placa
valido, mensaje = ValidadorCampos.validar_placa(placa)
if not valido:
    return (False, mensaje)
```

### 4. Gestión de Secretos

- **Variables de entorno**: Credenciales en `.env` (no versionado)
- **Archivo `.env.example`**: Template sin valores sensibles
- **.gitignore**: Protege archivos sensibles

**IMPORTANTE**: Nunca commits archivos con:
- Contraseñas
- Claves API
- Tokens
- Conexiones de producción

### 5. Logging y Auditoría

- **Eventos de autenticación**: Todos los intentos de login se registran
- **Operaciones CRUD**: Logs de creación, actualización, eliminación
- **Errores de base de datos**: Registrados sin exponer información sensible
- **Ubicación**: `logs/parking_system.log`

```python
# Ejemplo de logging seguro
logger.info(f"Usuario {username} inició sesión correctamente")
logger.warning(f"Intento de login fallido para usuario {username}")
logger.error(f"Error de base de datos: {type(error).__name__}")  # Sin detalles sensibles
```

### 6. Protección de Base de Datos

- **Credenciales separadas**: Usa usuario específico, no `root`
- **Privilegios mínimos**: Solo permisos necesarios
- **Conexión local**: Por defecto solo `localhost`
- **Soporte SSL/TLS**: Configuración disponible

```sql
-- Crear usuario con privilegios mínimos
CREATE USER 'parking_user'@'localhost' IDENTIFIED BY 'contraseña_segura';
GRANT SELECT, INSERT, UPDATE, DELETE ON parking_management.* TO 'parking_user'@'localhost';
FLUSH PRIVILEGES;
```

### 7. Configuración de Producción

```env
# .env de PRODUCCIÓN
DEBUG=False                    # CRÍTICO: Desactivar debug
LOG_LEVEL=WARNING              # Solo warnings y errors
SECRET_KEY=<clave_generada_segura_32_chars>
DB_PASSWORD=<contraseña_fuerte>
DB_SSL_VERIFY=True             # Si usas SSL
```

---

## Checklist de Seguridad para Producción

Antes de desplegar en producción, verifica:

### Configuración

- [ ] `DEBUG=False` en `.env`
- [ ] `SECRET_KEY` única y segura (32+ caracteres aleatorios)
- [ ] Contraseñas de base de datos fuertes (16+ caracteres, alfanuméricos + símbolos)
- [ ] Usuario de BD con privilegios mínimos (no `root`)
- [ ] `LOG_LEVEL=WARNING` o `INFO`
- [ ] Cambiar contraseña del usuario `admin` por defecto

### Base de Datos

- [ ] Backup automático configurado
- [ ] MySQL en versión estable y actualizada
- [ ] Puerto 3306 no expuesto públicamente (firewall)
- [ ] SSL/TLS habilitado si hay acceso remoto
- [ ] Autenticación de usuario con clave fuerte

### Aplicación

- [ ] Archivo `.env` con permisos restrictivos (chmod 600)
- [ ] `.git/` no accesible en producción
- [ ] Logs con rotación automática
- [ ] Actualizar todas las dependencias (`pip install --upgrade`)
- [ ] Verificar que no hay dependencias con vulnerabilidades conocidas

### Red y Sistema

- [ ] Firewall configurado (solo puertos necesarios)
- [ ] HTTPS si hay acceso web remoto
- [ ] Sistema operativo actualizado
- [ ] Antivirus/antimalware activo (Windows)
- [ ] Backups automáticos de datos

---

## Vulnerabilidades Conocidas

Consultamos regularmente:
- [CVE Database](https://cve.mitre.org/)
- [Snyk Vulnerability Database](https://snyk.io/vuln/)
- [GitHub Security Advisories](https://github.com/advisories)

### Historial de Vulnerabilidades

#### Ninguna reportada hasta la fecha (v2.0.3)

---

## Actualizaciones de Seguridad

### Cómo Mantenerse Actualizado

1. **Suscríbete a notificaciones** del repositorio en GitHub
2. **Watch → Custom → Security alerts**
3. **Revisa CHANGELOG.md** regularmente
4. **Actualiza dependencias**:
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

### Aplicar Parches de Seguridad

```bash
# 1. Backup de base de datos
mysqldump -u root -p parking_management > backup_$(date +%Y%m%d).sql

# 2. Actualizar código
git pull origin main

# 3. Actualizar dependencias
pip install --upgrade -r requirements.txt

# 4. Aplicar migraciones si las hay
mysql -u root -p parking_management < db/migrations/security_patch_vX.X.X.sql

# 5. Reiniciar aplicación
# (método depende de cómo esté desplegada)
```

---

## Dependencias de Terceros

### Monitoreo de Vulnerabilidades

Usamos las siguientes herramientas para monitorear dependencias:

```bash
# Instalar safety (herramienta de seguridad)
pip install safety

# Verificar vulnerabilidades conocidas
safety check --file requirements.txt

# Verificar con Bandit (análisis estático)
pip install bandit
bandit -r src/
```

### Dependencias Críticas

| Dependencia | Propósito | Riesgo si Comprometida |
|-------------|-----------|------------------------|
| **PyQt5** | GUI | Ejecución de código arbitrario |
| **mysql-connector-python** | BD | Inyección SQL |
| **bcrypt** | Hashing | Compromiso de contraseñas |
| **python-dotenv** | Config | Exposición de secretos |

---

## Mejores Prácticas para Desarrolladores

### 1. Nunca Hardcodear Credenciales

```python
# MALO: Hardcoded
password = "admin123"
db_connection = "mysql://root:password@localhost/parking"

# BUENO: Desde variables de entorno
from src.config.settings import DB_CONFIG
db_connection = DB_CONFIG.connection_string
```

### 2. Validar TODA Entrada del Usuario

```python
# Siempre validar antes de procesar
from src.utils.validaciones import ValidadorCampos

cedula = input("Ingrese cédula: ")
valido, mensaje = ValidadorCampos.validar_cedula(cedula)
if not valido:
    print(f"Error: {mensaje}")
    return
```

### 3. Usar Queries Parametrizadas SIEMPRE

```python
# BUENO
query = "SELECT * FROM funcionarios WHERE cedula = %s"
result = db.fetch_one(query, (cedula,))

# MALO (vulnerable a SQL injection)
query = f"SELECT * FROM funcionarios WHERE cedula = '{cedula}'"
result = db.fetch_one(query, ())
```

### 4. Manejo Seguro de Errores

```python
# No expongas detalles internos al usuario
try:
    db.execute_query(query, params)
except Exception as e:
    logger.error(f"Error en operación: {e}", exc_info=True)  # Log detallado
    return (False, "Error al procesar la solicitud")  # Mensaje genérico al usuario
```

### 5. Logging Sin Información Sensible

```python
# BUENO
logger.info(f"Usuario {username} autenticado exitosamente")

# MALO (expone información sensible)
logger.info(f"Login exitoso: usuario={username}, password={password}")
```

---

## OWASP Top 10 - Cobertura

### A01: Broken Access Control
✅ **Implementado**: Sistema de autenticación con roles y permisos

### A02: Cryptographic Failures
✅ **Implementado**: bcrypt para contraseñas, variables de entorno para secretos

### A03: Injection
✅ **Implementado**: Queries parametrizadas, sanitización de entrada

### A04: Insecure Design
✅ **Implementado**: Principios SOLID, separación de capas

### A05: Security Misconfiguration
⚠️ **Parcial**: DEBUG debe ser False en producción, documentación completa

### A06: Vulnerable and Outdated Components
⚠️ **Monitoreo activo**: Actualizar dependencias regularmente

### A07: Identification and Authentication Failures
✅ **Implementado**: Control de intentos, timeout de sesión, hashing seguro

### A08: Software and Data Integrity Failures
✅ **Implementado**: Validaciones de integridad, transacciones ACID

### A09: Security Logging and Monitoring Failures
✅ **Implementado**: Logging completo de eventos de seguridad

### A10: Server-Side Request Forgery (SSRF)
✅ **No aplica**: Aplicación desktop sin requests externos

---

## Recursos de Seguridad

### Documentación
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

### Herramientas Recomendadas
- **Bandit**: Análisis estático de seguridad en Python
- **Safety**: Verificación de vulnerabilidades en dependencias
- **Snyk**: Monitoreo continuo de vulnerabilidades
- **OWASP ZAP**: Testing de seguridad (si hay componente web)

---

## Contacto de Seguridad

- **Email**: security@example.com
- **PGP Key**: [Disponible en keyserver]
- **Tiempo de respuesta**: 48 horas máximo

---

**Última actualización**: Noviembre 2025
**Versión de esta política**: 1.0
