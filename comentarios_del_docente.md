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
- Datos en **SQLite**. Pueden usar **SQLAlchemy** (ORM, con la guía [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md)) o **`sqlite3` con SQL directo**: las dos formas valen. **Pydantic es opcional**: el cuerpo del `POST` se puede validar con un modelo de Pydantic (`class StudentIn(BaseModel)`) o a mano en `validation.py`. Las dos formas valen.
- Repositorio en GitHub con commits de **todos** los integrantes.
- **Demo local:** la API se corre en la notebook de cada grupo con `uvicorn`. No hace falta desplegarla en la web (ver *Demo local*, abajo).

### Nombres en el código (criterio acordado con la cátedra de Inglés)

> **Actualizado el 15/10:** los nombres de tablas, columnas y rutas en inglés pasan a ser una **recomendación**. Si quedan en español, no es un error.

- **Variables, funciones y clases en inglés**: `list_students`, `get_session`, `class Student(Base)`.
- **Tablas, columnas, rutas y query params:** se recomienda que también vayan en inglés (`__tablename__ = "students"`, columna `career_id`, ruta `GET /students`), pero pueden quedar en español, como figuran en el alcance.
- Lo que sí es obligatorio: usar **el mismo nombre en todos los archivos** (`models.py`, `seed.py`, `crud.py`, `main.py`, `validation.py`). Si la tabla se llama `estudiantes` en el seed, se llama `estudiantes` en todos lados.
- **Documentación en inglés**: `README.md`, docstrings y los mensajes que devuelve la API.
- **Comentarios**: pueden estar en español mientras desarrollan, pero para la **entrega final** tienen que estar en inglés.

### Demo local (sin despliegue)

> **Actualizado el 15/10:** no se despliega a producción. La defensa es **local**, en la notebook del grupo.

`requirements.txt` debe incluir:
```
fastapi
uvicorn
python-dotenv
```
y `sqlalchemy` si lo usan.

Para levantar el proyecto desde cero (lo mismo tiene que estar en el README):
```
python -m venv venv
venv\Scripts\activate          (en Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```
Y abrir http://127.0.0.1:8000/docs.

- El seed se corre **una vez, antes** de levantar el servidor. No va adentro de `main.py`.
- Antes de la defensa, prueben todo esto en la notebook con la que van a presentar.

### Base de datos
- **3 tablas**, cada una con clave primaria (`id`).
- Al menos **1 relación** entre tablas (clave foránea, ej. `equipo_id`).
- **Algunos datos de ejemplo** en cada tabla, los suficientes para ver funcionar los endpoints. No hay mínimo ni máximo. Siempre **datos ficticios**.
- Recomendación: que los datos permitan ver los filtros en acción, por ejemplo productos de varias categorías, para que `?category=` devuelva algo distinto de la lista completa.
- Un script de carga inicial `seed.py` que crea las tablas (con `create_all` o con `CREATE TABLE IF NOT EXISTS`) y carga los datos **solo si la base está vacía**. Se ejecuta antes de levantar el servidor y, si se corre dos veces, no duplica nada.
- El archivo `.db` **puede estar en el repo**. Si lo suben, que esté actualizado (el que genera el seed actual).

### Seguridad: TODOS los endpoints van protegidos

> **Actualizado el 15/10:** se **recomienda** guardar la clave en una variable de entorno en lugar de escribirla en el código. No es obligatorio; en la defensa se puede preguntar por qué conviene hacerlo.

- Todos los endpoints piden la API key en el encabezado `X-API-Key`.
- Sin clave o con clave incorrecta → **401**. Con la clave correcta → **200** y los datos.
- **Recomendado:** guardar la clave en un archivo **`.env`** que **no se sube** (va en el `.gitignore`) y leerla con `python-dotenv`. Al repo se sube un **`.env.example`** con el nombre de la variable y sin el valor. Paso a paso en [guias/variables_de_entorno.md](guias/variables_de_entorno.md). Si la dejan como constante en `security.py`, también vale.
- Los datos son todos **ficticios**: esta API no se usa para nada real.

`security.py` con la clave en el `.env` (la forma recomendada):

```python
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv()
API_KEY = os.getenv("API_KEY")
header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Depends(header)):
    if API_KEY is None or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

Y en `main.py` se protege toda la app de una vez:

```python
app = FastAPI(dependencies=[Depends(verify_api_key)])
```

En `/docs` usá el botón **Authorize** para cargar la clave y probar.
---

## Nivel A — obligatorio (igual para todos)

Cada grupo implementa **exactamente estos 6 endpoints**, adaptados a su tema (ver *Alcance de este grupo*):

| # | Tipo | Ejemplo genérico | Qué practica |
|---|---|---|---|
| 1 | Listado con filtro | `GET /cosas?campo=valor` | Query param y filtro en la consulta |
| 2 | Detalle | `GET /cosas/{id}` | Path param, **404** si no existe |
| 3 | Relación | `GET /cosas/{id}/otras` | Cruzar dos tablas por la clave foránea |
| 4 | Segundo listado con filtro | `GET /otras?campo=valor` | Query param sobre otra tabla |
| 5 | Calculado | `GET /resumen` | Contar, sumar o agrupar (en Python o en la consulta) |
| 6 | Alta | `POST /cosas` | Recibir el cuerpo (con un modelo de Pydantic o como `dict` validado a mano), rechazar los datos inválidos con **400** o **422**, e insertar en la base |

Además, en Nivel A:
- **Errores:** 401 (sin clave), 404 (no existe), y la API no se cae si la base no está o falla una consulta (`try/except`).
- **Filtros opcionales:** si no se manda el query param, devuelve todo.
- **Seguridad (recomendado):** API key en variable de entorno (`.env`) en lugar de escrita en el código.
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
2. Video demo (máx. 5 min): endpoints funcionando con clave, y un pedido **sin** clave mostrando el 401.
3. Defensa oral el **miércoles 28/10**: demo en vivo desde `/docs`, en local, y preguntas sobre el código. El repositorio tiene que estar al día el **miércoles 21/10**.

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

## 08/10

**📌 Cambio de criterio: todo en inglés.** Ahora también las **tablas, columnas, rutas y query params** van en inglés, igual que el README, los docstrings y los mensajes de la API. Reemplaza lo dicho el 24/09; está detallado arriba en *Nombres en el código*. El alcance sigue listando los nombres en español solo como referencia.

**📌 Guía nueva (opcional):** [guias/variables_de_entorno.md](guias/variables_de_entorno.md), para sacar la clave del código con un `.env`.

**Lo que hay:** un salto enorme. 👍 Probé la API y **los 6 endpoints funcionan**: `GET /productos` con filtro, `GET /ventas/{id}` y `GET /productos/{id}/ventas` con su 404, `GET /egresos`, `GET /caja/cierre` (para el 2026-09-10 da 18.800 vendido, 14.000 de egresos y saldo 4.800) y `POST /egresos`. Sin clave o con clave mala responde 401. El seed carga 15 + 15 + 14 registros y no duplica si se corre dos veces. `main.py` y `seed.py` están en la raíz, `requirements.txt` está bien y hay commits de los dos.

**⚠️ Tienen que poder explicar todo lo que está escrito.** El 24/09 ninguno de los dos archivos corría; ahora hay código con `APIKeyHeader`, `relationship(back_populates=...)`, `ilike` y `async def` con `await request.json()`, que no vimos en clase. No está mal usarlo, pero:
- Si usaron IA, **declárenlo en el README**: es parte del alcance.
- En la defensa les voy a preguntar por esas líneas a los dos. Si no pueden explicar qué hace una, reemplácenla por la forma que vimos en la guía.

**A corregir en `main.py`**
- **Nombres en inglés** (criterio nuevo). Las clases y funciones ya están bien; faltan tablas, columnas y rutas:

  | Hoy | Tiene que ser |
  |---|---|
  | tablas `productos`, `ventas`, `egresos` | `products`, `sales`, `expenses` |
  | columnas `nombre`, `categoria`, `precio`, `fecha`, `cantidad`, `medio_pago`, `concepto`, `monto`, `producto_id` | `name`, `category`, `price`, `date`, `quantity`, `payment_method`, `concept`, `amount`, `product_id` |
  | `GET /productos?categoria=` | `GET /products?category=` |
  | `GET /ventas/{id}` · `GET /productos/{id}/ventas` | `GET /sales/{id}` · `GET /products/{id}/sales` |
  | `GET /egresos?fecha=` · `POST /egresos` | `GET /expenses?date=` · `POST /expenses` |
  | `GET /caja/cierre?fecha=` | `GET /cash/closing?date=` |

  También los docstrings y los mensajes de error. Como cambian los nombres de las tablas, borren `kiosko.db` y vuelvan a correr el seed.
- El `POST /egresos` acepta cosas que no debería. Probé y entraron las dos:
  - `"monto": true` se guarda como `1.0`. Hay que descartar los booleanos: `isinstance(monto, bool)`.
  - `"fecha": "cualquiera"` se guarda tal cual. Validen el formato con `date.fromisoformat(fecha)` adentro de un `try/except ValueError`.
- Falta el `try/except` para que la API no se caiga si la base no está o falla una consulta.
- Todo está en un solo archivo. Funciona, pero queda más claro separar las clases y el `engine` en `db.py`, como en la guía. Hoy `seed.py` tiene que importar `main.py` para conseguir las tablas.

**A corregir en el repo**
- `kiosko.db` está subido. Agreguen `*.db` al `.gitignore` y sáquenlo con `git rm --cached kiosko.db`.
- El **README está vacío**. Tiene que explicar (en inglés) qué hace la API, los 6 endpoints, cómo usar la clave, cómo correrla y la declaración de uso de IA.
- Los mensajes de commit tienen que decir qué se hizo. Los 17 commits de esta semana se llaman "avance", "casi lito", "control_de_pedidos" o el nombre de un archivo.
- Modificaron los imports de `guias/pokedex/`. Esa carpeta es material de la cátedra: déjenla como estaba.

**Próximos pasos**
1. Pasar tablas, columnas, rutas, docstrings y mensajes a inglés. Probar los 6 endpoints de nuevo en `/docs`.
2. Arreglar las dos validaciones del `POST` y agregar el `try/except`.
3. Sacar `kiosko.db` del repo y escribir el README.
4. **Desplegar en Render.** Ya tienen todo para hacerlo; no lo dejen para el final.

## 15/10

**📌 Cambios en las reglas** (están arriba, en *Reglas comunes*):
- **SQLAlchemy es opcional:** también vale `sqlite3` con SQL directo.
- **No hay que desplegar.** La defensa es **local**, en su notebook, el **miércoles 28/10**. El repo tiene que estar al día el **miércoles 21/10**.
- **Recomendado:** la API key en una variable de entorno (`.env`) en lugar de escrita en el código. No es obligatorio, pero en la defensa se puede preguntar dónde está la clave y por qué conviene sacarla del código.

**Lo que hay:** pasaron todo a inglés (tablas, columnas, rutas y mensajes), separaron el código en `db.py`, `crud.py`, `security.py` y `seed.py`, y escribieron el README con la declaración de IA. 👍 El seed sigue cargando bien y sin duplicar.

**⚠️ Hoy la API no tiene ningún endpoint.** En `main.py`, todo el código entre la línea 7 y la 109 quedó **adentro de un string** (`'''` al principio y al final). Python lo toma como texto, así que FastAPI no registra ninguna ruta: todas dan 404. El 08/10 los seis funcionaban.

Además, `main.py` no importa nada de lo que separaron: ni `engine`, ni los modelos, ni los `*_to_dict`, ni `verify_api_key`. La clave no se aplica en ningún lado.

**Lo probé sacando los `'''` y agregando los imports.** Aparecen estos errores, que hay que arreglar igual:
- `GET /products/{id}/sales` da 500: usa `product.sales`, pero `Product` ya no tiene la `relationship`. Agréguenla en `db.py` o filtren con `select(Sale).where(Sale.product_id == id)`.
- `GET /cash-closing` da 500 cuando hay ventas: suma `s.amount`, y la columna de `Sale` es `total`.
- El desglose por medio de pago da siempre 0: el seed guarda `efectivo`, `debito` y `transferencia`, y el cierre busca `cash`, `debit` y `transfer`. Usen los mismos valores en los dos lados.
- `POST /expenses` da 500 con datos válidos: crea `Expense(concept=...)`, pero la columna es `description`.
- Siguen pendientes los dos puntos del 08/10: el `POST` acepta `"amount": true` y cualquier texto como fecha.
- No hay `try/except` en ningún endpoint.

**Lo que falta para la entrega del 21/10**
1. Sacar los `'''`, importar lo necesario y proteger la app con `FastAPI(dependencies=[Depends(verify_api_key)])`. Probar el 401.
2. Arreglar los cuatro errores de arriba y las dos validaciones del `POST`.
3. `try/except` en las consultas.
4. README: los números del ejemplo del cierre no coinciden con el seed, `?category=beverages` no existe en los datos (están en español) y el texto está sin formato Markdown.

**Recomendación:** pasar la clave a un `.env` (ver *Seguridad*, arriba, y [guias/variables_de_entorno.md](guias/variables_de_entorno.md)). No es obligatorio, pero en la defensa se puede preguntar dónde está la clave y por qué conviene sacarla del código.

**⚠️ Commits.** Los 10 commits de esta semana son de la misma cuenta y se llaman "avance" o "casi listo". Vélez no tiene commits desde el 08/10. Si trabajan juntos en una compu, pónganlo en el mensaje: `"Fix cash closing totals (pair coding with Ignacio)"`. En la defensa la nota es grupal y a cualquiera de los dos le pueden pedir que explique cualquier parte.

Antes de cada commit: `uvicorn main:app --reload`, abrir `/docs` y probar. Esta regresión se hubiera visto en un minuto.

> En el commit `4b623b8` se modificó sin querer una línea de la devolución del 08/10. Ya la restauré.

## 21/10 (entrega)

**Lo que hay:** un solo commit desde el 15/10 (Ignacio, "savage"), que agrega en `db.py` la `relationship` entre `Product` y `Sale`. Está bien hecho y arregla `GET /products/{id}/sales`. 👍

**⚠️ La API sigue sin endpoints.** `main.py` no cambió: el código entre las líneas 7 y 109 sigue **adentro de un string `'''`**, así que FastAPI no registra ninguna ruta. Todas dan 404, y la clave no se aplica porque `main.py` no importa `security.py`. Tal como está, en la defensa no hay nada que mostrar en `/docs`.

**Lo mínimo para tener la demo andando el 28/10**, en este orden:
1. **Sacar los dos `'''`** de `main.py` y agregar arriba los imports de lo que usa: `engine`, los modelos, los `*_to_dict` y `verify_api_key`. Proteger la app con `FastAPI(dependencies=[Depends(verify_api_key)])`. Con eso ya andan los endpoints 1 a 4, con sus 404.
2. **Cierre de caja:** cambiar `s.amount` por `s.total` (líneas 53 y 57-59) y usar en el filtro los mismos medios de pago que el seed (`efectivo`, `debito`, `transferencia`). Hoy da 500.
3. **`POST /expenses`:** la columna se llama `description`, no `concept` (línea 102). Hoy da 500 con datos válidos. De paso, rechacen los booleanos en `amount` y validen el formato de la fecha.
4. **`try/except`** en las consultas.
5. **README:**
   - Los números del ejemplo del cierre no coinciden con el seed. Para el 2026-09-10 son: 18.800 vendido, 9.500 de egresos y saldo de 9.300.
   - `?category=beverages` no existe: los datos dicen `bebidas`.
   - Donde dice `concept` es `description`.

**Commits.** Desde el 08/10, todos los commits salvo este último son de la cuenta de Rosso. Si trabajan juntos, aclárenlo en el mensaje (*pair coding*). En la defensa la nota es grupal y les vamos a preguntar a los dos.

Antes de la defensa, levanten la API con `uvicorn main:app --reload` y prueben los 6 endpoints en `/docs`, en la notebook con la que van a presentar.
