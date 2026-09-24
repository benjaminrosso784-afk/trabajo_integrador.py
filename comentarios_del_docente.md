# Comentarios de la cátedra

Informática (TDS05) · Proyecto Integrador · UM Río Cuarto

Acá va la devolución de cada revisión semanal. Léanlo antes de seguir programando.
Primero está el alcance completo del proyecto; al final, la devolución de cada semana.

**Grupo:** Benjamín Rosso, Ignacio Vélez
**Tema:** Cierre de caja

---

# Alcances de este proyecto

Esto es lo que hay que entregar. Lo que no está acá, no se pide.

## Reglas comunes a todos los grupos

### Stack
- Python + **FastAPI** + Uvicorn.
- Datos en **SQLite** usando **SQLAlchemy** (ORM): las tablas se definen como clases de Python y las consultas se hacen con métodos, sin escribir SQL a mano. **No se usa Pydantic**: las validaciones se hacen a mano en Python. Guía con ejemplo completo: [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md).
- Repositorio en GitHub con commits de **todos** los integrantes.
- API desplegada **en producción con Gunicorn** en Render, con URL pública y `/docs` funcionando (ver abajo).

### Nombres en el código (criterio acordado con la cátedra de Inglés)
- **Variables, funciones y clases en inglés**: `list_students`, `get_session`, `class Student(Base)`.
- **Tablas, columnas, rutas y query params** quedan **como figuran en el alcance** (en español): son el contrato de la API. Ejemplo: `class Student(Base)` con `__tablename__ = "estudiantes"` y columna `anio_cursada`.
- **Comentarios**: pueden estar en español mientras desarrollan, pero para la **entrega final** tienen que estar en inglés.

### Despliegue a producción (Render + Gunicorn)

En tu compu desarrollás con `uvicorn main:app --reload`. En producción corre **Gunicorn** como administrador de procesos, con workers de Uvicorn adentro.

> Gunicorn **no funciona en Windows**. Localmente seguí usando `uvicorn`; Gunicorn corre en el servidor (Linux).

`requirements.txt` debe incluir:
```
fastapi
uvicorn
uvicorn-worker
gunicorn
sqlalchemy
```

En Render → **New → Web Service** → conectás el repo, y configurás:

| Campo | Valor |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python seed.py && gunicorn main:app -k uvicorn_worker.UvicornWorker -w 2 -b 0.0.0.0:$PORT` |

La clave viaja en el código, así que no hay que configurar nada más en Render.

- El seed corre **una sola vez antes** de levantar Gunicorn. Si lo pusieras adentro de `main.py`, cada worker lo ejecutaría por su cuenta y podrían cargar los datos duplicados.
- El plan gratis se duerme tras ~15 min sin uso (la primera visita tarda ~1 min) y su disco se borra al reiniciar: por eso el seed.

### Base de datos
- **3 tablas**, cada una con clave primaria (`id`).
- Al menos **1 relación** entre tablas (clave foránea, ej. `equipo_id`).
- Unos **10 registros de ejemplo** por tabla. Siempre **datos ficticios**.
- Un script de carga inicial `seed.py` que crea las tablas (`create_all`) y carga los datos **si la base está vacía** (ver sección 9 de la guía). Se ejecuta antes de levantar el servidor. En Render el disco se borra al reiniciar: así la API siempre arranca con datos.
- El archivo `.db` **no se sube** a GitHub (agregalo al `.gitignore`); se genera solo.

### Seguridad: TODOS los endpoints van protegidos
- Todos los endpoints piden la API key en el encabezado `X-API-Key`.
- La clave se define como una constante al principio de `main.py`. Más adelante en la carrera van a ver cómo sacarla del código con variables de entorno; por ahora, así.
- Como la clave está a la vista en el repo, **los datos son todos ficticios** y no se usa esta API para nada real.
- Sin clave o con clave incorrecta → **401**.

Se protege toda la app de una vez:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader

CLAVE = "clave-de-prueba-2026"   # clave del grupo
header = APIKeyHeader(name="X-API-Key")

def verificar(clave: str = Depends(header)):
    if clave != CLAVE:
        raise HTTPException(status_code=401, detail="API key invalida")

app = FastAPI(dependencies=[Depends(verificar)])
```

En `/docs` usá el botón **Authorize** para cargar la clave y probar.

---

## Nivel A — obligatorio (igual para todos)

Cada grupo implementa **exactamente estos 6 endpoints**, adaptados a su tema (ver *Alcance de este grupo*):

| # | Tipo | Ejemplo genérico | Qué practica |
|---|---|---|---|
| 1 | Listado con filtro | `GET /cosas?campo=valor` | Query param, `select(...).where(...)` |
| 2 | Detalle | `GET /cosas/{id}` | Path param, **404** si no existe |
| 3 | Relación | `GET /cosas/{id}/otras` | Cruzar dos tablas por la clave foránea (`relationship` o filtro por FK) |
| 4 | Segundo listado con filtro | `GET /otras?campo=valor` | Query param sobre otra tabla |
| 5 | Calculado | `GET /resumen` | Contar, sumar o agrupar (en Python o con `func` de SQLAlchemy) |
| 6 | Alta | `POST /cosas` | Recibir el cuerpo como `dict`, **validar a mano** (400 si está mal) e insertar con la sesión |

Además, en Nivel A:
- **Errores:** 401 (sin clave), 404 (no existe), y la API no se cae si la base no está o falla una consulta (`try/except`).
- **Filtros opcionales:** si no se manda el query param, devuelve todo.
- **Deploy:** URL pública en Render con `/docs` operativo.
- **README:** qué hace la API, lista de endpoints, cómo usar la API key, cómo correrla localmente, y declaración de uso de IA si la usaron.

## Nivel B — opcional

Existe un Nivel B que suma hasta 1 punto sobre la nota final. **No se preocupen por eso todavía:** lo vemos en clase más adelante, cuando el Nivel A esté andando.

---

## Alcance de este grupo

### Grupo 7 · Cierre de caja
**Integrantes:** Benjamín Rosso, Ignacio Vélez

**Tablas**
- `productos`: id, nombre, categoria, precio
- `ventas`: id, fecha, cantidad, medio_pago (efectivo / debito / transferencia), total, producto_id (FK)
- `egresos`: id, fecha, concepto, monto

**Endpoints Nivel A**
1. `GET /productos?categoria=bebidas`
2. `GET /ventas/{id}`
3. `GET /productos/{id}/ventas`
4. `GET /egresos?fecha=2026-09-10`
5. `GET /caja/cierre?fecha=2026-09-10` → total vendido, total por medio de pago, total de egresos y saldo del día
6. `POST /egresos`


---

## Fuera de alcance (para todos)

No se pide y **no suma**:
- Frontend o páginas web.
- Login de usuarios, registro, JWT.
- Bases de datos externas (PostgreSQL, MySQL, etc.).
- Docker.
- Integración con IA o con el chatbot (eso corresponde a Análisis de Sistemas).
- Pagos, facturación, envío de mails, hardware real.

## Entregables

1. Repositorio GitHub: `main.py`, script de seed, `requirements.txt`, `README.md`, commits de todos.
2. URL pública en Render con `/docs` funcionando.
3. Video demo (máx. 5 min): endpoints funcionando con clave, y un pedido **sin** clave mostrando el 401.
4. Defensa oral: demo en vivo desde `/docs` y preguntas sobre el código.

---

# Devolución semanal

## 23/09

**📌 Novedad:** la base se maneja con **SQLAlchemy** (ORM) y **sin Pydantic**; las validaciones del `POST` van a mano. Hay una guía con ejemplo completo en [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md) y el código en `guias/pokedex/`. Agreguen `sqlalchemy` a `requirements.txt`.

**Lo que hay:** `trabajo_integrador_1.py` con un router y un modelo. ⚠️ El código **no arranca**.

**A corregir**
- Los imports están mal escritos: es `from fastapi import APIRouter` (no `fastapis`). Y `pydantic` ya no va: los datos se validan a mano y las tablas son clases de SQLAlchemy (ver guía).
- `APIRouter(predix=...)` es `prefix`.
- El archivo está adentro de una carpeta llamada `trabajo_integrador.py`. El archivo principal va en la raíz y se llama `main.py`.
- Para este tamaño de proyecto no hace falta `APIRouter`: alcanza con los endpoints en `main.py`.
- En Python las clases se escriben con mayúscula: `class Venta(Base)` (heredando de la `Base` de SQLAlchemy, ver guía).

**Próximos pasos**
1. Ordenar los archivos y probar que levante con `uvicorn main:app --reload`.
2. `seed.py` con las 3 tablas: `productos`, `ventas` (con `producto_id`) y `egresos`.

**Sobre el tema:** este proyecto no maneja stock, eso es de TiendaDB. Acá lo importante es el cierre de caja: total vendido, total por medio de pago, egresos y saldo del día.

## 24/09

**📌 Criterio de nombres.** Variables, funciones y clases en **inglés**; tablas, columnas y rutas como en el alcance; comentarios en inglés para la entrega final. Está detallado arriba en *Reglas comunes* y la guía ya lo aplica.

**Lo que hay:** borraron `trabajo_integrador_1.py` y subieron dos archivos nuevos: `control_de_pedidos.py/main.py` (Benjamín) y `cierredecaja.py/trabajo.py` (Ignacio). Hay commits de los dos 👍, pero **ninguno de los dos archivos corre** y ninguno está donde tiene que estar.

**Estructura del repo**
- Sigue sin haber `main.py` en la raíz. Las dos carpetas se llaman con `.py` al final (`control_de_pedidos.py/`, `cierredecaja.py/`): una carpeta no lleva extensión. Borren las carpetas y dejen `main.py` y `seed.py` en la raíz.
- El README está vacío.

**`cierredecaja.py/trabajo.py`**
- Parece pegado desde un chat: hay líneas cortadas a la mitad (`from fastapi import FastAPI,` y `HTTPException` en la línea siguiente), flechas `→` en vez de `->`, `true` en vez de `True`, `from enum import enum` en vez de `Enum`, `=` en vez de `==` en los `where`, un `;` en el `with`, y un `)` de más. Nada de eso lo entiende Python.
- Usa **SQLModel**, que no es lo que se pide. La base va con **SQLAlchemy** (ver [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md)).
- La tabla `cierre` con turno, cigarrillos, gas y markup no es el alcance. Las tablas son `productos`, `ventas` (con `producto_id`) y `egresos`. El cierre de caja **no se guarda**: se calcula en `GET /caja/cierre?fecha=` sumando ventas y egresos del día.

**`control_de_pedidos.py/main.py`**
- Va por el lado correcto: usa `create_engine` y `sessionmaker` de SQLAlchemy 👍. Pero importa `schemas.pedidos_schema`, que no existe en el repo, así que rompe en la primera línea. Y `APIRouter` no hace falta (ya lo dije el 23/09).
- La guía muestra la forma más simple: `Session(engine)` directo, sin `sessionmaker` ni `get_db`. Sigan ese ejemplo.
- "Control de pedidos" tampoco es el tema: es cierre de caja.

**Próximos pasos**
1. Un solo `main.py` en la raíz que levante con `uvicorn main:app --reload` y abra `/docs`. Escríbanlo a mano, de a poco, probando cada vez.
2. `seed.py` con SQLAlchemy: `productos`, `ventas` (con `producto_id` y `medio_pago`) y `egresos`, ~10 registros por tabla.
3. `requirements.txt` con `fastapi`, `uvicorn`, `uvicorn-worker`, `gunicorn`, `sqlalchemy`.
