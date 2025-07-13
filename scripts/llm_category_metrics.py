import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
import os
import json
import sys

def calculate_metrics(llm_name, y_true, y_pred):
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    vp = sum((yt == 1 and yp == 1) for yt, yp in zip(y_true, y_pred))
    fp = sum((yt == 0 and yp == 1) for yt, yp in zip(y_true, y_pred))
    fn = sum((yt == 1 and yp == 0) for yt, yp in zip(y_true, y_pred))

    fp_rate = fp / (vp + fp) if (vp + fp) > 0 else 0

    return {
        'LLM': llm_name,
        'Precisão': precision,
        'Recall': recall,
        'F1-Score': f1,
        'FP Rate': fp_rate,
        'VP': vp,
        'FP': fp,
        'FN': fn
    }

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/calculate_llm_metrics.py <caminho_para_ground_truth.csv>")
        sys.exit(1)
    
    ground_truth_path = sys.argv[1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    llm_detections_path = os.path.join(project_root, 'results', 'llm_detections_results.csv')
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)

    if not os.path.exists(ground_truth_path):
        raise FileNotFoundError(f"Arquivo de ground truth não encontrado: {ground_truth_path}")
    df_gt = pd.read_csv(ground_truth_path)

    if not os.path.exists(llm_detections_path):
        print(f"⚠️ Arquivo de detecções LLM não encontrado em {llm_detections_path}")
        sys.exit(1)
    df_llm = pd.read_csv(llm_detections_path)

    df_combined = pd.merge(df_gt, df_llm, on='ID', how='left')

    for col in ['Detected_Deepseek', 'Detected_CodeLlama']:
        if col not in df_combined.columns:
            df_combined[col] = 0
        else:
            df_combined[col] = df_combined[col].fillna(0)

    if 'Is_Vulnerable' not in df_combined.columns:
        raise ValueError("Coluna 'Is_Vulnerable' não encontrada no dataset.")

    y_true = df_combined["Is_Vulnerable"]
    llm_tools = {
        "DeepSeek": df_combined["Detected_Deepseek"],
        "CodeLlama": df_combined["Detected_CodeLlama"]
    }

    metrics = []
    for name, preds in llm_tools.items():
        metrics.append(calculate_metrics(name, y_true, preds.astype(int)))

    df_metrics = pd.DataFrame(metrics)

    # Exportar resultados
    csv_path = os.path.join(results_dir, 'llm_metrics_table.csv')
    df_metrics.to_csv(csv_path, index=False)

    json_path = os.path.join(results_dir, 'llm_metrics_summary.json')
    with open(json_path, 'w') as f:
        json.dump(df_metrics.round(4).to_dict(orient='records'), f, indent=4)

    html_path = os.path.join(results_dir, 'llm_metrics_table.html')
    with open(html_path, 'w') as f:
        f.write("<h2>Tabela: Métricas dos LLMs</h2>")
        f.write(df_metrics.to_html(index=False, float_format='{:.2%}'.format))

    print(f"✅ Métricas dos LLMs salvas em:\n- {csv_path}\n- {html_path}\n- {json_path}")
    print(df_metrics[['LLM', 'Precisão', 'Recall', 'F1-Score', 'FP Rate']].to_string(index=False))

if __name__ == "__main__":
    main()
