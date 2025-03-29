#!/bin/bash

# Sair imediatamente se um comando falhar
set -e

# Variáveis (pegas do ambiente) - Adicione valores padrão ou verificação se desejar
APP_URL="${APP_URL}" # Workflow passará essa variável
MAX_ATTEMPTS="${MAX_ATTEMPTS:-15}" # Usa 15 como padrão se não for passada
SLEEP_DURATION="${SLEEP_DURATION:-10}" # Usa 10s como padrão
CONNECT_TIMEOUT="${CONNECT_TIMEOUT:-15}"
MAX_TIME="${MAX_TIME:-30}"

if [ -z "$APP_URL" ]; then
  echo "Erro: Variável de ambiente APP_URL não definida."
  exit 1
fi

echo "Iniciando warm-up para: $APP_URL"
echo "Máximo de tentativas: $MAX_ATTEMPTS, Espera entre tentativas: ${SLEEP_DURATION}s"

attempt=1
while [ $attempt -le $MAX_ATTEMPTS ]; do
  echo "Tentativa $attempt/$MAX_ATTEMPTS: Pingando..."
  STATUS_CODE=$(curl -s -L -o /dev/null -w "%{http_code}" --connect-timeout "$CONNECT_TIMEOUT" --max-time "$MAX_TIME" "$APP_URL")

  if [ "$STATUS_CODE" -ge 200 ] && [ "$STATUS_CODE" -lt 400 ]; then
    echo "Aplicação respondeu! Status: $STATUS_CODE."
    exit 0 # Sucesso
  else
    echo "Status recebido: $STATUS_CODE. Aplicação pode estar acordando. Aguardando ${SLEEP_DURATION}s..."
    sleep "$SLEEP_DURATION"
  fi
  attempt=$((attempt + 1))
done

echo "Erro: Aplicação não respondeu com sucesso após $MAX_ATTEMPTS tentativas."
exit 1 # Falha