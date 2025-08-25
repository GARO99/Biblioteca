# 📚 Biblioteca API — FastAPI + SQLModel + MySQL

## 1) Descripción del problema resuelto
API REST para gestionar una **biblioteca**:

- **Catálogo**: autores, géneros, editoriales, libros y sus copias físicas.  
- **Usuarios**: miembros de la biblioteca.  
- **Operación**: **préstamos**, **reservas** (holds) y **multas** (fines).  
- La API publica documentación interactiva automáticamente en **Swagger UI** (`/docs`)

---

## 2) Estructura de la base de datos

### Entidades principales
- **author**: `id`, `full_name`, `bio`
- **genre**: `id`, `name`, `description`
- **publisher**: `id`, `name`, `website`
- **book**: `id`, `title`, `isbn_13`, `language`, `published_year`, `publisher_id (FK)`
- **book_author_link** *(M:N)*: `book_id (FK)`, `author_id (FK)` — relación muchos-a-muchos vía `link_model`. :contentReference[oaicite:1]{index=1}
- **book_genre_link** *(M:N)*: `book_id (FK)`, `genre_id (FK)` — relación muchos-a-muchos vía `link_model`. :contentReference[oaicite:2]{index=2}
- **copy**: `id`, `book_id (FK)`, `inventory_code (único)`, `status`, `location`
- **member**: `id`, `full_name`, `email`, `phone`, `active`
- **loan**: `id`, `copy_id (FK)`, `member_id (FK)`, `loan_date`, `due_date`, `return_date`, `status`
- **hold**: `id`, `book_id (FK)`, `member_id (FK)`, `status`, `placed_at`, `fulfilled_copy_id (FK opcional)`
- **fine**: `id`, `member_id (FK)`, `loan_id (FK opcional)`, `amount_cents`, `reason`, `paid`, `paid_at`

### Enumeraciones
- **CopyStatus**: `AVAILABLE`, `LOANED`, `RESERVED`, `LOST`, `DAMAGED`
- **LoanStatus**: `OPEN`, `RETURNED`, `LATE`, `LOST`
- **HoldStatus**: `ACTIVE`, `FULFILLED`, `CANCELLED`, `EXPIRED`

> Nota: Las relaciones M:N con SQLModel se configuran utilizando una **tabla de enlace** y el parámetro `link_model` en `Relationship()`.

---

## 3) Diagrama Entidad–Relación

```text
docs/
  er/
    erd-overview.png
```

# 4) Instalación local

### 4.1 Requisitos
- **Python 3.11+** (recomendado usar entorno virtual con `venv`).
- **MySQL** en ejecución y accesible.

### 4.2 Crear entorno virtual e instalar dependencias
```bash
# 1) Clonar el repo
git clone <URL_DEL_REPO>
cd <CARPETA_DEL_REPO>

# 2) Crear entorno virtual
python -m venv .venv

# 3) Activar el entorno
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

# 4) Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 Variables de entorno (`.env`)
Crea un archivo **`.env`** en la raíz del proyecto con las propiedades mínimas (la app arma la URL con ellas):

```env
# Conexión a MySQL
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=
DB_PORT=3306

# Driver / Dialecto: mysqlclient -> mysql+mysqldb | PyMySQL -> mysql+pymysql
DB_ENGINE=mysql+mysqldb
DB_NAME=biblioteca_fastapi
```

La URL de SQLAlchemy sigue el formato:
```
dialect[+driver]://user:password@host:port/dbname
```
(p.ej. `mysql+mysqldb://root:pass@127.0.0.1:3306/biblioteca_fastapi`).  
> Si tu contraseña tiene caracteres especiales, usa **URL encoding**.

### 4.4 Ejecutar la API
```bash
uvicorn main:app --reload
# Swagger UI: http://127.0.0.1:8000/docs
# ReDoc:      http://127.0.0.1:8000/redoc
```

---

# 5) Migraciones con Alembic

### 5.1 Configuración básica
- Alembic compara el **estado de la BD** con tu **metadata** (modelos) y genera migraciones **candidatas** usando `--autogenerate`. Revisa siempre el script generado antes de aplicarlo.
- En proyectos con **SQLModel**, importa **todos tus modelos** antes de exponer la metadata (por ejemplo `SQLModel.metadata`) en `migrations/env.py`, para que Alembic detecte todas las tablas.

Ejemplo mínimo en `migrations/env.py`:
```python
from sqlmodel import SQLModel
# importa aquí tus modelos para registrar las tablas en la metadata
# from domain.entities import *  # o tus imports agregadores
target_metadata = SQLModel.metadata
```

### 5.2 Flujo de trabajo típico
```bash
# (una vez) inicializar Alembic si no existe la carpeta migrations/
alembic init migrations

# crear una revisión autogenerada con los cambios detectados
alembic revision --autogenerate -m "init schema"

# aplicar migraciones pendientes
alembic upgrade head

# ver historial / versión actual
alembic history
alembic current

# revertir la última migración
alembic downgrade -1
```

> **Caso BD existente**: si conectas una base ya creada y quieres marcar el estado actual sin ejecutar scripts, puedes **sellar** la versión:
> ```bash
> alembic stamp head
> ```

---
