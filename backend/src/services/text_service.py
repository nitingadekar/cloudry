"""Text utility service — Base64, JSON, and Color conversion."""

import base64
import colorsys
import json
import re

from src.logging_config import get_logger

logger = get_logger("text_service")


class TextService:
    """Handles text-related utility operations."""

    # ── Base64 ─────────────────────────────────────────────────────────────────

    def base64_encode(self, content: bytes) -> str:
        """Encode bytes to base64 string."""
        encoded = base64.b64encode(content).decode("utf-8")
        logger.info("Base64 encoded", extra={"input_size": len(content)})
        return encoded

    def base64_decode(self, encoded: str) -> bytes:
        """Decode base64 string to bytes."""
        try:
            decoded = base64.b64decode(encoded)
        except Exception:
            raise ValueError("Invalid base64 input") from None
        logger.info("Base64 decoded", extra={"output_size": len(decoded)})
        return decoded

    # ── JSON ───────────────────────────────────────────────────────────────────

    def json_format(self, content: str) -> str:
        """Pretty-print JSON string with 2-space indentation."""
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from None
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        logger.info("JSON formatted")
        return formatted

    def json_validate(self, content: str) -> dict:
        """Validate JSON and return status."""
        try:
            json.loads(content)
            return {"valid": True, "error": None}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}

    # ── Color ──────────────────────────────────────────────────────────────────

    def color_convert(self, color: str, to_format: str) -> dict:
        """Convert color between hex, rgb, and hsl formats.

        Accepts:
        - HEX: "#ff5733" or "ff5733"
        - RGB: "rgb(255, 87, 51)" or "255,87,51"
        - HSL: "hsl(11, 100%, 60%)" or "11,100,60"
        """
        r, g, b = self._parse_color(color)
        to_format = to_format.lower().strip()

        result = {"input": color, "r": r, "g": g, "b": b}

        if to_format == "hex":
            result["output"] = f"#{r:02x}{g:02x}{b:02x}"
        elif to_format == "rgb":
            result["output"] = f"rgb({r}, {g}, {b})"
        elif to_format == "hsl":
            hue, lightness, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            result["output"] = f"hsl({int(hue * 360)}, {int(saturation * 100)}%, {int(lightness * 100)}%)"
        else:
            raise ValueError(f"Unsupported target format: {to_format}. Use hex, rgb, or hsl.")

        logger.info("Color converted", extra={"to_format": to_format})
        return result

    def _parse_color(self, color: str) -> tuple[int, int, int]:
        """Parse a color string into (r, g, b) values."""
        color = color.strip()

        # HEX format: #ff5733 or ff5733
        hex_match = re.match(r"^#?([0-9a-fA-F]{6})$", color)
        if hex_match:
            hex_str = hex_match.group(1)
            return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)

        # RGB format: rgb(255, 87, 51) or 255,87,51
        rgb_match = re.match(r"^(?:rgb\()?\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)?$", color)
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            if all(0 <= v <= 255 for v in (r, g, b)):
                return r, g, b

        # HSL format: hsl(11, 100%, 60%) or 11,100,60
        hsl_match = re.match(r"^(?:hsl\()?\s*(\d{1,3})\s*,\s*(\d{1,3})%?\s*,\s*(\d{1,3})%?\s*\)?$", color)
        if hsl_match:
            hue, sat, lit = int(hsl_match.group(1)), int(hsl_match.group(2)), int(hsl_match.group(3))
            r, g, b = colorsys.hls_to_rgb(hue / 360, lit / 100, sat / 100)
            return int(r * 255), int(g * 255), int(b * 255)

        raise ValueError(f"Cannot parse color: {color}. Use hex (#ff5733), rgb (255,87,51), or hsl (11,100,60).")
