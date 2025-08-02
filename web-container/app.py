import logging
from flask import Flask, render_template, request, jsonify
import requests
from requests.utils import quote as url_quote

app = Flask(__name__)

# === CONFIGURAÇÃO DE LOG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# === LINK DO WHATSAPP (substitua pelo seu número real) ===
WHATSAPP_NUMERO = "551199887766"  # Ex: 5511912345678
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP_NUMERO}?text="

# === PALAVRAS-JURIDICAS ORGANIZADAS POR ÁREA ===
PALAVRAS_JURIDICAS = {
    "Família": [
        "divórcio", "separação", "casamento", "união estável", "pensão", "alimentos", "guarda", "filho", "criança",
        "adoção", "testamento", "herança", "inventário", "custódia", "partilha", "regime de bens", "pensão alimentícia"
    ],
    "Trabalhista": [
        "trabalho", "demitido", "justa causa", "reclamação", "emprego", "carteira", "horas extras", "acidente de trabalho",
        "rescisão", "fgts", "aviso prévio", "13º", "férias", "salário", "verbas rescisórias", "pedido de demissão"
    ],
    "Previdenciário": [
        "aposentadoria", "inss", "auxílio", "benefício", "bpc", "idoso", "doença", "invalidez", "revisão", "pedágio",
        "tempo de contribuição", "auxílio-doença", "auxílio-acidente", "perícia", "afastamento", "incapacidade",
        "loas", "deficiência", "sequela", "doença ocupacional", "doença profissional"
    ],
    "Consumidor": [
        "consumidor", "golpe", "cobrança", "dívida", "juros", "banco", "nubank", "itau", "caixa", "pix", "boleto",
        "sac", "procon", "contrato", "cancelamento", "tarifa", "produto com defeito", "juros abusivos"
    ],
    "Indenização": [
        "acidente", "indenização", "danos", "moral", "estético", "responsabilidade", "civil", "lesão", "erro médico",
        "acidente de carro", "dano material", "dano emocional"
    ],
    "Imobiliário": [
        "imóvel", "aluguel", "fiador", "despejo", "locação", "condomínio", "chave", "depósito", "reajuste", "multa rescisória"
    ],
    "Penal": [
        "prisão", "flagrante", "habeas", "corpus", "fiança", "delação", "crime", "polícia", "liberdade provisória"
    ],
    "Empresarial": [
        "mei", "eireli", "contrato social", "sociedade", "falência", "empresa", "lucro", "simples nacional"
    ],
    "LGPD": [
        "dados", "lgpd", "vazamento", "privacidade", "fake", "notícia", "internet", "uso de imagem"
    ],
    "Geral": [
        "lei", "direito", "advogado", "juiz", "justiça", "tribunal", "código civil", "constituição", "petição", "mandado"
    ]
}

# Função para verificar se é tema jurídico
def eh_tema_juridico(pergunta: str) -> bool:
    pergunta_lower = pergunta.lower()
    return any(
        palavra in pergunta_lower
        for area in PALAVRAS_JURIDICAS.values()
        for palavra in area
    )

# Função para detectar a área jurídica
def detectar_area(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    for area, palavras in PALAVRAS_JURIDICAS.items():
        if any(palavra in pergunta_lower for palavra in palavras):
            return area
    return "Jurídico Geral"

# === BOTÃO WHATSAPP PERSONALIZADO ===
def botao_whatsapp(texto: str, mensagem: str) -> str:
    mensagem_url = url_quote(mensagem)
    return (
        f'<a href="{WHATSAPP_LINK}{mensagem_url}" '
        'style="background:#1a3a6e; color:white; border:none; padding:10px 15px; '
        'border-radius:8px; cursor:pointer; text-decoration:none; display:inline-block; font-weight:bold;">'
        f'{texto}</a>'
    )

# === CHAMADA À IA: SOMENTE PARA PERGUNTAS JURÍDICAS ===
def perguntar(pergunta: str, modelo="tinyllama:1.1b") -> dict | None:
    """
    Usa IA apenas para responder perguntas jurídicas.
    Nunca é chamada para saudações, contatos ou temas fora de escopo.
    """
    prompt = f"""
Você é um assistente jurídico do escritório Dr. Legal, especializado em Direito Brasileiro.
Responda com clareza, em até 3 frases, sem jargões excessivos.
Nunca dê parecer conclusivo. Sempre diga que o caso será analisado por um advogado.
Identifique a especialidade jurídica ao final.
Pergunta: "{pergunta}"
Responda no formato:
1. Resposta útil e educada
2. Nova linha
3. Especialidade: [Nome da área]
    """
    url = "http://localhost:11434/api/generate"  # Corrigido: localhost
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
    except Exception as e:
        logging.error(f"Erro ao chamar Ollama: {e}")
        return None

# === ROTAS ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    pergunta = data.get("pergunta", "").strip()
    if not pergunta:
        return jsonify({
            "resposta": (
                "Olá! Como posso te ajudar?<br><br>"
                "Você pode me perguntar sobre:<br>"
                "⚖️ <b>Divórcio, pensão, guarda</b><br>"
                "💼 <b>Direitos no trabalho, demissão, FGTS</b><br>"
                "🚗 <b>Indenização por acidente</b><br>"
                "💳 <b>Golpes, PIX, cobrança indevida</b><br>"
                "🏠 <b>Problemas com aluguel ou imóvel</b><br><br>"
                f"{botao_whatsapp('💬 Falar com um advogado agora', 'Tenho uma dúvida jurídica e preciso de ajuda.')}"
            )
        })

    p = pergunta.lower()

    # --- 1. Saudações e despedidas ---
    if any(word in p for word in ["tchau", "obrigado", "até logo", "vlw", "valeu"]):
        return jsonify({"resposta": "Foi um prazer ajudar! Conte com nosso escritório quando precisar. 👋"})

    if p in ["oi", "olá", "oie", "bom dia", "boa tarde", "boa noite", "hello", "e aí", "eaí"]:
        return jsonify({
            "resposta": (
                "Olá! Sou o assistente do <b>Dr. Legal</b>.<br>"
                "Posso te ajudar com:<br>"
                "⚖️ Divórcio | 💼 Trabalho | 🚗 Acidentes | 🏠 Imóveis | 💳 Consumidor | 🏥 Previdenciário<br><br>"
                f"{botao_whatsapp('💬 Iniciar atendimento', 'Olá, gostaria de iniciar um atendimento jurídico.')}"
            )
        })

    # --- 2. Informações do escritório ---
    if any(word in p for word in ["contato", "telefone", "email", "endereço", "localização"]):
        return jsonify({
            "resposta": (
                "📞 <b>(11) 3000-4000</b><br>"
                "📧 <b>contato@drlegal.com.br</b><br>"
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

    # --- 3. Perguntas vagas ou genéricas ---
    if any(frase in p for frase in ["ajuda", "problema", "o que fazer", "me orienta"]) or len(pergunta.split()) < 4:
        return jsonify({
            "resposta": (
                "Entendo que você está com uma situação difícil.<br><br>"
                "Pode me contar melhor qual é o seu problema?<br><br>"
                "Exemplos:<br>"
                "🔹 <i>Fui demitido, tenho direito a algo?</i><br>"
                "🔹 <i>Como fazer um divórcio rápido?</i><br>"
                "🔹 <i>Caí em um golpe no PIX, o que fazer?</i><br><br>"
                f"{botao_whatsapp('📞 Falar direto com um advogado', 'Quero falar com um advogado agora, por favor.')}"
            )
        })

    # --- 4. Temas fora de escopo ---
    temas_nao_juridicos = {"bolo", "pizza", "filme", "jogo", "música", "esporte", "futebol", "namoro", "amor", "vida"}
    if any(palavra in p for palavra in temas_nao_juridicos) and not eh_tema_juridico(pergunta):
        return jsonify({
            "resposta": (
                "Isso é importante, mas está fora do meu foco jurídico.<br><br>"
                "Se o seu caso envolve:<br>"
                "🔸 <b>Direito do trabalho</b><br>"
                "🔸 <b>Divórcio, guarda ou pensão</b><br>"
                "🔸 <b>Acidente, golpe ou imóvel</b><br><br>"
                "Posso te conectar com um advogado especialista!<br><br>"
                f"{botao_whatsapp('📲 Falar com um advogado', 'Tenho uma dúvida jurídica importante.')}"
            )
        })

    # --- 5. Respostas rápidas para temas comuns (sem IA) ---
    temas_rapidos = {
        "divórcio": "Temos especialistas em divórcio rápido, consensual e litigioso.",
        "trabalho": "Direitos trabalhistas: demissão, horas extras, FGTS, 13º e férias.",
        "acidente": "Indenização por acidente é nosso forte. Temos peritos prontos para avaliar.",
        "consumidor": "Banco, PIX, cobrança abusiva? Vamos resolver com o CDC.",
        "imóvel": "Problemas com aluguel, despejo ou fiador? Temos solução rápida.",
        "golpe": "Caí em golpe? Podemos te ajudar a reaver seus direitos, especialmente no PIX.",
        "pix": "Errou ou foi enganado no PIX? Temos ações rápidas para recuperar seu dinheiro."
    }

    for tema, descricao in temas_rapidos.items():
        if tema in p:
            area = detectar_area(pergunta)
            return jsonify({
                "resposta": (
                    f"{descricao}<br><br>"
                    f"📌 <b>Área indicada:</b> {area}<br><br>"
                    f"{botao_whatsapp(f'📞 Falar com especialista em {area}', f'Quero falar sobre {tema}.')}"
                )
            })

    # --- 6. Respostas rápidas para benefícios (Previdenciário) ---
    temas_beneficios = {
        "auxílio-doença": (
            "Se você está afastado por doença há mais de 15 dias, pode ter direito ao <b>auxílio-doença</b>, mesmo que o INSS tenha negado.<br>"
            "Podemos entrar com ação judicial com seus laudos médicos."
        ),
        "bpc": (
            "O <b>BPC/LOAS</b> é um benefício de 1 salário-mínimo para idosos acima de 65 anos ou pessoas com deficiência em situação de baixa renda.<br>"
            "Mesmo sem contribuir ao INSS, é possível ter direito comprovando vulnerabilidade social."
        ),
        "aposentadoria por invalidez": (
            "A <b>aposentadoria por invalidez</b> é vitalícia e pode virar pensão por morte.<br>"
            "Mesmo que o INSS negue, podemos recorrer com laudos médicos e perícia particular."
        ),
        "auxílio-acidente": (
            "O <b>auxílio-acidente</b> é pago mesmo após voltar ao trabalho, se houver sequela.<br>"
            "É vitalício e não exige tempo de contribuição. Temos ações bem-sucedidas nesse tema."
        ),
        "perícia": (
            "Errou a perícia ou foi considerado apto injustamente? Podemos recorrer.<br>"
            "Temos médicos peritos parceiros para contrapor o laudo do INSS."
        ),
        "afastamento": (
            "Você tem direito a afastamento por doença com pagamento do INSS a partir do 16º dia.<br>"
            "Se foi demitido durante o afastamento, pode ter direito a indenização."
        ),
        "revisão": (
            "Há várias <b>revisões de benefício</b>: RMI, teto, 20%, 25% de acréscimo, entre outras.<br>"
            "Muitos segurados recebem menos do que têm direito por anos. Podemos revisar seu caso."
        ),
        "loas": (
            "O <b>BPC/LOAS</b> é para idosos ou pessoas com deficiência em situação de vulnerabilidade.<br>"
            "A renda familiar por pessoa deve ser inferior a 1/4 do salário-mínimo."
        ),
        "deficiência": (
            "Pessoas com deficiência podem ter direito a BPC, aposentadoria por invalidez ou auxílio-acidente.<br>"
            "Tudo depende do tipo de deficiência, tempo de afastamento e laudos médicos."
        )
    }

    for tema, descricao in temas_beneficios.items():
        if tema in p:
            return jsonify({
                "resposta": (
                    f"{descricao}<br><br>"
                    "📌 <b>Área indicada:</b> Direito Previdenciário<br><br>"
                    f"{botao_whatsapp('📞 Falar com advogado previdenciarista', 'Quero saber se tenho direito a auxílio-doença, BPC ou aposentadoria por invalidez.')}"
                )
            })

    # --- 7. ✅ USAR IA SOMENTE PARA TEMAS JURÍDICOS REAIS ---
    if eh_tema_juridico(pergunta):
        resultado = perguntar(pergunta)
        if resultado:
            esp = resultado["especialidade"]
            resp = resultado["resposta"]
            return jsonify({
                "resposta": (
                    f"{resp}<br><br>📌 <b>Área indicada:</b> {esp}<br><br>"
                    f"{botao_whatsapp(f'📞 Falar com especialista em {esp}', f'Olá, preciso de ajuda com um caso de {esp}.')}"
                )
            })

    # --- 8. Caso genérico final (seguro) ---
    area_sugerida = detectar_area(pergunta)
    return jsonify({
        "resposta": (
            "Sua situação precisa de análise jurídica detalhada.<br><br>"
            f"Vamos encaminhar você para um <b>advogado especialista em {area_sugerida}</b>.<br><br>"
            f"{botao_whatsapp('✅ Enviar caso para análise', f'Quero enviar meu caso jurídico: {pergunta[:100]}...')}"
        )
    })

# === INICIAR SERVIDOR ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)