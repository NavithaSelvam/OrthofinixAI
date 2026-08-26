import sqlite3
import os
import glob

print("=" * 80)
print("INSPECTING LOCAL SQLITE DATABASES FOR USER CASES")
print("=" * 80)

db_files = glob.glob("**/*.db", recursive=True)
for db_path in db_files:
    print(f"\n--- Database: {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables: {tables}")
        for t in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                count = cursor.fetchone()[0]
                print(f"  Table '{t}': {count} rows")
                if count > 0 and t in ["analysis_reports", "cases", "patients", "users", "reports", "patient_entities", "case_entities"]:
                    cursor.execute(f"SELECT * FROM {t} LIMIT 5")
                    rows = cursor.fetchall()
                    col_names = [d[0] for d in cursor.description]
                    print(f"    Columns: {col_names}")
                    for r in rows:
                        print(f"    Row: {r}")
            except Exception as e:
                print(f"    Error reading table {t}: {e}")
        conn.close()
    except Exception as e:
        print(f"Error opening {db_path}: {e}")
