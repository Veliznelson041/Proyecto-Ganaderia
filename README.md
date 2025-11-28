
---

# 📘 **SIGRAMS – Sistema de Gestión de Marcas y Señales**

**Python · Django · PostgreSQL · Bootstrap · JavaScript**
Sistema web administrativo en desarrollo para la **Dirección de Ganadería de Catamarca**, orientado a reemplazar y digitalizar los libros físicos de registro de marcas y señales ganaderas.

SIGRAMS optimiza tareas administrativas internas, automatiza el registro de productores, marcas, señales y movimientos de ganado, y permite gestionar el historial completo de cada productor.

---

## 🚀 **Descripción General**

SIGRAMS es una plataforma fullstack diseñada para uso interno del personal administrativo de la Dirección de Ganadería.
Permite gestionar de forma rápida, segura y organizada toda la información relacionada con:

* Productores ganaderos
* Marcas y señales asociadas
* Transferencias oficiales
* Ganado registrado
* Historial de movimientos

El sistema busca reemplazar procesos manuales basados en formularios y libros físicos, mejorando la trazabilidad y reduciendo errores administrativos.

---

## 🧩 **Funcionalidades Principales**

### 👤 **Gestión de Productores**

* Alta, baja, modificación y consulta
* Visualización de datos completos
* Asociar marcas, señales y ganado
* Historial del productor
* Geolocalización

### 🔖 **Gestión de Marcas y Señales**

* Registro de nuevas marcas y señales
* CRUD completo
* Vinculación con productores
* Búsqueda y filtros avanzados

### 🐄 **Gestión de Ganado**

* Registro del ganado de cada productor
* Visualización por categoría
* Relación con transferencias

### 🔄 **Transferencias Ganaderas**

* Registro de transferencias oficiales
* Validaciones administrativas
* Requiere intervención presencial (está contemplado en el sistema)

### 🔐 **Autenticación y Roles**

* Login para personal administrativo
* Panel especial para Administrador del sistema
* Control de permisos y vistas restringidas

### 📂 **Otras funcionalidades**

* Filtros avanzados en listados
* Vistas dinámicas y ordenamiento
* En desarrollo:

  * 📄 Generación de reportes PDF
  * 📊 Módulo de estadísticas e indicadores

---

## 🛠️ **Tecnologías Utilizadas**

* **Python**
* **Django (MVC)**
* **PostgreSQL**
* **Bootstrap 5**
* **JavaScript**
* **HTML5 / CSS3**

---

## 🧪 **Estado del Proyecto**

> 🟡 En desarrollo
---

## 🎯 **Objetivo**

Crear un sistema moderno, seguro y totalmente digital para la administración ganadera, mejorando la trazabilidad, reduciendo errores y optimizando los tiempos del personal del Ministerio.

---

## 📌 **Instalación y Ejecución**

```bash
git clone https://github.com/Veliznelson041/proyecto-ganaderia.git
cd proyecto-ganaderia

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## 🧑‍💼 **Usuarios del Sistema**

* **Administrador del sistema (developer)**

  * Gestión completa
  * Configuraciones internas
* **Personal administrativo**

  * CRUD y consultas
  * Transferencias
  * Registro de ganado
  * Gestión de marcas y señales

---
