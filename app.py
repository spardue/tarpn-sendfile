from fastapi import FastAPI, File, UploadFile, Form
import base64
import magic  # Requires `pip install python-magic`
from typing import List

from tarpn_sendfile import send_over_rf, CALL_SIGN
from process_mes_files import process_mes_files_to_base64

from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
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
        "note": note,
        "from": CALL_SIGN
    }
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Upload</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; }
        .container { max-width: 600px; margin: auto; }
        .card { border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .download-btn { display: inline-block; padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload a File</h1>
        <form action="/upload/" method="post" enctype="multipart/form-data">
            <label>To (comma-separated emails):</label><br>
            <input type="text" name="to" required><br><br>
            <label>Note:</label><br>
            <input type="text" name="note" required><br><br>
            <label>Please only upload small files. For images use .avif file with the quality reduced up to 10 percent. This can be done in gnome. To install gnome on your pi run the following linux command on your pi: </label>
            <pre>
            sudo apt install gimp
            </pre>
            <br>
            <br>
            <input type="file" name="file" required>
            <br><br>
            <button type="submit">Upload</button>
        </form>
        <hr>
        <h2>Uploaded Files</h2>
        {% for file in files %}
            <div class="card">
                <h2>Filename: {{ file.filename }}</h2>
                <p><strong>To:</strong> {{ file.to }}</p>
                <p><strong>From:</strong> {{ file.from.upper() }}</p>
                <p><strong>Note:</strong> {{ file.note }}</p>
                <p><strong>Decoded Content:</strong></p>

                {% if file.filename.endswith('.avif') %}
                    <img src="data:image/avif;base64,{{ file.body }}" alt="Uploaded Image" width="300">
                {% elif file.filename.endswith('.txt') %}
                    
                    <pre id="txtContent"></pre>
                    <script>
                        const data = atob('{{ file.body }}');
                        document.getElementById('txtContent').textContent = data;
                    </script>
                {% else %}
                    <p>Download</p>
                {% endif %}
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def upload_page():
    template = Template(html_template)
    uploaded_files = process_mes_files_to_base64()
    rendered_html = template.render(files=uploaded_files)
    return HTMLResponse(content=rendered_html)

@app.post("/upload/")
async def upload_file(
    to: str = Form(...),  # Accepts comma-separated recipients
    note: str = Form(...),
    file: UploadFile = File(...)
):
    """Handles file uploads and stores metadata."""
    file_bytes = await file.read()
    encoded_content = base64.b85encode(file_bytes).decode("utf-8")
    toList = to.split(",")

    data = {
        "filename": file.filename,
        "to": to,  # Store as a string for now
        "mimetype": file.content_type,
        "body": encoded_content,
        "from": CALL_SIGN,
        "note": note
    }

    send_over_rf(data, toList)

    return RedirectResponse(url="/", status_code=303)
