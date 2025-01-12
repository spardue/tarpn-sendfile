from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, Response, RedirectResponse
import base64
import magic  # Requires `pip install python-magic`
from typing import List
from jinja2 import Template

from tarpn_sendfile import send_over_rf, CALL_SIGN
from process_mes_files import process_mes_files_to_base64

app = FastAPI()

# Jinja2 HTML Template
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
            <label>To (comma-separated call signs):</label><br>
            <input type="text" name="to" required><br><br>
            <label>Note:</label><br>
            <input type="text" name="note" required><br><br>
            <label>Please only upload small files. For images use .avif file with the quality reduced up to 10 percent.</label>
            <pre>sudo apt install gimp</pre>
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

                {% if file.filename.endswith('.avif') %}
                    <p><strong>Image Preview:</strong></p>
                    <img src="data:image/avif;base64,{{ file.body }}" alt="Uploaded Image" width="300">
                {% endif %}

                <br>
                <a href="/download/{{ file.filename }}" class="download-btn">Download File</a>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def upload_page():
    """Renders the HTML page with uploaded files."""
    template = Template(html_template)
    uploaded_files = process_mes_files_to_base64()
    rendered_html = template.render(files=uploaded_files)
    return HTMLResponse(content=rendered_html)

@app.post("/upload/")
async def upload_file(
    to: str = Form(...),
    note: str = Form(...),
    file: UploadFile = File(...)
):
    """Handles file uploads and stores metadata."""
    file_bytes = await file.read()
    encoded_content = base64.b85encode(file_bytes).decode("utf-8")
    to_list = to.split(",")

    data = {
        "filename": file.filename,
        "to": to,
        "mimetype": file.content_type,
        "body": encoded_content,
        "from": CALL_SIGN,
        "note": note
    }

    send_over_rf(data, to_list)

    return RedirectResponse(url="/", status_code=303)

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Retrieves and decodes files from the stored .msg messages and returns them as binary."""
    uploaded_files = process_mes_files_to_base64()
    
    for file in uploaded_files:
        if file["filename"] == filename:
            decoded_bytes = base64.b64decode(file["body"])  # Decode Base85 back to binary
            mime_type = file["mimetype"]  # Use the stored MIME type
            
            return Response(content=decoded_bytes, media_type=mime_type, headers={
                "Content-Disposition": f"attachment; filename={filename}"
            })

    return HTMLResponse(content="File not found", status_code=404)

