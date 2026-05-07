
import psycopg2
NEW_RENDER_URL = "postgresql://candidates:F3J5QY5ZYCztdJUFx59ZUIfDDsNLZyeH@dpg-d7s5pejeo5us73djctag-a.oregon-postgres.render.com/resume_05hg"
def check_tables():
    try:
        url = f"{NEW_RENDER_URL}?sslmode=require"
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cur.fetchall()
        print(f"Tables in NEW DB: {[t[0] for t in tables]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    check_tables()
