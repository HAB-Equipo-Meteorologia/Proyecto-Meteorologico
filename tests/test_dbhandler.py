from db.db_handler import DBHandler

db = DBHandler()


def test_get_table(table: str = "provincias"):
    result = db.get_table(table)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], dict)


def test_get_table_columns(table: str = "provincias"):
    result = db.get_columns(table, ["id"])
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], dict)
