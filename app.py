# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# Rota de saúde para o Render (GET)
@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200

# Rota principal - aceita GET (teste) e POST (webhook)
@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "GET":
        return "Servidor funcionando!", 200

    # POST: ler o JSON enviado
    data = {}
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        pass

    # Aceite tanto "message" quanto "text" (cobrir ReqBin e ManyChat)
    text = data.get("message") or data.get("text") or ""

    # Resposta no formato que você mapeou no ManyChat (JSONPath $.reply)
    resposta = f"Recebi: {text}" if text else "Mande uma mensagem no campo 'message' ou 'text'."
    return jsonify({"reply": resposta}), 200

# Opcional: para rodar localmente (não é usado no Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
