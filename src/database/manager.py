# -*- coding: utf-8 -*-
"""Manejador de base de datos MySQL optimizado"""

from typing import Dict, List, Optional

import mysql.connector
from mysql.connector import Error

from ..config.settings import DatabaseConfig
from ..core.logger import logger


class DatabaseManager:
    """Manejador de base de datos con patrón Singleton"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.config = DatabaseConfig()
            self.connection = None
            self.cursor = None
            self.initialized = True
            self.connect()

    def connect(self) -> bool:
        try:
            logger.info(f"Intentando conectar a la base de datos: {self.config.database}")
            self.connection = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                port=self.config.port,
            )
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info(f"Conexión establecida correctamente a: {self.config.database}")
            print(f"Conectado a la base de datos: {self.config.database}")
            return True
        except Error as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            print(f"Error al conectar a la base de datos: {e}")
            return False

    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logger.info("Desconectado de la base de datos")
            print("Desconectado de la base de datos")

    def ensure_connection(self):
        """Asegura que haya una conexión activa, reconecta si es necesario"""
        if not self.connection or not self.connection.is_connected():
            print("Reconectando a la base de datos...")
            return self.connect()
        return True

    def execute_query(self, query: str, params: tuple = None) -> tuple:
        """
        Ejecuta una consulta que modifica datos (INSERT, UPDATE, DELETE)
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
        Returns:
            tuple: (bool: éxito, str: mensaje de error si existe)
        """
        try:
            # Asegurar conexión antes de ejecutar
            if not self.ensure_connection():
                return (False, "No se pudo establecer conexión a la base de datos")

            self.cursor.execute(query, params or ())
            self.connection.commit()
            logger.debug(f"Query ejecutado exitosamente: {query[:50]}...")
            return (True, "")
        except Error as e:
            if self.connection:
                self.connection.rollback()
            error_msg = str(e)
            logger.error(f"Error ejecutando query: {error_msg}")
            print(f"Error ejecutando query: {error_msg}")
            return (False, error_msg)

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Ejecuta una consulta SELECT y retorna todos los resultados
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
        Returns:
            Lista de diccionarios con los resultados
        """
        try:
            # Asegurar conexión antes de ejecutar
            if not self.ensure_connection():
                print("No se pudo establecer conexión a la base de datos")
                return []

            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error en consulta: {e}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Ejecuta una consulta SELECT y retorna el primer resultado
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
        Returns:
            Diccionario con el resultado o None
        """
        try:
            # Asegurar conexión antes de ejecutar
            if not self.ensure_connection():
                print("No se pudo establecer conexión a la base de datos")
                return None

            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error en consulta: {e}")
            return None

    def call_procedure(self, proc_name: str, params: tuple = None) -> List:
        """
        Llama a un procedimiento almacenado
        Args:
            proc_name: Nombre del procedimiento
            params: Parámetros del procedimiento
        Returns:
            Resultados del procedimiento
        """
        try:
            self.cursor.callproc(proc_name, params or ())
            results = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            return results
        except Error as e:
            print(f"Error llamando procedimiento {proc_name}: {e}")
            return []
