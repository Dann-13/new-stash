# Desarrollo

## Setup

```bash
# Linux (Debian / Ubuntu)
sudo apt install python3 python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Alternativa Linux con `pipx`: `pipx install -e /ruta/a/opencode-usage`.

## Correr

```bash
opencode-usage                 # o: python -m opencode_usage
opencode-usage --lang en       # inglés
opencode-usage --days 7        # ventana inicial
opencode-usage --db /ruta/opencode.db --refresh 10
```

Teclas: `1/2/3/4` rangos 7/30/90/todo, `r` refrescar, `e` exportar, `q` salir.

## Configuración del usuario

`config.toml` en `%APPDATA%\opencode-usage\` (Windows) o
`~/.config/opencode-usage/` (Linux, respeta `XDG_CONFIG_HOME`):

```toml
language = "auto"            # es | en | auto
monthly_budget_usd = 20.0    # opcional; ausente = sin presupuesto
```

Valores inválidos se ignoran y se avisa al arrancar; la app no se cae.

## Versionado y releases

- Semántico: `MAJOR.MINOR.PATCH`. Cada fase de features sube MINOR.
- Al cambiar versión, actualiza **tres** sitios a la vez:
  `pyproject.toml`, `src/opencode_usage/__init__.py` (`__version__`) y una entrada
  nueva en `CHANGELOG.md` (arriba, en español).
- Historial: 0.1.0 MVP · 0.2.0 costo/presupuesto/sesión/export/CI ·
  0.3.0 DeepSeek · 0.4.0 i18n.

## Commits y push

- Conventional Commits: `feat:`, `fix:`, `perf:`, `docs:`, `test:`, `chore:`.
- Mensaje en español, imperativo, una línea de intención.
- **No hagas `git push` sin aprobación explícita del usuario.**
- El CI (4 jobs) corre al push; espera a que quede verde antes de dar por cerrado.

## Cierre de una fase

1. `ruff check src tests` limpio.
2. `pytest -q` verde (con tests nuevos para lo añadido).
3. Smoke de la app.
4. README + CHANGELOG + docs actualizados.
5. Commit. Push solo con visto bueno.

## Roadmap

Hecho: Fase 1 (MVP), optimización + Linux, Fase A (funcional), Fase B (DeepSeek),
i18n.

**Fase C (v0.5.0), pendiente:**

| Feature | Nota |
|---|---|
| Top sesiones / proyectos | datos ya existen; query nueva de ranking. |
| Comparador de modelos | costo por 1K tokens output; tabla derivada. |
| Tokens/min sparkline | requiere muestreo en vivo (ritmo de consumo). |
| Tendencia de caché | % cache hit por día, línea de tendencia. |
| `--compact` | vista mínima para terminales chicas. |
| Temas | claro/oscuro u otros, vía `.tcss`. |

Orden sugerido: top sesiones + comparador primero (fáciles, datos presentes),
luego tokens/min (muestreo), después compact y temas.

## Principios al añadir features

- Respeta las capas (`docs/ARCHITECTURE.md`): query pura en `data/`, widget que
  solo muestra, conexión en `app.py`.
- Todo texto por `i18n.t()` (`docs/I18N.md`).
- No rompas el fingerprint de refresco: nada de recalcular sin cambios.
- Cada función nueva con test (`docs/TESTING.md`).
- Sin dependencias nuevas sin justificar.
