import logging
from flask import Flask, render_template, request, jsonify, session
import requests
from requests.utils import quote as url_quote
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Para usar sessões

# === CONFIGURAÇÃO DE LOG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === CONFIGURAÇÕES DO WHATSAPP ===
WHATSAPP_NUMERO = "551199887766"  # Atualize com seu número real
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP_NUMERO}?text="

# === PALAVRAS-CHAVE JURÍDICAS POR ÁREA ===
PALAVRAS_JURIDICAS = {
    "Direito de Família": [
        "divórcio", "separação", "casamento", "união estável", "pensão", "alimentos", "guarda", "filho", "criança",
        "adoção", "testamento", "herança", "inventário", "custódia", "partilha", "regime de bens", "pensão alimentícia"
    ],
    "Direito Trabalhista": [
        "trabalho", "demitido", "justa causa", "reclamação", "emprego", "carteira", "horas extras", "acidente de trabalho",
        "rescisão", "fgts", "aviso prévio", "13º", "férias", "salário", "verbas rescisórias", "pedido de demissão"
    ],
    "Direito Previdenciário": [
        "aposentadoria", "inss", "auxílio", "benefício", "bpc", "idoso", "doença", "invalidez", "revisão", "pedágio",
        "tempo de contribuição", "auxílio-doença", "auxílio-acidente", "perícia", "afastamento", "incapacidade",
        "loas", "deficiência", "sequela", "doença ocupacional", "doença profissional"
    ],
    "Direito do Consumidor": [
        "consumidor", "golpe", "cobrança", "dívida", "juros", "banco", "nubank", "itau", "caixa", "pix", "boleto",
        "sac", "procon", "contrato", "cancelamento", "tarifa", "produto com defeito", "juros abusivos"
    ],
    "Indenização por Danos": [
        "acidente", "indenização", "danos", "moral", "estético", "responsabilidade", "civil", "lesão", "erro médico",
        "acidente de carro", "dano material", "dano emocional"
    ],
    "Direito Imobiliário": [
        "imóvel", "aluguel", "fiador", "despejo", "locação", "condomínio", "chave", "depósito", "reajuste", "multa rescisória"
    ],
    "Direito Penal": [
        "prisão", "flagrante", "habeas", "corpus", "fiança", "crime", "polícia", "liberdade provisória"
    ],
    "Direito Empresarial": [
        "mei", "eireli", "contrato social", "sociedade", "falência", "empresa", "lucro", "simples nacional"
    ],
    "LGPD e Privacidade": [
        "dados", "lgpd", "vazamento", "privacidade", "fake", "notícia", "internet", "uso de imagem"
    ],
    "Geral": [
        "lei", "direito", "advogado", "juiz", "justiça", "tribunal", "código civil", "constituição", "petição", "mandado"
    ]
}

# === FUNÇÃO: Detecta se é tema jurídico ===
def eh_tema_juridico(pergunta: str) -> bool:
    pergunta_lower = pergunta.lower()
    return any(
        palavra in pergunta_lower
        for area in PALAVRAS_JURIDICAS.values()
        for palavra in area
    )

# === FUNÇÃO: Detecta a área jurídica mais provável ===
def detectar_area(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    melhor_area = "Jurídico Geral"
    max_palavras = 0
    for area, palavras in PALAVRAS_JURIDICAS.items():
        contagem = sum(1 for palavra in palavras if palavra in pergunta_lower)
        if contagem > max_palavras:
            max_palavras = contagem
            melhor_area = area
    return melhor_area

# === FUNÇÃO: Gera botão do WhatsApp com mensagem de conversão ===
def botao_whatsapp(texto: str, mensagem: str) -> str:
    mensagem_url = url_quote(mensagem)
    return (
        f'<a href="{WHATSAPP_LINK}{mensagem_url}" '
        'style="background:#1a3a6e; color:white; border:none; padding:12px 18px; '
        'border-radius:8px; cursor:pointer; text-decoration:none; display:inline-block; '
        'font-weight:bold; font-size:14px; margin-top:10px;">'
        f'📞 {texto}</a>'
    )

# === FUNÇÃO: Consulta IA com foco em conversão e humanização ===
def perguntar(pergunta: str, modelo="tinyllama:1.1b") -> dict | None:
    """
    Prompt otimizado para conversão: responde como um advogado real,
    com empatia, clareza e sempre direcionando para o WhatsApp.
    """
    prompt = f"""
Você é o Dr. Legal, um advogado virtual empático e direto.
Responda como se estivesse falando com um cliente real.
Use linguagem simples, até 2 frases. NUNCA diga 'será analisado por um advogado'.
Seja humano, acolhedor e objetivo. Termine com uma chamada para ação natural.
Pergunta: {pergunta}
Resposta:
    """.strip()

    url = "http://ollama:11434/api/generate"
    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        resposta_bruta = response.json().get("response", "").strip()

        if not resposta_bruta:
            return None

        # Limpeza: remove linhas com instruções ou robóticas
        linhas = [linha.strip() for linha in resposta_bruta.split('\n') if linha.strip()]
        corpo = []
        for linha in linhas:
            if any(bloco in linha.lower() for bloco in [
                "você é o dr. legal",
                "como assistente",
                "será analisado",
                "você pode procurar",
                "eu sou um assistente",
                "resposta:"
            ]):
                continue
            corpo.append(linha)

        resposta_final = " ".join(corpo).strip()
        if not resposta_final or len(resposta_final) < 10:
            resposta_final = "Posso te ajudar com isso. Vamos conversar melhor?"

        # Limita a 2 frases para manter o foco
        frases = [f.strip() for f in resposta_final.split('.') if f.strip()]
        resposta_final = ". ".join(frases[:2]) + "." if len(frases) > 2 else resposta_final

        # Detecta especialidade
        especialidade = "Jurídico Geral"
        for area in PALAVRAS_JURIDICAS.keys():
            if area.lower() in resposta_bruta.lower():
                especialidade = area
                break

        return {
            "resposta": resposta_final,
            "especialidade": especialidade
        }

    except Exception as e:
        logger.error(f"Erro ao consultar IA: {e}")
        return None

# === ROTAS DA APLICAÇÃO ===
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
                "Olá! Aqui é o <b>Dr. Legal</b> 🌟<br><br>"
                "Seu direito é importante — e eu estou aqui para te ajudar.<br><br>"
                "Posso te orientar sobre:<br>⚖️ Família | 💼 Trabalho | 🛡️ Consumidor | 🏥 Previdência<br><br>"
                f"{botao_whatsapp('💬 Falar com um advogado agora', 'Tenho uma dúvida jurídica urgente.')}"
            )
        })

    p = pergunta.lower()

    # --- 1. Saudações e despedidas ---
    saudacoes = ["oi", "olá", "oie", "bom dia", "boa tarde", "boa noite", "hello", "e aí", "eaí"]
    despedidas = ["tchau", "obrigado", "obrigada", "até logo", "vlw", "valeu"]

    if any(word in p for word in despedidas):
        return jsonify({
            "resposta": "Fico feliz em ter ajudado! Conte com o Dr. Legal sempre que precisar. Até breve! 👋"
        })

    if any(word in p for word in saudacoes):
        return jsonify({
            "resposta": (
                "Olá! Aqui é o <b>Dr. Legal</b>, seu assistente jurídico. 😊<br><br>"
                "Estou aqui para te ajudar com:<br>"
                "🔹 Divórcio, guarda, pensão<br>"
                "🔹 Demissão, FGTS, horas extras<br>"
                "🔹 Golpes no PIX, cobranças indevidas<br>"
                "🔹 Aposentadoria, auxílio-doença, BPC<br><br>"
                "Me conta o que você precisa?<br><br>"
                f"{botao_whatsapp('📞 Falar com especialista agora', 'Quero falar com um advogado agora.')}"
            )
        })

    # --- 2. Informações de contato ---
    if any(word in p for word in ["contato", "telefone", "email", "endereço", "localização"]):
        return jsonify({
            "resposta": (
                "Aqui estão nossos contatos:<br><br>"
                "📞 <b>(11) 3000-4000</b><br>"
                "📍 <b>Av. Paulista, 1000 - São Paulo, SP</b><br><br>"
                f"{botao_whatsapp('📲 Falar no WhatsApp', 'Olá, quero falar com um advogado.')}"
            )
        })

    # --- 3. Horário de atendimento ---
    if any(word in p for word in ["horário", "funcionamento", "aberto", "atendimento", "plantão"]):
        return jsonify({
            "resposta": (
                "Atendemos de <b>segunda a sexta, das 9h às 18h</b>.<br>"
                "Para emergências, temos <b>plantão 24h</b>.<br><br>"
                f"{botao_whatsapp('🚨 Preciso de ajuda urgente', 'Tenho um caso urgente e preciso de ajuda agora.')}"
            )
        })

    # --- 4. Honorários ---
    if any(word in p for word in ["honorários", "preço", "quanto custa", "valor", "orçamento", "grátis"]):
        return jsonify({
            "resposta": (
                "A <b>primeira consulta é gratuita</b>!<br>"
                "Depois, combinamos o valor de forma justa.<br><br>"
                f"{botao_whatsapp('📅 Agendar consulta gratuita', 'Gostaria de agendar minha consulta gratuita.')}"
            )
        })

    # --- 5. Perguntas vagas (mas com intenção) ---
    vagas = ["ajuda", "problema", "o que fazer", "me orienta", "me ajuda", "preciso de ajuda"]
    if any(frase in p for frase in vagas) or len(pergunta.split()) < 5:
        return jsonify({
            "resposta": (
                "Entendi que você está passando por algo difícil.<br><br>"
                "Vamos te encaminhar para um <b>especialista</b> agora.<br><br>"
                f"{botao_whatsapp('✅ Falar com um advogado agora', 'Tenho um problema jurídico e preciso de ajuda.')}"
            )
        })

    # --- 6. Temas comuns (respostas rápidas + CTA) ---
    temas_comuns = {
        "divórcio": "Temos especialistas em divórcio rápido, consensual ou litigioso. Podemos agilizar tudo.",
        "trabalho": "Direitos trabalhistas? Podemos te ajudar com demissão, FGTS, horas extras e verbas rescisórias.",
        "acidente": "Indenização por acidente? Temos peritos prontos para avaliar seu caso e buscar justiça.",
        "golpe": "Caí em golpe? Podemos te ajudar a reaver seu dinheiro, especialmente em golpes no PIX.",
        "pix": "Errou ou foi enganado no PIX? Temos ações rápidas para tentar recuperar seu dinheiro.",
        "imóvel": "Problemas com aluguel, fiador ou despejo? Podemos te ajudar com uma solução rápida.",
        "consumidor": "Cobrança abusiva, banco ou contrato injusto? Vamos resolver com base no Código de Defesa do Consumidor."
    }

    for tema, descricao in temas_comuns.items():
        if tema in p:
            area = detectar_area(pergunta)
            return jsonify({
                "resposta": (
                    f"{descricao}<br><br>"
                    f"📌 <b>Especialidade:</b> {area}<br><br>"
                    f"{botao_whatsapp(f'📞 Falar com especialista em {area}', f'Quero falar sobre {tema}.')}"
                )
            })

    # --- 7. Benefícios previdenciários (com CTA forte) ---
    beneficios = {
        "auxílio-doença": (
            "Se você está afastado por doença há mais de 15 dias, pode ter direito ao auxílio-doença, mesmo que o INSS tenha negado."
        ),
        "bpc": (
            "O BPC/LOAS é um benefício de 1 salário-mínimo para idosos acima de 65 anos ou pessoas com deficiência em situação de baixa renda."
        ),
        "aposentadoria por invalidez": (
            "A aposentadoria por invalidez é vitalícia e pode virar pensão por morte. Mesmo que o INSS tenha negado, podemos recorrer."
        ),
        "auxílio-acidente": (
            "O auxílio-acidente é pago mesmo após voltar ao trabalho, se houver sequela. É vitalício e não exige tempo de contribuição."
        ),
        "perícia": (
            "Se você foi considerado apto injustamente na perícia, podemos recorrer. Contamos com médicos peritos parceiros."
        ),
        "afastamento": (
            "Você tem direito ao afastamento por doença com pagamento do INSS a partir do 16º dia. Se foi demitido, pode ter indenização."
        ),
        "revisão": (
            "Existem várias revisões possíveis: do teto, da RMI, de 20% ou 25% de acréscimo. Muitos segurados recebem menos do que têm direito."
        ),
        "loas": (
            "O BPC/LOAS é para idosos ou pessoas com deficiência em situação de vulnerabilidade. A renda familiar deve ser inferior a 1/4 do salário-mínimo."
        ),
        "deficiência": (
            "Pessoas com deficiência podem ter direito a BPC, aposentadoria por invalidez ou auxílio-acidente. Depende do tipo e laudos médicos."
        )
    }

    for tema, descricao in beneficios.items():
        if tema in p:
            return jsonify({
                "resposta": (
                    f"{descricao}<br><br>"
                    "📌 <b>Especialidade:</b> Direito Previdenciário<br><br>"
                    f"{botao_whatsapp('📞 Falar com advogado previdenciarista', 'Quero saber se tenho direito a esse benefício.')}"
                )
            })

    # --- 8. USAR IA PARA QUALQUER TEMA JURÍDICO (com foco em conversão) ---
    if eh_tema_juridico(pergunta):
        resultado = perguntar(pergunta)
        if resultado:
            esp = resultado["especialidade"]
            resp = resultado["resposta"]
            return jsonify({
                "resposta": (
                    f"{resp}<br><br>"
                    f"📌 <b>Especialidade:</b> {esp}<br><br>"
                    f"{botao_whatsapp(f'📞 Falar com especialista em {esp}', f'Preciso de ajuda com um caso de {esp}.')}"
                )
            })
        else:
            area_sugerida = detectar_area(pergunta)
            return jsonify({
                "resposta": (
                    "Sua situação envolve direitos importantes.<br><br>"
                    f"Vamos te encaminhar para um <b>especialista em {area_sugerida}</b>.<br><br>"
                    f"{botao_whatsapp('📩 Enviar caso para análise', f'Quero ajuda com: {pergunta[:100]}...')}"
                )
            })

    # --- 9. Temas não jurídicos (redirecionamento educado) ---
    temas_nao_juridicos = {"bolo", "pizza", "filme", "jogo", "música", "esporte", "futebol", "namoro", "amor", "vida"}
    if any(palavra in p for palavra in temas_nao_juridicos):
        return jsonify({
            "resposta": (
                "Isso é importante para a vida, mas nosso foco é te ajudar com direitos.<br><br>"
                "Como:<br>⚖️ Família | 💼 Trabalho | 🛡️ Consumidor | 🏥 Previdência<br><br>"
                f"{botao_whatsapp('✅ Falar sobre meu caso', 'Quero falar sobre um problema jurídico.')}"
            )
        })

    # --- 10. Fallback final: SEMPRE encaminhar para WhatsApp (nunca falhar) ---
    area_sugerida = detectar_area(pergunta)
    return jsonify({
        "resposta": (
            "Sua situação pode envolver direitos importantes.<br><br>"
            f"Vamos te encaminhar para um <b>especialista em {area_sugerida}</b>.<br><br>"
            f"{botao_whatsapp('✅ Enviar caso para análise', f'Quero ajuda com: {pergunta[:100]}...')}"
        )
    })

# === INICIAR SERVIDOR ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)