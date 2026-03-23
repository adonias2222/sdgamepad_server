from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    print("Recebeu GET /")
    return jsonify({"ok": True})

@app.route("/upload", methods=["POST"])
def upload():
    print("Recebeu POST /upload")

    if "file" not in request.files:
        print("Arquivo nao enviado")
        return jsonify({"ok": False, "error": "arquivo ausente"}), 400

    file = request.files["file"]

    print(f"Nome do arquivo: {file.filename}")
    print(f"Tipo: {file.mimetype}")

    return jsonify({
        "ok": True,
        "message": "upload route reached",
        "file_name": file.filename
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
