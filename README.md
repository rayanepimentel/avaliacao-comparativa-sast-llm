
# Avaliação Comparativa do Desempenho de Inteligências Artificiais Generativas e Ferramentas Tradicionais na Análise de Código-Fonte JavaScript

**Artigo:** "Avaliação comparativa do desempenho de inteligências artificiais generativas e ferramentas tradicionais na análise de código-fonte JavaScript"

**Resumo do Artefato:** Este artefato implementa uma comparação sistemática do desempenho de inteligências artificiais generativas e ferramentas tradicionais na análise de código-fonte JavaScript. Ele permite a replicação dos experimentos que avaliaram ferramentas SAST (Semgrep/SonarQube) e modelos Large Language Models (LLMs) como DeepSeek e CodeLlama na detecção de vulnerabilidades JavaScript utilizando o OWASP Juice Shop como dataset. O estudo revela que as ferramentas SAST alcançam 100% de precisão para vulnerabilidades padrão (XSS/SQLi) , enquanto os LLMs oferecem maior recall (70% no DeepSeek) para ameaças contextuais (NoSQLi/controle de acesso quebrado), demonstrando a complementaridade entre as abordagens.

## Estrutura do readme.md

```
├── .github/workflows/                           # Pipelines SAST (GitHub Actions)
│   ├── semgrep.yml
│   └── sonarqube.yml
├── dataset/
│   ├── code_snippets/                           # Trechos de código analisados (15 arquivos .ts)
│   ├── juice_shop_15_files.csv                  # Metadados das análises e ground truth
│   ├── templates/                               # Modelos de arquivos para preenchimento manual
│       ├── llm_detections_manual_template.csv   # Template para registro manual das detecções dos LLMs
├── results/                                     # Armazena os resultados gerados pelos experimentos. Esta pasta inicia vazia e é preenchida pelos scripts.
├── scripts/
│   ├── calculate_metrics.py    # Gera a Tabela 2 do artigo
│   ├── run_llm_analysis.py     # Executa análise com LLMs (atualizado)
│   ├── run_sonar_analysis.sh   # Análise SonarQube automatizada (NOVO)
│   ├── validate_contextual_recall.py
│   ├── validate_environment.sh # Validação completa do ambiente (86 testes)
│   └── requirements.txt        # Dependências Python com versões travadas
├── Makefile                    # Interface de comandos simplificada 
├── docker-compose.yml          # Orquestração de serviços (Ollama, SonarQube, etc.)
└── README.md                   # Este arquivo
```

## Selos Considerados

Os selos considerados para este artefato são:

  * **Artefatos Disponíveis (Selo D):** O código-fonte, os scripts de automação e os dados (dataset de arquivos e ground truth) estão publicados em um repositório público no GitHub.
  * **Artefatos Funcionais (Selo F):** O artefato inclui instruções claras e scripts para a instalação e execução das ferramentas, permitindo que o revisor observe as funcionalidades de análise de vulnerabilidades tanto das ferramentas SAST quanto dos LLMs. Um teste mínimo com saída esperada é fornecido.
  * **Artefatos Sustentáveis (Selo S):** As dependências são versionadas através de `requirements.txt`, o ambiente é documentado, e a estrutura do código é organizada para facilitar a compreensão e manutenção.
  * **Experimentos Reprodutíveis (Selo R):** Os experimentos, incluindo o cálculo das métricas comparativas e a demonstração da análise de LLMs e SASTs, podem ser reproduzidos a partir de instruções passo a passo e scripts, com a indicação das saídas esperadas.

## Informações básicas

### Ambiente de Execução

  * **Sistema Operacional:** Linux (Ubuntu 20.04+), macOS ou WSL2
  * **Python:** 3.11
  * **Docker:** 20.10 (necessário para a execução local do SonarQube, se optar por não usar GitHub Actions)
  * **Memória RAM:** Mínimo 4GB (8GB recomendado para a execução dos LLMs).
  * **Espaço em disco:** 5GB livres.

### Recursos Adicionais

  * **Acesso à Internet:** Necessário para o download de dependências (modelos Ollama, pacotes Python, etc.).
  * **GPU:** Opcional para aceleração da inferência dos LLMs (altamente recomendado para reduzir o tempo de execução).



## Dataset Base

  * **OWASP Juice Shop v17.3.0:** O artefato utiliza um subconjunto de 15 arquivos desta aplicação web intencionalmente vulnerável.
  * **Arquivos de código-fonte:** Localizados em `dataset/code_snippets/`. Estes arquivos incluem exemplos vulneráveis e seguros, alguns dos quais foram pré-processados (remoção de comentários de desafio) para a análise dos LLMs, conforme descrito no artigo.
  * **Ground Truth:** O arquivo `dataset/juice_shop_15_files.csv` contém o mapeamento das vulnerabilidades conhecidas para cada arquivo, servindo como a "verdade" para o cálculo das métricas de desempenho.

## 🔄 Notas sobre Reprodutibilidade dos LLMs

Resultados de modelos generativos (DeepSeek/CodeLlama) **podem variar entre execuções** devido à:

- Natureza probabilística dos modelos
- Sensibilidade contextual em JavaScript
- Limitações de janela de contexto
- Variações na inicialização de pesos

## Instalação

Siga os passos abaixo para configurar o ambiente e as ferramentas:

### 1\. Clonagem do Repositório

```bash
git clone https://github.com/rayanepimentel/avaliacao-comparativa-sast-llm.git
cd avaliacao-comparativa-sast-llm
```

### 2\.Execute ambiente completo

```bash
make quick-start
```
A execução do `make quick-start` pode levar de 15 a 40 minutos, pois inclui o download dos modelos de linguagem.

## Teste Mínimo

Ao rodar `make quick-start`, será gerado o teste mímino.

**Saída esperada no terminal (similar à Tabela 2 do artigo):**

**Tabela 2. Comparação de Métricas entre Ferramentas de Análise de Segurança**

| Ferramenta | Precisão | Recall | F1-Score | FP Rate | VP | FP | FN |
|------------|----------|--------|----------|---------|----|----|----|
| Semgrep    | 100%     | 50%    | 67%      | 0%      | 5  | 0  | 5  |
| SonarQube  | 100%     | 10%    | 18%      | 0%      | 1  | 0  | 9  |
| DeepSeek   | 78%      | 70%    | 74%      | 22%     | 7  | 2  | 3  |
| CodeLlama  | 55%      | 60%    | 57%      | 45%     | 6  | 5  | 4  |

> **Nota:** VP = Verdadeiros Positivos, FP = Falsos Positivos, FN = Falsos Negativos.  
> Dados obtidos da análise do OWASP Juice Shop v17.3.0.


**Arquivos gerados/atualizados na pasta `results/` (inicialmente vazia):**

* `results/metrics_table.csv`: Um arquivo CSV contendo as métricas detalhadas para cada ferramenta.
* `results/metrics_table.html`: Um arquivo HTML com a Tabela 2 formatada.

### Validação da Execução

Para validar que o artefato foi corretamente instalado e executado:

1. Verifique a presença dos arquivos `metrics_table.csv` e `metrics_table.html` na pasta `results/`.
2. Abra o HTML no navegador e compare com a Tabela 2 do artigo.
3. Os tempos de execução devem estar próximos dos relatados.


## Experimentos

Esta seção descreve os passos para reproduzir os resultados apresentados no artigo.


### Reivindicação \#1: Recall de LLMs em Vulnerabilidades Contextuais

**Objetivo**: Validar que os modelos DeepSeek e CodeLlama alcançam alto recall em ameaças complexas e contextuais (como NoSQLi e Broken Access Control), compreendendo a natureza de suas detecções e a variabilidade inerente a modelos generativos.

**Processo**:
Este processo é dividido em duas etapas e deve ser executado na sequência:

1.  **Execução da Análise Bruta de LLMs (`run_llm_analysis.py`)**:

  ```bash
    make test-llm
   ```
 **Registre a Detecção e a Categoria Identificada:**
 O script `run_llm_analysis.py` gera automaticamente o arquivo `results/llm_detections_results.csv`. 
 
 Caso queira revisar ou preencher os dados manualmente, utilize o template de planilha fornecido em `dataset/templates/llm_detections_manual_template.csv`.

 - Se a resposta do LLM for `Código seguro`, registre a detecção como **0** (não vulnerável) e a categoria como `N/A`.
 - Se a resposta for um JSON com detalhes da vulnerabilidade, registre a 

2.  **Cálculo do Recall Contextual `(validate_contextual_recall.py)`**:

Com o arquivo `results/llm_detections_results.csv` gerado (automaticamente ou manualmente), execute o script `validate_contextual_recall.py`. Este script calculará o recall dos LLMs especificamente para as vulnerabilidades contextuais.

```Bash
make validate
```

- Tempo esperado: Menos de 10 segundos.
- Recursos esperados: Baixo consumo de CPU/RAM.

Saída Esperada no terminal:

🔍 **Resultados para Vulnerabilidades Contextuais:**

- **Amostras analisadas:** XY  
- **DeepSeek:** 4 detectadas | **Recall:** Y.Y% 
- **CodeLlama:** 3 detectadas | **Recall:** X.X%

**Detalhes por vulnerabilidade:**

| ID       | Vulnerability             | Detected_Deepseek | Detected_CodeLlama |
|----------|---------------------------|-------------------|--------------------|
| VULN-04  | NoSQL Injection           | X                 | X                  |
| VULN-05  | Broken Access Control     | X                 | X                  |
| VULN-06  | Sensitive Data Exposure   | X                 | X                  |
| VULN-09  | Broken Access Control     | X                 | X                  |
| VULN-10  | Validação insuficiente    | X                 | X                  |


Onde XY é o número de amostras contextuais, Y.Y% e X.X% são os recalls calculados para DeepSeek e CodeLlama, e X na tabela será 1 ou 0, indicando se o LLM detectou uma vulnerabilidade (1) ou não (0) naquela amostra.


### Reivindicação \#2: Execução SAST 

Execute

```bash
make test-sast
```

Verifique a saída no terminal e na pasta `/results/`

- semgrep_results.json
- semgrep_results.sarif
- sonarqube.issues.json


## Interface de Comandos Simplificada

Use o `Makefile` para comandos mais simples:

```bash
# Setup completo (recomendado para iniciantes)
make quick-start

# Comandos individuais
make test-minimal    # Teste rápido (2 min) - gera Tabela 2
make test-llm        # Análise com IA (30-80 min)
make test-sast       # Ferramentas profissionais (5-10 min)

# Gerenciamento
make logs           # Ver logs em tempo real
make shell          # Acessar terminal interno

# Solução de problemas
make reinit-models  # Se os modelos LLM falharem
make restart-sonarqube # Se o SonarQube travar
make clean          # Limpar tudo e recomeçar

# Validação
make validate-env   # 86 verificações do ambiente
make validate       # Validação completa
```

## LICENSE

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

