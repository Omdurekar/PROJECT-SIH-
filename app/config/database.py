from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(bind_engine=None):
    target_engine = bind_engine or engine
    import app.models.orm  # Ensure all ORM models are registered with Base.metadata
    Base.metadata.create_all(bind=target_engine)

    from sqlalchemy import inspect, text
    inspector = inspect(target_engine)
    if "users" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("users")]
        if "is_verified" not in columns:
            with target_engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 0"))
                conn.commit()

