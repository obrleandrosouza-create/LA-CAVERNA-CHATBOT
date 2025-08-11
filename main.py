from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Página inicial (só para ver que está no ar)
@app.get("/")
def home():
    return "Chatbot La Caverna rodando com sucesso!"

# Saude do servidor (teste rápido)
@app.get("/health")
def health():
    return "ok", 200

# >>> AQUI É A PORTA QUE O MANYCHAT VAI USAR <<<
@app.post("/webhook")
def webhook():
    # Tenta pegar o JSON enviado pelo ManyChat
    data = request.get_json(force=True, silent=True) or {}

    # Pega nome e texto (se vierem com outros nomes, tentamos variações)
    name = data.get("name") or data.get("first_name") or "visitante"
    text = data.get("text") or data.get("message") or ""

    # Monta a resposta que o bot vai devolver
    reply = f"Olá {name}! Você disse: {text}".strip()

    # Devolve um JSON para o ManyChat
    return jsonify({"reply": reply}), 200

if __name__ == "__main__":
    # Render define a porta em uma variável de ambiente chamada PORT
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
