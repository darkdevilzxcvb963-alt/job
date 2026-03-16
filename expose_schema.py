import sys
import os
from pathlib import Path

# Setup Path as in config.py
BASE_DIR = Path(os.getcwd()) / 'backend'
db_url = f"sqlite:///{str(Path(BASE_DIR.parent / 'resume_matching.db').resolve()).replace(chr(92), '/')}"

from sqlalchemy import create_engine, inspect

engine = create_engine(db_url)
inspector = inspect(engine)

print(f"DATABASE_URL: {db_url}")
for table_name in inspector.get_table_names():
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    print(f"Table: {table_name}, Columns: {columns}")
