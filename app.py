from fastapi import FastAPI, File, UploadFile, Form
import base64
import magic  # Requires `pip install python-magic`
from typing import List

from tarpn_sendfile import send_over_rf

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

