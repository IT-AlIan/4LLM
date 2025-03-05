import requests
import json
import streamlit as st
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

# Disabilita gli avvisi di verifica SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configurazione dei LLM (nomi dei modelli su Ollama)
LLM_NAMES = ["qwen2.5", "llama3.1","mistral","gemma2"]
OLLAMA_URL = "http://localhost:21434/api/generate"

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

def ask_ollama(prompt, model):
    """Funzione per interrogare un LLM su Ollama."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    headers = {
        "Authorization": "Bearer e3073a10946d295e36df489bd7783508b00412c004df559a516843d3d8651f82"  # Se richiesto
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, verify=False)
        logging.debug(f"Richiesta: {payload}")
        logging.debug(f"Risposta: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return f"Errore: {response.status_code} - {response.text}"
    except requests.exceptions.SSLError as e:
        return f"Errore SSL: {str(e)}"

def evaluate_response(prompt, response, judge_model):
    """Funzione per valutare una risposta da 1 a 10."""
    evaluation_prompt = f"""
    Valuta la seguente risposta alla richiesta: "{prompt}"
    Risposta: "{response}"
    Assegna un punteggio da 1 a 10 basato sulla qualità, accuratezza e pertinenza.
    Fornisci anche un breve feedback.
    """
    evaluation = ask_ollama(evaluation_prompt, judge_model)
    return evaluation

def generate_text(model):
    """Funzione per generare un testo di 150 righe in inglese."""
    prompt = "Genera un testo di 150 righe in inglese su un argomento a tua scelta."
    text = ask_ollama(prompt, model)
    return text

def translate_text(text, model):
    """Funzione per tradurre un testo in italiano."""
    prompt = f"Traduci il seguente testo in italiano:\n{text}"
    translation = ask_ollama(prompt, model)
    return translation

def main():
    st.title("Interazione tra 4 LLM su Traduzione")

    if st.button("Avvia l'interazione"):
        results = {}

        # Fase 1: Ogni LLM genera un testo di 150 righe in inglese
        texts = {}
        translations = {}
        translation_evaluations = {}
        for llm in LLM_NAMES:
            st.header(f"**{llm}** interroga gli altri LLM", divider="blue")
            texts[llm] = generate_text(llm)
            st.subheader(f"**{llm}** ha generato il seguente testo in inglese:")
            st.text_area("Testo generato", texts[llm], height=300)

			# Fase 2: Ogni LLM traduce il testo degli altri LLM in italiano
            translations[llm] = {}
            for other_llm in LLM_NAMES:
                if other_llm != llm:
                    st.divider()
                    translations[llm][other_llm] = translate_text(texts[llm], other_llm)
                    st.subheader(f"**{other_llm}** ha tradotto il testo di **{llm}** in italiano:")
                    st.text_area("Traduzione", translations[llm][other_llm], height=300)

					# Fase 3: Ogni LLM valuta la traduzione degli altri LLM
                    evaluation = evaluate_response(
                        f"Traduci il seguente testo in italiano:\n{texts[llm]}",
                        translations[llm][other_llm],
                        llm
                    )
                    st.subheader(f"**{llm}** ha valutato la traduzione di **{other_llm}**:")
                    st.write(f"{evaluation}")

if __name__ == "__main__":
    main()
