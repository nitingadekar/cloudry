"""Caption generator endpoints."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.middleware.captcha import verify_turnstile
from src.services.caption_service import CaptionService

router = APIRouter()
caption_service = CaptionService()

# Max image size: 5MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024


@router.post("/generate", dependencies=[Depends(verify_turnstile)])
async def generate_captions(
    file: UploadFile = File(...),
    theme: str = Form(default="catchy"),
    language: str = Form(default="English"),
    count: int = Form(default=3),
):
    """Generate creative social media captions for an uploaded image.

    Upload an image and get AI-generated captions based on your chosen theme/vibe.
    Supports multiple languages and themes (romantic, funny, badass, etc.)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=422,
            detail="Please upload a valid image file (JPEG, PNG, or WebP).",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=422,
            detail="Image size exceeds 5MB limit. Please upload a smaller image.",
        )

    if len(content) < 100:
        raise HTTPException(
            status_code=422,
            detail="The uploaded file appears to be empty or invalid.",
        )

    # Generate captions
    try:
        result = caption_service.generate_captions(
            image_content=content,
            theme=theme,
            language=language,
            count=count,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        error_msg = str(e).lower()
        if "api_key" in error_msg or "authentication" in error_msg or "api key" in error_msg:
            raise HTTPException(
                status_code=503, detail="Caption service is temporarily unavailable. Please try again later."
            ) from e
        if "rate_limit" in error_msg or "rate limit" in error_msg:
            raise HTTPException(
                status_code=429, detail="Too many requests. Please wait a moment and try again."
            ) from e
        raise HTTPException(
            status_code=500, detail="Failed to generate captions. Please try again."
        ) from e

    return JSONResponse(content=result)


@router.get("/themes")
async def get_themes():
    """Get available caption themes/vibes."""
    return {"themes": CaptionService.get_themes()}


@router.get("/languages")
async def get_languages():
    """Get available languages for caption generation."""
    return {"languages": CaptionService.get_languages()}
