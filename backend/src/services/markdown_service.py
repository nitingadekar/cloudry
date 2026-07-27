"""Markdown to PDF conversion service."""

import io

import markdown
import weasyprint

from src.logging_config import get_logger

logger = get_logger("markdown_service")

# Simple, clean CSS for PDF output
PDF_CSS = """
body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #333;
    max-width: 700px;
    margin: 40px auto;
    padding: 0 20px;
}
h1 { font-size: 24pt; margin-top: 30px; color: #111; }
h2 { font-size: 18pt; margin-top: 25px; color: #222; }
h3 { font-size: 14pt; margin-top: 20px; color: #333; }
code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10pt;
}
pre {
    background: #f4f4f4;
    padding: 12px;
    border-radius: 5px;
    overflow-x: auto;
}
pre code { background: none; padding: 0; }
blockquote {
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 15px;
    color: #666;
}
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #f8f8f8; font-weight: bold; }
"""


class MarkdownService:
    """Handles Markdown to PDF conversion."""

    def to_pdf(self, content: str, title: str = "Document") -> io.BytesIO:
        """Convert Markdown text to a styled PDF.

        Pipeline: Markdown → HTML → PDF (via WeasyPrint).
        """
        if not content.strip():
            raise ValueError("Markdown content cannot be empty")

        # Convert Markdown to HTML
        html_body = markdown.markdown(
            content,
            extensions=["tables", "fenced_code", "codehilite", "toc"],
        )

        # Wrap in full HTML document
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>{PDF_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

        # Convert HTML to PDF
        output = io.BytesIO()
        weasyprint.HTML(string=html).write_pdf(output)
        output.seek(0)

        logger.info("Markdown converted to PDF", extra={"title": title, "content_length": len(content)})
        return output
