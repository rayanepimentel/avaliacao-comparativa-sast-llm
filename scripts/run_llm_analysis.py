# scripts/run_llm_analysis.py

import ollama
import pandas as pd
import os
import time
import json
import traceback
import re
from dotenv import load_dotenv
from collections import defaultdict

# Carregar configurações do .env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Caminho raiz do projeto (um nível acima do diretório 'scripts')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT) # Agora aponta para a raiz do seu repositório

# Configurações
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_VERSION', 'deepseek-coder:1.3b')
CODELLAMA_MODEL = os.getenv('CODELLAMA_VERSION', 'codellama:7b')
MAX_RETRIES = 3
RETRY_DELAY = 10  # segundos

PROMPT_TEMPLATE = """
Analise os riscos de segurança no código abaixo, seguindo o OWASP Top 10. Retorne APENAS se houver vulnerabilidades,
no formato JSON abaixo. Caso contrário, retorne "Código seguro".

{{
  "Arquivo": "Nome do arquivo",
  "Trecho Vulnerável": "O snippet de código específico que contém a vulnerabilidade.",
  "Tipo da Vulnerabilidade": "A categoria da vulnerabilidade",
  "Descrição Breve": "Uma explicação concisa (1-2 frases) de por que esse trecho é vulnerável"
}}

Code:
{code}
"""

def parse_llm_response_to_detection(llm_response):
    """
    Parses the LLM response to determine if a vulnerability was detected.
    Returns 1 if a vulnerability (JSON format or clear textual indication) is detected, 0 otherwise.
    """
    if llm_response is None:
        return 0

    response_lower = llm_response.strip().lower()

    # 1. Prioridade: Frase explícita de "Código seguro"
    if response_lower == "código seguro":
        return 0

    # 2. Prioridade: Tentativa de parsing JSON
    try:
        # Encontrar qualquer bloco JSON na resposta
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            # Verifica se o JSON tem as chaves esperadas para uma vulnerabilidade
            if isinstance(data, dict) and "tipo da vulnerabilidade" in {k.lower() for k in data.keys()}:
                return 1
            # Ou se é uma lista de JSONs e algum item tem a chave
            elif isinstance(data, list) and any(isinstance(item, dict) and "tipo da vulnerabilidade" in {k.lower() for k in item.keys()} for item in data):
                return 1
    except json.JSONDecodeError:
        pass # Ignora erros de JSONDecodeError, pois a resposta pode ser textual
    except Exception as e:
        pass # Ignora outros erros de parsing JSON, a resposta pode ser textual

    # 3. Fallback: Verificação de palavras-chave de vulnerabilidade no texto
    # (Adicione mais palavras-chave se julgar necessário)
    vulnerability_keywords = [
        "vulnerável", "vulnerability", "injection", "xss", "csrf",
        "access control", "insecure", "falha de segurança", "risco de segurança",
        "falha de validação", "sql", "nosql", "sensitive data", "ssrf",
        "cwe-" # Para capturar menções a Common Weakness Enumeration
    ]
    
    # Verifica se alguma palavra-chave de vulnerabilidade aparece no texto
    # e se a resposta não foi classificada como "código seguro" no passo 1
    # Adicionada uma verificação para evitar falsos positivos se o LLM "falar sobre" vulnerabilidades,
    # mas no final da frase dizer que o código está seguro ou não vulnerável.
    negative_phrases = ["não contém vulnerabilidades", "no vulnerabilities", "not vulnerable", "está seguro", "no security risks"]

    # Verifica se contém uma palavra-chave de vulnerabilidade E NÃO contém uma frase negativa
    if any(keyword in response_lower for keyword in vulnerability_keywords) and \
       not any(neg_phrase in response_lower for neg_phrase in negative_phrases):
        return 1
            
    return 0 # Não detectou vulnerabilidade de acordo com as regras acima

def analyze_code(file_path, model_name, file_name_for_prompt):
    """Analisa um arquivo com o modelo LLM especificado, com retries."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Ajusta o prompt para incluir o nome do arquivo corretamente
        final_prompt = PROMPT_TEMPLATE.format(code=code).replace('"Arquivo": "Nome do arquivo"', f'"Arquivo": "{file_name_for_prompt}"')

        for attempt in range(MAX_RETRIES):
            try:
                print(f"  Tentativa {attempt + 1}/{MAX_RETRIES} para {model_name} em {file_name_for_prompt}...")
                response = ollama.generate(
                    model=model_name,
                    prompt=final_prompt,
                    # Não forçar 'json' no formato aqui, pois o LLM pode nem sempre retornar JSON perfeito.
                    # O parse_llm_response_to_detection é mais robusto na verificação do retorno.
                    options={'temperature': 0.0} 
                )
                if 'response' in response:
                    return response['response'].strip()
                else:
                    return f"ERROR: Resposta inesperada - {response}"

            except ollama.ResponseError as e:
                error_msg = str(e).lower()
                if "context length" in error_msg:
                    print(f"  Context length exceeded para {file_name_for_prompt} com {model_name}. Pulando retries.")
                    return "ERROR: Context length exceeded"
                
                print(f"  Erro Ollama: {error_msg}. Retrying...")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    return f"ERROR: {type(e).__name__}: {str(e)}"
            except Exception as e:
                print(f"  Erro genérico Ollama: {e}. Retrying...")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    return f"ERROR: {type(e).__name__}: {str(e)}"

    except FileNotFoundError:
        # Este erro deve ser tratado *antes* de chamar analyze_code
        # mas mantido aqui como um fallback de segurança
        print(f"  AVISO: Arquivo snippet não encontrado: {file_path} dentro de analyze_code.")
        return "ERROR: Snippet file not found"
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        print(f"  ❌ Erro geral ao processar {file_path} com modelo {model_name}:\n{error_message}")
        print(traceback.format_exc())
        return f"ERROR: {error_message}"

def main():
    # Caminhos para o dataset e resultados
    dataset_ground_truth_path = os.path.join(PROJECT_ROOT, 'dataset', 'juice_shop_15_files.csv')
    snippets_dir = os.path.join(PROJECT_ROOT, 'dataset', 'code_snippets') 
    results_dir = os.path.join(PROJECT_ROOT, 'results')
    
    # Nome do arquivo de saída para os resultados dos LLMs
    llm_output_csv_name = 'llm_detections_results.csv'
    llm_output_csv_path = os.path.join(results_dir, llm_output_csv_name)

    os.makedirs(results_dir, exist_ok=True)

    if not os.path.exists(dataset_ground_truth_path):
        raise FileNotFoundError(f"Arquivo do dataset não encontrado: {dataset_ground_truth_path}.")
    if not os.path.exists(snippets_dir):
        raise FileNotFoundError(f"Pasta de snippets não encontrada: {snippets_dir}.")

    # Carregar o DataFrame original (ground truth e resultados SAST)
    df_ground_truth = pd.read_csv(dataset_ground_truth_path)

    # DataFrame para armazenar apenas os resultados dos LLMs
    df_llm_results = df_ground_truth[['ID', 'File', 'Vulnerability']].copy()
    
    # Adicionar colunas específicas para resultados LLM
    df_llm_results['Detected_Deepseek'] = 0
    df_llm_results['DeepSeek_Raw_Result'] = ''
    df_llm_results['DeepSeek_Time'] = 0.0

    df_llm_results['Detected_CodeLlama'] = 0
    df_llm_results['CodeLlama_Raw_Result'] = ''
    df_llm_results['CodeLlama_Time'] = 0.0

    print("Iniciando análise de LLMs. Isso pode levar um tempo...")
    start_time = time.time()

    for idx, row in df_llm_results.iterrows():
        # Construindo o caminho do snippet a partir do ID
        # O nome do arquivo real na pasta 'code_snippets' é baseado no ID do CSV
        # Assumimos extensão .ts para todos os arquivos de snippet
        filename_in_snippets_folder = f"{row['ID']}.ts" 
        snippet_file_full_path = os.path.join(snippets_dir, filename_in_snippets_folder)
        
        # O nome do arquivo para o prompt deve ser o caminho original do Juice Shop
        file_name_for_prompt = row['File'] # Esta coluna 'File' vem do CSV original

        if not os.path.exists(snippet_file_full_path):
            print(f"⚠️ Arquivo de snippet não encontrado em: {snippet_file_full_path}. Pulando ID: {row['ID']}")
            # Marcar como erro ou não detectado nos resultados LLM para este caso
            df_llm_results.at[idx, 'DeepSeek_Raw_Result'] = "ERROR: Snippet file not found"
            df_llm_results.at[idx, 'CodeLlama_Raw_Result'] = "ERROR: Snippet file not found"
            # As colunas Detected_Deepseek e Detected_CodeLlama permanecerão 0 por default
            continue
        
        print(f"Processando ID: {row['ID']} (arquivo: {file_name_for_prompt})...")

        # Análise com DeepSeek
        deepseek_start = time.time()
        deepseek_raw_result = analyze_code(snippet_file_full_path, DEEPSEEK_MODEL, file_name_for_prompt)
        deepseek_time = time.time() - deepseek_start
        
        df_llm_results.at[idx, 'DeepSeek_Raw_Result'] = deepseek_raw_result
        df_llm_results.at[idx, 'Detected_Deepseek'] = parse_llm_response_to_detection(deepseek_raw_result)
        df_llm_results.at[idx, 'DeepSeek_Time'] = deepseek_time

        # Análise com CodeLlama
        llama_start = time.time()
        codellama_raw_result = analyze_code(snippet_file_full_path, CODELLAMA_MODEL, file_name_for_prompt)
        llama_time = time.time() - llama_start
        
        df_llm_results.at[idx, 'CodeLlama_Raw_Result'] = codellama_raw_result
        df_llm_results.at[idx, 'Detected_CodeLlama'] = parse_llm_response_to_detection(codellama_raw_result)
        df_llm_results.at[idx, 'CodeLlama_Time'] = llama_time
        
        print(f"  Detecção DeepSeek: {df_llm_results.at[idx, 'Detected_Deepseek']} | Detecção CodeLlama: {df_llm_results.at[idx, 'Detected_CodeLlama']}")


    # Salvar o DataFrame de resultados dos LLMs em um NOVO arquivo CSV
    df_llm_results.to_csv(llm_output_csv_path, index=False)

    total_time = time.time() - start_time
    print(f"\n✅ Análise de LLMs completa em {total_time/60:.1f} minutos.")
    print(f"📊 Resultados dos LLMs salvos em: {llm_output_csv_path}")
    print("Agora você pode executar scripts/calculate_metrics.py para ver os resultados consolidados.")

if __name__ == "__main__":
    main()