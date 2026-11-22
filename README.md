# opencode-usage

Dashboard en terminal (100% TUI) que mide tu uso de tokens de OpenCode:
tokens por modelo, por agente, por día, heatmap de actividad y costo.

Lee en modo solo lectura la base de datos local de OpenCode
(`~/.local/share/opencode/opencode.db`). No escribe nada.

## Requisitos

- Python 3.12+
- OpenCode instalado (para tener datos)

## Instalación

```powershell
cd opencode-usage
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Uso

```powershell
opencode-usage
# o
python -m opencode_usage
```

Opciones:

```text
--db RUTA        ruta a opencode.db (default: ~/.local/share/opencode/opencode.db)
--refresh SEG    segundos entre refrescos en vivo (default: 5)
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
| `q`   | salir             |

## Estructura

```text
src/opencode_usage/
  config.py        rutas y ajustes
  pricing.py       tabla de precios de modelos (USD por 1M tokens)
  format.py        formatos de números
  data/
    db.py          conexión SQLite solo lectura
    models.py      dataclasses de datos
    queries.py     agregaciones (sin dependencia de UI)
  app.py           app Textual
  widgets/         tarjetas, gráfica diaria, heatmap, tablas
  styles/app.tcss  estilos
tests/             fixtures SQLite + pruebas de queries
```

## Tests

```powershell
pytest
```
