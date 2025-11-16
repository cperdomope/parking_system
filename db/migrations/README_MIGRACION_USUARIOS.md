# 🚨 MIGRACIÓN CRÍTICA DE SEGURIDAD - TABLA USUARIOS

## ⚠️ PROBLEMA DETECTADO

La tabla `usuarios` actualmente almacena contraseñas en **TEXTO PLANO** - esto es una **VULNERABILIDAD CRÍTICA** que debe corregirse antes de ir a producción.

### Problemas encontrados:
1. ❌ Campo `contraseña` VARCHAR(255) - almacena texto plano
2. ❌ Campo `usuario` en vez de `username` (inconsistencia con código)
3. ❌ INSERT con contraseña en texto plano visible en el código

## ✅ SOLUCIÓN IMPLEMENTADA

### Cambios realizados:
1. ✅ Eliminado campo `contraseña` (texto plano)
2. ✅ Agregado campo `password_hash` (bcrypt con work factor 12)
3. ✅ Renombrado `usuario` → `username`
4. ✅ Hash bcrypt generado para contraseña existente
5. ✅ Campos adicionales de seguridad: `intentos_fallidos`, `bloqueado_hasta`

## 📋 CÓMO EJECUTAR LA MIGRACIÓN

### Opción 1: Usar MySQL Workbench (Recomendado)

1. **Abrir MySQL Workbench**
2. **Conectar a la base de datos** `parking_management`
3. **Abrir el archivo de migración:**
   ```
   db/migrations/001_fix_usuarios_security.sql
   ```
4. **Ejecutar el script completo** (Ctrl+Shift+Enter o botón "Execute")
5. **Verificar los resultados** en la pestaña de output

### Opción 2: Usar línea de comandos MySQL

```bash
# Navegar al directorio del proyecto
cd "d:\grado 11 sahron\OneDrive\Escritorio\parking_system"

# Ejecutar la migración
mysql -u root -p parking_management < db/migrations/001_fix_usuarios_security.sql

# Verificar el resultado
mysql -u root -p parking_management -e "DESCRIBE usuarios;"
```

### Opción 3: Usar DBeaver/HeidiSQL

1. Conectar a la base de datos
2. Abrir y ejecutar `db/migrations/001_fix_usuarios_security.sql`
3. Revisar los resultados

## 🔍 VERIFICACIÓN POST-MIGRACIÓN

### 1. Verificar estructura de la tabla

```sql
DESCRIBE usuarios;
```

**Resultado esperado:**
```
+-------------------+--------------+------+-----+---------+----------------+
| Field             | Type         | Null | Key | Default | Extra          |
+-------------------+--------------+------+-----+---------+----------------+
| id                | int          | NO   | PRI | NULL    | auto_increment |
| username          | varchar(50)  | NO   | UNI | NULL    |                |
| password_hash     | varchar(255) | NO   |     | NULL    |                |
| rol               | varchar(20)  | YES  |     | Admi... |                |
| fecha_creacion    | timestamp    | YES  |     | CURRE...|                |
| ultimo_acceso     | timestamp    | YES  |     | NULL    |                |
| activo            | tinyint(1)   | YES  |     | 1       |                |
+-------------------+--------------+------+-----+---------+----------------+
```

**✅ NO DEBE EXISTIR el campo `contraseña`**

### 2. Verificar datos del usuario

```sql
SELECT
    id,
    username,
    rol,
    activo,
    LEFT(password_hash, 29) as 'hash_preview'
FROM usuarios;
```

**Resultado esperado:**
```
+----+----------+---------------+--------+---------------------------+
| id | username | rol           | activo | hash_preview              |
+----+----------+---------------+--------+---------------------------+
|  1 | splaza   | Administrador |   1    | $2b$12$dn3DwBjpkYwsq.TwX... |
+----+----------+---------------+--------+---------------------------+
```

**✅ El hash debe comenzar con `$2b$12$`** (bcrypt work factor 12)

### 3. Probar autenticación en la aplicación

```bash
# Ejecutar la aplicación
python main.py

# Credenciales de prueba:
# Usuario: splaza
# Contraseña: splaza123*
```

**✅ El login debe funcionar correctamente** con las credenciales hasheadas

## 📊 ESTRUCTURA FINAL ESPERADA

```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Hash bcrypt
    rol ENUM('Administrador', 'Usuario', 'Invitado'),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL
);
```

## 🔐 INFORMACIÓN DE SEGURIDAD

### Credenciales por defecto (POST-MIGRACIÓN):
- **Usuario:** `splaza`
- **Contraseña:** `splaza123*`
- **Hash bcrypt:** `$2b$12$dn3DwBjpkYwsq.TwXzAOv.gfbRes3F4xXt8xZIXQS6nB6jyCPAcE2`
- **Work factor:** 12 (2^12 = 4096 iteraciones)

### ⚠️ IMPORTANTE PARA PRODUCCIÓN:
1. Cambiar la contraseña por defecto inmediatamente
2. Crear usuarios adicionales con contraseñas seguras
3. Implementar política de contraseñas fuertes
4. Habilitar autenticación de dos factores (2FA) si es posible

## 🚫 QUÉ NO HACER

❌ **NUNCA** almacenar contraseñas en texto plano
❌ **NUNCA** usar MD5 o SHA1 para contraseñas (no son seguros)
❌ **NUNCA** compartir contraseñas hasheadas públicamente
❌ **NUNCA** usar work factor < 10 para bcrypt

## ✅ MEJORES PRÁCTICAS

✅ **SIEMPRE** usar bcrypt, scrypt o argon2 para contraseñas
✅ **SIEMPRE** usar work factor ≥ 12 (recomendado: 12-14)
✅ **SIEMPRE** usar salt único por contraseña (bcrypt lo hace automáticamente)
✅ **SIEMPRE** validar longitud mínima de contraseña (8+ caracteres)

## 📞 SOPORTE

Si tienes problemas con la migración:
1. Revisa los logs de MySQL para errores
2. Verifica que tienes permisos de ALTER TABLE
3. Asegúrate de que la base de datos `parking_management` existe
4. Verifica que no hay datos críticos que se perderán

## 🎯 CHECKLIST FINAL ANTES DE PRODUCCIÓN

- [ ] Migración ejecutada exitosamente
- [ ] Campo `contraseña` eliminado
- [ ] Campo `password_hash` existe y es NOT NULL
- [ ] Hash bcrypt del usuario splaza comienza con `$2b$12$`
- [ ] Login funciona con las credenciales actuales
- [ ] Tests de autenticación pasando
- [ ] Contraseña por defecto cambiada en producción
- [ ] Backup de la base de datos realizado
- [ ] Documentación de usuarios actualizada

---

**Fecha de migración:** 2025-11-16
**Versión:** 1.0.0
**Prioridad:** 🚨 CRÍTICA - EJECUTAR ANTES DE PRODUCCIÓN
