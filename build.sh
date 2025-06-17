#!/usr/bin/env bash
# build.sh

# Descarga los modelos de SpaCy que tu bot necesita
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

# Puedes añadir otros comandos de pre-procesamiento si los necesitas