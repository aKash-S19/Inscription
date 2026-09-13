import os
from sqlmodel import SQLModel, create_engine, Session
from config import settings
from supabase import create_client, Client
from typing import Optional

def get_database_url() -> str:
    url = settings.SUPABASE_DB_URL or settings.KALVETTU_DB_URL
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

db_url = get_database_url()

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    global _supabase_client
    if _supabase_client is None and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        except Exception as e:
            print(f"Warning: Could not initialize Supabase client: {e}")
    return _supabase_client

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
