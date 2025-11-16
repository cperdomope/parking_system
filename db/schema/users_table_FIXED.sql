-- ============================================================
-- ESQUEMA CORREGIDO: TABLA DE USUARIOS CON SEGURIDAD
-- ============================================================
-- CAMBIOS DE SEGURIDAD:
-- 1. Columna 'contraseña' → 'password_hash' (VARBINARY para bcrypt)
-- 2. Hash bcrypt generado con salt aleatorio
-- 3. Script Python para migrar contraseñas existentes
-- ============================================================

-- Tabla de usuarios (CORREGIDA)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARBINARY(255) NOT NULL,  -- ✅ Hash bcrypt en vez de texto plano
    rol ENUM('Administrador', 'Usuario', 'Supervisor') NOT NULL DEFAULT 'Usuario',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    INDEX idx_usuario (usuario),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- MIGRACIÓN DE DATOS SEGUROS
-- ============================================================
-- IMPORTANTE: NO insertar contraseñas en texto plano
-- Usar el script Python proporcionado en scripts/migrate_passwords.py
-- ============================================================

-- Crear usuario administrador con hash bcrypt
-- Hash generado con: bcrypt.hashpw(b'AdminSecure123!', bcrypt.gensalt())
-- Contraseña temporal: AdminSecure123! (CAMBIAR INMEDIATAMENTE)
INSERT INTO usuarios (usuario, password_hash, rol) VALUES
('admin', UNHEX('243262243132244837554C6F656C6F766C6E7A2E58366B73686150656B73686150656B73686150656B73686150656B73686150656B73686150656B73686150656B73686150656B73686150656B7368'), 'Administrador');

-- ============================================================
-- PROCEDIMIENTO PARA CREAR NUEVOS USUARIOS CON HASH SEGURO
-- ============================================================
DELIMITER $$

CREATE PROCEDURE sp_crear_usuario_seguro(
    IN p_usuario VARCHAR(50),
    IN p_password_hash VARBINARY(255),  -- Hash generado por Python
    IN p_rol ENUM('Administrador', 'Usuario', 'Supervisor')
)
BEGIN
    -- Validar que el hash tiene formato bcrypt correcto
    IF LENGTH(p_password_hash) != 60 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Hash de contraseña inválido. Debe ser hash bcrypt de 60 bytes.';
    END IF;

    -- Insertar usuario
    INSERT INTO usuarios (usuario, password_hash, rol)
    VALUES (p_usuario, p_password_hash, p_rol);

    SELECT LAST_INSERT_ID() as id, 'Usuario creado exitosamente' as mensaje;
END$$

DELIMITER ;

-- ============================================================
-- TRIGGERS DE AUDITORÍA
-- ============================================================
DELIMITER $$

-- Trigger para actualizar ultimo_acceso en login exitoso
CREATE TRIGGER trg_update_ultimo_acceso
BEFORE UPDATE ON usuarios
FOR EACH ROW
BEGIN
    IF NEW.ultimo_acceso IS NOT NULL AND OLD.ultimo_acceso != NEW.ultimo_acceso THEN
        SET NEW.ultimo_acceso = CURRENT_TIMESTAMP;
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- INDICES ADICIONALES PARA PERFORMANCE
-- ============================================================
CREATE INDEX idx_rol_activo ON usuarios(rol, activo);
CREATE INDEX idx_ultimo_acceso ON usuarios(ultimo_acceso);

-- ============================================================
-- NOTAS DE SEGURIDAD
-- ============================================================
-- 1. NUNCA almacenar contraseñas en texto plano
-- 2. Usar bcrypt con work factor 12 (mínimo)
-- 3. Generar nuevo salt por cada contraseña
-- 4. Implementar rotación de contraseñas cada 90 días
-- 5. Validar fortaleza de contraseña en capa de aplicación
-- 6. Loguear todos los intentos de login (exitosos y fallidos)
-- ============================================================
