# Convenciones de código

## Idioma

- **Identificadores** (variables, funciones, clases, claves i18n): inglés.
- **Docstrings y comentarios**: español.
- **Documentación** (README, docs/, CHANGELOG): español.
- Los textos que ve el usuario final van por `i18n.t()`, nunca hardcodeados.

## Python

- Objetivo: **Python ≥ 3.11** (Debian 12 trae 3.11; Ubuntu 24.04, 3.12).
- `from __future__ import annotations` al inicio de cada módulo.
- Type hints en todas las firmas públicas. `X | None` en vez de `Optional[X]`.
- Datos inmutables: `@dataclass(frozen=True)`. Nada de estado global mutable salvo
  el idioma de `i18n` (fijado una vez al arrancar).
- Funciones cortas, una responsabilidad. Si una función crece, extrae helpers.
- Nombres descriptivos. Sin abreviaturas inventadas (`cfg`, `impl`, `fn` no).
- Sin efectos secundarios ocultos: las funciones de `data/` y `export.py` son puras.

## Estilo y formato

- `ruff` es la única fuente de verdad de formato/lint.
  - `line-length = 88`, `target-version = "py311"`.
  - Reglas: `E, F, W, I, B, UP` (pycodestyle, pyflakes, isort, bugbear, pyupgrade).
- Corre `ruff check src tests` antes de commitear. Debe quedar limpio.
- Imports ordenados por ruff (isort): stdlib, terceros, locales.
- Strings: comillas dobles. Colores siempre en **hex** (`#58a6ff`); el parser de
  rich/Textual no acepta nombres como `grey18` o `deepskyblue3`.

## Textual

- Estilos en `styles/app.tcss`, no en Python, salvo colores de render dinámico.
- Los widgets exponen un método `set_*` que recibe datos y llama `refresh()` o
  `update()`. No leen la base.
- **Bindings:** no uses `BINDINGS` de clase si la descripción debe traducirse.
  Enlaza en `on_mount` con `self.bind(key, action, description=t(...))`.
  (En Textual, `BindingsMap` toma el primer binding por tecla; el de clase gana
  sobre los añadidos después, así que la clase debe quedar vacía.)
- Workers de red: `@work(thread=True, exclusive=True, group=...)` y
  `call_from_thread` para tocar la UI. La UI nunca espera la red.

## Datos y SQL

- Conexión siempre con `db.open_readonly()` (file: URI `mode=ro`). Nunca escribir.
- Usa `Path.resolve().as_uri()` para construir la URI: soporta espacios y `#`.
- Consultas parametrizadas (`?`), nunca interpolación de strings.
- Timestamps en ms epoch. Conversión a día/hora local con `datetime.fromtimestamp`.

## Errores

- Mensajes de error visibles: clave i18n + `t()`. Nunca incluyas secretos.
- En `providers/`, usa `raise ... from None` para no encadenar trazas que puedan
  contener la clave.
- La app no debe caerse ante config rota o red caída: degrada con aviso.

## Dependencias

- Stdlib primero. Hoy la única dependencia de runtime es `textual`.
- Añadir una dependencia requiere justificación (qué resuelve que stdlib no).
- Dev: `pytest`, `pytest-asyncio`, `ruff`.
