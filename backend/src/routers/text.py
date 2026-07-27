"""Text utility endpoints — Base64, JSON, Color conversion."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.middleware.captcha import verify_turnstile
from src.services.text_service import TextService

router = APIRouter()
text_service = TextService()


@router.post("/base64/encode", dependencies=[Depends(verify_turnstile)])
async def base64_encode(text: str = Form(default=None), file: UploadFile = File(default=None)):
    """Encode text or file to Base64.

    Provide either 'text' (form field) or 'file' (upload), not both.
    """
    if file:
        content = await file.read()
    elif text:
        content = text.encode("utf-8")
    else:
        return {"error": "Provide either 'text' or 'file'"}

    encoded = text_service.base64_encode(content)
    return {"encoded": encoded, "input_size": len(content), "output_size": len(encoded)}


@router.post("/base64/decode", dependencies=[Depends(verify_turnstile)])
async def base64_decode(encoded: str = Form(...)):
    """Decode a Base64 string back to text."""
    decoded = text_service.base64_decode(encoded)
    try:
        text_output = decoded.decode("utf-8")
        return {"decoded": text_output, "is_text": True, "size": len(decoded)}
    except UnicodeDecodeError:
        return {
            "decoded": None,
            "is_text": False,
            "size": len(decoded),
            "message": "Binary content, cannot display as text",
        }


@router.post("/json/format", dependencies=[Depends(verify_turnstile)])
async def json_format(content: str = Form(...)):
    """Pretty-print JSON with 2-space indentation."""
    formatted = text_service.json_format(content)
    return {"formatted": formatted}


@router.post("/json/validate", dependencies=[Depends(verify_turnstile)])
async def json_validate(content: str = Form(...)):
    """Validate JSON syntax."""
    result = text_service.json_validate(content)
    return result


@router.post("/color/convert", dependencies=[Depends(verify_turnstile)])
async def color_convert(color: str = Form(...), to_format: str = Form(...)):
    """Convert color between hex, rgb, and hsl formats.

    Examples:
    - color="#ff5733", to_format="rgb" → "rgb(255, 87, 51)"
    - color="255,87,51", to_format="hex" → "#ff5733"
    - color="#ff5733", to_format="hsl" → "hsl(11, 100%, 60%)"
    """
    result = text_service.color_convert(color, to_format)
    return result
