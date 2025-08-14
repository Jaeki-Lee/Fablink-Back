from __future__ import annotations

from typing import Dict
from pymongo import MongoClient, ASCENDING
from django.conf import settings
from django.utils import timezone

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client


def get_db():
    return get_mongo_client()[settings.MONGODB_DB]


def get_collection(name: str):
    db = get_db()
    return db[name]


def ensure_indexes():
    """Ensure required indexes exist on collections."""
    col_designer = get_collection(settings.MONGODB_COLLECTIONS['designer_orders'])
    # unique on order_id for idempotency
    col_designer.create_index([('order_id', ASCENDING)], unique=True, name='ux_order_id')
    # optional secondary indexes
    col_designer.create_index([('designer_id', ASCENDING)], name='ix_designer_id')
    col_designer.create_index([('overall_status', ASCENDING)], name='ix_overall_status')

    col_factory = get_collection(settings.MONGODB_COLLECTIONS['factory_orders'])
    col_factory.create_index([('order_id', ASCENDING)], unique=True, name='ux_order_id')


def now_iso_with_minutes() -> str:
    """Return ISO string with timezone info (KST by Django TIME_ZONE), minute precision."""
    dt = timezone.now().astimezone(timezone.get_current_timezone())
    return dt.isoformat(timespec='minutes')
