"""MiniCRM FastAPI entrypoint."""

from fastapi import FastAPI

app = FastAPI(title="MiniCRM")


@app.get("/api/health")
def health():
    return {"status": "ok"}
