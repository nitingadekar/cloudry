"""Text utility service — Base64, JSON, Color conversion, and Diff."""

import base64
import colorsys
import difflib
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

    # ── Diff ───────────────────────────────────────────────────────────────────

    def diff_texts(self, text1: str, text2: str, context_lines: int = 3) -> dict:
        """Compare two texts and return structured diff output.

        Args:
            text1: Original text (left side)
            text2: Modified text (right side)
            context_lines: Number of surrounding context lines (default 3)

        Returns:
            dict with unified diff, stats, and line-by-line changes
        """
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()

        # Generate unified diff (needs \n terminated lines)
        lines1_terminated = [line + "\n" for line in lines1]
        lines2_terminated = [line + "\n" for line in lines2]
        unified = list(
            difflib.unified_diff(
                lines1_terminated,
                lines2_terminated,
                fromfile="Original",
                tofile="Modified",
                n=context_lines,
            )
        )

        # Generate line-by-line changes for frontend rendering
        changes = []
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for line in lines1[i1:i2]:
                    changes.append({"type": "equal", "content": line})
            elif tag == "delete":
                for line in lines1[i1:i2]:
                    changes.append({"type": "removed", "content": line})
            elif tag == "insert":
                for line in lines2[j1:j2]:
                    changes.append({"type": "added", "content": line})
            elif tag == "replace":
                for line in lines1[i1:i2]:
                    changes.append({"type": "removed", "content": line})
                for line in lines2[j1:j2]:
                    changes.append({"type": "added", "content": line})

        # Calculate stats
        added = sum(1 for c in changes if c["type"] == "added")
        removed = sum(1 for c in changes if c["type"] == "removed")
        unchanged = sum(1 for c in changes if c["type"] == "equal")

        # Similarity ratio
        ratio = difflib.SequenceMatcher(None, text1, text2).ratio()

        result = {
            "unified_diff": "".join(unified),
            "changes": changes,
            "stats": {
                "added": added,
                "removed": removed,
                "unchanged": unchanged,
                "total_lines_original": len(lines1),
                "total_lines_modified": len(lines2),
                "similarity": round(ratio * 100, 1),
            },
            "identical": text1 == text2,
        }

        logger.info(
            "Diff computed",
            extra={"added": added, "removed": removed, "similarity": f"{ratio * 100:.1f}%"},
        )
        return result
