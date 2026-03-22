import io
import json
import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")

def get_drive_service():
    info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

@app.route("/")
def home():
    return jsonify({"ok": True})

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"ok": False}), 400

    file = request.files["file"]

    drive = get_drive_service()

    media = MediaIoBaseUpload(
        io.BytesIO(file.read()),
        mimetype=file.mimetype
    )

    file_metadata = {
        "name": file.filename,
        "parents": [FOLDER_ID]
    }

    uploaded = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return jsonify({"ok": True, "id": uploaded["id"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
