"""Veritabanı bağlantısı — STUB.

DATABASE_URL ile Supabase/PostgreSQL'e bağlanacak (psycopg). Deterministik çekirdek
DB'ye yazmaz; persist katmanı sonraki adımlarda eklenir.
"""

from __future__ import annotations

import os


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "")


def get_connection():
    # TODO: psycopg ile bağlantı aç (DATABASE_URL). pgvector register et.
    raise NotImplementedError("DB bağlantısı henüz uygulanmadı.")
