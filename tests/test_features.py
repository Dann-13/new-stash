from datetime import date, datetime

from conftest import _msg

from opencode_usage import export
from opencode_usage.config import Settings, load_settings
from opencode_usage.data import queries
from opencode_usage.data.models import DayTokens
from opencode_usage.widgets.tokens_by_day import _cost_line


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
