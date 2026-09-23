# Comentarios de la cátedra

Informática (TDS05) · Proyecto Integrador · UM Río Cuarto

Acá va la devolución de cada revisión semanal. Léanlo antes de seguir programando.
El alcance completo del grupo está en el documento de alcances.

**Grupo:** Benjamín Rosso, Ignacio Vélez
**Tema:** Cierre de caja

---

## 23/09

**Lo que hay:** `trabajo_integrador_1.py` con un router y un modelo. ⚠️ El código **no arranca**.

**A corregir**
- Los imports están mal escritos: es `from fastapi import APIRouter` y `from pydantic import BaseModel` (no `fastapis`, `pidantyc` ni `basemodel`).
- `APIRouter(predix=...)` es `prefix`.
- El archivo está adentro de una carpeta llamada `trabajo_integrador.py`. El archivo principal va en la raíz y se llama `main.py`.
- Para este tamaño de proyecto no hace falta `APIRouter`: alcanza con los endpoints en `main.py`.
- En Python las clases se escriben con mayúscula: `class Venta(BaseModel)`.

**Próximos pasos**
1. Ordenar los archivos y probar que levante con `uvicorn main:app --reload`.
2. `seed.py` con las 3 tablas: `productos`, `ventas` (con `producto_id`) y `egresos`.

**Sobre el tema:** este proyecto no maneja stock, eso es de TiendaDB. Acá lo importante es el cierre de caja: total vendido, total por medio de pago, egresos y saldo del día.

**Endpoints a entregar (Nivel A)**
- [ ] `GET /productos?categoria=bebidas`
- [ ] `GET /ventas/{id}` (404 si no existe)
- [ ] `GET /productos/{id}/ventas`
- [ ] `GET /egresos?fecha=2026-09-10`
- [ ] `GET /caja/cierre?fecha=2026-09-10` (total, por medio de pago, egresos y saldo)
- [ ] `POST /egresos`
- [ ] Todos protegidos con `X-API-Key` (clave como constante en `main.py`)
