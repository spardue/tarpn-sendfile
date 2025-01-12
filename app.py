from fastapi import FastAPI, File, UploadFile, Form
import base64
import magic  # Requires `pip install python-magic`
from typing import List

from tarpn_sendfile import send_over_rf
from process_mes_files import process_mes_files_to_base64

from fastapi.responses import HTMLResponse
from jinja2 import Template

app = FastAPI()

def encode_file(file_bytes, filename, note):
    """Encodes a file in Base85 and detects its MIME type."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_bytes)  # Detect from content
    encoded_content = base64.b85encode(file_bytes).decode("ascii")

    return {
        "filename": filename,
        "mimetype": mime_type,
        "body": encoded_content,
        "note": note
    }

@app.post("/send_file/")
async def send_file(to: List[str] = Form(...), note: str = Form(...), file: UploadFile = File(...)):
    """Handles file uploads and returns Base85-encoded content."""
    file_bytes = await file.read()
    encoded_data = encode_file(file_bytes, file.filename, note)
    send_over_rf(encoded_data, to)
    return encoded_data

@app.get("/feed")
async def feed():
    return process_mes_files_to_base64()

# Jinja2 HTML Template
html_template = """
    <div class="card">
        <h2>Filename: {{ filename }}</h2>
        <p><strong>Note:</strong> {{ note }}</p>
        <p><strong>MIME Type:</strong> {{ mimetype }}</p>
        <p><strong>Decoded Content:</strong></p>
        <pre>{{ content }}</pre>
    </div>
"""

@app.get("/", response_class=HTMLResponse)
async def display_feed():
    messages = process_mes_files_to_base64()
    rendered_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>JSON Feed</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; }
                .card { border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
                pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>Data Feed</h1>
    """
    for data in messages:
        content_decoded = base64.b64decode(data["content_base64"]).decode("utf-8", errors="ignore")

    # Render HTML using Jinja2
        template = Template(html_template)
        rendered_html += template.render(
            filename=data["filename"],
            note=data["note"],
            mimetype=data["mimetype"],
            content=content_decoded
        )
    rendered_html += "</body></html>"

    return HTMLResponse(content=rendered_html)
