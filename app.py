import io
import os
import traceback
from flask import Flask, jsonify, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "").strip()

def get_drive_service():
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", "").strip()

    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID não configurado")
    if not client_secret:
        raise RuntimeError("GOOGLE_CLIENT_SECRET não configurado")
    if not refresh_token:
        raise RuntimeError("GOOGLE_REFRESH_TOKEN não configurado")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

@app.route("/")
def home():
    print("Recebeu GET /")
    return jsonify({"ok": True})

@app.route("/upload", methods=["POST"])
def upload():
    print("Recebeu POST /upload")

    try:
        total_count = request.form.get("total_count", "0")
        jpg_count = request.form.get("jpg_count", "0")
        png_count = request.form.get("png_count", "0")
        current_index = request.form.get("current_index", "0")

        print(f"Meta total_count: {total_count}")
        print(f"Meta jpg_count: {jpg_count}")
        print(f"Meta png_count: {png_count}")
        print(f"Meta current_index: {current_index}")

        if "file" not in request.files:
            return jsonify({"ok": False, "error": "arquivo ausente"}), 400

        file = request.files["file"]

        print(f"Nome do arquivo: {file.filename}")
        print(f"Tipo: {file.mimetype}")

        if not FOLDER_ID:
            raise RuntimeError("DRIVE_FOLDER_ID não configurado")

        file_bytes = file.read()
        drive_service = get_drive_service()

        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype=file.mimetype or "application/octet-stream",
            resumable=False,
        )

        metadata = {
            "name": file.filename,
            "parents": [FOLDER_ID],
        }

        created = drive_service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name"
        ).execute()

        print(f"Upload concluído no Drive: {created.get('id')}")

        return jsonify({
            "ok": True,
            "file_id": created.get("id"),
            "file_name": created.get("name"),
        })

    except Exception as e:
        print("ERRO 500 NO UPLOAD")
        print(str(e))
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
