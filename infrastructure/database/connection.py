import duckdb


class DatabaseConnection:

    def __init__(self, path: str):
        self.conn = duckdb.connect(path)

    def execute(self, query, params=None):
        return self.conn.execute(query, params)

    def close(self):
        self.conn.close()