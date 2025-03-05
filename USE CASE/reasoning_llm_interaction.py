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

def evaluate_reasoning(problem, solution, judge_model):
    """Funzione per valutare una soluzione di reasoning da 1 a 10."""
    evaluation_prompt = f"""
    Valuta la seguente soluzione al problema di reasoning: "{problem}"
    Soluzione proposta: "{solution}"
    Assegna un punteggio da 1 a 10 basato sulla correttezza, logica e chiarezza del ragionamento.
    Fornisci anche un breve feedback.
    """
    evaluation = ask_ollama(evaluation_prompt, judge_model)
    return evaluation

def generate_reasoning_problem(model):
    """Funzione per generare un problema di reasoning di media difficoltà."""
    prompt = "Genera un problema di reasoning di media difficoltà."
    problem = ask_ollama(prompt, model)
    return problem

def solve_reasoning_problem(problem, model):
    """Funzione per risolvere un problema di reasoning."""
    prompt = f"Risolvi il seguente problema di reasoning:\n{problem}"
    solution = ask_ollama(prompt, model)
    return solution

def main():
    st.title("Interazione tra 4 LLM su Ollama - Problemi di Reasoning")

    if st.button("Avvia l'interazione"):
        results = {}

        # Fase 1: Ogni LLM genera un problema di reasoning
        problems = {}
        solutions = {}
        for llm in LLM_NAMES:
            problems[llm] = generate_reasoning_problem(llm)
            st.write(f"**{llm}** ha generato il seguente problema di reasoning:")
            st.text_area("Problema", problems[llm], height=150)

            # Fase 2: Ogni LLM risolve il problema degli altri LLM
            solutions[llm] = {}
            for other_llm in LLM_NAMES:
                if other_llm != llm:
                    solutions[llm][other_llm] = solve_reasoning_problem(problems[llm], other_llm)
                    st.write(f"**{other_llm}** ha risolto il problema di **{llm}**:")
                    st.text_area("Soluzione", solutions[llm][other_llm], height=300)

        # Fase 3: Ogni LLM valuta la soluzione degli altri LLM
                    evaluation = evaluate_reasoning(
                        problems[llm],
                        solutions[llm][other_llm],
                        llm
                    )
                    st.write(f"**{llm}** ha valutato la soluzione di **{other_llm}**: {evaluation}")

if __name__ == "__main__":
    main()
