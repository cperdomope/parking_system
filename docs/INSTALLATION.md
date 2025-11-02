# Guía de Instalación - Sistema de Gestión de Parqueaderos

Esta guía proporciona instrucciones detalladas para instalar y configurar el Sistema de Gestión de Parqueaderos en diferentes entornos.

---

## Tabla de Contenidos

- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación en Windows](#instalación-en-windows)
- [Instalación en Linux](#instalación-en-linux)
- [Instalación en macOS](#instalación-en-macos)
- [Configuración de Base de Datos](#configuración-de-base-de-datos)
- [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
- [Verificación de Instalación](#verificación-de-instalación)
- [Despliegue en Producción](#despliegue-en-producción)
- [Solución de Problemas](#solución-de-problemas)

---

## Requisitos del Sistema

### Software Requerido

| Software | Versión Mínima | Recomendado | Notas |
|----------|---------------|-------------|-------|
| Python | 3.8 | 3.10+ | Con pip incluido |
| MySQL / MariaDB | 8.0 / 10.5 | 8.0+ / 10.6+ | Con soporte UTF-8 |
| Git | 2.20+ | 2.40+ | Opcional |
| Sistema Operativo | Windows 10 / Ubuntu 20.04 / macOS 11+ | - | 64-bit |

### Hardware Recomendado

- **CPU**: 2 cores o más
- **RAM**: 4 GB mínimo, 8 GB recomendado
- **Disco**: 500 MB para la aplicación + espacio para base de datos
- **Resolución**: 1366x768 o superior

---

## Instalación en Windows

### Paso 1: Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Ejecuta el instalador
3. **IMPORTANTE**: Marca "Add Python to PATH"
4. Verifica la instalación:
```cmd
python --version
pip --version
```

### Paso 2: Instalar MySQL

1. Descarga [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
2. Ejecuta el instalador y selecciona "Developer Default"
3. Durante la configuración:
   - Authentication Method: **Use Strong Password Encryption**
   - Root password: Anota esta contraseña
   - Windows Service: **Iniciar automáticamente**
4. Verifica la instalación:
```cmd
mysql --version
```

### Paso 3: Clonar el Repositorio

```cmd
# Opción 1: Con Git
git clone https://github.com/tu-usuario/parking_system.git
cd parking_system

# Opción 2: Sin Git (descargar ZIP)
# Descargar desde GitHub y extraer
cd parking_system-main
```

### Paso 4: Crear Entorno Virtual

```cmd
python -m venv venv
venv\Scripts\activate
```

**Nota**: Verás `(venv)` al inicio de tu prompt cuando esté activado.

### Paso 5: Instalar Dependencias

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 6: Configurar Base de Datos

1. **Abrir MySQL Command Line Client** o MySQL Workbench

2. **Crear la base de datos**:
```sql
CREATE DATABASE parking_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE parking_management;
```

3. **Importar esquemas** (desde CMD):
```cmd
mysql -u root -p parking_management < db\schema\parking_database_schema.sql
mysql -u root -p parking_management < db\schema\users_table_schema.sql
```

### Paso 7: Configurar .env

1. Copiar archivo de ejemplo:
```cmd
copy .env.example .env
```

2. Editar `.env` con Notepad o tu editor favorito:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=parking_management

SECRET_KEY=genera_una_clave_segura_aqui
DEBUG=False
LOG_LEVEL=INFO
```

### Paso 8: Ejecutar la Aplicación

```cmd
python -m src --auth
```

**Primera vez**: Usuario `admin`, contraseña `admin123`

---

## Instalación en Linux

### Paso 1: Actualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 2: Instalar Dependencias del Sistema

**Ubuntu/Debian**:
```bash
sudo apt install -y python3 python3-pip python3-venv \
    mysql-server libmysqlclient-dev python3-dev \
    build-essential git
```

**Fedora/RHEL**:
```bash
sudo dnf install -y python3 python3-pip python3-devel \
    mysql-server mysql-devel gcc git
```

### Paso 3: Configurar MySQL

```bash
# Iniciar servicio
sudo systemctl start mysql
sudo systemctl enable mysql

# Configuración segura
sudo mysql_secure_installation

# Entrar a MySQL
sudo mysql
```

Dentro de MySQL:
```sql
-- Crear usuario y base de datos
CREATE DATABASE parking_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'parking_user'@'localhost' IDENTIFIED BY 'contraseña_segura';
GRANT ALL PRIVILEGES ON parking_management.* TO 'parking_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Paso 4: Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/parking_system.git
cd parking_system
```

### Paso 5: Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 6: Instalar Dependencias Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 7: Importar Esquemas

```bash
mysql -u parking_user -p parking_management < db/schema/parking_database_schema.sql
mysql -u parking_user -p parking_management < db/schema/users_table_schema.sql
```

### Paso 8: Configurar .env

```bash
cp .env.example .env
nano .env  # o vim, gedit, etc.
```

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=parking_user
DB_PASSWORD=contraseña_segura
DB_NAME=parking_management

SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
LOG_LEVEL=INFO
```

### Paso 9: Ejecutar

```bash
python3 -m src --auth
```

---

## Instalación en macOS

### Paso 1: Instalar Homebrew (si no está instalado)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 2: Instalar Dependencias

```bash
brew install python@3.10 mysql git
```

### Paso 3: Iniciar MySQL

```bash
brew services start mysql

# Configurar contraseña root
mysql_secure_installation
```

### Paso 4: Clonar y Configurar

```bash
git clone https://github.com/tu-usuario/parking_system.git
cd parking_system

# Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Dependencias
pip install -r requirements.txt
```

### Paso 5: Base de Datos

```bash
mysql -u root -p
```

```sql
CREATE DATABASE parking_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

```bash
mysql -u root -p parking_management < db/schema/parking_database_schema.sql
mysql -u root -p parking_management < db/schema/users_table_schema.sql
```

### Paso 6: Configurar y Ejecutar

```bash
cp .env.example .env
# Editar .env con tus credenciales

python3 -m src --auth
```

---

## Configuración de Base de Datos

### Esquema de Tablas

El sistema requiere las siguientes tablas:

- `funcionarios`: Empleados del sistema
- `vehiculos`: Vehículos registrados
- `parqueaderos`: Espacios de parqueo
- `asignaciones_parqueaderos`: Relación vehículo-parqueadero
- `users`: Usuarios del sistema (autenticación)

### Importar Esquemas Manualmente

Si prefieres importar usando MySQL Workbench:

1. Abre MySQL Workbench
2. Conecta a tu servidor
3. File → Run SQL Script
4. Selecciona `db/schema/parking_database_schema.sql`
5. Ejecuta
6. Repite con `db/schema/users_table_schema.sql`

### Verificar Tablas

```sql
USE parking_management;
SHOW TABLES;

-- Debe mostrar:
-- +--------------------------------+
-- | Tables_in_parking_management   |
-- +--------------------------------+
-- | asignaciones_parqueaderos      |
-- | funcionarios                   |
-- | parqueaderos                   |
-- | users                          |
-- | vehiculos                      |
-- +--------------------------------+
```

---

## Configuración de Variables de Entorno

### Archivo .env Completo

```env
# ============================================
# APLICACIÓN
# ============================================
APP_NAME=Sistema de Gestión de Parqueaderos
APP_VERSION=2.0.3
DEBUG=False
LOG_LEVEL=INFO
LOG_DIR=logs

# ============================================
# BASE DE DATOS
# ============================================
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_segura_aqui
DB_NAME=parking_management

# Conexión avanzada (opcional)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_SSL_CA=
DB_SSL_CERT=
DB_SSL_KEY=
DB_SSL_VERIFY=False

# ============================================
# SEGURIDAD
# ============================================
SECRET_KEY=cambia_esto_por_una_clave_segura_de_32_caracteres_o_mas
SESSION_TIMEOUT=480
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_TIME=30

# ============================================
# INTERFAZ DE USUARIO
# ============================================
UI_THEME=light
UI_LANGUAGE=es
SHOW_TOOLTIPS=True

# ============================================
# REPORTES
# ============================================
REPORTS_DIR=reports
DEFAULT_EXPORT_FORMAT=csv
REPORTS_RETENTION_DAYS=90

# ============================================
# AVANZADO
# ============================================
TIMEZONE=America/Bogota
ENCODING=utf-8
MAINTENANCE_MODE=False
MAINTENANCE_MESSAGE=Sistema en mantenimiento
```

### Generar SECRET_KEY Segura

**Windows (PowerShell)**:
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Linux/Mac**:
```bash
openssl rand -hex 32
```

**Python**:
```python
import secrets
print(secrets.token_hex(32))
```

---

## Verificación de Instalación

### Test de Conexión a Base de Datos

```python
# test_connection.py
from src.database.manager import DatabaseManager

try:
    db = DatabaseManager()
    result = db.fetch_one("SELECT VERSION()", ())
    print(f"✅ Conexión exitosa a MySQL {result[0]}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

Ejecutar:
```bash
python test_connection.py
```

### Test de Importaciones

```python
# test_imports.py
try:
    from src.models import FuncionarioModel, ParqueaderoModel, VehiculoModel
    from src.auth import AuthManager
    from src.ui import DashboardWidget
    print("✅ Todas las importaciones exitosas")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
```

### Test de Interfaz

```bash
# Ejecutar sin autenticación (desarrollo)
python -m src

# Debe abrir la ventana principal
```

---

## Despliegue en Producción

### Checklist de Producción

- [ ] Cambiar `DEBUG=False` en `.env`
- [ ] Generar `SECRET_KEY` única y segura
- [ ] Usar credenciales de base de datos fuertes
- [ ] Configurar backup automático de base de datos
- [ ] Habilitar logs en nivel `INFO` o `WARNING`
- [ ] Configurar firewall para puerto MySQL (3306)
- [ ] Usar HTTPS si hay conexión remota
- [ ] Cambiar contraseña del usuario `admin` por defecto
- [ ] Revisar permisos de archivos `.env` (no público)
- [ ] Configurar rotación de logs
- [ ] Implementar monitoreo de errores

### Configuración de Servicio (Linux)

Crear archivo `/etc/systemd/system/parking-system.service`:

```ini
[Unit]
Description=Sistema de Gestión de Parqueaderos
After=network.target mysql.service

[Service]
Type=simple
User=parking_user
WorkingDirectory=/opt/parking_system
Environment="PATH=/opt/parking_system/venv/bin"
ExecStart=/opt/parking_system/venv/bin/python -m src --auth
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable parking-system
sudo systemctl start parking-system
sudo systemctl status parking-system
```

---

## Solución de Problemas

### Error: "No module named 'PyQt5'"

**Causa**: PyQt5 no está instalado o el entorno virtual no está activado.

**Solución**:
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar PyQt5
pip install --upgrade PyQt5
```

### Error: "Access denied for user"

**Causa**: Credenciales incorrectas en `.env`.

**Solución**:
1. Verifica usuario y contraseña en `.env`
2. Prueba conexión manualmente:
```bash
mysql -u root -p
```

### Error: "Can't connect to MySQL server"

**Causa**: MySQL no está corriendo.

**Solución**:
```bash
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql

# macOS
brew services start mysql
```

### Error: "Table doesn't exist"

**Causa**: Esquemas no importados.

**Solución**:
```bash
mysql -u root -p parking_management < db/schema/parking_database_schema.sql
mysql -u root -p parking_management < db/schema/users_table_schema.sql
```

### Aplicación se cierra inmediatamente

**Causa**: Error en configuración o dependencias.

**Solución**:
```bash
# Ejecutar con logs de error
python -m src --auth 2>&1 | tee error.log

# Revisar logs/
cat logs/parking_system.log
```

### Error: "ImportError: DLL load failed"

**Causa**: Faltan dependencias de sistema en Windows.

**Solución**:
1. Instalar [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Reiniciar sistema

---

## Actualizaciones

### Actualizar desde Git

```bash
# Backup de base de datos primero
mysqldump -u root -p parking_management > backup_$(date +%Y%m%d).sql

# Actualizar código
git pull origin main

# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Aplicar migraciones (si hay)
mysql -u root -p parking_management < db/migrations/nueva_migracion.sql
```

### Migración de Datos

Si necesitas migrar datos de una instalación antigua, consulta [docs/MIGRATION.md](MIGRATION.md).

---

## Soporte

Si encuentras problemas durante la instalación:

1. Revisa los logs en `logs/parking_system.log`
2. Consulta la sección [Solución de Problemas](#solución-de-problemas)
3. Abre un issue en GitHub con:
   - Sistema operativo y versión
   - Versión de Python (`python --version`)
   - Mensaje de error completo
   - Pasos para reproducir

---

**Última actualización**: Noviembre 2025
**Versión de esta guía**: 1.0
