# opencode-usage

Dashboard en terminal (100% TUI) que mide tu uso de tokens de OpenCode:
tokens por modelo, por agente, por día, heatmap de actividad y costo.

Lee en modo solo lectura la base de datos local de OpenCode
(`~/.local/share/opencode/opencode.db`). No escribe nada.

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
```

Atajos:

| Tecla | Acción            |
|-------|-------------------|
| `1`   | ventana 7 días    |
| `2`   | ventana 30 días   |
| `3`   | ventana 90 días   |
| `4`   | todo el histórico |
| `r`   | refrescar ya      |
| `e`   | exportar CSV y Markdown a la carpeta actual |
| `q`   | salir             |

## Configuración (opcional)

Archivo `config.toml`:

- Linux: `~/.config/opencode-usage/config.toml`
- Windows: `%APPDATA%\opencode-usage\config.toml`

```toml
# Presupuesto mensual en USD. Sin esta línea, no hay presupuesto.
monthly_budget_usd = 20.0
```

Si el archivo tiene un error, la app sigue funcionando con valores por defecto y muestra un aviso.

## Exportar

La tecla `e` escribe dos archivos en la carpeta desde donde ejecutas la app:

- `opencode-usage-AAAAMMDD-HHMMSS.csv`: una fila por día (fecha, tokens, costo).
- `opencode-usage-AAAAMMDD-HHMMSS.md`: resumen de totales, modelos y agentes.

## Privacidad y seguridad

- Solo lee `opencode.db` en modo solo lectura. Nunca escribe en ella.
- No envía datos a internet. No tiene telemetría.
- Los únicos archivos que crea son los que exportas con `e`.
- Sin clave de API ni contraseñas: no las pide ni las guarda.

## Estructura

```text
src/opencode_usage/
  config.py        rutas, tiempos y config.toml
  pricing.py       tabla de precios de modelos (USD por 1M tokens)
  format.py        formatos de números
  export.py        exportación a CSV y Markdown
  data/
    db.py          conexión SQLite solo lectura
    models.py      dataclasses de datos
    queries.py     agregaciones (sin dependencia de UI)
  app.py           app Textual
  widgets/         tarjetas, gráfica diaria, heatmap, tablas, presupuesto, sesión
  styles/app.tcss  estilos
tests/             fixtures SQLite, pruebas de queries, config y app
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
