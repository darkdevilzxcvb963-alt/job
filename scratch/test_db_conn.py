
import psycopg2
import os

OLD_RENDER_URL = "postgresql://resume_db_26qd_user:yFgjUlH4gdcFZy9sEzJePN8syYyudTP5@dpg-d7bse55m5p6s73f595l0-a.oregon-postgres.render.com/resume_db_26qd"
NEW_RENDER_URL = "postgresql://candidates:F3J5QY5ZYCztdJUFx59ZUIfDDsNLZyeH@dpg-d7s5pejeo5us73djctag-a.oregon-postgres.render.com/resume_05hg"

def test_conn(name, url):
    try:
        print(f"Testing {name}...")
        url_with_ssl = url if "?" in url else f"{url}?sslmode=require"
        conn = psycopg2.connect(url_with_ssl)
        print(f"SUCCESS: Connected to {name}")
        conn.close()
    except Exception as e:
        print(f"FAILED: Could not connect to {name}: {e}")

if __name__ == "__main__":
    test_conn("OLD DB", OLD_RENDER_URL)
    test_conn("NEW DB", NEW_RENDER_URL)
