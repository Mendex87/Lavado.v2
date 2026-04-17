#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_HOST="127.0.0.1:11434"

if pgrep -af "ollama serve" >/dev/null 2>&1; then
  exit 0
fi

nohup ollama serve >/tmp/ollama-serve.log 2>&1 &

for _ in $(seq 1 20); do
  if ollama list >/dev/null 2>&1; then
    exit 0
  fi
  sleep 1
done

echo "Ollama did not start correctly" >&2
exit 1
