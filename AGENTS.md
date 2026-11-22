# AGENTS.md

Guía para agentes de IA (y humanos) que trabajan en este repo. Léela antes de
cambiar código. El detalle vive en `docs/`.

## Qué es

`opencode-usage`: dashboard 100% terminal (Textual) que mide el uso de tokens de
OpenCode. Lee `opencode.db` en **solo lectura**. No escribe en la base, no envía
telemetría. La única conexión de red opcional es el saldo de DeepSeek.

## Reglas que no se rompen

1. **Capas separadas.** `data/` es puro (SQLite + agregaciones, sin UI).
   `widgets/` solo muestran. `app.py` conecta. `providers/` habla con APIs.
   No metas lógica de negocio en widgets ni imports de Textual en `data/`.
2. **Todo texto visible pasa por `i18n.t()`.** Nunca hardcodees un string de UI.
   Añade la clave a los dos catálogos (`es` y `en`) en `src/opencode_usage/i18n.py`.
   Ver `docs/I18N.md`.
3. **Rendimiento.** No recalcules ni releas la base si no cambió. El refresco usa
   un fingerprint (mtime + tamaño de `opencode.db` y su `-wal`). Respétalo.
4. **Seguridad.** La clave de DeepSeek solo llega por `DEEPSEEK_API_KEY`. Nunca la
   guardes, imprimas, registres ni incluyas en errores. Solo HTTPS. Ver
   `docs/SECURITY.md`.
5. **Sin dependencias nuevas** sin justificarlo. Stdlib primero. Hoy solo `textual`.
6. **Cada función nueva lleva test.** `pytest` y `ruff` deben quedar verdes.
7. **Idioma del código:** identificadores en inglés, docstrings y comentarios en
   español. Docs en español.

## Estilo rápido

- Python ≥ 3.11. `from __future__ import annotations` en cada módulo.
- Dataclasses `frozen=True` para datos. Type hints en firmas públicas.
- Funciones cortas, una responsabilidad. Nombres claros, sin abreviaturas inventadas.
- `ruff` con `line-length = 88`, reglas `E,F,W,I,B,UP`. Pásalo antes de commitear.
- Colores en hex (`#58a6ff`), no nombres como `grey18` (el parser no los acepta).

## Flujo de trabajo

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check src tests
pytest -q
```

- Commits: Conventional Commits (`feat:`, `fix:`, `perf:`, `docs:`, `test:`).
- Versionado semántico en `pyproject.toml` + `__init__.py` + entrada en `CHANGELOG.md`.
- **No hagas `git push` sin aprobación explícita del usuario.** El CI corre al push.
- Cada fase cierra con: pytest verde + ruff limpio + smoke + README/CHANGELOG + commit.

## Dónde mirar

| Tema | Archivo |
|---|---|
| Estructura y capas | `docs/ARCHITECTURE.md` |
| Estilo y convenciones | `docs/CONVENTIONS.md` |
| Traducciones / i18n | `docs/I18N.md` |
| Tests y CI | `docs/TESTING.md` |
| Seguridad y privacidad | `docs/SECURITY.md` |
| Setup, versiones, roadmap | `docs/DEVELOPMENT.md` |
