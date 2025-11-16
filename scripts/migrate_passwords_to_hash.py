#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 SCRIPT DE MIGRACIÓN DE CONTRASEÑAS
============================================================
Migra contraseñas de texto plano a hash bcrypt

ADVERTENCIA: Este script es de uso único para migración
Solo ejecutar en entorno de desarrollo/staging
============================================================
"""

import sys
import bcrypt
import mysql.connector
from pathlib import Path
from getpass import getpass

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def hash_password(password: str) -> bytes:
    """
    Genera hash bcrypt de una contraseña

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash bcrypt (60 bytes)
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))


def migrate_passwords():
    """
    Migra contraseñas de texto plano a hash bcrypt

    PROCESO:
    1. Conectar a BD
    2. Agregar columna password_hash
    3. Para cada usuario:
       - Leer contraseña en texto plano
       - Generar hash bcrypt
       - Actualizar password_hash
    4. Eliminar columna contraseña antigua
    """
    print("=" * 70)
    print("🔐 MIGRACIÓN DE CONTRASEÑAS A HASH BCRYPT")
    print("=" * 70)
    print()

    # Confirmación de seguridad
    print("⚠️  ADVERTENCIA:")
    print("   - Este proceso modificará la base de datos")
    print("   - Se recomienda hacer backup antes de continuar")
    print("   - Solo ejecutar en entorno de desarrollo/staging")
    print()

    confirmacion = input("¿Desea continuar? (escriba 'SI' para confirmar): ")

    if confirmacion.upper() != "SI":
        print("❌ Migración cancelada")
        return

    print()

    try:
        # Conectar a base de datos
        print("📡 Conectando a base de datos...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        print("✅ Conectado exitosamente")
        print()

        # Verificar si ya existe password_hash
        cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'password_hash'")
        if cursor.fetchone():
            print("⚠️  La columna 'password_hash' ya existe")
            sobrescribir = input("¿Desea sobrescribir? (SI/NO): ")
            if sobrescribir.upper() != "SI":
                print("❌ Migración cancelada")
                return
        else:
            # Agregar columna password_hash
            print("📝 Agregando columna 'password_hash'...")
            cursor.execute("""
                ALTER TABLE usuarios
                ADD COLUMN password_hash VARBINARY(255) NULL AFTER contraseña
            """)
            conn.commit()
            print("✅ Columna agregada")
            print()

        # Obtener todos los usuarios
        cursor.execute("SELECT id, usuario, contraseña FROM usuarios")
        usuarios = cursor.fetchall()

        if not usuarios:
            print("⚠️  No se encontraron usuarios para migrar")
            return

        print(f"👥 Se encontraron {len(usuarios)} usuarios")
        print()

        # Migrar cada usuario
        for i, usuario in enumerate(usuarios, 1):
            user_id = usuario['id']
            username = usuario['usuario']
            plaintext_password = usuario['contraseña']

            print(f"[{i}/{len(usuarios)}] Migrando usuario: {username}")

            # Generar hash bcrypt
            password_hash = hash_password(plaintext_password)

            # Actualizar en BD
            cursor.execute("""
                UPDATE usuarios
                SET password_hash = %s
                WHERE id = %s
            """, (password_hash, user_id))

            print(f"   ✅ Hash generado y guardado")

        conn.commit()
        print()
        print("=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print()

        # Verificar columna contraseña antigua
        print("🔍 Verificando migración...")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN password_hash IS NOT NULL THEN 1 ELSE 0 END) as migrados
            FROM usuarios
        """)
        stats = cursor.fetchone()

        print(f"   Total usuarios: {stats['total']}")
        print(f"   Migrados: {stats['migrados']}")

        if stats['total'] == stats['migrados']:
            print()
            print("⚠️  PASO FINAL:")
            print("   1. Verificar que todos los usuarios pueden hacer login")
            print("   2. Ejecutar el siguiente comando para eliminar columna antigua:")
            print()
            print("      ALTER TABLE usuarios DROP COLUMN contraseña;")
            print()
            print("   3. Actualizar código para usar password_hash en vez de contraseña")
        else:
            print()
            print("⚠️  ADVERTENCIA: No todos los usuarios fueron migrados")
            print("   No elimine la columna contraseña hasta verificar")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"❌ ERROR DE BASE DE DATOS: {e}")
        print()
        print("   Posibles causas:")
        print("   - Credenciales incorrectas")
        print("   - Base de datos no existe")
        print("   - Permisos insuficientes")

    except Exception as e:
        print(f"❌ ERROR: {e}")


def create_admin_user():
    """
    Crea un nuevo usuario administrador con contraseña segura
    """
    print("=" * 70)
    print("👤 CREAR USUARIO ADMINISTRADOR")
    print("=" * 70)
    print()

    username = input("Usuario: ")
    password = getpass("Contraseña (mín. 8 caracteres): ")
    password_confirm = getpass("Confirmar contraseña: ")

    if password != password_confirm:
        print("❌ Las contraseñas no coinciden")
        return

    if len(password) < 8:
        print("❌ La contraseña debe tener mínimo 8 caracteres")
        return

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Generar hash
        password_hash = hash_password(password)

        # Insertar usuario
        cursor.execute("""
            INSERT INTO usuarios (usuario, password_hash, rol)
            VALUES (%s, %s, 'Administrador')
        """, (username, password_hash))

        conn.commit()

        print()
        print(f"✅ Usuario '{username}' creado exitosamente")

        cursor.close()
        conn.close()

    except mysql.connector.IntegrityError:
        print(f"❌ El usuario '{username}' ya existe")
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    print()
    print("Seleccione una opción:")
    print("1. Migrar contraseñas existentes a hash bcrypt")
    print("2. Crear nuevo usuario administrador")
    print("3. Salir")
    print()

    opcion = input("Opción: ")

    if opcion == "1":
        migrate_passwords()
    elif opcion == "2":
        create_admin_user()
    else:
        print("Saliendo...")
