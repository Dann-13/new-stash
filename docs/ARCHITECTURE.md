# Arquitectura

## Principio central: capas separadas

El flujo de datos es unidireccional. Cada capa conoce solo a la de abajo.

```
opencode.db (SQLite, solo lectura)
        │
        ▼
   data/            puro: conexión + queries + dataclasses. SIN Textual.
        │
        ▼
   app.py           orquesta: lee datos, decide qué mostrar, refresca.
        │
        ▼
   widgets/         solo renderizan lo que app.py les entrega.
        │
        ▼
   styles/app.tcss  presentación (colores, tamaños, layout).
```

`providers/` es una rama aparte: habla con APIs externas (DeepSeek) y devuelve
dataclasses. `i18n.py`, `format.py`, `export.py` y `pricing.py` son utilidades
puras transversales.

## Mapa de módulos

```
src/opencode_usage/
  __main__.py        CLI: argparse, carga Settings, fija idioma, lanza la app.
  app.py             UsageApp(App): compose, bindings, refresh, acciones.
  config.py          Settings (frozen) + load_settings() desde config.toml.
  i18n.py            catálogos es/en, t(), set_language(), resolve_language().
  format.py          format_tokens (B/M/K), format_cost ($), format_percent.
  pricing.py         tabla de precios USD/1M tokens + estimate().
  export.py          export_csv / export_markdown (puro, recibe datos calculados).
  data/
    db.py            open_readonly(): file: URI mode=ro. Nunca escribe.
    models.py        dataclasses frozen de datos (TokenTotals, DayTokens, ...).
    queries.py       load_messages + agregaciones puras (totals, by_model, ...).
  providers/
    deepseek.py      fetch_balance(): GET HTTPS /user/balance, errores seguros.
  widgets/
    stat_card.py     tarjeta label/valor/sub.
    tokens_by_day.py barras apiladas por día + línea de costo.
    heatmap.py       7×24 coloreado por intensidad.
    models_table.py  DataTable de modelos.
    agents_table.py  DataTable de agentes.
    budget_bar.py    barra de presupuesto mensual.
    session_live.py  línea de la sesión más reciente.
    provider_panel.py línea de saldo DeepSeek (oculta sin clave).
  styles/app.tcss    tema oscuro, layout, tamaños.
```

## Fuente de datos

Tabla `session_message` con `type='assistant'`. La columna `data` (JSON) trae por
mensaje: `model{id,providerID}`, `agent`, `tokens{input,output,reasoning,cache{read,write}}`,
`cost`, `time{created}` (ms epoch). Los mensajes sin `tokens` se ignoran.

Las tablas `session` / `session_v2` guardan agregados por sesión, pero la fuente
elegida es `session_message` porque da granularidad por día, hora y modelo.

## Reglas de dependencia

- `data/` NO importa Textual ni widgets. Debe poder testearse sin UI.
- `widgets/` NO leen la base ni calculan agregaciones; reciben datos ya hechos.
- `app.py` es el único punto que une datos con widgets.
- `providers/` no importa widgets; devuelve datos o lanza errores con clave i18n.
- Las utilidades (`i18n`, `format`, `pricing`, `export`) no importan app ni widgets.

## Rendimiento

`UsageApp.refresh_data(force=False)` calcula un fingerprint de `opencode.db` y
`opencode.db-wal` (mtime_ns + tamaño). Si no cambió y pasaron < 60 s, no hace nada.
Cada 60 s recalcula igual para que la ventana de días avance. `r` y los rangos
fuerzan recálculo. Cualquier feature nueva debe respetar este esquema: nada de
releer o recalcular en cada tick si no hay cambios.
