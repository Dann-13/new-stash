from datetime import date, datetime
from pathlib import Path

from conftest import _msg

from opencode_usage import export
from opencode_usage.config import Settings, load_settings
from opencode_usage.data import queries
from opencode_usage.data.models import DayTokens, ModelStat
from opencode_usage.format import format_rate
from opencode_usage.widgets.tokens_by_day import _cache_line, _cost_line


def test_tokens_by_day_incluye_costo(con):
    msgs = queries.load_messages(con)
    days = queries.tokens_by_day(msgs)
    assert days[0].day == date(2026, 11, 18)
    assert round(days[0].cost, 4) == 0.03
    assert round(days[1].cost, 4) == 0.03


def test_month_start_ms_es_dia_uno_medianoche():
    ms = queries.month_start_ms(datetime(2026, 11, 21, 15, 30))
    assert datetime.fromtimestamp(ms / 1000) == datetime(2026, 11, 1)


def test_current_session_usa_mensaje_mas_reciente(con):
    stat = queries.current_session(queries.load_messages(con))
    assert stat is not None
    assert stat.session_id == "s2"
    assert stat.turns == 1
    assert stat.input == 300


def test_current_session_sin_datos():
    assert queries.current_session([]) is None


def test_cost_line_escala_y_marca_dias_sin_costo():
    days = [
        DayTokens(day=date(2026, 1, 1), input=0, output=0, cost=0.0),
        DayTokens(day=date(2026, 1, 2), input=0, output=0, cost=1.0),
        DayTokens(day=date(2026, 1, 3), input=0, output=0, cost=0.5),
    ]
    line = _cost_line(days)
    assert line[0] == "·"
    assert line[1] == "█"
    assert len(line) == 3


def test_config_ausente_usa_defaults(tmp_path):
    s = load_settings(tmp_path / "no.toml")
    assert s == Settings()
    assert s.monthly_budget_usd is None


def test_config_presupuesto_valido(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text("monthly_budget_usd = 20.5\n", encoding="utf-8")
    assert load_settings(f).monthly_budget_usd == 20.5


def test_config_presupuesto_invalido_se_ignora(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('monthly_budget_usd = "mucho"\n', encoding="utf-8")
    s = load_settings(f)
    assert s.monthly_budget_usd is None
    assert s.config_error is not None


def test_config_toml_roto_no_tumba_la_app(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text("esto no es toml = = =\n", encoding="utf-8")
    s = load_settings(f)
    assert s.monthly_budget_usd is None
    assert s.config_error is not None


def test_config_language_valido(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('language = "en"\n', encoding="utf-8")
    s = load_settings(f)
    assert s.language == "en"
    assert s.config_error is None


def test_config_language_invalido_cae_a_auto(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('language = "fr"\n', encoding="utf-8")
    s = load_settings(f)
    assert s.language == "auto"
    assert s.config_error is not None


def test_export_csv_y_markdown(con, tmp_path):
    msgs = queries.load_messages(con)
    csv_path = tmp_path / "u.csv"
    md_path = tmp_path / "u.md"
    export.export_csv(csv_path, queries.tokens_by_day(msgs))
    export.export_markdown(
        md_path,
        "últimos 7 días",
        queries.totals(msgs),
        queries.by_model(msgs),
        queries.by_agent(msgs),
    )
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "date,input_tokens,output_tokens,cost_usd"
    assert lines[1].startswith("2026-11-18,")
    md = md_path.read_text(encoding="utf-8")
    assert "# opencode usage" in md
    assert "model-a" in md
    assert "| Agente |" in md


def test_mensajes_nuevos_aparecen_en_costo_diario(con):
    con.execute(
        "INSERT INTO session_message VALUES (?, ?, ?, ?, ?, ?, ?)",
        _msg("m9", "s3", datetime(2026, 11, 20, 9, 0), cost=0.5),
    )
    days = queries.tokens_by_day(queries.load_messages(con))
    assert days[-1].day == date(2026, 11, 20)
    assert days[-1].cost == 0.5


# ---- Fase C: top sesiones, comparador, caché, export dir ----


def test_top_sessions_ordena_por_costo_y_limita(con):
    stats = queries.top_sessions(queries.load_messages(con))
    assert {s.session_id for s in stats} == {"s1", "s2"}
    assert stats[0].cost >= stats[1].cost
    s1 = next(s for s in stats if s.session_id == "s1")
    assert s1.turns == 2
    assert len(queries.top_sessions(queries.load_messages(con), limit=1)) == 1


def test_tokens_by_day_acumula_cache(con):
    days = queries.tokens_by_day(queries.load_messages(con))
    assert days[0].cache_read == 12000  # 8000 + 4000 del 2026-11-18


def test_daytokens_cache_hit_ratio():
    d = DayTokens(day=date(2026, 1, 1), input=100, output=0, cache_read=900)
    assert d.cache_hit_ratio == 0.9
    assert DayTokens(day=date(2026, 1, 1), input=0, output=0).cache_hit_ratio == 0.0


def test_model_cost_per_1k_output():
    s = ModelStat("m", "p", input=0, output=2000, reasoning=0,
                  cache_read=0, cost=0.05, turns=1)
    assert s.cost_per_1k_output == 0.025
    s0 = ModelStat("m", "p", 0, 0, 0, 0, 0.0, 0)
    assert s0.cost_per_1k_output is None


def test_format_rate():
    assert format_rate(None) == "—"
    assert format_rate(0) == "$0"
    assert format_rate(0.025) == "$0.0250"


def test_cache_line_escala_y_marca_dias_sin_datos():
    days = [
        DayTokens(day=date(2026, 1, 1), input=0, output=0, cache_read=0),
        DayTokens(day=date(2026, 1, 2), input=0, output=0, cache_read=100),
    ]
    line = _cache_line(days)
    assert line[0] == "·"
    assert line[1] == "█"  # ratio 1.0 -> bloque lleno


def test_config_export_dir_valido(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('export_dir = "~/usage"\n', encoding="utf-8")
    s = load_settings(f)
    assert s.export_dir == Path("~/usage").expanduser()
    assert s.config_error is None


def test_config_export_dir_invalido_cae_a_none(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text("export_dir = 5\n", encoding="utf-8")
    s = load_settings(f)
    assert s.export_dir is None
    assert s.config_error is not None
