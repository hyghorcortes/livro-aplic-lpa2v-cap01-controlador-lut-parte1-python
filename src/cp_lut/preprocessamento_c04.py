from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np


# LUT padrão preservada da conversão anterior do C04.
# Observação: o livro descreve o Para-Analisador como base para estados lógicos
# em função de Gc e Gct. Nesta implementação Python do exemplo 1, foi mantida
# a tabela prática usada no código C04 convertido, com 14 entradas.
TABELA_KE_PADRAO = np.array(
    [
        0.05,  # 1  Verdadeiro
        0.55,  # 2  Quase verdadeiro -> inconsistente
        0.55,  # 3  Quase verdadeiro -> indeterminado
        0.95,  # 4  Inconsistente -> verdadeiro
        0.95,  # 5  Indeterminado -> verdadeiro
        1.05,  # 6  Inconsistente -> falso
        1.05,  # 7  Indeterminado -> falso
        1.45,  # 8  Quase falso -> inconsistente
        1.45,  # 9  Quase falso -> indeterminado
        1.95,  # 10 Falso
        0.95,  # 11 Inconsistente +
        1.05,  # 12 Inconsistente -
        0.95,  # 13 Indeterminado +
        1.05,  # 14 Indeterminado -
    ],
    dtype=float,
)


def saturar(x: float, xmin: float = 0.0, xmax: float = 1.0) -> float:
    """Satura um valor no intervalo [xmin, xmax]."""
    return float(np.clip(x, xmin, xmax))


def _validar_escalar(nome: str, valor: float) -> float:
    if isinstance(valor, (list, tuple, np.ndarray)):
        raise ValueError(f"{nome} deve ser um escalar numérico finito.")
    try:
        valor = float(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{nome} deve ser um escalar numérico finito.") from exc
    if not np.isfinite(valor):
        raise ValueError(f"{nome} deve ser um escalar numérico finito.")
    return valor


def classifica_estado_14(
    gc: float,
    gct: float,
    c1: float = 0.5,
    c2: float = -0.5,
    c3: float = 0.5,
    c4: float = -0.5,
) -> Tuple[int, str]:
    """Classifica o ponto (Gc, Gct) em um dos 14 estados lógicos."""

    if gc >= c1:
        return 1, "Verdadeiro"

    if gc <= c2:
        return 10, "Falso"

    if gct >= c3:
        if gc >= 0:
            return 11, "Inconsistente +"
        return 12, "Inconsistente -"

    if gct <= c4:
        if gc >= 0:
            return 13, "Indeterminado +"
        return 14, "Indeterminado -"

    if (gc >= 0) and (gc < c1) and (gct >= 0) and (gct < c3):
        if gc >= gct:
            return 2, "Quase verdadeiro tendendo a inconsistente"
        return 4, "Inconsistente tendendo a verdadeiro"

    if (gc >= 0) and (gc < c1) and (gct > c4) and (gct < 0):
        if gc >= abs(gct):
            return 3, "Quase verdadeiro tendendo a indeterminado"
        return 5, "Indeterminado tendendo a verdadeiro"

    if (gc > c2) and (gc < 0) and (gct > c4) and (gct < 0):
        if abs(gc) >= abs(gct):
            return 9, "Quase falso tendendo a indeterminado"
        return 7, "Indeterminado tendendo a falso"

    if (gc > c2) and (gc < 0) and (gct >= 0) and (gct < c3):
        if abs(gc) >= gct:
            return 8, "Quase falso tendendo a inconsistente"
        return 6, "Inconsistente tendendo a falso"

    if gc >= 0:
        if gct >= 0:
            return 4, "Inconsistente tendendo a verdadeiro"
        return 5, "Indeterminado tendendo a verdadeiro"

    if gct >= 0:
        return 6, "Inconsistente tendendo a falso"
    return 7, "Indeterminado tendendo a falso"


def pre_processa_erro_c04(
    r: float,
    y: float,
    e: Optional[float] = None,
    tabela_ke: Optional[np.ndarray] = None,
    modo_limite: str = "saturar",
) -> Tuple[float, Dict[str, float | int | str]]:
    """
    Pré-processa o erro do controlador CP-LUT usando o bloco C04.

    Regra principal:
        e' = k_e(estado) * e

    Em que:
        - mu1 = sat(y / escala)
        - lambda2 = sat(r / escala)
        - Gc = mu1 - lambda2
        - Gct = mu1 + lambda2 - 1
        - estado = classifica_estado_14(Gc, Gct)
        - k_e = LUT(estado)

    Retorna:
        - e_pp: erro pré-processado
        - info: dicionário com sinais intermediários
    """

    r = _validar_escalar("r", r)
    y = _validar_escalar("y", y)
    if e is None:
        e = r - y
    e = _validar_escalar("e", e)

    if tabela_ke is None:
        tabela_ke = TABELA_KE_PADRAO.copy()
    else:
        tabela_ke = np.asarray(tabela_ke, dtype=float).reshape(-1)
        if tabela_ke.size == 0:
            raise ValueError("tabela_ke deve ser um vetor numérico não vazio.")

    escala = max(1.0, abs(r), abs(y))

    mu1 = saturar(y / escala, 0.0, 1.0)
    lambda2 = saturar(r / escala, 0.0, 1.0)

    gc = mu1 - lambda2
    gct = mu1 + lambda2 - 1.0

    estado_id, estado_nome = classifica_estado_14(gc, gct, 0.5, -0.5, 0.5, -0.5)

    idx = int(round(estado_id))
    n = int(tabela_ke.size)

    modo_limite_norm = modo_limite.lower().strip()
    if modo_limite_norm == "saturar":
        idx = max(1, min(n, idx))
    elif modo_limite_norm == "erro":
        if idx < 1 or idx > n:
            raise ValueError(f"estado_id = {estado_id} fora da faixa válida 1..{n}.")
    else:
        raise ValueError("modo_limite deve ser 'saturar' ou 'erro'.")

    k_e = float(tabela_ke[idx - 1])
    e_pp = float(k_e * e)

    info: Dict[str, float | int | str] = {
        "mu1": float(mu1),
        "lambda2": float(lambda2),
        "Gc": float(gc),
        "Gct": float(gct),
        "estado_id": int(estado_id),
        "estado_nome": estado_nome,
        "idx_lut": int(idx),
        "k_e": float(k_e),
        "e_original": float(e),
        "e_pp": float(e_pp),
        "escala": float(escala),
    }
    return e_pp, info
