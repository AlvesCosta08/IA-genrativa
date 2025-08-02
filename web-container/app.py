import logging
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PALAVRAS_JURIDICAS = {
    "trabalho", "demitido", "justa causa", "reclamação", "emprego", "carteira", "horas extras",
    "acidente de trabalho", "rescisão", "fgts", "aviso prévio", "13º", "férias", "salário",
    "divórcio", "separação", "casamento", "união estável", "pensão", "alimentos", "guarda",
    "filho", "criança", "adoção", "testamento", "herança", "inventário", "custódia",
    "acidente", "indenização", "danos", "moral", "estético", "responsabilidade", "civil",
    "processo", "ação", "recurso", "sentença", "laudo", "perícia",
    "consumidor", "golpe", "cobrança", "dívida", "juros", "banco", "nubank", "itau", "caixa",
    "pix", "boleto", "sac", "procon", "contrato", "cancelamento",
    "aposentadoria", "inss", "auxílio", "benefício", "bpc", "idoso", "doença", "invalidez",
    "revisão", "pedágio", "tempo de contribuição",
    "imóvel", "aluguel", "fiador", "despejo", "locação", "luz", "taxa",
    "condomínio", "chave", "depósito",
    "prisão", "flagrante", "habeas", "corpus", "fiança", "delação", "crime", "polícia",
    "mei", "eireli", "contrato social", "sociedade", "falência", "empresa", "lucro",
    "dados", "lgpd", "vazamento", "privacidade", "fake", "notícia", "internet",
    "lei", "direito", "advogado", "juiz", "justiça", "tribunal", "código civil", "constituição"
}

WHATSAPP_LINK = "https://wa.me/551130004000?text="

def eh_tema_juridico(pergunta: str) -> bool:
    pergunta_lower = pergunta.lower()
    return any(palavra in pergunta_lower for palavra in PALAVRAS_JURIDICAS)

def botao_whatsapp(texto: str, mensagem: str) -> str:
    from requests.utils import quote
    mensagem_url = quote(mensagem)
    return (
        f'<a href="{WHATSAPP_LINK}{mensagem_url}" '
        'style="background:#1a3a6e; color:white; border:none; padding:10px 15px; '
        'border-radius:8px; cursor:pointer; text-decoration:none; display:inline-block;">'
        f'{texto}</a>'
    )

def perguntar(pergunta: str, modelo="tinyllama:1.1b") -> dict | None:
    prompt = f"""
Você é um assistente jurídico de um escritório de advocacia brasileiro.
Responda em português do Brasil, de forma clara, educada e profissional.
Seja direto. Evite jargões. Máximo de 3 frases.

Além disso, identifique a especialidade jurídica mais adequada ao caso:
- Direito de Família
- Direito Trabalhista
- Direito Previdenciário
- Direito do Consumidor
- Responsabilidade Civil (Indenização)
- Direito Imobiliário
- Outra (especifique)

Formato da resposta:
1. Resposta clara à pergunta
2. Quebra de linha
3. Especialidade: [Nome da área]

Pergunta: "{pergunta}"

Resposta:
"""

    url = "http://ollama:11434/api/generate"
    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        resposta_completa = response.json().get("response", "").strip()
        if not resposta_completa:
            logging.warning("Resposta vazia do modelo para a pergunta: %s", pergunta)
            return None

        linhas = [l.strip() for l in resposta_completa.split("\n") if l.strip()]
        especialidade = "Jurídico Geral"
        corpo = []

        for linha in linhas:
            if linha.lower().startswith("especialidade:"):
                especialidade = linha.split(":", 1)[1].strip()
            else:
                corpo.append(linha)

        resposta_final = "<br>".join(corpo)
        return {
            "resposta": resposta_final,
            "especialidade": especialidade
        }

    except requests.RequestException as e:
        logging.error(f"Erro na requisição para Ollama API: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado ao processar a resposta: {e}")

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

    # Respostas rápidas por palavra-chave - escopo existente
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

    # Se não encontrou resposta rápida, mas é tema jurídico, chama o modelo
    if eh_tema_juridico(pergunta):
        resultado = perguntar(pergunta)
        if resultado:
            especialidade = resultado["especialidade"]
            resposta = resultado["resposta"]
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

    # Caso geral - pergunta fora do escopo jurídico
    return jsonify({
        "resposta": (
            "Essa pergunta está fora do escopo jurídico.<br><br>"
            "Se precisar de ajuda com <b>divórcio, trabalho, acidentes, família, imóveis ou consumidor</b>, "
            "posso te orientar!<br><br>"
            f"{botao_whatsapp('📲 Falar com um advogado agora', 'Tenho dúvidas jurídicas. Pode me ajudar?')}"
        )
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

