import traceback
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

PC_UPLOAD_URL = "https://e3aa-179-48-36-29.ngrok-free.app/upload"
PC_HEALTH_URL = "https://e3aa-179-48-36-29.ngrok-free.app/"

@app.route("/")
def home():
    print("[RENDER] Recebeu GET /")
    return jsonify({"ok": True})

@app.route("/upload", methods=["POST"])
def upload():
    print("\n[RENDER] ===== NOVO UPLOAD =====")
    try:
        if "file" not in request.files:
            print("[RENDER] arquivo ausente")
            return jsonify({"ok": False, "error": "arquivo ausente"}), 400

        file = request.files["file"]
        file_bytes = file.read()

        print(f"[RENDER] Nome: {file.filename}")
        print(f"[RENDER] Tipo: {file.mimetype}")
        print(f"[RENDER] Tamanho: {len(file_bytes)} bytes")

        print("[RENDER] Testando health do PC...")
        health = requests.get(PC_HEALTH_URL, timeout=30)
        print(f"[RENDER] Health status: {health.status_code}")
        print(f"[RENDER] Health body: {health.text[:300]}")

        print("[RENDER] Enviando pro PC...")
        pc_response = requests.post(
            PC_UPLOAD_URL,
            files={
                "file": (
                    file.filename,
                    file_bytes,
                    file.mimetype or "application/octet-stream"
                )
            },
            timeout=300
        )

        print(f"[RENDER] Resposta PC status: {pc_response.status_code}")
        print(f"[RENDER] Resposta PC body: {pc_response.text[:500]}")
        print("[RENDER] ===== FIM UPLOAD =====\n")

        return (
            pc_response.text,
            pc_response.status_code,
            {"Content-Type": pc_response.headers.get("Content-Type", "application/json")},
        )

    except Exception as e:
        print("[RENDER] ERRO:", str(e))
        print(traceback.format_exc())
        print("[RENDER] ===== FALHA UPLOAD =====\n")
        return jsonify({"ok": False, "error": str(e)}), 500
