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

# Caminho raiz do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurações com fallbacks robustos
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_VERSION', 'deepseek-coder:1.3b')
CODELLAMA_MODEL = os.getenv('CODELLAMA_VERSION', 'codellama:7b')
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT_SECONDS = 120  # Timeout para cada requisição

PROMPT_TEMPLATE = """
Analise os riscos de segurança no código abaixo, seguindo o OWASP Top 10. 
Retorne APENAS se houver vulnerabilidades, no formato JSON abaixo. 
Caso contrário, retorne "Código seguro".

{{
  "Arquivo": "{filename}",
  "Trecho Vulnerável": "O snippet específico",
  "Tipo da Vulnerabilidade": "A categoria da vulnerabilidade",
  "Descrição Breve": "Explicação concisa"
}}

Code:
{code}
"""

def check_ollama_connection():
    """Verifica se Ollama está funcionando."""
    try:
        response = ollama.list()
        print(f"✅ Ollama conectado. Modelos disponíveis: {[model['model'] for model in response.get('models', [])]}")
        return True
    except Exception as e:
        print(f"❌ Ollama não está respondendo: {e}")
        return False
def check_model_availability(model_name):
    """Verifica se um modelo específico está disponível."""
    try:
        models = ollama.list()
        model_names = [model['model'] for model in models.get('models', [])]
        if model_name in model_names:
            return True
        else:
            print(f"⚠️ Modelo {model_name} não encontrado. Tentando baixar...")
            try:
                # Adicionar timeout para operação de pull
                import threading
                
                def pull_model():
                    ollama.pull(model_name)
                
                thread = threading.Thread(target=pull_model)
                thread.start()
                thread.join(timeout=300)  # 5 minutos de timeout
                
                if thread.is_alive():
                    print(f"❌ Timeout ao baixar modelo {model_name}")
                    return False
                    
                # Verificar novamente após o pull
                models = ollama.list()
                model_names = [model['model'] for model in models.get('models', [])]
                return model_name in model_names
            except Exception as pull_error:
                print(f"❌ Erro ao baixar modelo {model_name}: {pull_error}")
                return False
    except Exception as e:
        print(f"❌ Erro verificando modelo {model_name}: {e}")
        return False

def parse_llm_response_to_detection(llm_response):
    """
    Parses the LLM response to determine if a vulnerability was detected.
    Returns 1 if vulnerability detected, 0 otherwise.
    """
    if llm_response is None or llm_response.strip() == "":
        return 0

    response_lower = llm_response.strip().lower()

    # 1. Código explicitamente seguro
    if response_lower in ["código seguro", "codigo seguro", "safe code", "no vulnerabilities"]:
        return 0

    # 2. Verificar se começa com ERROR
    if response_lower.startswith("error"):
        print(f"⚠️ Resposta com erro: {llm_response[:100]}...")
        return 0

    # 3. Tentar parsing JSON
    try:
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            if isinstance(data, dict) and any(key.lower() in ["tipo da vulnerabilidade", "vulnerability type", "tipo"] for key in data.keys()):
                return 1
    except json.JSONDecodeError:
        pass

    # 4. Verificação de palavras-chave
    vulnerability_keywords = [
        "vulnerável", "vulnerability", "injection", "xss", "csrf",
        "access control", "insecure", "falha de segurança", "risco",
        "sql", "nosql", "sensitive data", "broken", "cwe-"
    ]
    
    negative_phrases = [
        "não contém vulnerabilidades", "no vulnerabilities", "not vulnerable", 
        "está seguro", "no security risks", "secure code", "sem riscos"
    ]

    has_vuln_keyword = any(keyword in response_lower for keyword in vulnerability_keywords)
    has_negative_phrase = any(neg_phrase in response_lower for neg_phrase in negative_phrases)
    
    if has_vuln_keyword and not has_negative_phrase:
        return 1
            
    return 0

def analyze_code(file_path, model_name, file_name_for_prompt):
    """Analisa um arquivo com o modelo LLM especificado, com retries robustos."""
    try:
        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            return "ERROR: Snippet file not found"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Truncar código se muito longo (limitação de contexto)
        if len(code) > 8000:
            code = code[:8000] + "\n// ... código truncado ..."
            print(f"  ⚠️ Código truncado para {file_name_for_prompt}")

        # Preparar prompt
        final_prompt = PROMPT_TEMPLATE.format(
            filename=file_name_for_prompt,
            code=code
        )

        # Verificar modelo antes de usar
        if not check_model_availability(model_name):
            return f"ERROR: Model {model_name} not available"

        for attempt in range(MAX_RETRIES):
            try:
                print(f"  📡 Tentativa {attempt + 1}/{MAX_RETRIES} para {model_name}...")
                
                start_time = time.time()
                response = ollama.generate(
                    model=model_name,
                    prompt=final_prompt,
                    options={
                        'temperature': 0.0,
                        'timeout': TIMEOUT_SECONDS
                    }
                )
                elapsed = time.time() - start_time
                
                if 'response' in response and response['response']:
                    result = response['response'].strip()
                    print(f"  ✅ Resposta recebida em {elapsed:.1f}s ({len(result)} chars)")
                    return result
                else:
                    print(f"  ⚠️ Resposta vazia: {response}")
                    if attempt == MAX_RETRIES - 1:
                        return "ERROR: Empty response from model"

            except Exception as e:
                error_msg = str(e).lower()
                print(f"  ❌ Erro: {error_msg}")
                
                # Tratamento específico para diferentes tipos de erro
                if "context length" in error_msg or "context" in error_msg:
                    return "ERROR: Context length exceeded"
                elif "timeout" in error_msg:
                    print(f"  ⏱️ Timeout na tentativa {attempt + 1}")
                elif "connection" in error_msg or "network" in error_msg:
                    print(f"  🌐 Problema de conexão na tentativa {attempt + 1}")
                elif "model" in error_msg and "not found" in error_msg:
                    return f"ERROR: Model {model_name} not found"
                
                if attempt < MAX_RETRIES - 1:
                    print(f"  🔄 Aguardando {RETRY_DELAY}s antes de tentar novamente...")
                    time.sleep(RETRY_DELAY)
                else:
                    return f"ERROR: {type(e).__name__}: {str(e)[:200]}"

    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
        print(f"  💥 Erro geral ao processar {file_path}: {error_message}")
        return f"ERROR: {error_message}"

def main():
    print("🚀 Iniciando análise de LLMs...")
    
    # Verificar Ollama
    if not check_ollama_connection():
        print("❌ Ollama não está disponível. Certifique-se de que está rodando.")
        exit(1)

    # Caminhos
    dataset_ground_truth_path = os.path.join(PROJECT_ROOT, 'dataset', 'juice_shop_15_files.csv')
    snippets_dir = os.path.join(PROJECT_ROOT, 'dataset', 'code_snippets') 
    results_dir = os.path.join(PROJECT_ROOT, 'results')
    llm_output_csv_path = os.path.join(results_dir, 'llm_detections_results.csv')

    os.makedirs(results_dir, exist_ok=True)

    # Verificar arquivos necessários
    if not os.path.exists(dataset_ground_truth_path):
        raise FileNotFoundError(f"Arquivo do dataset não encontrado: {dataset_ground_truth_path}")
    if not os.path.exists(snippets_dir):
        raise FileNotFoundError(f"Pasta de snippets não encontrada: {snippets_dir}")

    # Carregar ground truth
    df_ground_truth = pd.read_csv(dataset_ground_truth_path)
    print(f"📊 Carregados {len(df_ground_truth)} arquivos para análise")

    # Verificar modelos disponíveis
    models_to_test = [DEEPSEEK_MODEL, CODELLAMA_MODEL]
    available_models = []
    
    for model in models_to_test:
        if check_model_availability(model):
            available_models.append(model)
            print(f"✅ Modelo disponível: {model}")
        else:
            print(f"❌ Modelo indisponível: {model}")
    
    if not available_models:
        print("❌ Nenhum modelo LLM disponível. Verifique a instalação do Ollama.")
        exit(1)

    # DataFrame para resultados LLM
    df_llm_results = df_ground_truth[['ID', 'File', 'Vulnerability']].copy()
    
    # Inicializar colunas para cada modelo disponível
    if DEEPSEEK_MODEL in available_models:
        df_llm_results['Detected_Deepseek'] = 0
        df_llm_results['DeepSeek_Raw_Result'] = ''
        df_llm_results['DeepSeek_Time'] = 0.0

    if CODELLAMA_MODEL in available_models:
        df_llm_results['Detected_CodeLlama'] = 0
        df_llm_results['CodeLlama_Raw_Result'] = ''
        df_llm_results['CodeLlama_Time'] = 0.0

    print(f"🔬 Iniciando análise com {len(available_models)} modelo(s)...")
    start_time = time.time()

    for idx, row in df_llm_results.iterrows():
        filename_in_snippets = f"{row['ID']}.ts" 
        snippet_file_path = os.path.join(snippets_dir, filename_in_snippets)
        file_name_for_prompt = row['File']

        if not os.path.exists(snippet_file_path):
            print(f"⚠️ Arquivo não encontrado: {snippet_file_path}")
            # Marcar como erro para todos os modelos disponíveis
            if DEEPSEEK_MODEL in available_models:
                df_llm_results.at[idx, 'DeepSeek_Raw_Result'] = "ERROR: Snippet file not found"
            if CODELLAMA_MODEL in available_models:
                df_llm_results.at[idx, 'CodeLlama_Raw_Result'] = "ERROR: Snippet file not found"
            continue
        
        print(f"\n📁 Processando {row['ID']} ({file_name_for_prompt})...")

        # Análise com DeepSeek (se disponível)
        if DEEPSEEK_MODEL in available_models:
            print(f"🤖 Analisando com DeepSeek...")
            deepseek_start = time.time()
            deepseek_result = analyze_code(snippet_file_path, DEEPSEEK_MODEL, file_name_for_prompt)
            deepseek_time = time.time() - deepseek_start
            
            df_llm_results.at[idx, 'DeepSeek_Raw_Result'] = deepseek_result
            df_llm_results.at[idx, 'Detected_Deepseek'] = parse_llm_response_to_detection(deepseek_result)
            df_llm_results.at[idx, 'DeepSeek_Time'] = deepseek_time
            
            detection_status = "✅ DETECTADO" if df_llm_results.at[idx, 'Detected_Deepseek'] == 1 else "❌ NÃO DETECTADO"
            print(f"  DeepSeek: {detection_status} ({deepseek_time:.1f}s)")

        # Análise com CodeLlama (se disponível)
        if CODELLAMA_MODEL in available_models:
            print(f"🦙 Analisando com CodeLlama...")
            llama_start = time.time()
            codellama_result = analyze_code(snippet_file_path, CODELLAMA_MODEL, file_name_for_prompt)
            llama_time = time.time() - llama_start
            
            df_llm_results.at[idx, 'CodeLlama_Raw_Result'] = codellama_result
            df_llm_results.at[idx, 'Detected_CodeLlama'] = parse_llm_response_to_detection(codellama_result)
            df_llm_results.at[idx, 'CodeLlama_Time'] = llama_time
            
            detection_status = "✅ DETECTADO" if df_llm_results.at[idx, 'Detected_CodeLlama'] == 1 else "❌ NÃO DETECTADO"
            print(f"  CodeLlama: {detection_status} ({llama_time:.1f}s)")

        # Progresso
        progress = (idx + 1) / len(df_llm_results) * 100
        print(f"📊 Progresso: {progress:.1f}% ({idx + 1}/{len(df_llm_results)})")

    # Salvar resultados
    df_llm_results.to_csv(llm_output_csv_path, index=False)

    total_time = time.time() - start_time
    print(f"\n🎉 Análise concluída em {total_time/60:.1f} minutos!")
    print(f"💾 Resultados salvos em: {llm_output_csv_path}")

    # Relatório resumido
    print(f"\n📈 Relatório Resumido:")
    if DEEPSEEK_MODEL in available_models:
        deepseek_detections = df_llm_results['Detected_Deepseek'].sum()
        print(f"  DeepSeek: {deepseek_detections}/{len(df_llm_results)} detecções")
    
    if CODELLAMA_MODEL in available_models:
        codellama_detections = df_llm_results['Detected_CodeLlama'].sum()
        print(f"  CodeLlama: {codellama_detections}/{len(df_llm_results)} detecções")

    print(f"\n🔄 Próximo passo: python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv")

if __name__ == "__main__":
    main()