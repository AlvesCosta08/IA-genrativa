# ollama-container/Dockerfile
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