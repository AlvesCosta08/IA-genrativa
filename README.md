📄 Dr. Legal & Advogados – Assistente Jurídico Virtual
Sistema completo de atendimento jurídico automatizado com IA local, chatbot inteligente e conversão direta via WhatsApp.
Desenvolvido com Flask, Ollama e Docker para garantir privacidade, desempenho e escalabilidade. 

🌟 Visão Geral
O Dr. Legal & Advogados é uma solução moderna e eficaz para escritórios de advocacia que desejam:

Oferecer atendimento 24h com um assistente jurídico virtual inteligente.
Entender dúvidas em linguagem natural.
Classificar automaticamente a área do direito mais adequada.
Responder com empatia, clareza e tom humano.
Gerar conversões por meio de CTAs personalizados e direcionamento direto ao WhatsApp.
Todo o processamento de inteligência artificial é feito localmente com Ollama, sem dependência de APIs externas, garantindo:

✅ Privacidade total
✅ Conformidade com a LGPD
✅ Baixa latência
✅ Operação offline (sem envio de dados)

🔧 Arquitetura do Sistema
O sistema é composto por dois serviços containerizados, orquestrados com Docker Compose:

ollama
Ubuntu + Ollama
Executa modelos de IA localmente (ex:
tinyllama
)
web
Python + Flask
Backend, frontend e API de comunicação

A arquitetura permite fácil implantação, manutenção e escalabilidade.

📦 Estrutura de Projetos

´´´
dr-legal-advogados/
│
├── ollama-container/               # Serviço de IA local
│   ├── Dockerfile                  # Imagem base: Ubuntu 22.04 + Ollama
│   └── start.sh                    # Inicialização e download do modelo
│
├── web-container/                  # Serviço web (Flask)
│   ├── Dockerfile                  # Imagem: Python 3.10-slim
│   ├── app.py                      # Backend com lógica de IA e CTA
│   ├── requirements.txt            # Dependências: Flask, requests
│   └── templates/
│       └── index.html              # Frontend responsivo com chatbot
│
├── docker-compose.yml              # Orquestração dos serviços
└── README.md                       # Este arquivo
⚙️ Serviço 1: ollama-container (IA Local)
Dockerfile



FROM ubuntu:22.04

# Evita interações durante instalação de pacotes
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências básicas
RUN apt update && \
    apt install -y curl wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Instala o Ollama via script oficial
RUN curl -fsSL https://ollama.com/install.sh | sh

# Cria usuário dedicado
RUN useradd -m -s /bin/bash ollama && \
    usermod -aG ollama ollama && \
    echo "ollama ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Permite acesso externo à API
ENV OLLAMA_HOST=0.0.0.0

# Diretório persistente para modelos
VOLUME ["/root/.ollama"]

# Porta da API
EXPOSE 11434

# Script de inicialização
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Inicia o serviço
CMD ["/start.sh"]
start.sh
bash



#!/bin/bash
echo "🚀 Iniciando Ollama..."
ollama serve &

sleep 10

echo "📥 Baixando modelo leve: tinyllama:1.1b"
ollama pull tinyllama:1.1b

echo "✅ Modelo pronto!"
wait
🔍 Funcionalidades
Instala e configura o Ollama em ambiente Ubuntu.
Inicia o servidor ollama serve em segundo plano.
Baixa automaticamente o modelo tinyllama:1.1b para inferência local.
Expõe a API em http://localhost:11434.
Persiste modelos com volume Docker (ollama_data), evitando downloads repetidos.
Compatível com GPU (NVIDIA/AMD) — o script oficial instala drivers se necessário.
🌐 Serviço 2: web-container (Backend + Frontend)
Dockerfile
Dockerfile



FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
requirements.txt
txt


flask
requests
app.py – Backend Flask
O backend implementa uma camada inteligente de triagem jurídica, com:

1. Detecção de Intenção
Saudações, despedidas, contato, horários, honorários.
Temas comuns: "divórcio", "acidente", "golpe no PIX", "aposentadoria".
2. Classificação por Área do Direito
Utiliza dicionário de palavras-chave para mapear perguntas a especialidades:

python



⌄
PALAVRAS_JURIDICAS = {
    "Direito de Família": ["divórcio", "guarda", "pensão", ...],
    "Direito Trabalhista": ["demitido", "horas extras", "FGTS", ...],
    "Direito Previdenciário": ["aposentadoria", "auxílio-doença", ...],
    # + outras áreas
}
3. Integração com IA Local
Consulta o modelo via API do Ollama com prompt otimizado para:

Linguagem humana e empática.
Respostas curtas (máx. 2 frases).
Foco em conversão, nunca em automação total.
4. Geração de CTA (Call to Action)
Sempre termina com botão do WhatsApp, personalizado por área:

⌄
<a href="https://wa.me/551199887766?text=Quero+falar+sobre+divórcio">
  📞 Falar com especialista em Direito de Família
</a>
5. Redirecionamento Garantido
Mesmo em falhas da IA, o usuário é direcionado ao WhatsApp.
Nenhum caso é perdido.
🖥️ Frontend (index.html)
Características Técnicas
Design responsivo com Bootstrap 5.3.
Tipografia elegante usando Google Fonts (Inter + Playfair Display).
Chatbot flutuante com animação de pulsação (CSS + JavaScript).
Totalmente acessível e compatível com dispositivos móveis.
Funcionalidades do Chat
Abre com clique no botão fixo (canto inferior direito).
Interface com mensagens do usuário (azul) e IA (cinza).
Mostra "digitando..." durante processamento.
Envio com Enter.
Comunicação via fetch com o backend Flask.
Comunicação com Backend
javascript

⌄
fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pergunta: msg })
})
🐳 Docker Compose
docker-compose.yml
yaml


services:
  ollama:
    build: ./ollama-container
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  web:
    build: ./web-container
    ports:
      - "5000:5000"
    depends_on:
      - ollama

volumes:
  ollama_data:
Recursos de Orquestração
O serviço web inicia apenas após ollama estar ativo.
Volume ollama_data garante persistência dos modelos.
Portas expostas:
5000: site e API Flask
11434: API do Ollama
🚀 Como Executar
Clone o repositório:
bash


1
git clone https://github.com/seu-usuario/dr-legal-advogados.git
Certifique-se de ter Docker e Docker Compose instalados.
Suba os serviços:
bash


1
docker-compose up --build
Acesse:
Site: http://localhost:5000
API da IA: http://localhost:11434
💡 Estratégia de Conversão
O sistema foi projetado para maximizar conversões com:

Primeira consulta gratuita
Reduz barreira inicial
Botões do WhatsApp
Conversão direta e imediata
CTAs personalizados por área
Maior relevância e conversão
Plantão 24h
Atrai casos urgentes
Respostas curtas e humanas
Clareza e empatia
Redirecionamento garantido
Nenhum lead perdido

🛡️ Privacidade e Conformidade
Nenhum dado do usuário é armazenado.
Toda IA roda localmente — sem envio a OpenAI, Gemini ou outras nuvens.
Sem cookies de rastreamento.
Totalmente compatível com:
LGPD
Código de Ética da Advocacia
Normas de proteção de dados sensíveis
🧠 Modelo de IA Utilizado
tinyllama:1.1b
Modelo leve, rápido e eficiente.
Adequado para inferência em CPU.
Treinado em linguagem natural.
Adaptado via prompt para responder como um advogado empático e direto.
✅ Futuramente pode ser substituído por modelos mais robustos como llama3, phi3 ou gemma para maior precisão. 

📈 Fluxo de Atendimento
Usuário digita: "Caí em golpe no PIX, o que fazer?"
Sistema detecta palavra-chave → "golpe", "PIX"
Classifica como: Direito do Consumidor
Gera resposta com CTA:
"Se você foi enganado no PIX, podemos tentar recuperar seu dinheiro.
📞 Falar com especialista em Consumidor " 
Usuário clica e conversa com advogado real.
📊 Benefícios para Escritórios de Advocacia
Atendimento 24h
Captura leads fora do expediente
Triagem automatizada
Reduz tempo de análise inicial
Aumento de conversão
Mais contatos convertidos em clientes
Redução de custos
Menos atendentes humanos necessários
Imagem moderna
Transmite inovação e confiança

📞 Contato
Este projeto foi desenvolvido para escritórios de advocacia que desejam modernizar seu atendimento com tecnologia segura e eficaz.

Entre em contato para implantação personalizada:

📧 contato@drlegal.com.br
📞 (11) 99887-7766

📄 Licença
Este projeto é fornecido como exemplo educacional e de referência.
Você tem permissão para:

Adaptar para uso comercial
Personalizar para seu escritório
Distribuir com atribuição
Não inclui suporte oficial. 

Dr. Legal & Advogados – Justiça Acessível, com Tecnologia e Humanidade. ⚖️💙 