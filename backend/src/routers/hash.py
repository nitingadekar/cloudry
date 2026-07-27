"""File hash calculator endpoints."""

from fastapi import APIRouter, Depends, File, UploadFile

from src.middleware.captcha import verify_turnstile
from src.services.hash_service import HashService

router = APIRouter()
hash_service = HashService()


@router.post("/calculate", dependencies=[Depends(verify_turnstile)])
async def calculate_hash(file: UploadFile = File(...)):
    """Calculate MD5, SHA1, and SHA256 hashes for a file."""
    content = await file.read()
    hashes = hash_service.calculate(content)
    return {
        "filename": file.filename,
        "size_bytes": len(content),
        "hashes": hashes,
    }
