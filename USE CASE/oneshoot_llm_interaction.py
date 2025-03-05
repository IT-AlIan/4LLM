import requests
import json
import streamlit as st
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

# Disabilita gli avvisi di verifica SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configurazione dei LLM (nomi dei modelli su Ollama)
#LLM_NAMES = ["LLM-A", "LLM-B", "LLM-C", "LLM-D"]
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
        "Authorization": "Bearer 7b22b1b62737ade2dd3b8f2f8781a506de5fdbbded5015727a088e17b2ad5aaf"  # Se richiesto
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, verify=False)
        logging.debug(f"Richiesta: {payload}")
        logging.debug(f"Risposta: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return f"Errore: {response.status_code} - {response.text}"
    except requests.exceptions.SSLError as e:
        return f"Errore SSL: {str(e)}"

def evaluate_response(question, response, judge_model):
    """Funzione per valutare una risposta da 1 a 10."""
    prompt = f"""
    Valuta la seguente risposta alla domanda: "{question}"
    Risposta: "{response}"
    Assegna un punteggio da 1 a 10 basato sulla pertinenza, completezza e chiarezza.
    Fornisci anche un breve feedback.
    """
    evaluation = ask_ollama(prompt, judge_model)
    return evaluation

def generate_question(category, model):
    """Funzione per generare una domanda in una certa categoria."""
    prompt = f"Crea una domanda sulla categoria: {category}"
    question = ask_ollama(prompt, model)
    return question

def main():
    st.title("Interazione tra 4 LLM su domande a tema")
    category = st.text_input("Inserisci una categoria per le domande (es. scienza, storia):", "scienza")

    if st.button("Avvia l'interazione"):
        results = {}

        # Fase 1: Ogni LLM genera una domanda
        questions = {}
        responses = {}
        evaluations = {}
        for llm in LLM_NAMES:
            st.header(f"**{llm}** interroga gli altri LLM", divider="blue")
            questions[llm] = generate_question(category, llm)
            st.subheader(f"**{llm}** ha generato la domanda:")
            st.write(f"{questions[llm]}")

            # Fase 2: Ogni LLM risponde alle domande degli altri
            responses[llm] = {}
            evaluations[llm] = {}
            for other_llm in LLM_NAMES:
                if other_llm != llm:
                    st.divider()
                    responses[llm][other_llm] = ask_ollama(questions[llm], other_llm)
                    st.subheader(f"**{other_llm}** ha risposto alla domanda di **{llm}**:")
                    st.write(f"{responses[llm][other_llm]}")

                    # Fase 3: Ogni LLM valuta le risposte degli altri
                    evaluations[llm][other_llm] = evaluate_response(questions[llm], responses[llm][other_llm], llm)
                    st.subheader(f"**{llm}** ha valutato la risposta di **{other_llm}**:")
                    st.write(f"{evaluations[llm][other_llm]}")

if __name__ == "__main__":
    main()
