import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# --- Configuração do cliente OpenAI ---
# Defina a variável de ambiente OPENAI_API_KEY no Render
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY)

# Contexto base fixo do restaurante (reforça a IA a não inventar)
BASE_CONTEXT = (
    "Você é a La Caverna Assistente Virtual, atendente oficial do restaurante La Caverna Fondue, "
    "localizado na Av. Conde Figueira, 332, Morada do Vale 1, Gravataí - RS. "
    "Responda sempre em português do Brasil, de forma educada, cordial, clara e objetiva. "
    "Use apenas as informações reais do restaurante (horários, preços, reservas, endereço, cardápio e regras). "
    "Se não souber, diga: 'Vou verificar essa informação e retorno para você o mais rápido possível.' "
    "Evite informações inventadas. Prefira parágrafos curtos e, quando fizer sentido, use 1 emoji discreto."
)

def build_messages(user_message: str, extra_context: str = ""):
    """
    Monta o prompt para o ChatGPT:
    - system: regras + contexto fixo
    - user: mensagem do cliente + contexto enviado pelo ManyChat
    """
    context = BASE_CONTEXT
    if extra_context:
        context += f"\n\nInformações adicionais: {extra_context.strip()}"

    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_message.strip() if user_message else "Sem mensagem."}
    ]
    return messages

@app.route("/", methods=["GET"])
def home():
    return "Chatbot La Caverna rodando com sucesso!", 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Espera um JSON similar a:
    {
      "source": "manychat",
      "platform": "whatsapp",
      "contact_id": "123",
      "name": "Leandro",
      "message": "Quais os valores?",
      "context": "… (opcional, vindo do ManyChat) ..."
    }
    Retorna: {"reply": "texto"}
    """
    try:
        if not OPENAI_API_KEY:
            return jsonify({"reply": "Chave da OpenAI ausente no servidor."}), 200

        data = request.get_json(force=True, silent=True) or {}
        user_name = data.get("name", "").strip()
        user_message = data.get("message", "") or ""
        extra_context = data.get("context", "") or ""

        # Se veio vazio, evita erro
        if not user_message.strip():
            user_message = "Olá! Gostaria de informações do restaurante (valores, reservas, endereço e horários)."

        # Monta as mensagens para a IA
        messages = build_messages(user_message=user_message, extra_context=extra_context)

        # Chamada ao ChatGPT
        completion = client.chat.completions.create(
            model="gpt-4o-mini",            # leve e barato; pode trocar por outro compatível
            messages=messages,
            temperature=0.3,                # respostas mais estáveis
            max_tokens=350,                 # limite razoável para WhatsApp
        )

        ai_text = completion.choices[0].message.content.strip()

        # (Opcional) Personaliza saudação quando souber o nome
        if user_name:
            # Só adiciona saudação curta no início se fizer sentido
            ai_text = f"Olá {user_name}! {ai_text}"

        return jsonify({"reply": ai_text}), 200

    except Exception as e:
        # Nunca quebre o ManyChat; devolve fallback amigável
        return jsonify({
            "reply": "Desculpe, tive um imprevisto técnico agora. Pode repetir sua pergunta ou tentar novamente em instantes? 🙏"
        }), 200


if __name__ == "__main__":
    # Para teste local: python main.py
    app.run(host="0.0.0.0", port=5000)
