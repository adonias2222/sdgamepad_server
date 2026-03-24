import os
import traceback
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Link do seu PC exposto pelo ngrok
PC_UPLOAD_URL = "https://5802-179-48-36-29.ngrok-free.app/upload"
PC_HEALTH_URL = "https://5802-179-48-36-29.ngrok-free.app/"

@app.route("/")
def home():
    print("[RENDER] Recebeu GET /")
    return jsonify({
        "ok": True,
        "service": "sdgamepad-backup",
        "pc_upload_url": PC_UPLOAD_URL
    })

@app.route("/upload", methods=["POST"])
def upload():
    print("\n========== NOVO UPLOAD ==========")

    try:
        total_count = request.form.get("total_count", "0")
        jpg_count = request.form.get("jpg_count", "0")
        png_count = request.form.get("png_count", "0")
        current_index = request.form.get("current_index", "0")
        file_name_meta = request.form.get("file_name", "")

        print(f"[META] total_count: {total_count}")
        print(f"[META] jpg_count: {jpg_count}")
        print(f"[META] png_count: {png_count}")
        print(f"[META] current_index: {current_index}")
        print(f"[META] file_name: {file_name_meta}")

        if "file" not in request.files:
            print("[ERRO] arquivo ausente")
            return jsonify({"ok": False, "error": "arquivo ausente"}), 400

        file = request.files["file"]

        if not file.filename:
            print("[ERRO] nome de arquivo vazio")
            return jsonify({"ok": False, "error": "nome de arquivo vazio"}), 400

        file_bytes = file.read()

        print(f"[FILE] Nome do arquivo: {file.filename}")
        print(f"[FILE] Tipo: {file.mimetype}")
        print(f"[FILE] Tamanho: {len(file_bytes)} bytes")

        print("[RENDER] Testando conexão com o PC...")
        health = requests.get(PC_HEALTH_URL, timeout=20)
        print(f"[RENDER] Health do PC: {health.status_code} - {health.text}")

        if health.status_code != 200:
            return jsonify({
                "ok": False,
                "error": f"PC offline ou health inválido: {health.status_code}"
            }), 502

        print("[RENDER] Encaminhando arquivo para o PC via ngrok...")

        files = {
            "file": (
                file.filename,
                file_bytes,
                file.mimetype or "application/octet-stream"
            )
        }

        data = {
            "total_count": total_count,
            "jpg_count": jpg_count,
            "png_count": png_count,
            "current_index": current_index,
            "file_name": file_name_meta,
        }

        pc_response = requests.post(
            PC_UPLOAD_URL,
            files=files,
            data=data,
            timeout=120
        )

        print(f"[RENDER] Resposta do PC: {pc_response.status_code}")
        print(f"[RENDER] Corpo do PC: {pc_response.text}")

        if pc_response.status_code < 200 or pc_response.status_code >= 300:
            return jsonify({
                "ok": False,
                "error": f"Falha ao enviar para o PC: {pc_response.status_code}",
                "pc_body": pc_response.text
            }), 502

        print("[RENDER] Upload concluído com sucesso no PC.")
        print("=================================\n")

        return jsonify({
            "ok": True,
            "message": "arquivo encaminhado para o PC com sucesso",
            "file_name": file.filename,
            "pc_status": pc_response.status_code
        })

    except requests.Timeout:
        print("[ERRO] Timeout ao conectar no PC/ngrok")
        print("=================================\n")
        return jsonify({
            "ok": False,
            "error": "timeout ao conectar no PC/ngrok"
        }), 504

    except Exception as e:
        print("[ERRO 500 NO RENDER]")
        print(str(e))
        print(traceback.format_exc())
        print("=================================\n")
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
