# scripts/validate_contextual_recall.py
import pandas as pd

# Vulnerabilidades contextuais alvo
CONTEXTUAL_VULNS = ["VULN-04", "VULN-05", "VULN-06", "VULN-09", "VULN-10"]

def main():
    # Carregar ground truth
    truth = pd.read_csv("dataset/juice_shop_15_files.csv")
    
    # Filtrar apenas vulnerabilidades contextuais
    contextual_truth = truth[truth["ID"].isin(CONTEXTUAL_VULNS)]
    
    # Carregar resultados LLM
    llm_results = pd.read_csv("results/llm_detections_results.csv")
    
    # Juntar dados
    merged = pd.merge(
        contextual_truth[["ID", "Vulnerability"]], 
        llm_results[["ID", "Detected_Deepseek", "Detected_CodeLlama"]],
        on="ID"
    )
    
    # Calcular True Positives para cada modelo
    merged["DeepSeek_Correct"] = merged["Detected_Deepseek"] == 1
    merged["CodeLlama_Correct"] = merged["Detected_CodeLlama"] == 1
    
    # Calcular recall
    deepseek_recall = merged["DeepSeek_Correct"].mean()
    codellama_recall = merged["CodeLlama_Correct"].mean()
    
    print("\n🔍 Resultados para Vulnerabilidades Contextuais:")
    print(f"- Amostras analisadas: {len(merged)}")
    print(f"- DeepSeek: {merged['DeepSeek_Correct'].sum()} detectadas | Recall: {deepseek_recall:.1%}")
    print(f"- CodeLlama: {merged['CodeLlama_Correct'].sum()} detectadas | Recall: {codellama_recall:.1%}")
    
    # Salvar relatório detalhado
    merged.to_csv("results/contextual_validation_report.csv", index=False)
    
    # Exibir tabela resumo
    print("\nDetalhes por vulnerabilidade:")
    print(merged[["ID", "Vulnerability", "Detected_Deepseek", "Detected_CodeLlama"]])

if __name__ == "__main__":
    main()