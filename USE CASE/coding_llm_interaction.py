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
    Assegna un punteggio da 1 a 10 basato sulla correttezza, efficienza e leggibilità del codice.
    Fornisci anche un breve feedback.
    """
    evaluation = ask_ollama(evaluation_prompt, judge_model)
    return evaluation

def generate_coding_problem(model):
    """Funzione per generare un problema di coding di media difficoltà."""
    prompt = "Genera un problema di coding di media difficoltà. Descrivi il problema in modo chiaro e fornisci un esempio di input e output."
    problem = ask_ollama(prompt, model)
    return problem

def solve_coding_problem(problem, model):
    """Funzione per risolvere un problema di coding."""
    prompt = f"""
    Scrivi un programma per risolvere il seguente problema di coding:
    {problem}
    Fornisci il codice completo e una breve spiegazione del funzionamento.
    """
    solution = ask_ollama(prompt, model)
    return solution

def main():
    st.title("Interazione tra 4 LLM su Ollama: Valutazione di problemi di coding")

    if st.button("Avvia l'interazione"):
        results = {}

        # Fase 1: Ogni LLM genera un problema di coding
        problems = {}
        solutions = {}
        for llm in LLM_NAMES:
            st.header(f"**{llm}** interroga gli altri LLM", divider="blue")
            problems[llm] = generate_coding_problem(llm)
            st.subheader(f"**{llm}** ha generato il seguente problema di coding:")
            st.text_area("Problema", problems[llm], height=200)

            # Fase 2: Ogni LLM risolve il problema degli altri LLM
            solutions[llm] = {}
            for other_llm in LLM_NAMES:
                if other_llm != llm:
                    st.divider()
                    solutions[llm][other_llm] = solve_coding_problem(problems[llm], other_llm)
                    st.subheader(f"**{other_llm}** ha risolto il problema di **{llm}**:")
                    st.text_area("Soluzione", solutions[llm][other_llm], height=300)

                    # Fase 3: Ogni LLM valuta la soluzione degli altri LLM
                    evaluation = evaluate_response(
                        f"Risolvi il seguente problema di coding:\n{problems[llm]}",
                        solutions[llm][other_llm],
                        llm
                    )
                    st.subheader(f"**{llm}** ha valutato la soluzione di **{other_llm}**:")
                    st.write(f"{evaluation}")

if __name__ == "__main__":
    main()
