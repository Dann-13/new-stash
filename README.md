# opencode-usage

Dashboard en terminal (100% TUI) que mide tu uso de tokens de OpenCode:
tokens por modelo, por agente, por día, heatmap de actividad, costo,
ranking de sesiones, comparador de modelos y tendencia de caché.

Lee en modo solo lectura la base de datos local de OpenCode
(`~/.local/share/opencode/opencode.db`). No escribe nada.

## Documentación

Las convenciones del proyecto viven en [`docs/`](docs/) y en
[`AGENTS.md`](AGENTS.md) (guía de entrada para agentes de IA y humanos).
Léelas antes de cambiar código:

| Tema | Archivo |
|---|---|
| Estructura y capas | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Estilo y convenciones | [docs/CONVENTIONS.md](docs/CONVENTIONS.md) |
| Traducciones / i18n | [docs/I18N.md](docs/I18N.md) |
| Tests y CI | [docs/TESTING.md](docs/TESTING.md) |
| Seguridad y privacidad | [docs/SECURITY.md](docs/SECURITY.md) |
| Setup, versiones, roadmap | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |

## Requisitos

- Python 3.11+
- OpenCode instalado (para tener datos)

## Instalación en Linux (Debian / Ubuntu)

Debian y Ubuntu bloquean `pip` global, así que se usa un entorno virtual:

```bash
sudo apt install python3 python3-venv
cd opencode-usage
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Alternativa con `pipx` (instala el comando en el sistema sin tocar Python global):

```bash
sudo apt install pipx
pipx install -e /ruta/a/opencode-usage
```

## Instalación en Windows

```powershell
cd opencode-usage
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Uso

Linux:

```bash
.venv/bin/opencode-usage
# o
.venv/bin/python -m opencode_usage
```

Windows:

```powershell
.\.venv\Scripts\opencode-usage.exe
```

Ruta de la base: `$XDG_DATA_HOME/opencode/opencode.db` (por defecto `~/.local/share/opencode/opencode.db` en Linux, y `%USERPROFILE%\.local\share\opencode\opencode.db` en Windows).

Rendimiento: la app solo relee la base cuando cambia `opencode.db` o su `-wal`. Con OpenCode quieto, consume casi nada de CPU.

Opciones:

```text
--db RUTA        ruta a opencode.db (default: ~/.local/share/opencode/opencode.db)
--refresh SEG    segundos entre revisiones de cambios (default: 5)
--days N         ventana inicial en días: 7, 30, 90 o 0 = todo (default: 30)
--lang es|en     idioma de la interfaz (default: config.toml o auto)
--export-dir RUTA  carpeta destino del export (default: config.toml o la actual)
```

Atajos:

| Tecla | Acción            |
|-------|-------------------|
| `1`   | ventana 7 días    |
| `2`   | ventana 30 días   |
| `3`   | ventana 90 días   |
| `4`   | todo el histórico |
| `r`   | refrescar ya      |
| `e`   | exportar CSV y Markdown (elige la carpeta en un diálogo) |
| `q`   | salir             |

## Configuración (opcional)

Archivo `config.toml`:

- Linux: `~/.config/opencode-usage/config.toml`
- Windows: `%APPDATA%\opencode-usage\config.toml`

```toml
# Presupuesto mensual en USD. Sin esta línea, no hay presupuesto.
monthly_budget_usd = 20.0

# Idioma de la interfaz: "es", "en" o "auto" (detecta el del sistema).
language = "auto"

# Carpeta destino del export. Sin esta línea, se usa la carpeta actual.
export_dir = "~/Documentos/usage"
```

Si el archivo tiene un error, la app sigue funcionando con valores por defecto y muestra un aviso.

## Idiomas

La interfaz está en español e inglés. Prioridad, de mayor a menor:

1. Línea de comandos: `opencode-usage --lang en`
2. `config.toml`: `language = "en"` (o `"es"`, o `"auto"`)
3. Automático: con `auto` se mira `LANG`/`LC_ALL` del sistema. Sin pistas, español.

Se traduce todo lo visible: tarjetas, atajos del footer, gráficas, presupuesto,
sesión actual, panel de DeepSeek, tablas, el Markdown exportado y los errores.

## Exportar

La tecla `e` abre un diálogo para elegir la carpeta destino. Escribe la ruta
(acepta `~`), `Enter` exporta y `Esc` cancela. La app recuerda la última carpeta
usada durante la sesión. El destino inicial sale de `--export-dir`, de
`export_dir` en `config.toml`, o de la carpeta actual, en ese orden.

Se escriben dos archivos:

- `opencode-usage-AAAAMMDD-HHMMSS.csv`: una fila por día (fecha, tokens, costo).
- `opencode-usage-AAAAMMDD-HHMMSS.md`: resumen de totales, modelos y agentes.

Si la carpeta no existe, se crea. Si no se puede usar, se avisa y no se exporta.

## Privacidad y seguridad

- Solo lee `opencode.db` en modo solo lectura. Nunca escribe en ella.
- Sin telemetría. Los únicos archivos que crea son los que exportas con `e`.
- La clave de DeepSeek solo se lee de la variable de entorno `DEEPSEEK_API_KEY`.
  No se pide en pantalla, no se guarda en archivos y no aparece en logs ni errores.
- Si defines esa clave, la app hace una única consulta HTTPS a
  `https://api.deepseek.com/user/balance` cada 60 segundos, en un hilo aparte.
  Solo lee el saldo: no puede gastar ni modificar tu cuenta.
- Si no defines la clave, no hay ninguna conexión a internet.

## DeepSeek (opcional)

Define la variable de entorno y arranca la app:

Linux:

```bash
export DEEPSEEK_API_KEY="tu-clave"
opencode-usage
```

Windows (PowerShell):

```powershell
$env:DEEPSEEK_API_KEY = "tu-clave"
opencode-usage
```

El panel muestra saldo total, moneda y si hay saldo para llamadas.
DeepSeek no ofrece endpoint de uso por API: el uso por modelo que ves en las
tablas viene de la base local de OpenCode.

## Estructura

```text
src/opencode_usage/
  config.py        rutas, tiempos y config.toml
  pricing.py       tabla de precios de modelos (USD por 1M tokens)
  format.py        formatos de números
  i18n.py          idiomas español/inglés (catálogos y traducción)
  export.py        exportación a CSV y Markdown
  providers/
    deepseek.py    saldo de DeepSeek (HTTPS, solo lectura, clave por env)
  data/
    db.py          conexión SQLite solo lectura
    models.py      dataclasses de datos
    queries.py     agregaciones (sin dependencia de UI)
  app.py           app Textual
  widgets/         tarjetas, gráfica diaria, heatmap, tablas (modelos, agentes,
                   sesiones), presupuesto, sesión, diálogo de export
  styles/app.tcss  estilos
tests/             fixtures SQLite, pruebas de queries, config y app
docs/              convenciones: arquitectura, estilo, i18n, tests, seguridad
AGENTS.md          guía de entrada para agentes de IA
```

## Desarrollo

```bash
python -m ruff check src tests
python -m pytest
```

## Tests

```powershell
pytest
```
