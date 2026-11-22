import sqlite3

from opencode_usage.data import db


def test_open_readonly_ruta_con_espacios_y_numeral(tmp_path):
    folder = tmp_path / "mi carpeta #1"
    folder.mkdir()
    path = folder / "opencode.db"
    with sqlite3.connect(path) as w:
        w.execute("CREATE TABLE t (x INTEGER)")
        w.execute("INSERT INTO t VALUES (7)")

    con = db.open_readonly(path)
    assert con.execute("SELECT x FROM t").fetchone()[0] == 7
    con.close()
