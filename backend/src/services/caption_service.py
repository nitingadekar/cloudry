"""Social caption generator service using Groq multimodal API."""

import base64
import io

from groq import Groq
from PIL import Image

from src.config import settings
from src.logging_config import get_logger

logger = get_logger("caption_service")

# Available caption themes/vibes
THEMES = [
    "romantic",
    "poetic",
    "funny",
    "sarcastic",
    "badass",
    "motivational",
    "devotional",
    "naughty",
    "catchy",
    "aesthetic",
    "savage",
    "deep",
    "foodie",
    "travel",
    "fitness",
    "party",
    "chill",
    "nostalgic",
    "festive",
]

# Supported languages
LANGUAGES = [
    "English",
    "Hindi",
    "Marathi",
    "Tamil",
    "Telugu",
    "Bengali",
    "Punjabi",
    "Gujarati",
    "Spanish",
    "French",
    "Portuguese",
    "Arabic",
]

# Vision model for image understanding + caption generation
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


class CaptionService:
    """Generates creative social media captions from images using Groq API."""

    def __init__(self):
        self._client: Groq | None = None

    @property
    def client(self) -> Groq:
        """Lazy-initialize Groq client."""
        if self._client is None:
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is not configured")
            self._client = Groq(api_key=settings.groq_api_key)
        return self._client

    def generate_captions(
        self,
        image_content: bytes,
        theme: str = "catchy",
        language: str = "English",
        count: int = 3,
    ) -> dict:
        """Generate creative captions for an uploaded image.

        Args:
            image_content: Raw image bytes (JPEG/PNG/WebP)
            theme: Caption vibe/theme (e.g., romantic, funny, badass)
            language: Language for captions
            count: Number of captions to generate (2-5)

        Returns:
            dict with 'description' and 'captions' list
        """
        # Validate theme
        theme = theme.lower()
        if theme not in THEMES:
            raise ValueError(f"Invalid theme '{theme}'. Available: {', '.join(THEMES)}")

        # Validate language
        if language not in LANGUAGES:
            raise ValueError(f"Invalid language '{language}'. Available: {', '.join(LANGUAGES)}")

        # Clamp count
        count = max(2, min(5, count))

        # Preprocess image (resize for API efficiency)
        image_base64 = self._prepare_image(image_content)

        # Generate captions using Groq vision API
        prompt = self._build_prompt(theme, language, count)

        response = self.client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )

        # Parse response
        raw_text = response.choices[0].message.content
        result = self._parse_response(raw_text, theme, language)

        logger.info(
            "Captions generated",
            extra={"theme": theme, "language": language, "count": len(result["captions"])},
        )
        return result

    def _prepare_image(self, content: bytes) -> str:
        """Resize image and convert to base64 for API efficiency.

        Resizes to max 1024px on longest side to reduce token usage.
        """
        img = Image.open(io.BytesIO(content))

        # Convert RGBA to RGB (JPEG doesn't support alpha)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        # Resize if larger than 1024px
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.LANCZOS)

        # Encode as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _build_prompt(self, theme: str, language: str, count: int) -> str:
        """Build the prompt for caption generation."""
        language_instruction = ""
        if language != "English":
            language_instruction = (
                f" Write the captions in {language} language (use {language} script). "
                "Do NOT transliterate — write in the native script."
            )

        return f"""Look at this image and generate {count} creative social media captions with a "{theme}" vibe.{language_instruction}

Rules:
- Each caption should be under 200 characters
- Make them Instagram/social media ready
- Include relevant emojis
- Be creative and original
- No hashtags (user will add their own)

Respond in this exact format:
DESCRIPTION: [One line describing what's in the image]
CAPTION 1: [first caption]
CAPTION 2: [second caption]
CAPTION 3: [third caption]"""

    def _parse_response(self, raw_text: str, theme: str, language: str) -> dict:
        """Parse the AI response into structured data."""
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]

        description = ""
        captions = []

        for line in lines:
            if line.upper().startswith("DESCRIPTION:"):
                description = line.split(":", 1)[1].strip()
            elif line.upper().startswith("CAPTION"):
                # Handle "CAPTION 1:", "CAPTION 2:", etc.
                parts = line.split(":", 1)
                if len(parts) > 1:
                    caption = parts[1].strip()
                    if caption:
                        captions.append(caption)

        # Fallback if parsing fails — use the whole response
        if not captions:
            captions = [raw_text.strip()]

        return {
            "description": description or "Image analyzed",
            "captions": captions,
            "theme": theme,
            "language": language,
        }

    @staticmethod
    def get_themes() -> list[str]:
        """Return available caption themes."""
        return THEMES

    @staticmethod
    def get_languages() -> list[str]:
        """Return available languages."""
        return LANGUAGES
