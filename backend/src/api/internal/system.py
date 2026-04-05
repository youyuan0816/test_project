"""System router — /health"""
from fastapi import APIRouter


router = APIRouter(tags=["System"])


@router.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}
