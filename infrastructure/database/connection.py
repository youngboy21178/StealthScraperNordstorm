import duckdb
from pathlib import Path


class DatabaseConnection:

    def __init__(self, path: str, schema_path: str):
        self.path = path
        self.schema_path = schema_path
        self.conn = duckdb.connect(self.path)

        self._initialize_schema()

    def _initialize_schema(self):
        schema_file = Path(self.schema_path)

        if not schema_file.exists():
            raise FileNotFoundError("Schema file not found")

        with open(schema_file, "r") as f:
            self.conn.execute(f.read())

    def execute(self, query, params=None):
        return self.conn.execute(query, params)

    def close(self):
        self.conn.close()