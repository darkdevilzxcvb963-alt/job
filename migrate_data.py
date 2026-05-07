
import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# 1. PASTE YOUR URLS HERE
OLD_RENDER_URL = "postgresql://resume_db_26qd_user:yFgjUlH4gdcFZy9sEzJePN8syYyudTP5@dpg-d7bse55m5p6s73f595l0-a.oregon-postgres.render.com/resume_db_26qd"
NEW_RENDER_URL = "postgresql://candidates:F3J5QY5ZYCztdJUFx59ZUIfDDsNLZyeH@dpg-d7s5pejeo5us73djctag-a.oregon-postgres.render.com/resume_05hg"

def migrate():
    try:
        print("Starting Migration...")
        
        # Ensure SSL mode is enabled for Render
        old_url = OLD_RENDER_URL if "?" in OLD_RENDER_URL else f"{OLD_RENDER_URL}?sslmode=require"
        new_url = NEW_RENDER_URL if "?" in NEW_RENDER_URL else f"{NEW_RENDER_URL}?sslmode=require"
        
        # Create engines
        old_engine = create_engine(old_url)
        new_engine = create_engine(new_url)
        
        # Reflect old schema
        print("Reflecting old database schema...")
        metadata = MetaData()
        metadata.reflect(bind=old_engine)
        
        # Create tables in new database
        print("Creating tables in new database...")
        metadata.create_all(bind=new_engine)
        
        # Copy data table by table
        for table in metadata.sorted_tables:
            print(f"Copying table: {table.name}...")
            
            # Read from old
            with old_engine.connect() as conn_old:
                rows = conn_old.execute(table.select()).fetchall()
                
                if rows:
                    # Write to new
                    with new_engine.connect() as conn_new:
                        # Convert rows to dicts for insertion
                        data = [dict(row._mapping) for row in rows]
                        conn_new.execute(table.insert(), data)
                        conn_new.commit()
                        print(f"SUCCESS: Successfully copied {len(rows)} rows to {table.name}")
                else:
                    print(f"Table {table.name} is empty, skipping.")

        print("\nMIGRATION COMPLETE! Your data is now in the new Render Database.")
        print("Now you can safely update your DATABASE_URL in Render.")

    except Exception as e:
        print(f"\nERROR during migration: {e}")

if __name__ == "__main__":
    if "PASTE_YOUR" in OLD_RENDER_URL:
        print("Error: Please open migrate_data.py and paste your actual database URLs first!")
    else:
        migrate()
