from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# --- CONFIG --- coloque sua chave:
openai.api_key = os.environ["OPENAI_API_KEY"]


@app.route("/", methods=["GET"])
def health():
    return "La Caverna bot está no ar ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True) or {}
        text = (data.get("text") or "").strip()

        if not text:
            return jsonify({"reply": "Pode me enviar sua dúvida? 🙂"}), 200

        # Chamada ao ChatGPT
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role":
                "system",
                "content":
                "Você é um atendente simpático do restaurante La Caverna. Responda com clareza sobre reservas, cardápio, horários, localização e dúvidas frequentes."
            }, {
                "role": "user",
                "content": text
            }],
            temperature=0.4)
        answer = completion.choices[0].message["content"].strip()

        # >>> formato que o ManyChat espera <<<
        return jsonify({"reply": answer}), 200

    except Exception as e:
        # fallback amigável
        return jsonify({
            "reply":
            "Desculpa, tive um probleminha técnico agora. Pode repetir a pergunta ou tentar novamente em instantes?"
        }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
