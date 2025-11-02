# Base de Datos - Parking Management System

Este directorio contiene los esquemas de base de datos y migraciones para el sistema de gestión de parqueadero.

## Estructura

```
db/
├── schema/      # Esquemas base de la base de datos
└── migrations/  # Migraciones y actualizaciones incrementales
```

---

## 📋 Esquemas Base (schema/)

### 1. parking_database_schema.sql
Esquema principal del sistema que incluye:
- Tablas: `parqueaderos`, `funcionarios`, `vehiculos`, `asignaciones`, `historial_accesos`
- Triggers automáticos para gestión de estados
- Vistas y procedimientos almacenados
- 200 espacios de parqueadero pre-configurados

### 2. users_table_schema.sql
Tabla de autenticación del sistema:
- Tabla `usuarios` con roles y permisos
- Usuario de prueba pre-configurado

---

## 🔄 Migraciones (migrations/)

### migracion_carro_hibrido.sql
Migración para funcionalidad de Carro Híbrido (v1.3):
- Agrega columna `tiene_carro_hibrido` a tabla `funcionarios`
- Actualiza triggers y procedimientos almacenados

---

## 🚀 Instrucciones de Uso

### Configuración Inicial (Primera vez)

**IMPORTANTE:** Ejecutar en este orden:

```bash
# 1. Conectar a MySQL
mysql -u root -p

# 2. Crear esquema principal (tablas, triggers, vistas, datos iniciales)
mysql -u root -p < db/schema/parking_database_schema.sql

# 3. Crear tabla de usuarios para autenticación
mysql -u root -p < db/schema/users_table_schema.sql
```

### Aplicar Migraciones (Actualizaciones)

```bash
# Migración de Carro Híbrido (solo si se necesita la funcionalidad v1.3)
mysql -u root -p parking_management < db/migrations/migracion_carro_hibrido.sql
```

---

## ⚙️ Configuración de Conexión

Las credenciales de base de datos se configuran mediante variables de entorno.

**Archivo `.env` (en la raíz del proyecto):**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_aqui
DB_NAME=parking_management
```

Ver `.env.example` en la raíz del proyecto para más detalles.

---

## 🔍 Verificación

Después de ejecutar los esquemas, verificar que todo esté correcto:

```sql
-- Conectar a la base de datos
USE parking_management;

-- Verificar tablas creadas
SHOW TABLES;

-- Verificar cantidad de parqueaderos (debe ser 200)
SELECT COUNT(*) FROM parqueaderos;

-- Verificar triggers activos
SHOW TRIGGERS;

-- Verificar usuario de prueba
SELECT * FROM usuarios WHERE username = 'splaza';
```

---

## 📝 Notas Importantes

- **Motor requerido:** MySQL 5.7 o superior
- **Encoding:** UTF-8 (para soporte de caracteres especiales)
- **Puerto por defecto:** 3306
- **Credenciales de prueba:**
  - Usuario: `splaza`
  - Contraseña: `splaza123*`

---

## 🛠️ Troubleshooting

### Error: "Database already exists"
```sql
-- Eliminar base de datos existente (⚠️ CUIDADO: elimina todos los datos)
DROP DATABASE IF EXISTS parking_management;

-- Luego volver a ejecutar el esquema
SOURCE db/schema/parking_database_schema.sql;
```

### Error: "Access denied"
Verificar que el usuario MySQL tenga permisos:
```sql
GRANT ALL PRIVILEGES ON parking_management.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Error: "Triggers already exist"
Si necesitas recrear los triggers:
```sql
-- Eliminar triggers existentes
DROP TRIGGER IF EXISTS before_insert_vehiculo;
DROP TRIGGER IF EXISTS after_insert_asignacion;
DROP TRIGGER IF EXISTS after_update_asignacion;

-- Luego volver a ejecutar el esquema o migración
```

---

## 📚 Documentación Adicional

- **Documentación completa:** Ver `docs/CLAUDE.md`
- **Instrucciones de Carro Híbrido:** Ver `docs/INSTRUCCIONES_CARRO_HIBRIDO.md`

---

**Última actualización:** 2025-10-26
**Versión del sistema:** 2.0.3
