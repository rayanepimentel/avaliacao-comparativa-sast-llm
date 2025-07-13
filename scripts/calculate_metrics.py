# scripts/calculate_metrics.py

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
import os
import json
import sys

# Função para calcular métricas (mantida igual)
def calculate_metrics(tool_name, y_true, y_pred):
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    vp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    fp_rate = fp / (vp + fp) if (vp + fp) > 0 else 0

    return {
        'Ferramenta': tool_name,
        'Precisão': precision,
        'Recall': recall,
        'F1-Score': f1,
        'FP Rate': fp_rate,
        'VP': vp,
        'FP': fp,
        'FN': fn
    }

def main():
    # Obter o caminho do ground truth via argumento de linha de comando
    if len(sys.argv) < 2:
        print("Uso: python scripts/calculate_metrics.py <caminho_para_ground_truth.csv>")
        sys.exit(1)
    
    ground_truth_input_path = sys.argv[1] # O primeiro argumento é o caminho do arquivo

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Caminhos dos arquivos de entrada e saída
    llm_detections_path = os.path.join(project_root, 'results', 'llm_detections_results.csv')
    results_dir = os.path.join(project_root, 'results')
    
    os.makedirs(results_dir, exist_ok=True) 
    
    # Carregar o ground truth e resultados SAST do caminho fornecido
    if not os.path.exists(ground_truth_input_path):
        raise FileNotFoundError(f"Arquivo do ground truth não encontrado: {ground_truth_input_path}")
    df_ground_truth = pd.read_csv(ground_truth_input_path)
    
    # Carregar os resultados das detecções dos LLMs
    if not os.path.exists(llm_detections_path):
        print(f"AVISO: Arquivo de resultados LLM não encontrado em {llm_detections_path}.")
        print("Certifique-se de executar 'run_llm_analysis.py' primeiro para gerar os resultados dos LLMs.")
        # Se o arquivo LLM não existir, criamos um DataFrame vazio para merge
        # e as colunas serão preenchidas com NaN, que trataremos depois
        df_llm_detections = pd.DataFrame({'ID': df_ground_truth['ID'].unique()}) # Garante que todos os IDs do GT estão presentes
        df_llm_detections['Detected_Deepseek'] = pd.NA # Usa pd.NA para tipo Int64Dtype que suporta NA
        df_llm_detections['Detected_CodeLlama'] = pd.NA
    else:
        df_llm_detections = pd.read_csv(llm_detections_path)
        # Seleciona apenas as colunas de interesse para merge
        df_llm_detections = df_llm_detections[['ID', 'Detected_Deepseek', 'Detected_CodeLlama']]

    # Unir os DataFrames com base no ID do snippet
    df_combined = pd.merge(df_ground_truth, df_llm_detections, on='ID', how='left')

    # Renomear as colunas LLM para um nome consistente após o merge
    # Se existirem sufixos como '_x' ou '_y' após o merge, você pode precisar ajustar aqui
    # Assumimos que o merge não criou duplicação de nomes para as colunas de LLM.
    # Se houver, a coluna de LLM virá como 'Detected_Deepseek' do df_llm_detections
    # e a do ground_truth como 'Detected_Deepseek_x' se houver conflito de nomes.
    # Vamos verificar e renomear se necessário, ou usar as colunas criadas no merge.
    
    # Preencher NaN nas colunas de detecção dos LLMs com 0 (zero)
    # Isso é crucial antes de converter para int, representando "não detectado"
    if 'Detected_Deepseek' in df_combined.columns: # Verifica se a coluna existe após o merge
        df_combined['Detected_Deepseek'] = df_combined['Detected_Deepseek'].fillna(0)
    else: # Se a coluna não existiu por algum motivo no merge, crie-a e preencha com 0
        df_combined['Detected_Deepseek'] = 0
        
    if 'Detected_CodeLlama' in df_combined.columns: # Verifica se a coluna existe após o merge
        df_combined['Detected_CodeLlama'] = df_combined['Detected_CodeLlama'].fillna(0)
    else: # Se a coluna não existiu, crie-a e preencha com 0
        df_combined['Detected_CodeLlama'] = 0
        

    # Usar as colunas de detecção corretas para cada ferramenta
    # Assumimos que 'Detected_Semgrep' e 'Detected_Sonar' já estão no ground_truth
    # e que as colunas 'Detected_Deepseek' e 'Detected_CodeLlama' são as que vieram do merge (e foram tratadas para NaN)
    tools = {
        "Semgrep": df_combined["Detected_Semgrep"],
        "SonarQube": df_combined["Detected_Sonar"],
        "DeepSeek": df_combined["Detected_Deepseek"],
        "CodeLlama": df_combined["Detected_CodeLlama"]
    }
    
    # Verifica se a coluna Is_Vulnerable existe
    if 'Is_Vulnerable' not in df_combined.columns:
        raise ValueError("A coluna 'Is_Vulnerable' (Ground Truth) não foi encontrada no dataset combinado.")

    # A coluna 'Is_Vulnerable' é o y_true para todas as ferramentas
    y_true_common = df_combined["Is_Vulnerable"]
    
    results = []
    for tool_name, preds in tools.items():
        # Converte para int. Agora que NaN foi preenchido, deve funcionar.
        results.append(calculate_metrics(tool_name, y_true_common, preds.astype(int)))
    
    # Criar DataFrame de métricas
    df_metrics = pd.DataFrame(results)
    
    # Salvar CSV das métricas
    csv_path = os.path.join(results_dir, 'metrics_table.csv')
    df_metrics.to_csv(csv_path, index=False)
    
    # Salvar JSON do resumo das métricas (para o README)
    json_summary_path = os.path.join(results_dir, 'metrics_summary.json')
    df_metrics_for_json = df_metrics.copy()
    for col in ['Precisão', 'Recall', 'F1-Score', 'FP Rate']:
        df_metrics_for_json[col] = df_metrics_for_json[col].round(4)
    
    with open(json_summary_path, 'w') as f:
        json.dump(df_metrics_for_json.to_dict(orient='records'), f, indent=4)
    
    # Gerar HTML formatado
    html = df_metrics.to_html(
        index=False,
        float_format='{:.2%}'.format,
        columns=['Ferramenta', 'Precisão', 'Recall', 'F1-Score', 'FP Rate', 'VP', 'FP', 'FN'],
        border=1
    )
    
    html_path = os.path.join(results_dir, 'metrics_table.html')
    with open(html_path, 'w') as f:
        f.write("<h2>Tabela 2: Comparação de Métricas entre Ferramentas</h2>")
        f.write(html)
    
    print(f"✅ Resultados consolidados salvos em:\n- {csv_path}\n- {html_path}\n- {json_summary_path}")
    print("\nResumo da Tabela 2:")
    print(df_metrics[['Ferramenta', 'Precisão', 'Recall', 'F1-Score', 'FP Rate']].to_string(index=False))

if __name__ == "__main__":
    main()