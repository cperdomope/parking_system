-- =====================================================
-- SISTEMA DE GESTIÓN DE PARQUEADERO
-- Tabla de Usuarios para Autenticación
-- =====================================================

USE parking_management;

-- =====================================================
-- TABLA: USUARIOS
-- Almacena credenciales de acceso al sistema
-- =====================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'Administrador',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Insertar usuario por defecto
INSERT INTO usuarios (usuario, contraseña, rol) VALUES
('splaza', 'splaza123*', 'Administrador');

-- Verificar inserción
SELECT * FROM usuarios;