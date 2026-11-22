# Tests y CI

## Regla

**Cada función nueva lleva test.** Una fase no cierra si `pytest` o `ruff` fallan.

## Correr en local

```bash
ruff check src tests     # lint, debe quedar limpio
pytest -q                # toda la suite
```

## Cómo están organizados

```
tests/
  conftest.py          fixture `con` (SQLite :memory: con session_message) +
                       helper _msg(); fixture autouse que resetea el idioma a es.
  test_queries.py      agregaciones puras (totals, by_day, heatmap, by_model...).
  test_db.py           apertura solo lectura, rutas con espacios y #.
  test_features.py     costo diario, presupuesto, sesión, config, export.
  test_i18n.py         paridad de claves, t(), resolve_language, export en inglés.
  test_deepseek.py     parseo, Bearer, errores seguros (nunca filtran la clave).
  test_provider_panel.py  panel oculto sin clave, saldo y error con mock.
  test_app.py          app Textual con run_test(): presupuesto, footer en inglés.
```

## Patrones

- **Datos:** usa la fixture `con` y `_msg()` para insertar mensajes assistant.
  No dependas de la base real del usuario.
- **UI:** `async with app.run_test() as pilot:` + `await pilot.pause()`.
  Para workers: `await app.workers.wait_for_complete()`.
- **Red:** nunca llames a la API real. Mockea `urllib.request.urlopen` o
  `deepseek.fetch_balance` con `unittest.mock.patch`.
- **Idioma:** el defecto es `es`. Para probar inglés, `set_language("en")` dentro
  del test; el fixture autouse lo restaura.
- **Footer traducido:** lee `app.active_bindings`; la descripción está en
  `ab.binding.description`.

## CI (GitHub Actions)

`.github/workflows/ci.yml` corre en cada push y pull_request:

- Matrix: `ubuntu-latest` y `windows-latest` × Python `3.11` y `3.12` (4 jobs).
- Pasos: checkout, setup-python, `pip install -e ".[dev]"`, `ruff check`, `pytest`.

El CI es la prueba de que funciona en Linux. Debian no se prueba aparte; Ubuntu
sirve de proxy (misma familia, Python 3.11+).

## Smoke manual

Hay scripts de humo en el directorio temporal del entorno (no en el repo):
arrancan la app con `run_test`, verifican tarjetas y tablas, y pulsan teclas.
Úsalos tras cambios grandes de UI. No forman parte de la suite.
