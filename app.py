import io
import json
import os
import traceback
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = Flask(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "").strip()

def get_drive_service():
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON não configurado")

    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=creds)

@app.get("/")
def health():
    print("[SERVER] Health check recebido")
    return jsonify({"ok": True, "service": "sdgamepad-backup"})

@app.post("/upload")
def upload():
    print("\n========== NOVO UPLOAD ==========")
    print(f"[REQUEST] Content-Type: {request.content_type}")
    print(f"[REQUEST] Remote addr: {request.remote_addr}")

    try:
        total_count = request.form.get("total_count", "0")
        jpg_count = request.form.get("jpg_count", "0")
        png_count = request.form.get("png_count", "0")
        current_index = request.form.get("current_index", "0")
        client_file_name = request.form.get("file_name", "")

        print(f"[META] current_index: {current_index}")
        print(f"[META] total_count: {total_count}")
        print(f"[META] jpg_count: {jpg_count}")
        print(f"[META] png_count: {png_count}")
        print(f"[META] client_file_name: {client_file_name}")

        if "file" not in request.files:
            print("[ERRO] Campo 'file' ausente no request.files")
            return jsonify({"ok": False, "error": "arquivo ausente"}), 400

        file = request.files["file"]

        if not file.filename:
            print("[ERRO] Nome de arquivo vazio")
            return jsonify({"ok": False, "error": "nome de arquivo vazio"}), 400

        if not FOLDER_ID:
            print("[ERRO] DRIVE_FOLDER_ID não configurado")
            return jsonify({"ok": False, "error": "DRIVE_FOLDER_ID não configurado"}), 500

        file_bytes = file.read()
        file_size = len(file_bytes)

        print(f"[FILE] filename: {file.filename}")
        print(f"[FILE] mimetype: {file.mimetype}")
        print(f"[FILE] size: {file_size} bytes")
        print("[SERVER] Conectou e recebeu o arquivo, iniciando upload no Drive...")

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
            fields="id,name,parents",
        ).execute()

        print(f"[SUCESSO] Upload concluído")
        print(f"[SUCESSO] Drive file id: {created.get('id')}")
        print("=================================\n")

        return jsonify({
            "ok": True,
            "fileId": created.get("id"),
            "name": created.get("name"),
            "currentIndex": current_index,
            "totalCount": total_count,
        })

    except Exception as e:
        print("[ERRO 500] Falha durante o upload")
        print(f"[ERRO 500] Mensagem: {str(e)}")
        print(traceback.format_exc())
        print("=================================\n")
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
