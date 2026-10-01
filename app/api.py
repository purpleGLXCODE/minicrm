"""Minimal REST API for MiniCRM."""

from fastapi import APIRouter

from .database import all, one

router = APIRouter(prefix="/api")


@router.get("/leads")
def get_leads():
    return all("""
        SELECT id, name, contact, request, source, created_at
        FROM leads
        ORDER BY created_at DESC, id DESC
    """)


@router.get("/leads/{lead_id}")
def get_lead(lead_id: int):
    return one("""
        SELECT id, name, contact, request, source, created_at
        FROM leads
        WHERE id = %s
    """, [lead_id])


@router.get("/tags")
def get_tags():
    return all("""
        SELECT id, name
        FROM tags
        ORDER BY name
    """)
