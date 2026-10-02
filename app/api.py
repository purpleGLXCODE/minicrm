"""Minimal REST API for MiniCRM."""

import time

from fastapi import APIRouter

from .database import all, one, sql

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


@router.post("/leads")
def add_lead(data: dict):
    return one("""
        INSERT INTO leads (name, contact, request, source, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, name, contact, request, source, created_at
    """, [
        data["name"],
        data["contact"],
        data["request"],
        data.get("source", "manual"),
        int(time.time())
    ])


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, data: dict):
    return one("""
        UPDATE leads
        SET name = %s,
            contact = %s,
            request = %s,
            source = %s
        WHERE id = %s
        RETURNING id, name, contact, request, source, created_at
    """, [
        data["name"],
        data["contact"],
        data["request"],
        data.get("source", "manual"),
        lead_id
    ])


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int):
    sql("""
        DELETE FROM leads
        WHERE id = %s
    """, [lead_id])

    return {"ok": True}


@router.get("/tags")
def get_tags():
    return all("""
        SELECT id, name
        FROM tags
        ORDER BY name
    """)