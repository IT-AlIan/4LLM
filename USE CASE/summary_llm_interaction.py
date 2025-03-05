import requests
import json
import streamlit as st
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

# Disabilita gli avvisi di verifica SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configurazione dei LLM (nomi dei modelli su Riassunto)
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
    """Funzione per generare un testo di 150 righe in italiano."""
    prompt = "Genera un testo di 150 righe in italiano su un argomento a tua scelta."
    text = ask_ollama(prompt, model)
    return text

def summarize_text(text, model):
    """Funzione per fare un riassunto di 10 righe."""
    prompt = f"Fai un riassunto del seguente testo in 10 righe:\n{text}"
    summary = ask_ollama(prompt, model)
    return summary

def main():
    st.title("Interazione tra 4 LLM su Riassunto")

    if st.button("Avvia l'interazione"):
        results = {}

        # Fase 1: Ogni LLM genera un testo di 150 righe in inglese
        texts = {}
        summaries = {}
        summary_evaluations = {}
        for llm in LLM_NAMES:
            st.header(f"**{llm}** interroga gli altri LLM", divider="blue")
            texts[llm] = generate_text(llm)
            st.subheader(f"**{llm}** ha generato il seguente testo in italiano:")
            st.text_area("Testo generato", texts[llm], height=300)

            # Fase 4: Ogni LLM fa un riassunto del testo in 10 righe
            summaries[llm] = {}
            for other_llm in LLM_NAMES:
                if other_llm != llm:
                    st.divider()
                    summaries[llm][other_llm] = summarize_text(texts[llm], other_llm)
                    st.subheader(f"**{other_llm}** ha fatto un riassunto del testo di **{llm}**:")
                    st.text_area("Riassunto", summaries[llm][other_llm], height=150)

                    # Fase 5: Ogni LLM valuta il riassunto degli altri LLM
                    evaluation = evaluate_response(
                         f"Fai un riassunto del seguente testo in 10 righe:\n{texts[llm]}",
                         summaries[llm][other_llm],
                         llm
                    )       
                    st.subheader(f"**{llm}** ha valutato il riassunto di **{other_llm}**:")
                    st.write(f"{evaluation}")

if __name__ == "__main__":
    main()
