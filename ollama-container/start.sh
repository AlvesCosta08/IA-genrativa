#!/bin/bash
# start.sh

echo "🚀 Iniciando Ollama..."
ollama serve &

sleep 10

echo "📥 Baixando modelo ultra leve: tinyllama:1.1b"
ollama pull tinyllama:1.1b

echo "✅ Modelo pronto!"
wait