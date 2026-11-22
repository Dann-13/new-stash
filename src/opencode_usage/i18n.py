"""Internacionalización: catálogos español/inglés y traducción ``t()``.

Módulo puro, sin dependencias. El idioma global se fija una vez al
arrancar (CLI ``--lang`` o config.toml ``language``). ``t(key, **kw)``
devuelve el texto del idioma activo; si la clave no existe, devuelve la
propia clave para no romper la UI.
"""

from __future__ import annotations

import os

CATALOGS: dict[str, dict[str, str]] = {
    "es": {
        # atajos / footer
        "quit": "Salir",
        "refresh": "Refrescar",
        "export": "Exportar",
        "days_7": "7 días",
        "days_30": "30 días",
        "days_90": "90 días",
        "all": "Todo",
        # tarjetas
        "card_input": "INPUT TOKENS",
        "card_output": "OUTPUT TOKENS",
        "card_turns": "TURNS",
        "card_cost": "COST",
        "from_cache": "{pct} from cache",
        "per_turn": "{n} per turn",
        "sessions": "{n} sessions",
        "recorded": "recorded by OpenCode",
        "updated": "actualizado {time}",
        "db_error": "error: {exc}",
        # rango / export
        "range_all": "todo",
        "range_days": "últimos {n} días",
        "export_ok": "exportado: {csv} y {md}",
        "export_fail": "no se pudo exportar: {exc}",
        # gráficas
        "no_data": "sin datos",
        "weekdays": "lun,mar,mié,jue,vie,sáb,dom",
        "most_active": "más activo: ",
        "legend_output": "■ output ",
        "legend_input": "■ input ",
        "legend_cost": "▁ costo/día",
        "legend_cache": "  ▁ caché {pct}",
        # presupuesto
        "budget_none": "presupuesto: no definido (monthly_budget_usd en config.toml)",
        "budget_month": "mes ",
        "budget_over": "  límite superado",
        "budget_near": "  cerca del límite",
        # sesión
        "session_none": "sesión actual: sin actividad",
        "session_label": "sesión actual ",
        "session_detail": "  in {input} · out {output} · {cost}"
        " · {turns} turnos · {ago}",
        "ago_s": "hace {n} s",
        "ago_min": "hace {n} min",
        "ago_h": "hace {n} h",
        # proveedor
        "provider_balance": "saldo {total} {currency}",
        "provider_available": "  · disponible",
        "provider_unavailable": "  · sin saldo para llamadas",
        "provider_loading": "deepseek  consultando saldo…",
        # tablas
        "col_model": "MODEL",
        "col_provider": "PROVIDER",
        "col_input": "INPUT",
        "col_output": "OUTPUT",
        "col_turns": "TURNS",
        "col_cost": "COST",
        "col_agent": "AGENT",
        "col_rate": "$/1K OUT",
        "col_session": "SESSION",
        # exportar
        "export_title": "Exportar a carpeta",
        "export_hint": "Enter exporta · Esc cancela",
        "export_bad_dir": "no se pudo usar la carpeta: {exc}",
        # export markdown
        "md_range": "Rango: {label}",
        "md_totals": "## Totales",
        "md_input": "- Input tokens: {n}",
        "md_output": "- Output tokens: {n}",
        "md_cache": "- Caché leída: {pct}",
        "md_turns": "- Turnos: {n}",
        "md_sessions": "- Sesiones: {n}",
        "md_cost": "- Costo registrado: {c}",
        "md_models": "## Modelos",
        "md_models_header": "| Modelo | Proveedor | Input | Output | Turnos | Costo |",
        "md_agents": "## Agentes",
        "md_agents_header": "| Agente | Input | Output | Turnos | Costo |",
        # errores deepseek
        "ds_no_key": "falta la clave (variable DEEPSEEK_API_KEY)",
        "ds_https": "solo se permiten conexiones HTTPS",
        "ds_rejected": "clave rechazada por DeepSeek (401/403)",
        "ds_http": "DeepSeek respondió HTTP {code}",
        "ds_network": "sin conexión con DeepSeek",
        "ds_json": "respuesta de DeepSeek no es JSON válido",
        "ds_no_balance": "DeepSeek no reportó saldo",
        "ds_bad_format": "saldo de DeepSeek con formato inesperado",
        # errores config
        "cfg_read": "config.toml no se pudo leer: {exc}",
        "cfg_budget": "monthly_budget_usd debe ser un número mayor que 0",
        "cfg_language": "language debe ser es, en o auto",
        "cfg_export_dir": "export_dir debe ser una ruta de texto",
    },
    "en": {
        "quit": "Quit",
        "refresh": "Refresh",
        "export": "Export",
        "days_7": "7 days",
        "days_30": "30 days",
        "days_90": "90 days",
        "all": "All",
        "card_input": "INPUT TOKENS",
        "card_output": "OUTPUT TOKENS",
        "card_turns": "TURNS",
        "card_cost": "COST",
        "from_cache": "{pct} from cache",
        "per_turn": "{n} per turn",
        "sessions": "{n} sessions",
        "recorded": "recorded by OpenCode",
        "updated": "updated {time}",
        "db_error": "error: {exc}",
        "range_all": "all",
        "range_days": "last {n} days",
        "export_ok": "exported: {csv} and {md}",
        "export_fail": "could not export: {exc}",
        "no_data": "no data",
        "weekdays": "mon,tue,wed,thu,fri,sat,sun",
        "most_active": "most active: ",
        "legend_output": "■ output ",
        "legend_input": "■ input ",
        "legend_cost": "▁ cost/day",
        "legend_cache": "  ▁ cache {pct}",
        "budget_none": "budget: not set (monthly_budget_usd in config.toml)",
        "budget_month": "month ",
        "budget_over": "  over limit",
        "budget_near": "  near limit",
        "session_none": "current session: no activity",
        "session_label": "current session ",
        "session_detail": "  in {input} · out {output} · {cost}"
        " · {turns} turns · {ago}",
        "ago_s": "{n}s ago",
        "ago_min": "{n}m ago",
        "ago_h": "{n}h ago",
        "provider_balance": "balance {total} {currency}",
        "provider_available": "  · available",
        "provider_unavailable": "  · no balance for calls",
        "provider_loading": "deepseek  checking balance…",
        "col_model": "MODEL",
        "col_provider": "PROVIDER",
        "col_input": "INPUT",
        "col_output": "OUTPUT",
        "col_turns": "TURNS",
        "col_cost": "COST",
        "col_agent": "AGENT",
        "col_rate": "$/1K OUT",
        "col_session": "SESSION",
        "export_title": "Export to folder",
        "export_hint": "Enter exports · Esc cancels",
        "export_bad_dir": "could not use folder: {exc}",
        "md_range": "Range: {label}",
        "md_totals": "## Totals",
        "md_input": "- Input tokens: {n}",
        "md_output": "- Output tokens: {n}",
        "md_cache": "- Cache read: {pct}",
        "md_turns": "- Turns: {n}",
        "md_sessions": "- Sessions: {n}",
        "md_cost": "- Recorded cost: {c}",
        "md_models": "## Models",
        "md_models_header": "| Model | Provider | Input | Output | Turns | Cost |",
        "md_agents": "## Agents",
        "md_agents_header": "| Agent | Input | Output | Turns | Cost |",
        "ds_no_key": "missing key (DEEPSEEK_API_KEY variable)",
        "ds_https": "only HTTPS connections allowed",
        "ds_rejected": "key rejected by DeepSeek (401/403)",
        "ds_http": "DeepSeek returned HTTP {code}",
        "ds_network": "no connection to DeepSeek",
        "ds_json": "DeepSeek response is not valid JSON",
        "ds_no_balance": "DeepSeek reported no balance",
        "ds_bad_format": "unexpected DeepSeek balance format",
        "cfg_read": "could not read config.toml: {exc}",
        "cfg_budget": "monthly_budget_usd must be a number greater than 0",
        "cfg_language": "language must be es, en or auto",
        "cfg_export_dir": "export_dir must be a text path",
    },
}

_language = "es"


def set_language(lang: str) -> None:
    """Fija el idioma global. Valor desconocido cae a español."""
    global _language
    _language = lang if lang in CATALOGS else "es"


def current_language() -> str:
    return _language


def resolve_language(setting: str) -> str:
    """Resuelve ``es``/``en`` directo; ``auto`` mira el entorno.

    Sin pistas en el entorno, el defecto es español.
    """
    if setting in CATALOGS:
        return setting
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        val = os.environ.get(var, "")
        if val:
            return "es" if val.lower().startswith("es") else "en"
    return "es"


def t(key: str, **kwargs: object) -> str:
    """Texto del idioma activo. Clave ausente devuelve la propia clave."""
    text = CATALOGS[_language].get(key) or CATALOGS["es"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text
