
from sqlalchemy import create_engine, text
from app.core.config import settings

def add_status_column():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE matches ADD COLUMN status VARCHAR(50) DEFAULT 'matched'"))
            conn.commit()
            print("Successfully added 'status' column to 'matches' table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column 'status' already exists.")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    add_status_column()
