"""Minimal REST API for MiniCRM."""

import time

from fastapi import APIRouter

from .database import all, one, sql

router = APIRouter(prefix="/api")


LEAD_SELECT = """
    SELECT
        l.id,
        l.name,
        l.contact,
        l.request,
        l.source,
        l.created_at,
        COALESCE(
            (
                SELECT array_agg(t.name::text ORDER BY t.name)
                FROM tags t
                JOIN lead_tags lt ON lt.tag_id = t.id
                WHERE lt.lead_id = l.id
            ),
            ARRAY[]::text[]
        ) AS tags
    FROM leads l
"""


@router.get("/leads")
def get_leads():
    return all(LEAD_SELECT + """
        ORDER BY l.created_at DESC, l.id DESC
    """)


@router.get("/leads/{lead_id}")
def get_lead(lead_id: int):
    return one(LEAD_SELECT + """
        WHERE l.id = %s
    """, [lead_id])


@router.post("/leads")
def add_lead(data: dict):
    lead = one("""
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

    for tag_name in data.get("tags", []):
        tag = one("""
            INSERT INTO tags (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """, [tag_name])

        sql("""
            INSERT INTO lead_tags (lead_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, [lead["id"], tag["id"]])

    return one(LEAD_SELECT + """
        WHERE l.id = %s
    """, [lead["id"]])


@router.put("/leads/{lead_id}")
def update_lead(lead_id: int, data: dict):
    lead = one("""
        UPDATE leads
        SET name = %s,
            contact = %s,
            request = %s,
            source = %s
        WHERE id = %s
        RETURNING id
    """, [
        data["name"],
        data["contact"],
        data["request"],
        data.get("source", "manual"),
        lead_id
    ])

    if not lead:
        return None

    sql("""
        DELETE FROM lead_tags
        WHERE lead_id = %s
    """, [lead_id])

    for tag_name in data.get("tags", []):
        tag = one("""
            INSERT INTO tags (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """, [tag_name])

        sql("""
            INSERT INTO lead_tags (lead_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, [lead_id, tag["id"]])

    return one(LEAD_SELECT + """
        WHERE l.id = %s
    """, [lead_id])


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


@router.post("/tags")
def add_tag(data: dict):
    return one("""
        INSERT INTO tags (name)
        VALUES (%s)
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id, name
    """, [data["name"]])
