"""
Setup script para Sistema de Gestión de Parqueaderos
Permite instalar el paquete con: pip install -e .
"""

from setuptools import setup, find_packages
import os

# Leer el contenido del README para la descripción larga
def read_file(filename):
    """Lee el contenido de un archivo"""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), encoding='utf-8') as f:
        return f.read()

# Leer dependencias desde requirements.txt
def read_requirements(filename='requirements.txt'):
    """Lee dependencias desde requirements.txt"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith('#')
                and not line.startswith('-r')]

setup(
    # Información básica del paquete
    name='parking-system',
    version='2.0.3',
    description='Sistema integral de gestión de parqueaderos institucionales',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Sistema de Gestión de Parqueaderos',
    author_email='dev@example.com',
    url='https://github.com/tu-usuario/parking_system',
    license='MIT',

    # Clasificadores PyPI
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications :: Qt',
    ],

    # Palabras clave
    keywords='parking management system pyqt5 mysql institucional',

    # Paquetes a incluir
    packages=find_packages(exclude=['tests', 'docs', 'scripts']),

    # Versión mínima de Python
    python_requires='>=3.8',

    # Dependencias
    install_requires=read_requirements('requirements.txt'),

    # Dependencias extras
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
        'test': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-qt>=4.2.0',
        ],
        'docs': [
            'sphinx>=7.2.0',
            'sphinx-rtd-theme>=2.0.0',
        ],
    },

    # Incluir archivos no-Python
    include_package_data=True,
    package_data={
        'parking_system': [
            'config/*.json',
            'ui/assets/*',
        ],
    },

    # Datos adicionales
    data_files=[
        ('', ['README.md', 'LICENSE']),
    ],

    # Scripts de entrada
    entry_points={
        'console_scripts': [
            'parking-system=src.__main__:main',
            'parking-system-auth=src.__main__:main_with_auth',
        ],
    },

    # Configuración del proyecto
    project_urls={
        'Bug Reports': 'https://github.com/tu-usuario/parking_system/issues',
        'Documentation': 'https://github.com/tu-usuario/parking_system/docs',
        'Source': 'https://github.com/tu-usuario/parking_system',
    },

    # Zip safe
    zip_safe=False,
)
