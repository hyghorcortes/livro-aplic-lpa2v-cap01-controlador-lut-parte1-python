# Visão geral do projeto

Este repositório representa o **Exemplo 1 do Capítulo 1** do livro, dedicado ao **CP-LUT**.

## Núcleo lógico do exemplo

O fluxo implementado é:

1. calcular o erro de rastreamento `e = r - y`;
2. aplicar o pré-processamento C04;
3. normalizar sinais para obter `mu` e `lambda`;
4. calcular `Gc` e `Gct`;
5. classificar o estado lógico;
6. consultar a LUT para obter `k_e`;
7. formar o erro ajustado `e' = k_e * e`;
8. enviar `e'` ao PI/PID;
9. aplicar o sinal de controle à planta `G(s)=1/(s+1)`.

## Arquivos mais importantes

- `src/cp_lut/preprocessamento_c04.py`
- `src/cp_lut/simulacao_c04.py`
- `scripts/simula_pid_c04_malha_fechada.py`
- `assets/previews/cp_lut_resposta.png`
