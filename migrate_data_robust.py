
import os
import sys
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time

# Database URLs
OLD_RENDER_URL = "postgresql://resume_db_26qd_user:yFgjUlH4gdcFZy9sEzJePN8syYyudTP5@dpg-d7bse55m5p6s73f595l0-a.oregon-postgres.render.com/resume_db_26qd"
NEW_RENDER_URL = "postgresql://candidates:F3J5QY5ZYCztdJUFx59ZUIfDDsNLZyeH@dpg-d7s5pejeo5us73djctag-a.oregon-postgres.render.com/resume_05hg"

def migrate_with_retry(max_retries=3):
    try:
        print("STARTING: Robust Migration...")
        
        # Ensure SSL mode
        old_url = OLD_RENDER_URL if "?" in OLD_RENDER_URL else f"{OLD_RENDER_URL}?sslmode=require"
        new_url = NEW_RENDER_URL if "?" in NEW_RENDER_URL else f"{NEW_RENDER_URL}?sslmode=require"
        
        old_engine = create_engine(old_url, pool_pre_ping=True)
        new_engine = create_engine(new_url, pool_pre_ping=True)
        
        metadata = MetaData()
        print("INFO: Reflecting old schema...")
        metadata.reflect(bind=old_engine)
        
        print("INFO: Creating tables in new database (if they don't exist)...")
        metadata.create_all(bind=new_engine)
        
        # We need to respect foreign keys, so we sort the tables
        for table in metadata.sorted_tables:
            print(f"COPYING: Table {table.name}")
            
            # Use a connection
            with old_engine.connect() as conn_old:
                # Get count
                from sqlalchemy import func
                total_rows = conn_old.execute(select(func.count()).select_from(table)).scalar()
                
                if total_rows == 0:
                    print(f"   - Table {table.name} is empty, skipping.")
                    continue
                
                print(f"   - Found {total_rows} rows. Copying in chunks...")
                
                # Fetch in chunks
                chunk_size = 100
                for i in range(0, total_rows, chunk_size):
                    # Fetch chunk
                    rows = conn_old.execute(table.select().offset(i).limit(chunk_size)).fetchall()
                    
                    # Insert chunk with retries
                    success = False
                    for attempt in range(max_retries):
                        try:
                            with new_engine.begin() as conn_new:
                                data = [dict(row._mapping) for row in rows]
                                conn_new.execute(table.insert(), data)
                            success = True
                            break
                        except OperationalError as e:
                            print(f"   - Attempt {attempt+1} failed for {table.name} chunk {i//chunk_size}: {e}")
                            time.sleep(2)
                        except Exception as e:
                            # Handle case where record already exists (if partial migration happened)
                            if "already exists" in str(e).lower():
                                print(f"   - Record in {table.name} already exists, skipping chunk.")
                                success = True
                                break
                            else:
                                raise e
                    
                    if success:
                        print(f"   - Progress: {min(i + chunk_size, total_rows)}/{total_rows} rows copied.")
                    else:
                        print(f"   - FAIL: Failed to copy chunk {i//chunk_size} of {table.name} after {max_retries} attempts.")
            
        print("\nSUCCESS: MIGRATION COMPLETE!")
        print("Your data has been moved to the new Render account.")

    except Exception as e:
        print(f"\nERROR: CRITICAL ERROR during migration: {e}")

if __name__ == "__main__":
    migrate_with_retry()
