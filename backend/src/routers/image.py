"""Image tool endpoints."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from src.middleware.captcha import verify_turnstile
from src.services.image_service import ImageService

router = APIRouter()
image_service = ImageService()


@router.post("/to-pdf", dependencies=[Depends(verify_turnstile)])
async def images_to_pdf(files: list[UploadFile] = File(...)):
    """Convert one or more images to a single PDF file."""
    contents = [await f.read() for f in files]
    result = image_service.to_pdf(contents)
    return StreamingResponse(
        result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=images.pdf"},
    )


@router.post("/compress", dependencies=[Depends(verify_turnstile)])
async def compress_image(file: UploadFile = File(...), quality: int = Form(default=75)):
    """Compress an image to reduce file size.

    Quality: 1-95 (lower = smaller file, lower quality). Default: 75.
    """
    content = await file.read()
    result, media_type = image_service.compress(content, file.filename or "image.jpg", quality)
    return StreamingResponse(
        result,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"},
    )


@router.post("/resize", dependencies=[Depends(verify_turnstile)])
async def resize_image(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...),
):
    """Resize an image to specified dimensions."""
    content = await file.read()
    result, media_type = image_service.resize(content, file.filename or "image.jpg", width, height)
    return StreamingResponse(
        result,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=resized_{file.filename}"},
    )


@router.post("/convert", dependencies=[Depends(verify_turnstile)])
async def convert_image(file: UploadFile = File(...), target_format: str = Form(...)):
    """Convert image to a different format (png, jpg, webp, bmp, gif)."""
    content = await file.read()
    result, media_type, ext = image_service.convert_format(content, target_format)
    filename = file.filename or "image"
    base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
    return StreamingResponse(
        result,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={base_name}.{ext}"},
    )
