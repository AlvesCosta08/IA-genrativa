📄 Dr. Legal & Advogados – Assistente Jurídico Virtual
Um sistema completo de atendimento jurídico automatizado com chatbot, IA local e integração web.
Desenvolvido com Flask, Ollama e Docker para privacidade, desempenho e conversão. 

🌟 Visão Geral
O Dr. Legal & Advogados é um site institucional com um assistente jurídico virtual inteligente, capaz de:

Entender dúvidas jurídicas em linguagem natural.
Responder com empatia e clareza.
Detectar a área do direito mais adequada (Família, Trabalhista, Previdenciário, etc.).
Direcionar o usuário para um advogado real via WhatsApp com mensagens personalizadas.
Todo o processamento de IA é feito localmente com Ollama, garantindo privacidade e baixa latência.

🔧 Arquitetura do Sistema
O sistema é composto por dois serviços Docker:

ollama
Ollama + Ubuntu
Executa modelos de IA localmente (ex:
tinyllama
)
web
Flask + Python
Backend do chatbot e frontend do site

Eles são orquestrados com Docker Compose, garantindo fácil implantação.


projeto/
│
├── ollama-container/
│   ├── Dockerfile         # ✔️ (já existente)
│   └── start.sh           # ✔️ (já existente)
│
├── web-container/
│   ├── Dockerfile         # ✅ 
│   ├── app.py             # ✔️ (backend Flask)
│   ├── requirements.txt   # ✔️ (com flask e requests)
│   └── templates/
│       └── index.html     # ✔️ (frontend completo com chatbot)
│
├── docker-compose.yml     # ✔️ (orquestração dos serviços)
└── README.md              # ✔️ (documentação completa)


⚙️ Serviço 1: ollama-container (IA Local)

FROM ubuntu:22.04

# Evita perguntas durante instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala curl e wget
RUN apt update && \
    apt install -y curl wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Instala o Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Cria usuário ollama
RUN useradd -m -s /bin/bash ollama && \
    usermod -aG ollama ollama && \
    echo "ollama ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Permite acesso externo
ENV OLLAMA_HOST=0.0.0.0

# Diretório do Ollama
VOLUME ["/root/.ollama"]

# Porta da API
EXPOSE 11434

# Script de inicialização
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Inicia o Ollama
CMD ["/start.sh"]


#!/bin/bash
echo "🚀 Iniciando Ollama..."
ollama serve &

sleep 10

echo "📥 Baixando modelo ultra leve: tinyllama:1.1b"
ollama pull tinyllama:1.1b

echo "✅ Modelo pronto!"
wait

O que faz?
Instala o Ollama no Ubuntu.
Inicia o servidor ollama serve.
Baixa automaticamente o modelo leve TinyLlama (1.1B) para inferência local.
Expõe a API em http://localhost:11434.
Usa volume Docker para não baixar o modelo novamente em reinicializações.
✅ O script oficial do Ollama detecta automaticamente GPU (NVIDIA/AMD) e instala drivers se necessário. 


FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]

profile
Qwen3-235B-A22B-2507
8:42 pm
Claro! Abaixo está o conteúdo completo do README.md em um único arquivo, com todas as informações integradas: código, arquitetura, funcionalidades, frontend, backend, Docker, IA local, conversão e muito mais. Você pode copiar e salvar como README.md.

📄 Dr. Legal & Advogados – Assistente Jurídico Virtual
Um sistema completo de atendimento jurídico automatizado com chatbot, IA local e integração web.
Desenvolvido com Flask, Ollama e Docker para privacidade, desempenho e conversão. 

🌟 Visão Geral
O Dr. Legal & Advogados é um site institucional com um assistente jurídico virtual inteligente, capaz de:

Entender dúvidas jurídicas em linguagem natural.
Responder com empatia e clareza.
Detectar a área do direito mais adequada (Família, Trabalhista, Previdenciário, etc.).
Direcionar o usuário para um advogado real via WhatsApp com mensagens personalizadas.
Todo o processamento de IA é feito localmente com Ollama, garantindo privacidade, conformidade com a LGPD e baixa latência.

🔧 Arquitetura do Sistema
O sistema é composto por dois serviços Docker:

ollama
Ollama + Ubuntu
Executa modelos de IA localmente (ex:
tinyllama
)
web
Flask + Python
Backend do chatbot e frontend do site

Eles são orquestrados com Docker Compose, garantindo fácil implantação e escalabilidade.

📦 Estrutura de Pastas


1
2
3
4
5
6
7
8
9
10
11
12
13
14
projeto/
│
├── ollama-container/
│   ├── Dockerfile         # Cria o container do Ollama
│   └── start.sh           # Inicia o Ollama e baixa o modelo
│
├── web-container/
│   ├── app.py             # Backend Flask do chatbot
│   ├── requirements.txt   # Dependências Python
│   └── templates/
│       └── index.html     # Frontend do site
│
├── docker-compose.yml     # Orquestração dos serviços
└── README.md              # Este arquivo
⚙️ Serviço 1: ollama-container (IA Local)
Dockerfile
Dockerfile


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
FROM ubuntu:22.04

# Evita perguntas durante instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala curl e wget
RUN apt update && \
    apt install -y curl wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Instala o Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Cria usuário ollama
RUN useradd -m -s /bin/bash ollama && \
    usermod -aG ollama ollama && \
    echo "ollama ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Permite acesso externo
ENV OLLAMA_HOST=0.0.0.0

# Diretório do Ollama
VOLUME ["/root/.ollama"]

# Porta da API
EXPOSE 11434

# Script de inicialização
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Inicia o Ollama
CMD ["/start.sh"]
start.sh
bash


1
2
3
4
5
6
7
8
9
10
11
#!/bin/bash
echo "🚀 Iniciando Ollama..."
ollama serve &

sleep 10

echo "📥 Baixando modelo ultra leve: tinyllama:1.1b"
ollama pull tinyllama:1.1b

echo "✅ Modelo pronto!"
wait
🔍 O que faz?
Instala o Ollama no Ubuntu.
Inicia o servidor ollama serve.
Baixa automaticamente o modelo leve TinyLlama (1.1B) para inferência local.
Expõe a API em http://localhost:11434.
Usa volume Docker para não baixar o modelo novamente em reinicializações.
✅ O script oficial do Ollama detecta automaticamente GPU (NVIDIA/AMD) e instala drivers se necessário. 

🌐 Serviço 2: web-container (Backend + Frontend)
Dockerfile
Dockerfile


1
2
3
4
5
6
7
8
9
10
11
12
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
requirements.txt
txt


1
2
flask
requests
app.py – Backend Flask
Este script:

Detecta temas jurídicos com base em palavras-chave (ex: "divórcio", "FGTS", "aposentadoria").
Classifica a área do direito mais relevante.
Consulta o modelo local tinyllama via API do Ollama.
Gera respostas humanizadas com chamadas para ação (CTA).
Insere botões do WhatsApp para conversão.
Redireciona sempre para contato humano – nunca diz "não posso ajudar".
Exemplo de CTA gerado:

<a href="https://wa.me/551199887766?text=Quero+falar+sobre+divórcio">
  📞 Falar com especialista em Direito de Família
</a>

💬 Funcionalidades do Chatbot (app.py)
O backend app.py possui múltiplas camadas de inteligência:

1. Detecção de Intenção
Saudações, despedidas, contato, horários, honorários.
Temas comuns como "divórcio", "acidente", "golpe no PIX".
Benefícios previdenciários com respostas específicas.
2. Palavras-Chave por Área


3. IA com Foco em Conversão
Prompt otimizado para empathia e ação.
Nunca responde como robô.
Sempre termina com CTA para WhatsApp.
4. Redirecionamento Garantido
Mesmo se a IA falhar, o usuário é direcionado ao WhatsApp.
Nenhum caso é perdido.
🖥️ Frontend (index.html)
Características
Design moderno com Bootstrap 5 e Font Awesome.
Tipografia elegante com Google Fonts (Inter + Playfair Display).
Chatbot fixo no canto inferior direito com animação de pulsação.
Totalmente responsivo (móvel e desktop).
Recursos do Chat
Abre com clique no botão flutuante.
Interface limpa com mensagens do usuário (azul) e IA (cinza).
Mostra "digitando..." enquanto aguarda resposta.
Envia mensagem com Enter.
Comunicação com Backend

fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pergunta: msg })
})

🐳 Docker Compose
docker-compose.yml

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

  profile
Qwen3-235B-A22B-2507
8:42 pm
Claro! Abaixo está o conteúdo completo do README.md em um único arquivo, com todas as informações integradas: código, arquitetura, funcionalidades, frontend, backend, Docker, IA local, conversão e muito mais. Você pode copiar e salvar como README.md.

📄 Dr. Legal & Advogados – Assistente Jurídico Virtual
Um sistema completo de atendimento jurídico automatizado com chatbot, IA local e integração web.
Desenvolvido com Flask, Ollama e Docker para privacidade, desempenho e conversão. 

🌟 Visão Geral
O Dr. Legal & Advogados é um site institucional com um assistente jurídico virtual inteligente, capaz de:

Entender dúvidas jurídicas em linguagem natural.
Responder com empatia e clareza.
Detectar a área do direito mais adequada (Família, Trabalhista, Previdenciário, etc.).
Direcionar o usuário para um advogado real via WhatsApp com mensagens personalizadas.
Todo o processamento de IA é feito localmente com Ollama, garantindo privacidade, conformidade com a LGPD e baixa latência.

🔧 Arquitetura do Sistema
O sistema é composto por dois serviços Docker:

ollama
Ollama + Ubuntu
Executa modelos de IA localmente (ex:
tinyllama
)
web
Flask + Python
Backend do chatbot e frontend do site

Eles são orquestrados com Docker Compose, garantindo fácil implantação e escalabilidade.

📦 Estrutura de Pastas


1
2
3
4
5
6
7
8
9
10
11
12
13
14
projeto/
│
├── ollama-container/
│   ├── Dockerfile         # Cria o container do Ollama
│   └── start.sh           # Inicia o Ollama e baixa o modelo
│
├── web-container/
│   ├── app.py             # Backend Flask do chatbot
│   ├── requirements.txt   # Dependências Python
│   └── templates/
│       └── index.html     # Frontend do site
│
├── docker-compose.yml     # Orquestração dos serviços
└── README.md              # Este arquivo
⚙️ Serviço 1: ollama-container (IA Local)
Dockerfile
Dockerfile


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
FROM ubuntu:22.04

# Evita perguntas durante instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala curl e wget
RUN apt update && \
    apt install -y curl wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Instala o Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Cria usuário ollama
RUN useradd -m -s /bin/bash ollama && \
    usermod -aG ollama ollama && \
    echo "ollama ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Permite acesso externo
ENV OLLAMA_HOST=0.0.0.0

# Diretório do Ollama
VOLUME ["/root/.ollama"]

# Porta da API
EXPOSE 11434

# Script de inicialização
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Inicia o Ollama
CMD ["/start.sh"]
start.sh
bash


1
2
3
4
5
6
7
8
9
10
11
#!/bin/bash
echo "🚀 Iniciando Ollama..."
ollama serve &

sleep 10

echo "📥 Baixando modelo ultra leve: tinyllama:1.1b"
ollama pull tinyllama:1.1b

echo "✅ Modelo pronto!"
wait
🔍 O que faz?
Instala o Ollama no Ubuntu.
Inicia o servidor ollama serve.
Baixa automaticamente o modelo leve TinyLlama (1.1B) para inferência local.
Expõe a API em http://localhost:11434.
Usa volume Docker para não baixar o modelo novamente em reinicializações.
✅ O script oficial do Ollama detecta automaticamente GPU (NVIDIA/AMD) e instala drivers se necessário. 

🌐 Serviço 2: web-container (Backend + Frontend)
Dockerfile
Dockerfile


1
2
3
4
5
6
7
8
9
10
11
12
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
requirements.txt
txt


1
2
flask
requests
app.py – Backend Flask
Este script:

Detecta temas jurídicos com base em palavras-chave (ex: "divórcio", "FGTS", "aposentadoria").
Classifica a área do direito mais relevante.
Consulta o modelo local tinyllama via API do Ollama.
Gera respostas humanizadas com chamadas para ação (CTA).
Insere botões do WhatsApp para conversão.
Redireciona sempre para contato humano – nunca diz "não posso ajudar".
Exemplo de CTA gerado:
html


1
2
3
⌄
<a href="https://wa.me/551199887766?text=Quero+falar+sobre+divórcio">
  📞 Falar com especialista em Direito de Família
</a>
💬 Funcionalidades do Chatbot (app.py)
O backend app.py possui múltiplas camadas de inteligência:

1. Detecção de Intenção
Saudações, despedidas, contato, horários, honorários.
Temas comuns como "divórcio", "acidente", "golpe no PIX".
Benefícios previdenciários com respostas específicas.
2. Palavras-Chave por Área
python


1
2
3
4
5
6
⌄
PALAVRAS_JURIDICAS = {
    "Direito de Família": ["divórcio", "guarda", "pensão", ...],
    "Direito Trabalhista": ["demitido", "horas extras", "FGTS", ...],
    "Direito Previdenciário": ["aposentadoria", "auxílio-doença", ...],
    # + outras áreas
}
3. IA com Foco em Conversão
Prompt otimizado para empathia e ação.
Nunca responde como robô.
Sempre termina com CTA para WhatsApp.
4. Redirecionamento Garantido
Mesmo se a IA falhar, o usuário é direcionado ao WhatsApp.
Nenhum caso é perdido.
🖥️ Frontend (index.html)
Características
Design moderno com Bootstrap 5 e Font Awesome.
Tipografia elegante com Google Fonts (Inter + Playfair Display).
Chatbot fixo no canto inferior direito com animação de pulsação.
Totalmente responsivo (móvel e desktop).
Recursos do Chat
Abre com clique no botão flutuante.
Interface limpa com mensagens do usuário (azul) e IA (cinza).
Mostra "digitando..." enquanto aguarda resposta.
Envia mensagem com Enter.
Comunicação com Backend
javascript


1
2
3
4
5
⌄
fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pergunta: msg })
})
🐳 Docker Compose
docker-compose.yml
yaml


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
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
Funcionalidades:
O serviço web só inicia após o ollama estar pronto.
Dados do Ollama são persistidos no volume ollama_data.
Portas expostas: 5000 (site) e 11434 (API da IA).
🚀 Como Executar
Clone o repositório
Certifique-se de ter Docker e Docker Compose instalados
Execute:

docker-compose up --build

Acesse:
Site: http://localhost:5000
API da IA: http://localhost:11434
💡 Recursos de Conversão
O sistema foi projetado para maximizar conversões:

Primeira consulta gratuita
Reduz barreira inicial
Botões do WhatsApp
Conversão direta
CTAs personalizados por área
Maior relevância
Plantão 24h
Urgência
Respostas curtas e humanas
Clareza e empatia
Redirecionamento para humano
Nenhum caso perdido

🛡️ Privacidade e Segurança
Nenhum dado do usuário é armazenado.
Toda IA roda localmente (sem envio a nuvens como OpenAI).
Sem cookies de rastreamento.
Ideal para advocacia: cumple LGPD e ética profissional.
🧠 Modelo de IA Utilizado
tinyllama:1.1b
Pequeno, rápido e eficiente.
Roda bem em CPU (ideal para produção).
Treinado em linguagem natural.
Adaptado via prompt para responder como um advogado empático.
✅ Futuramente pode ser substituído por modelos maiores como llama3, phi3 ou gemma com melhor desempenho. 

📈 Fluxo de Atendimento
Usuário digita: "Caí em golpe no PIX, o que fazer?"
Sistema detecta palavra-chave → "golpe", "PIX"
Classifica como: Direito do Consumidor
Gera resposta com CTA:
"Se você foi enganado no PIX, podemos tentar recuperar seu dinheiro.
📞 Falar com especialista em Consumidor " 
Usuário clica e conversa com advogado real.
📞 Contato
Este projeto foi desenvolvido para escritórios de advocacia que desejam:

Atendimento 24h
Redução de custos
Aumento de conversão
Entre em contato:
📧 contato@drlegal.com.br
📞 (11) 99999-9999

📄 Licença
Este projeto é um exemplo educacional.
Você pode adaptá-lo livremente para uso comercial ou institucional.