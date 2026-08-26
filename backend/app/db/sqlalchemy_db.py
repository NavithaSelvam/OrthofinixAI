import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "orthofinix_summit.db")
)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _auto_migrate_sqlite(conn):
    """Automatically adds any missing columns to existing SQLite tables."""
    try:
        # Check analysis_reports columns
        cursor = conn.execute(text("PRAGMA table_info(analysis_reports);"))
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        if "patient_id" not in existing_cols:
            conn.execute(text("ALTER TABLE analysis_reports ADD COLUMN patient_id VARCHAR;"))
        if "case_id" not in existing_cols:
            conn.execute(text("ALTER TABLE analysis_reports ADD COLUMN case_id VARCHAR;"))
        if "root_angulation_score" not in existing_cols:
            conn.execute(text("ALTER TABLE analysis_reports ADD COLUMN root_angulation_score FLOAT DEFAULT 0.0;"))
    except Exception as e:
        print(f"Notice: SQLite column migration check: {e}")


def init_sqlalchemy():
    from app.db import orm_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    if DATABASE_URL.startswith("sqlite"):
        with engine.begin() as conn:
            _auto_migrate_sqlite(conn)
