
# Avaliação Comparativa do Desempenho de Inteligências Artificiais Generativas e Ferramentas Tradicionais na Análise de Código-Fonte JavaScript

**Artigo:** "Avaliação comparativa do desempenho de inteligências artificiais generativas e ferramentas tradicionais na análise de código-fonte JavaScript"

**Resumo do Artefato:** Este artefato implementa uma comparação sistemática do desempenho de inteligências artificiais generativas e ferramentas tradicionais na análise de código-fonte JavaScript. Ele permite a replicação dos experimentos que avaliaram ferramentas SAST (Semgrep/SonarQube) e modelos Large Language Models (LLMs) como DeepSeek e CodeLlama na detecção de vulnerabilidades JavaScript utilizando o OWASP Juice Shop como dataset. O estudo revela que as ferramentas SAST alcançam 100% de precisão para vulnerabilidades padrão (XSS/SQLi) , enquanto os LLMs oferecem maior recall (70% no DeepSeek) para ameaças contextuais (NoSQLi/controle de acesso quebrado), demonstrando a complementaridade entre as abordagens.

## Estrutura do readme.md

```
├── .github/workflows/                # Pipelines SAST (GitHub Actions)
│   ├── semgrep.yml
│   └── sonarqube.yml
├── dataset/
│   ├── code_snippets/                # Trechos de código analisados (15 arquivos .ts)
│   ├── juice_shop_15_files.csv       # Metadados das análises e ground truth
├── results/                          # Armazena os resultados gerados pelos experimentos. Esta pasta inicia vazia e é preenchida pelos scripts.
├── scripts/
│   ├── calculate_metrics.py          # Gera a Tabela 2 do artigo
│   ├── llm_calculate_metrics.py      # Gera calculo de métricas LLMs
│   ├── requirements.txt              # Dependências Python
│   ├── run_llm_analysis.py           # Executa análise com LLMs
│   ├── setup_models.sh               # Instala Ollama + modelos
└── README.md                         # Este arquivo
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
  * **Python:** 3.8+ (Recomendado: Python 3.9, 3.10, 3.11 ou 3.12 para melhor compatibilidade com as bibliotecas científicas como scikit-learn)
  * **Docker:** 20.10+ (necessário para a execução local do SonarQube, se optar por não usar GitHub Actions)
  * **Memória RAM:** Mínimo 4GB (8GB recomendado para a execução dos LLMs).
  * **Espaço em disco:** 5GB livres.

### Recursos Adicionais

  * **Acesso à Internet:** Necessário para o download de dependências (modelos Ollama, pacotes Python, etc.).
  * **GPU:** Opcional para aceleração da inferência dos LLMs (altamente recomendado para reduzir o tempo de execução).

## Dependências

### Essenciais (para reprodução básica e cálculo de métricas)

```bash
# Bibliotecas Python
pandas==2.0.3
scikit-learn==1.3.2
numpy==1.26.4
ollama==0.5.1 
python-dotenv==1.0.1 # Para carregar variáveis de ambiente
```

### Opcionais (para análise completa via Ollama e SAST)

```bash
# Para LLMs (Ollama e seus modelos)
ollama>=0.5.1 # Versão utilizada no desenvolvimento
# Os modelos CodeLlama-7b e DeepSeek-Coder-1.3b são gerenciados pelo Ollama.

# Para SASTs (via GitHub Actions ou Docker para SonarQube)
# As ferramentas Semgrep (versão 1.49) e SonarQube (Community Build versão 25.5)
# são instaladas e gerenciadas via GitHub Actions ou localmente via Docker.
```

## Dataset Base

  * **OWASP Juice Shop v17.3.0:** O artefato utiliza um subconjunto de 15 arquivos desta aplicação web intencionalmente vulnerável.
  * **Arquivos de código-fonte:** Localizados em `dataset/code_snippets/`. Estes arquivos incluem exemplos vulneráveis e seguros, alguns dos quais foram pré-processados (remoção de comentários de desafio) para a análise dos LLMs, conforme descrito no artigo.
  * **Ground Truth:** O arquivo `dataset/juice_shop_15_files.csv` contém o mapeamento das vulnerabilidades conhecidas para cada arquivo, servindo como a "verdade" para o cálculo das métricas de desempenho.

## Preocupações com segurança

⚠️ **ATENÇÃO:** Este artefato utiliza código intencionalmente vulnerável proveniente do OWASP Juice Shop para fins de pesquisa e demonstração. Não utilize este código ou o ambiente de teste em sistemas de produção ou em redes não seguras. Recomenda-se a execução em um ambiente isolado, como uma máquina virtual.

## 🔄 Notas sobre Reprodutibilidade dos LLMs

Resultados de modelos generativos (DeepSeek/CodeLlama) **podem variar entre execuções** devido à:

- Natureza probabilística dos modelos
- Sensibilidade contextual em JavaScript
- Limitações de janela de contexto
- Variações na inicialização de pesos

Para comparativos acadêmicos, em [Reivindicação #1](#reivindicação-1-métricas-comparativas-de-desempenho---llms) execute o script `run_llm_analysis.py` **3 vezes** e utilize a mediana dos resultados.

## Instalação

Siga os passos abaixo para configurar o ambiente e as ferramentas:

### 1\. Clonagem do Repositório

```bash
git clone https://github.com/rayanepimentel/avaliacao-comparativa-sast-llm.git
cd avaliacao-comparativa-sast-llm
```

### 2\. Ambiente Python

Crie um ambiente virtual e instale as dependências Python:

```bash
python3 -m venv venv
source venv/bin/activate  # Para Linux/macOS
# ou
.\venv\Scripts\activate   # Para Windows (no PowerShell)

# Instale as dependências 
pip install -r scripts/requirements.txt
```

### 3\. Instalação do Ollama e Modelos LLM (Opcional, mas necessário para análise LLM)

Este passo instala a ferramenta Ollama e baixa os modelos CodeLlama e DeepSeek-Coder.

```bash
# Dar permissão de execução e executar o script de instalação
chmod +x scripts/setup_models.sh
./scripts/setup_models.sh
```

*Este script automatiza:*

  * A instalação do Ollama para o seu sistema operacional.
  * O download dos modelos `codellama:7b` e `deepseek-coder:1.3b` via Ollama.


## Teste Mínimo

Execute o script de cálculo de métricas para verificar a funcionalidade básica do ambiente e a geração de resultados com o dataset original (juice_shop_15_files.csv). Este teste validará a correta instalação das dependências Python e a execução do calculate_metrics.py.

```bash
python scripts/calculate_metrics.py dataset/juice_shop_15_files.csv
```

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


### Reivindicação \#1: Análise de Desempenho de LLMs com Validação de Categoria

**Objetivo**: Reproduzir as métricas de precisão, recall, F1-score e taxa de falsos positivos **especificamente para DeepSeek e CodeLlama**, aplicando uma validação rigorosa da categoria da vulnerabilidade identificada.

**Processo**:
Este processo é dividido em duas etapas e deve ser executado na sequência:

1.  **Execução da Análise Bruta de LLMs (`run_llm_analysis.py`):** O script `run_llm_analysis.py` interage com os modelos Ollama, analisa cada trecho de código do dataset e consolida as respostas das detecções dos LLMs em um novo arquivo CSV na pasta `results/`.

    ```bash
    python scripts/run_llm_analysis.py
    ```

      * **Tempo esperado:** Aproximadamente 30-45 minutos (em CPU com 8GB RAM). Pode ser significativamente mais rápido com GPU.
      * **Recursos esperados:** Uso intensivo de CPU e RAM durante a inferência dos LLMs.
      * **Saída:** Um arquivo `results/llm_detections_results.csv` será gerado, contendo os IDs dos arquivos, caminhos, detecções binárias iniciais (0 ou 1, baseadas na *presença de qualquer vulnerabilidade*), tempos de execução e as respostas brutas dos LLMs (textos ou JSONs). Logs de execução e progresso serão exibidos no terminal.

    **Alternativa Manual (se `run_llm_analysis.py` falhar):**
    Caso a execução automatizada do `run_llm_analysis.py` encontre problemas operacionais dentro do contêiner, é possível realizar a análise dos LLMs manualmente, interagindo diretamente com o Ollama CLI. Este processo deve ser repetido para cada um dos 15 arquivos de código-fonte no diretório `/dataset/code_snippets/` e para cada modelo LLM (DeepSeek-Coder:1.3b e CodeLlama:7b).

    **Passos para Análise Manual:**
    a.  **Inicie o Ollama com o modelo desejado no terminal:**

    ```bash 
    ollama run deepseek-coder:1.3b # Ou ollama run codellama:7b 
    ```

    Você verá o prompt `>>> Send a message (/? for help)`.

    b.  **Construa o Prompt:** Copie o template de prompt abaixo e cole no terminal do Ollama.
    \`\`\`text
    Analise os riscos de segurança no código abaixo, seguindo o OWASP Top 10. Retorne APENAS se houver vulnerabilidades, no formato JSON abaixo. Caso contrário, retorne "Código seguro".

    ````
    {
      "Arquivo": "Nome do arquivo",
      "Trecho Vulnerável": "O snippet de código específico que contém a vulnerabilidade.",
      "Tipo da Vulnerabilidade": "A categoria da vulnerabilidade",
      "Descrição Breve": "Uma explicação concisa (1-2 frases) de por que esse trecho é vulnerável"
    }

    Code:
    ```typescript
    # COLE AQUI O CONTEÚDO DO ARQUIVO DE CÓDIGO
    ```
    ```
    ````

    c.  **Obtenha o Conteúdo do Código:** Vá para o diretório `/dataset/code_snippets/` dentro do contêiner, abra um dos 15 arquivos (ex: `VULN-01.ts` ou `SAFE-01.ts`), copie todo o conteúdo e cole-o no prompt do Ollama, substituindo `# COLE AQUI O CONTEÚDO DO ARQUIVO DE CÓDIGO`.

    d.  **Envie e Colete a Resposta:** Pressione `Enter` para enviar o prompt ao LLM. Copie a resposta completa gerada pelo Ollama.

    e.  **Registre a Detecção e a Categoria Identificada:**
    - Se a resposta do LLM for `Código seguro`, registre a detecção como **0** (não vulnerável) e a categoria como `N/A`.
    - Se a resposta for um JSON com detalhes da vulnerabilidade, registre a detecção como **1** (vulnerável) e extraia a **"Tipo da Vulnerabilidade"** (`Vulnerability Category`) do JSON – Verifique se o tipo de vulnerabilidade identificada foi a categoria correta. Se o LLM descrever a vulnerabilidade em texto livre (sem JSON), tente identificar a categoria principal mencionada no texto.
    - Mantenha um registro em uma planilha ou similar (por exemplo, `llm_detections_manual.csv`) dos IDs dos arquivos, as detecções (0 ou 1), e a **categoria da vulnerabilidade identificada pelo LLM**. Isso é crucial para a próxima etapa.

    f.  **Repita:** Repita os passos de `a` a `e` para todos os 15 arquivos do dataset e para ambos os modelos LLM (DeepSeek-Coder:1.3b e CodeLlama:7b).

    g.  **Crie o `llm_detections_results.csv` manual:** 
    Após coletar todas as detecções e categorias, crie manualmente um arquivo `/results/llm_detections_results.csv` com as colunas `ID`, `File`, `Vulnerability`, `Detected_Deepseek` (0 ou 1), `DeepSeek_Raw_Result`, `DeepSeek_Time`, `CodeLlama_Detected` (0 ou 1), `CodeLlama_Raw_Result`, `CodeLlama_Time`, **`DeepSeek_Identified_Category`** (NOVA COLUNA), e **`CodeLlama_Identified_Category`** (NOVA COLUNA). As colunas `*_Raw_Result` conterão a resposta bruta do LLM e `*_Time` pode ser 0.0, a menos que você as cronometre manualmente.

2.  **Cálculo das Métricas de LLMs com Validação de Categoria (`llm_category_metrics.py`):**
    Uma vez que o arquivo `results/llm_detections_results.csv` (seja gerado automaticamente ou criado manualmente) esteja disponível, execute o novo script `llm_category_metrics.py`. Este script:

      * Lerá o `results/llm_detections_results.csv` (com as detecções e categorias identificadas pelos LLMs).
      * Aplicará a lógica de validação de categoria para contar VP/FP/FN.
      * Gerará uma tabela de métricas **APENAS para DeepSeek e CodeLlama**.

    <!-- end list -->

    ```bash
    python scripts/llm_category_metrics.py
    ```

      * **Tempo esperado:** Menos de 10 segundos.
      * **Recursos esperados:** Baixo consumo de CPU/RAM.
      * **Saída:** As métricas de desempenho de DeepSeek e CodeLlama (com validação de categoria) serão impressas no terminal e salvas nos arquivos `/results/llm_category_metrics.csv` e `/results/llm_category_metrics.html`.



### Reivindicação \#2: Execução SAST completa via GitHub Actions

Este processo demonstra como as análises SAST foram integradas e executadas no ambiente de CI/CD (GitHub Actions) sobre o repositório completo do OWASP Juice Shop.

1.  **Faça um fork do repositório oficial do OWASP Juice Shop**:

      * Acesse `https://github.com/juice-shop/juice-shop`
      * Clique em "Fork" no canto superior direito para criar uma cópia em sua conta.

2.  **Adicione os workflows SAST ao seu fork**:

      * No seu **fork** do repositório `juice-shop`, navegue até o diretório `.github/workflows`.
      * Se não existir, crie esta pasta.
      * Copie o conteúdo dos arquivos `semgrep.yml` e `sonarqube.yml` deste projeto (localizados em `.github/workflows/`) para a pasta `.github/workflows/` no seu fork.

3.  **Configure os Secrets do GitHub (APENAS PARA SONARQUBE)**:

      * Para o workflow do SonarQube funcionar, você precisa configurar os segredos no seu fork do GitHub.
      * No seu fork, vá em **Settings \> Secrets \> Actions \> New repository secret**.
      * Adicione dois segredos:
          * `SONAR_TOKEN`: Um token de autenticação gerado na sua instância SonarQube (ou SonarCloud).
          * `SONAR_HOST_URL`: A URL da sua instância SonarQube (ex: `https://sonarcloud.io` ou `http://localhost:9000`).
      * Se encontrar problemas, consulte a [documentação de integração do SonarQube com GitHub Actions](https://docs.sonarqube.org/latest/analysis/github-integration/).

4.  **Execute os workflows**:

      * No seu fork do `juice-shop` no GitHub, vá para a aba **Actions**.
      * No painel lateral esquerdo, selecione os workflows:
          * **Semgrep PR** (nome definido no `semgrep.yml`): Clique em "Run workflow" e selecione o branch principal (ou o branch que você adicionou os arquivos `.yml`).
          * **Sonar** (nome definido no `sonarqube.yml`): Clique em "Run workflow" e selecione o branch principal (ou o branch que você adicionou os arquivos `.yml`).

5.  **Obtenha os resultados**:

      * **Semgrep**: Após a execução bem-sucedida do workflow "Semgrep PR", um novo Pull Request será criado automaticamente em seu fork com o relatório de segurança do Semgrep. Acesse o PR para visualizar o relatório detalhado em Markdown.
      * **SonarQube**: Após a execução bem-sucedida do workflow "Sonar", os resultados da análise serão enviados para a instância SonarQube configurada. Acesse a interface web da sua instância SonarQube (ex: `https://sonarcloud.io` ou sua URL local) e navegue até o projeto correspondente ao seu fork do Juice Shop para visualizar os alertas de segurança.
      *  Verifique se o tipo de vulnerabilidade identificada foi a categoria correta.

> **Notas importantes**:
>
>   * O tempo de execução varia: o Semgrep geralmente leva 2-5 minutos, enquanto o SonarQube pode levar de 5-15 minutos para concluir a análise e enviar os resultados.
>   * A execução em GitHub Actions utiliza recursos do próprio GitHub; não há consumo de recursos locais para o avaliador.


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

