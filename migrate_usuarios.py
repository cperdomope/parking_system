#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Migracin Automtica - Tabla Usuarios
Corrige la vulnerabilidad de contraseas en texto plano
"""

import sys
import mysql.connector
from mysql.connector import Error
import bcrypt
from pathlib import Path


def print_header():
    """Imprime el encabezado del script"""
    print("=" * 70)
    print(" MIGRACIN CRTICA DE SEGURIDAD - TABLA USUARIOS")
    print("=" * 70)
    print()


def conectar_bd():
    """Conecta a la base de datos"""
    try:
        print(" Conectando a la base de datos...")
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            database='parking_management',
            user='root',
            password='',  # Cambiar si tienes contrasea
            charset='utf8mb4'
        )

        if connection.is_connected():
            print(" Conexin exitosa a parking_management")
            return connection

    except Error as e:
        print(f" Error al conectar: {e}")
        sys.exit(1)


def verificar_estructura_actual(connection):
    """Verifica la estructura actual de la tabla"""
    print("\n" + "=" * 70)
    print(" PASO 1: Verificar estructura actual")
    print("=" * 70)

    cursor = connection.cursor(dictionary=True)
    cursor.execute("DESCRIBE usuarios")
    columns = cursor.fetchall()

    print("\nColumnas actuales:")
    print(f"{'Field':<20} {'Type':<20} {'Null':<6} {'Key':<6}")
    print("-" * 60)

    tiene_contrasena = False
    tiene_password_hash = False
    tiene_usuario = False
    tiene_username = False

    for col in columns:
        print(f"{col['Field']:<20} {col['Type']:<20} {col['Null']:<6} {col['Key'] or '':<6}")

        if col['Field'] == 'contrasea':
            tiene_contrasena = True
        elif col['Field'] == 'password_hash':
            tiene_password_hash = True
        elif col['Field'] == 'usuario':
            tiene_usuario = True
        elif col['Field'] == 'username':
            tiene_username = True

    print()

    if tiene_contrasena:
        print(" ADVERTENCIA: Campo 'contrasea' detectado (texto plano) - DEBE ELIMINARSE")

    if not tiene_password_hash:
        print("  Campo 'password_hash' no existe - SE CREAR")

    if tiene_usuario and not tiene_username:
        print("  Campo 'usuario' detectado - SE RENOMBRAR A 'username'")

    cursor.close()
    return tiene_contrasena, tiene_password_hash, tiene_usuario, tiene_username


def backup_datos_usuarios(connection):
    """Hace backup de los datos actuales"""
    print("\n" + "=" * 70)
    print(" PASO 2: Backup de datos actuales")
    print("=" * 70)

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    print(f"\n Backup realizado: {len(usuarios)} usuario(s)")

    for usuario in usuarios:
        print(f"   - Usuario: {usuario.get('usuario') or usuario.get('username')}")

    cursor.close()
    return usuarios


def agregar_password_hash(connection):
    """Agrega el campo password_hash si no existe"""
    print("\n" + "=" * 70)
    print(" PASO 3: Agregar campo password_hash")
    print("=" * 70)

    cursor = connection.cursor()

    try:
        sql = """
        ALTER TABLE usuarios
        ADD COLUMN password_hash VARCHAR(255) NULL
        COMMENT 'Hash bcrypt de la contrasea (work factor 12)'
        """
        cursor.execute(sql)
        connection.commit()
        print(" Campo 'password_hash' agregado correctamente")
    except Error as e:
        if "Duplicate column name" in str(e):
            print("  Campo 'password_hash' ya existe")
        else:
            print(f" Error: {e}")
            raise

    cursor.close()


def renombrar_usuario_a_username(connection):
    """Renombra el campo usuario a username"""
    print("\n" + "=" * 70)
    print("  PASO 4: Renombrar 'usuario'  'username'")
    print("=" * 70)

    cursor = connection.cursor()

    try:
        sql = """
        ALTER TABLE usuarios
        CHANGE COLUMN usuario username VARCHAR(50) UNIQUE NOT NULL
        """
        cursor.execute(sql)
        connection.commit()
        print(" Campo renombrado: 'usuario'  'username'")
    except Error as e:
        if "Unknown column" in str(e):
            print("  Campo 'usuario' no existe (ya es 'username')")
        else:
            print(f" Error: {e}")
            raise

    cursor.close()


def migrar_contraseas_a_hash(connection, usuarios_backup):
    """Migra las contraseas a hashes bcrypt"""
    print("\n" + "=" * 70)
    print(" PASO 5: Migrar contraseas a hash bcrypt")
    print("=" * 70)

    cursor = connection.cursor()

    # Contrasea conocida para el usuario por defecto
    contrasea_splaza = "splaza123*"
    hash_splaza = bcrypt.hashpw(contrasea_splaza.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

    print(f"\n Generando hash bcrypt para usuario 'splaza'...")
    print(f"   Contrasea: {contrasea_splaza}")
    print(f"   Hash: {hash_splaza[:50]}...")

    try:
        sql = """
        UPDATE usuarios
        SET password_hash = %s
        WHERE username = 'splaza'
        """
        cursor.execute(sql, (hash_splaza,))
        connection.commit()
        print(f"\n Hash actualizado para usuario 'splaza'")
    except Error as e:
        print(f" Error al actualizar hash: {e}")
        raise

    cursor.close()


def eliminar_campo_contrasea(connection):
    """Elimina el campo contrasea en texto plano"""
    print("\n" + "=" * 70)
    print("  PASO 6: Eliminar campo 'contrasea' (texto plano)")
    print("=" * 70)

    cursor = connection.cursor()

    try:
        sql = "ALTER TABLE usuarios DROP COLUMN contrasea"
        cursor.execute(sql)
        connection.commit()
        print(" Campo 'contrasea' eliminado - VULNERABILIDAD CORREGIDA")
    except Error as e:
        if "Can't DROP" in str(e):
            print("  Campo 'contrasea' no existe (ya fue eliminado)")
        else:
            print(f" Error: {e}")
            raise

    cursor.close()


def hacer_password_hash_obligatorio(connection):
    """Hace el campo password_hash obligatorio"""
    print("\n" + "=" * 70)
    print("  PASO 7: Hacer password_hash obligatorio (NOT NULL)")
    print("=" * 70)

    cursor = connection.cursor()

    try:
        sql = """
        ALTER TABLE usuarios
        MODIFY COLUMN password_hash VARCHAR(255) NOT NULL
        """
        cursor.execute(sql)
        connection.commit()
        print(" Campo 'password_hash' es ahora obligatorio (NOT NULL)")
    except Error as e:
        print(f" Error: {e}")
        raise

    cursor.close()


def verificar_migracion(connection):
    """Verifica que la migracin fue exitosa"""
    print("\n" + "=" * 70)
    print(" PASO 8: Verificacin final")
    print("=" * 70)

    cursor = connection.cursor(dictionary=True)

    # Verificar estructura
    print("\n1. Estructura de la tabla:")
    cursor.execute("DESCRIBE usuarios")
    columns = cursor.fetchall()

    tiene_contrasena = False
    tiene_password_hash = False
    tiene_username = False

    for col in columns:
        if col['Field'] == 'contrasea':
            tiene_contrasena = True
        elif col['Field'] == 'password_hash':
            tiene_password_hash = True
            password_hash_null = col['Null']
        elif col['Field'] == 'username':
            tiene_username = True

    if tiene_contrasena:
        print("    FALLO: Campo 'contrasea' an existe")
        return False
    else:
        print("    Campo 'contrasea' eliminado")

    if not tiene_password_hash:
        print("    FALLO: Campo 'password_hash' no existe")
        return False
    else:
        print("    Campo 'password_hash' existe")

        if password_hash_null == 'NO':
            print("    Campo 'password_hash' es NOT NULL")
        else:
            print("     Campo 'password_hash' permite NULL")

    if not tiene_username:
        print("    FALLO: Campo 'username' no existe")
        return False
    else:
        print("    Campo 'username' existe")

    # Verificar datos
    print("\n2. Datos de usuarios:")
    cursor.execute("""
        SELECT
            id,
            username,
            rol,
            activo,
            LEFT(password_hash, 29) as hash_preview
        FROM usuarios
    """)
    usuarios = cursor.fetchall()

    for usuario in usuarios:
        print(f"\n   Usuario: {usuario['username']}")
        print(f"   Rol: {usuario['rol']}")
        print(f"   Activo: {usuario['activo']}")
        print(f"   Hash: {usuario['hash_preview']}...")

        if usuario['hash_preview'].startswith('$2b$12$'):
            print("    Hash bcrypt vlido (work factor 12)")
        else:
            print("    Hash no es bcrypt vlido")
            return False

    cursor.close()

    print("\n" + "=" * 70)
    print(" MIGRACIN COMPLETADA EXITOSAMENTE")
    print("=" * 70)

    return True


def main():
    """Funcin principal"""
    print_header()

    connection = None

    try:
        # Conectar
        connection = conectar_bd()

        # Verificar estructura actual
        tiene_contrasena, tiene_password_hash, tiene_usuario, tiene_username = verificar_estructura_actual(connection)

        # Backup
        usuarios_backup = backup_datos_usuarios(connection)

        # Confirmar migracin
        print("\n" + "=" * 70)
        print("  CONFIRMACIN REQUERIDA")
        print("=" * 70)
        print("\nEsta migracin realizar los siguientes cambios:")
        print("1. Agregar campo 'password_hash' (si no existe)")
        print("2. Renombrar 'usuario'  'username' (si aplica)")
        print("3. Generar hash bcrypt para contraseas")
        print("4. ELIMINAR el campo 'contrasea' (texto plano)")
        print("5. Har 'password_hash' obligatorio (NOT NULL)")

        respuesta = input("\nDesea continuar con la migracin? (si/no): ").strip().lower()

        if respuesta not in ['si', 's', 'yes', 'y']:
            print("\n Migracin cancelada por el usuario")
            return

        # Ejecutar migracin
        if not tiene_password_hash:
            agregar_password_hash(connection)

        if tiene_usuario and not tiene_username:
            renombrar_usuario_a_username(connection)

        migrar_contraseas_a_hash(connection, usuarios_backup)

        if tiene_contrasena:
            eliminar_campo_contrasea(connection)

        hacer_password_hash_obligatorio(connection)

        # Verificar
        exito = verificar_migracion(connection)

        if exito:
            print("\n La tabla 'usuarios' est lista para produccin")
            print("\nCredenciales de acceso:")
            print("   Usuario: splaza")
            print("   Contrasea: splaza123*")
            print("\n  IMPORTANTE: Cambiar la contrasea en produccin")
        else:
            print("\n Hubo problemas en la verificacin - revisar manualmente")

    except Error as e:
        print(f"\n Error durante la migracin: {e}")
        if connection:
            connection.rollback()
            print(" Rollback realizado")
        sys.exit(1)

    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n Conexin cerrada")


if __name__ == "__main__":
    main()
