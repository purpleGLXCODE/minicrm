"""MiniCRM FastAPI entrypoint."""

from fastapi import FastAPI

from .api import router

app = FastAPI(title="MiniCRM")
app.include_router(router)
