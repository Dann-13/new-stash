from opencode_usage import export, i18n
from opencode_usage.data import queries


def test_catalogos_tienen_las_mismas_claves():
    assert set(i18n.CATALOGS["es"]) == set(i18n.CATALOGS["en"])


def test_default_espanol():
    assert i18n.current_language() == "es"
    assert i18n.t("quit") == "Salir"


def test_set_language_ingles():
    i18n.set_language("en")
    assert i18n.t("quit") == "Quit"
    assert i18n.t("budget_month") == "month "


def test_set_language_desconocido_cae_a_es():
    i18n.set_language("fr")
    assert i18n.current_language() == "es"


def test_t_formatea_kwargs():
    assert i18n.t("range_days", n=7) == "últimos 7 días"
    i18n.set_language("en")
    assert i18n.t("range_days", n=7) == "last 7 days"


def test_t_clave_ausente_devuelve_la_clave():
    assert i18n.t("no_existe_esta_clave") == "no_existe_esta_clave"


def test_resolve_language_directo():
    assert i18n.resolve_language("en") == "en"
    assert i18n.resolve_language("es") == "es"


def test_resolve_auto_detecta_entorno(monkeypatch):
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        monkeypatch.delenv(var, raising=False)
    assert i18n.resolve_language("auto") == "es"
    monkeypatch.setenv("LANG", "es_ES.UTF-8")
    assert i18n.resolve_language("auto") == "es"
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert i18n.resolve_language("auto") == "en"


def test_export_markdown_ingles(con, tmp_path):
    i18n.set_language("en")
    msgs = queries.load_messages(con)
    md = tmp_path / "u.md"
    export.export_markdown(
        md, "last 7 days", queries.totals(msgs),
        queries.by_model(msgs), queries.by_agent(msgs),
    )
    text = md.read_text(encoding="utf-8")
    assert "## Totals" in text
    assert "| Agent |" in text
    assert "## Agentes" not in text
