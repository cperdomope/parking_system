# 🔐 Guía de Configuración SSL/TLS para MySQL

**Fecha:** 2025-10-13
**Versión:** 1.0
**Aplicable a:** Sistema de Gestión de Parqueadero

---

## 📖 Introducción

Esta guía proporciona instrucciones paso a paso para configurar SSL/TLS en MySQL, lo cual es **crítico para producción** ya que cifra toda la comunicación entre la aplicación y la base de datos.

**Importancia:**
- ✅ Cifra contraseñas en tránsito
- ✅ Protege datos sensibles
- ✅ Previene ataques man-in-the-middle
- ✅ Cumple estándares de seguridad

**Estado actual:** ❌ Sin SSL/TLS (vulnerabilidad ALTA)
**Estado objetivo:** ✅ SSL/TLS habilitado y requerido

---

## 🎯 Requisitos Previos

- MySQL Server 5.7+ instalado
- Acceso root a MySQL
- OpenSSL instalado
- Permisos de escritura en directorio de configuración MySQL

---

## 📝 Paso 1: Generar Certificados SSL

### En Linux/Mac:

```bash
# Crear directorio para certificados
sudo mkdir -p /var/lib/mysql-ssl
cd /var/lib/mysql-ssl

# 1. Generar clave privada CA (Certificate Authority)
sudo openssl genrsa 2048 > ca-key.pem

# 2. Generar certificado CA
sudo openssl req -new -x509 -nodes -days 3650 \\
  -key ca-key.pem \\
  -out ca-cert.pem \\
  -subj "/C=CO/ST=Bogota/L=Bogota/O=SsaludPlazaClaro/CN=MySQL_CA"

# 3. Generar clave privada del servidor
sudo openssl req -newkey rsa:2048 -days 3650 \\
  -nodes -keyout server-key.pem \\
  -out server-req.pem \\
  -subj "/C=CO/ST=Bogota/L=Bogota/O=SsaludPlazaClaro/CN=MySQL_Server"

# 4. Generar certificado del servidor
sudo openssl rsa -in server-key.pem -out server-key.pem
sudo openssl x509 -req -in server-req.pem -days 3650 \\
  -CA ca-cert.pem -CAkey ca-key.pem \\
  -set_serial 01 -out server-cert.pem

# 5. Generar clave privada del cliente
sudo openssl req -newkey rsa:2048 -days 3650 \\
  -nodes -keyout client-key.pem \\
  -out client-req.pem \\
  -subj "/C=CO/ST=Bogota/L=Bogota/O=SsaludPlazaClaro/CN=MySQL_Client"

# 6. Generar certificado del cliente
sudo openssl rsa -in client-key.pem -out client-key.pem
sudo openssl x509 -req -in client-req.pem -days 3650 \\
  -CA ca-cert.pem -CAkey ca-key.pem \\
  -set_serial 01 -out client-cert.pem

# 7. Verificar certificados
sudo openssl verify -CAfile ca-cert.pem server-cert.pem client-cert.pem

# 8. Establecer permisos
sudo chown mysql:mysql *.pem
sudo chmod 600 *-key.pem
sudo chmod 644 *-cert.pem ca-cert.pem
```

### En Windows:

```powershell
# Descargar OpenSSL para Windows desde https://slproweb.com/products/Win32OpenSSL.html

# Crear directorio
mkdir C:\\mysql-ssl
cd C:\\mysql-ssl

# Ejecutar los mismos comandos openssl sin 'sudo'
# Ejemplo:
openssl genrsa 2048 > ca-key.pem
# ... (seguir los mismos pasos que Linux)
```

---

## ⚙️ Paso 2: Configurar MySQL Server

### Editar archivo de configuración

**Linux:** `/etc/mysql/my.cnf` o `/etc/my.cnf`
**Windows:** `C:\\ProgramData\\MySQL\\MySQL Server 8.0\\my.ini`

```ini
[mysqld]
# Habilitar SSL
ssl-ca=/var/lib/mysql-ssl/ca-cert.pem
ssl-cert=/var/lib/mysql-ssl/server-cert.pem
ssl-key=/var/lib/mysql-ssl/server-key.pem

# Requerir SSL para todas las conexiones
require_secure_transport=ON

# Configuración adicional de seguridad
tls_version=TLSv1.2,TLSv1.3
```

### Reiniciar MySQL

```bash
# Linux
sudo systemctl restart mysql

# Windows
net stop MySQL80
net start MySQL80
```

### Verificar que SSL está habilitado

```sql
-- Conectar a MySQL
mysql -u root -p

-- Verificar variables SSL
SHOW VARIABLES LIKE '%ssl%';

-- Debería mostrar:
-- have_ssl: YES
-- ssl_ca: /var/lib/mysql-ssl/ca-cert.pem
-- ssl_cert: /var/lib/mysql-ssl/server-cert.pem
-- ssl_key: /var/lib/mysql-ssl/server-key.pem
```

---

## 👤 Paso 3: Configurar Usuario para Requerir SSL

```sql
-- Crear usuario que REQUIERE SSL
CREATE USER 'parking_user'@'localhost'
IDENTIFIED BY 'tu_password_seguro_aqui'
REQUIRE SSL;

-- O modificar usuario existente
ALTER USER 'root'@'localhost' REQUIRE SSL;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON parking_management.* TO 'parking_user'@'localhost';
FLUSH PRIVILEGES;

-- Verificar configuración del usuario
SELECT user, host, ssl_type, ssl_cipher
FROM mysql.user
WHERE user = 'parking_user';
```

---

## 🐍 Paso 4: Actualizar Código Python

### Actualizar `.env`

```env
# Configuración MySQL con SSL
DB_HOST=localhost
DB_PORT=3306
DB_USER=parking_user
DB_PASSWORD=tu_password_seguro_aqui
DB_NAME=parking_management

# Rutas a certificados SSL (OBLIGATORIO para producción)
DB_SSL_CA=/var/lib/mysql-ssl/ca-cert.pem
DB_SSL_CERT=/var/lib/mysql-ssl/client-cert.pem
DB_SSL_KEY=/var/lib/mysql-ssl/client-key.pem
```

### El código en `src/config/settings.py` ya está preparado:

```python
@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "root")
    database: str = os.getenv("DB_NAME", "parking_management")
    port: int = int(os.getenv("DB_PORT", "3306"))

    # Configuración SSL (ya implementada)
    ssl_ca: str = os.getenv("DB_SSL_CA", None)
    ssl_cert: str = os.getenv("DB_SSL_CERT", None)
    ssl_key: str = os.getenv("DB_SSL_KEY", None)
```

### Actualizar `src/database/manager.py`

El manager ya debe usar SSL si las variables están configuradas. Verificar:

```python
# En la función de conexión
connection_params = {
    'host': self.config.host,
    'user': self.config.user,
    'password': self.config.password,
    'database': self.config.database,
    'port': self.config.port,
}

# Agregar SSL si está configurado
if self.config.ssl_ca:
    connection_params['ssl_ca'] = self.config.ssl_ca
    connection_params['ssl_verify_cert'] = True
    connection_params['ssl_disabled'] = False

    if self.config.ssl_cert:
        connection_params['ssl_cert'] = self.config.ssl_cert
    if self.config.ssl_key:
        connection_params['ssl_key'] = self.config.ssl_key

connection = mysql.connector.connect(**connection_params)
```

---

## ✅ Paso 5: Verificar Conexión SSL

### Script de prueba

Crear `test_ssl_connection.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba de conexión SSL a MySQL
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database.manager import DatabaseManager

def test_ssl_connection():
    """Prueba la conexión SSL a MySQL"""

    print("=" * 60)
    print("  PRUEBA DE CONEXION SSL A MYSQL")
    print("=" * 60)
    print()

    try:
        db = DatabaseManager()

        # Verificar SSL
        query = "SHOW STATUS LIKE 'Ssl_cipher'"
        result = db.fetch_one(query)

        if result and result['Value']:
            print("[OK] Conexion SSL activa")
            print(f"     Cipher: {result['Value']}")

            # Ver más detalles
            query = "SHOW STATUS LIKE 'Ssl_%'"
            results = db.fetch_all(query)

            print("\\n[INFO] Detalles de la conexión SSL:")
            for row in results:
                if row['Value']:
                    print(f"  {row['Variable_name']}: {row['Value']}")

            return True
        else:
            print("[ERROR] Conexion NO esta usando SSL")
            return False

    except Exception as e:
        print(f"[ERROR] Error al conectar: {e}")
        return False

if __name__ == "__main__":
    success = test_ssl_connection()
    sys.exit(0 if success else 1)
```

Ejecutar:

```bash
python test_ssl_connection.py
```

---

## 🔍 Paso 6: Verificar con Wireshark (Opcional)

Para confirmar que el tráfico está cifrado:

1. Instalar Wireshark
2. Capturar tráfico en puerto 3306
3. Filtrar por `mysql`
4. Verificar que los paquetes están cifrados (no se ve SQL en texto plano)

---

## 🚨 Solución de Problemas

### Error: "SSL connection error"

```bash
# Verificar permisos de archivos
ls -l /var/lib/mysql-ssl/
# Deben ser: 600 para *.key, 644 para *.cert y ca-cert

# Corregir permisos
sudo chmod 600 /var/lib/mysql-ssl/*-key.pem
sudo chmod 644 /var/lib/mysql-ssl/*-cert.pem
```

### Error: "Certificate verification failed"

```bash
# Regenerar certificados con fechas correctas
# Verificar que OpenSSL no tiene errores
openssl verify -CAfile ca-cert.pem server-cert.pem
```

### Error: "Access denied"

```sql
-- Verificar que el usuario requiere SSL
SELECT user, host, ssl_type FROM mysql.user WHERE user = 'parking_user';

-- Si ssl_type está vacío, ejecutar:
ALTER USER 'parking_user'@'localhost' REQUIRE SSL;
FLUSH PRIVILEGES;
```

---

## 📊 Checklist de Implementación

### Pre-Producción

- [ ] Generar certificados SSL
- [ ] Configurar MySQL server con SSL
- [ ] Reiniciar MySQL
- [ ] Verificar variables SSL en MySQL
- [ ] Crear/modificar usuario con REQUIRE SSL
- [ ] Actualizar archivo .env con rutas SSL
- [ ] Probar conexión con test_ssl_connection.py
- [ ] Verificar que la aplicación funciona
- [ ] (Opcional) Verificar cifrado con Wireshark

### Producción

- [ ] Usar certificados firmados por CA reconocida (Let's Encrypt, DigiCert)
- [ ] Configurar `require_secure_transport=ON`
- [ ] Backup de certificados en lugar seguro
- [ ] Documentar ubicación de certificados
- [ ] Establecer recordatorio de renovación (antes de expiración)
- [ ] Monitorear logs de conexión SSL

---

## ⚠️ Notas Importantes

### Certificados Autofirmados

Los certificados generados en esta guía son **autofirmados** y válidos para:
- ✅ Desarrollo
- ✅ Testing
- ✅ Producción interna (LAN)

Para producción en internet pública:
- ❌ NO usar certificados autofirmados
- ✅ Usar Let's Encrypt (gratuito) o certificado comercial

### Renovación de Certificados

Los certificados generados tienen validez de **10 años** (3650 días).

**Recordatorio:** Renovar antes de:
- **2035-10-13**

Para renovar:
1. Regenerar certificados siguiendo Paso 1
2. Reiniciar MySQL
3. No es necesario reconfigurar código

### Backup

Hacer backup de certificados:

```bash
sudo tar -czf mysql-ssl-backup-$(date +%Y%m%d).tar.gz /var/lib/mysql-ssl/
sudo cp mysql-ssl-backup-*.tar.gz /path/to/secure/backup/
```

---

## 📈 Impacto en Seguridad

**Antes de SSL/TLS:**
- Score: 32/100
- Vulnerabilidad ALTA: Tráfico sin cifrar

**Después de SSL/TLS:**
- Score esperado: 45+/100
- Vulnerabilidad ALTA eliminada
- Comunicación cifrada end-to-end

---

## 🎓 Referencias

- [MySQL SSL/TLS Documentation](https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [OWASP Transport Layer Protection](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)

---

**Creado por:** Claude Code + SecureShield
**Fecha:** 2025-10-13
**Versión:** 1.0

**⚠️ NOTA:** La configuración de SSL/TLS es **obligatoria** para ambientes de producción.
