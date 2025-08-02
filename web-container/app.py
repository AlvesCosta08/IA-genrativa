from flask import Flask, render_template, request, jsonify
import re
import ollama

app = Flask(__name__)

# Detecta se a pergunta é de tema jurídico
def eh_tema_juridico(texto):
    palavras_chave = [
        "divórcio", "pensão", "trabalhista", "carteira assinada", "justa causa", "indenização",
        "direito", "advogado", "jurídico", "ação", "processo", "audiência", "penal", "imóvel",
        "contrato", "dano moral", "aluguel", "propriedade", "guarda", "união estável", "inventário"
    ]
    return any(palavra in texto.lower() for palavra in palavras_chave)

# Gera botão de WhatsApp com mensagem pronta
def botao_whatsapp(texto, mensagem):
    return f'<a href="https://wa.me/5511999999999?text={mensagem}" class="whatsapp-btn" target="_blank">{texto}</a>'

# Chama o modelo LLM (Ollama)
def perguntar(pergunta):
    try:
        prompt = f"""Você é um advogado brasileiro. Responda de forma clara, objetiva e juridicamente correta.
Classifique a pergunta em uma das seguintes especialidades:
- Família
- Trabalhista
- Consumidor
- Imobiliário
- Penal
- Trânsito
- Cível

Pergunta: {pergunta}

Retorne exatamente neste formato JSON:
{{
  "especialidade": "<Área do Direito>",
  "resposta": "<Resposta objetiva>"
}}"""

        resposta = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        return eval(resposta["message"]["content"])  # ou use json.loads se retornar string JSON válida
    except Exception as e:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    pergunta = data.get("pergunta", "").strip()

    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."})

    p = pergunta.lower()

    if eh_tema_juridico(pergunta):
        # Respostas rápidas
        if any(word in p for word in ["sair", "tchau", "obrigado", "até logo", "vlw", "valeu"]):
            return jsonify({"resposta": "Foi um prazer ajudar! Entre em contato sempre que precisar. 👋"})

        if p in ["oi", "olá", "oie", "bom dia", "boa tarde", "boa noite", "hello", "e aí", "eaí"]:
            return jsonify({
                "resposta": (
                    "Olá! Sou o assistente jurídico do <b>Dr. Legal</b>.<br>"
                    "Posso te ajudar com dúvidas sobre:<br>"
                    "⚖️ Divórcio | 💼 Trabalho | 🚗 Acidentes | 🏠 Imóveis | 💳 Consumidor<br><br>"
                    f"{botao_whatsapp('💬 Iniciar atendimento', 'Olá, gostaria de iniciar um atendimento jurídico.')}"
                )
            })

        if any(word in p for word in ["contato", "telefone", "email", "endereço", "localização"]):
            return jsonify({
                "resposta": (
                    "📞 <b>(11) 3000-4000</b><br>"
                    "📧 <b>contato@seuadvogado.com.br</b><br>"
                    "📍 <b>Av. Paulista, 1000 - São Paulo, SP</b><br><br>"
                    f"{botao_whatsapp('📲 Falar no WhatsApp', 'Olá, quero falar com um advogado agora.')}"
                )
            })

        if any(word in p for word in ["horário", "funcionamento", "aberto", "atendimento"]):
            return jsonify({
                "resposta": (
                    "Atendemos de segunda a sexta, das <b>9h às 18h</b>.<br>"
                    "Casos urgentes têm <b>plantão 24h</b>.<br><br>"
                    f"{botao_whatsapp('📞 Falar com plantão jurídico', 'Preciso de ajuda urgente com um caso jurídico.')}"
                )
            })

        if any(word in p for word in ["honorários", "preço", "quanto custa", "valor", "orçamento"]):
            return jsonify({
                "resposta": (
                    "Oferecemos <b>primeira consulta gratuita</b>.<br>"
                    "Honorários são combinados conforme o caso.<br><br>"
                    f"{botao_whatsapp('📅 Agendar Consulta Gratuita', 'Gostaria de agendar uma consulta gratuita.')}"
                )
            })

        if any(word in p for word in ["divórcio", "separação", "casamento", "união estável"]):
            return jsonify({
                "resposta": (
                    "O divórcio pode ser:<br>"
                    "✅ <b>Consensual</b> – feito no cartório (sem filhos)<br>"
                    "✅ <b>Litigioso</b> – vai à justiça<br><br>"
                    f"{botao_whatsapp('⚖️ Falar com advogado de família', 'Tenho dúvidas sobre divórcio. Pode me ajudar?')}"
                )
            })

        if any(word in p for word in ["demitido", "trabalho", "justa causa"]):
            return jsonify({
                "resposta": (
                    "Se foi demitido sem justa causa, tem direito a:<br>"
                    "✔ Aviso prévio<br>"
                    "✔ FGTS + 40%<br>"
                    "✔ Saldo de salário e férias<br><br>"
                    f"{botao_whatsapp('🧾 Falar com advogado trabalhista', 'Fui demitido e quero saber meus direitos.')}"
                )
            })

        if any(word in p for word in ["acidente", "indenização", "danos"]):
            return jsonify({
                "resposta": (
                    "Você pode ter direito a indenização por danos materiais, morais ou estéticos.<br>"
                    "Preserve provas: boletim, laudos, fotos.<br><br>"
                    f"{botao_whatsapp('🚗 Falar com advogado de trânsito', 'Sofri um acidente e preciso de orientação.')}"
                )
            })

        # Se não encontrou resposta direta, chama o modelo
        resultado = perguntar(pergunta)
        if resultado:
            especialidade = resultado.get("especialidade", "Jurídica")
            resposta = resultado.get("resposta", "Não consegui entender completamente, mas posso te ajudar.")
            return jsonify({
                "resposta": (
                    f"{resposta}<br><br>📌 <b>Área indicada:</b> {especialidade}<br><br>"
                    f"{botao_whatsapp(f'📅 Falar com especialista em {especialidade}', f'Olá, quero falar com um advogado especializado em {especialidade}.')}"
                )
            })
        else:
            return jsonify({
                "resposta": (
                    "Estou analisando seu caso.<br>"
                    "Para garantir uma resposta precisa, recomendo conversar com um advogado:<br><br>"
                    f"{botao_whatsapp('💬 Falar com um advogado agora', 'Preciso de ajuda jurídica urgente.')}"
                )
            })

    # Fora do escopo jurídico
    return jsonify({
        "resposta": (
            "Essa pergunta está fora do escopo jurídico.<br><br>"
            "Se precisar de ajuda com <b>divórcio, trabalho, acidentes, família, imóveis ou consumidor</b>, "
            "posso te orientar!<br><br>"
            f"{botao_whatsapp('📲 Falar com um advogado agora', 'Tenho dúvidas jurídicas. Pode me ajudar?')}"
        )
    })

if __name__ == "__main__":
    app.run(debug=True)
