# livro-aplic-lpa2v-cap01-controlador-lut-parte1-python

Implementação em Python do **Exemplo 1 do Capítulo 1**, vinculada ao livro **Aplicações de LPA2v**.

Este repositório reúne a versão organizada do exemplo do **Controlador Paraconsistente Baseado em LUT (CP-LUT)**, mantendo a ideia central do capítulo: calcular o erro de rastreamento, aplicar o pré-processamento lógico C04, obter `Gc` e `Gct`, classificar o estado lógico, consultar a LUT e então ajustar o erro antes do controlador PI/PID.

---

## Visão geral

O projeto foi organizado como um repositório individual dentro da coleção de exemplos do livro, seguindo a convenção:

```text
livro-aplic-lpa2v-capXX-nome-do-exemplo-parteY-tecnologia
```

Nome deste repositório:

```text
livro-aplic-lpa2v-cap01-controlador-lut-parte1-python
```

---

## Objetivo do exemplo

Este exemplo mostra, em ambiente Python, uma versão reproduzível do **CP-LUT**, destacando:

- cálculo do erro `e(t) = r(t) - y(t)`;
- normalização dos sinais para a camada LPA2v;
- obtenção de `mu`, `lambda`, `Gc` e `Gct`;
- classificação do estado lógico;
- consulta da tabela LUT para obter `k_e`;
- formação do erro ajustado `e'(t) = k_e * e(t)`;
- ação do controlador PI/PID;
- resposta da planta de primeira ordem `G(s)=1/(s+1)`;
- geração de gráficos e exportação de CSV.

---

## Observação importante sobre os estados

O texto do capítulo apresenta o Para-Analisador como base conceitual da classificação por `Gc` e `Gct`. Nesta implementação Python, foi preservada a **LUT prática de 14 estados** da versão convertida do código C04, incluindo variantes como **Inconsistente + / -** e **Indeterminado + / -**. O núcleo lógico continua sendo o mesmo: a decisão depende da posição do ponto no plano definido por `Gc` e `Gct`.

---

## Diagrama do fluxo do exemplo

O Mermaid abaixo foi escrito para acompanhar o fluxo do exemplo do livro em versão Python.

```mermaid
flowchart TB

    A[Início] --> B[Definir parâmetros<br/>da simulação]
    B --> C[Gerar referência<br/>r(t)]
    C --> D[Calcular erro<br/>e(t) = r(t) - y(t)]

    D --> E[Pré-processamento C04]
    E --> F[Normalizar sinais e obter<br/>mu e lambda]
    F --> G[Calcular<br/>Gc = mu - lambda]
    G --> H[Calcular<br/>Gct = mu + lambda - 1]
    H --> I[Classificar estado lógico<br/>a partir de Gc e Gct]
    I --> J[Consultar LUT<br/>k_e = LUT(estado)]
    J --> K[Formar erro ajustado<br/>e'(t) = k_e * e(t)]

    K --> L[Controlador PI/PID]
    L --> M[Sinal de controle<br/>u(t)]
    M --> N[Planta<br/>G(s) = 1 / (s + 1)]
    N --> O[Saída<br/>y(t)]
    O --> D

    O --> P[Salvar gráficos,<br/>CSV e métricas]
```

---

## Como interpretar o diagrama

### 1. Erro de rastreamento

O sistema calcula a diferença entre a referência e a saída da planta.

### 2. Pré-processamento lógico

O bloco C04 converte a condição do sistema em uma representação compatível com a LPA2v.

### 3. Indicadores lógicos

A partir de `mu` e `lambda`, o código obtém:

- `Gc = mu - lambda`
- `Gct = mu + lambda - 1`

### 4. Estado lógico e LUT

O par `(Gc, Gct)` é classificado em um estado discreto. Em seguida, a LUT associa esse estado a um ganho `k_e`.

### 5. Erro ajustado e controle

O erro original é multiplicado por `k_e`, gerando `e'`. Esse sinal é enviado ao PI/PID.

### 6. Planta e realimentação

O sinal de controle atua sobre a planta `G(s)=1/(s+1)` e a saída retorna à malha.

### 7. Saídas do repositório

O projeto pode gerar:

- figura com a resposta temporal;
- CSV com sinais intermediários;
- métricas como valor final, overshoot e tempo de acomodação.

---

## Estrutura do repositório

```text
.
├── assets/
│   └── previews/
│       └── cp_lut_resposta.png
├── docs/
│   ├── book-context.md
│   ├── project-overview.md
│   └── repository-structure.md
├── scripts/
│   ├── pre_processa_erro_c04.py
│   └── simula_pid_c04_malha_fechada.py
├── src/
│   └── cp_lut/
│       ├── __init__.py
│       ├── preprocessamento_c04.py
│       └── simulacao_c04.py
├── tests/
│   └── test_smoke.py
├── .gitignore
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── COMO_SUBSTITUIR.md
├── CONTRIBUTING.md
├── IMPORTAR_NO_GITHUB.md
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
└── SECURITY.md
```

---

## Como executar

### Instalação local

```bash
pip install -r requirements.txt
pip install -e .
```

### Rodando o script principal

```bash
python scripts/simula_pid_c04_malha_fechada.py --save-dir results
```

### Rodando com exibição de figura

```bash
python scripts/simula_pid_c04_malha_fechada.py --show --save-dir results
```

---

## Arquivos principais

### Pacote principal

```text
src/cp_lut/
```

### Script de pré-processamento

```text
scripts/pre_processa_erro_c04.py
```

### Script de simulação

```text
scripts/simula_pid_c04_malha_fechada.py
```

---

## Saídas esperadas

Ao executar a simulação, o repositório gera:

- `results/cp_lut_resposta.png`
- `results/cp_lut_resultados.csv`

A pasta `assets/previews/` já inclui uma figura de preview pronta para o GitHub.

---

## Relação com o livro

Este repositório corresponde ao **Exemplo 1 do Capítulo 1** e foi organizado para funcionar como material complementar do texto do livro.

---

## Licença

Consulte o arquivo `LICENSE`.

---

## Citação

Consulte o arquivo `CITATION.cff`.
