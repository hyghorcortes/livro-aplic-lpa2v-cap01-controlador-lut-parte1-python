from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import csv
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

from .preprocessamento_c04 import TABELA_KE_PADRAO, pre_processa_erro_c04


@dataclass
class ConfigC04:
    tf: float = 100.0
    dt: float = 0.01
    t_step: float = 10.0

    kp: float = 1.0
    ki: float = 1.0
    kd: float = 0.0
    n: float = 100.0

    tabela_ke: np.ndarray = field(default_factory=lambda: TABELA_KE_PADRAO.copy())
    modo_limite: str = "saturar"


def referencia_degrau(t: float, t_step: float) -> float:
    return 0.0 if t < t_step else 1.0


def termo_derivativo_filtrado(e_pp: float, x_f: float, kd: float, n: float) -> float:
    return kd * n * (e_pp - x_f)


def malha_fechada_ode(t: float, x: np.ndarray, cfg: ConfigC04) -> np.ndarray:
    x_i, y, x_f = x

    r = referencia_degrau(t, cfg.t_step)
    e = r - y
    e_pp, _ = pre_processa_erro_c04(r, y, e, cfg.tabela_ke, cfg.modo_limite)

    x_i_dot = e_pp
    x_f_dot = cfg.n * (e_pp - x_f)
    d_term = termo_derivativo_filtrado(e_pp, x_f, cfg.kd, cfg.n)
    u = cfg.kp * e_pp + cfg.ki * x_i + d_term
    y_dot = -y + u

    return np.array([x_i_dot, y_dot, x_f_dot], dtype=float)


def simula_pid_c04_malha_fechada(cfg: Optional[ConfigC04] = None) -> Dict[str, Any]:
    if cfg is None:
        cfg = ConfigC04()

    x0 = np.array([0.0, 0.0, 0.0], dtype=float)
    t_eval = np.arange(0.0, cfg.tf + cfg.dt, cfg.dt)

    sol = solve_ivp(
        fun=lambda t, x: malha_fechada_ode(t, x, cfg),
        t_span=(0.0, cfg.tf),
        y0=x0,
        t_eval=t_eval,
        rtol=1e-8,
        atol=1e-10,
        method="RK45",
    )

    if not sol.success:
        raise RuntimeError(f"Falha na integração numérica: {sol.message}")

    t = sol.t
    x_i = sol.y[0, :]
    y = sol.y[1, :]
    x_f = sol.y[2, :]

    npts = t.size
    r = np.zeros(npts)
    e = np.zeros(npts)
    e_pp = np.zeros(npts)
    u = np.zeros(npts)
    k_e = np.zeros(npts)
    estado_id = np.zeros(npts, dtype=int)
    idx_lut = np.zeros(npts, dtype=int)
    gc = np.zeros(npts)
    gct = np.zeros(npts)
    mu1 = np.zeros(npts)
    lambda2 = np.zeros(npts)
    d_term = np.zeros(npts)
    estado_nome: List[str] = [""] * npts

    for k in range(npts):
        r[k] = referencia_degrau(t[k], cfg.t_step)
        e[k] = r[k] - y[k]

        e_pp[k], info = pre_processa_erro_c04(r[k], y[k], e[k], cfg.tabela_ke, cfg.modo_limite)

        k_e[k] = float(info["k_e"])
        estado_id[k] = int(info["estado_id"])
        estado_nome[k] = str(info["estado_nome"])
        idx_lut[k] = int(info["idx_lut"])
        gc[k] = float(info["Gc"])
        gct[k] = float(info["Gct"])
        mu1[k] = float(info["mu1"])
        lambda2[k] = float(info["lambda2"])

        d_term[k] = termo_derivativo_filtrado(e_pp[k], x_f[k], cfg.kd, cfg.n)
        u[k] = cfg.kp * e_pp[k] + cfg.ki * x_i[k] + d_term[k]

    idx_step = np.where(t >= cfg.t_step)[0][0]
    y_pos = y[idx_step:]
    t_pos = t[idx_step:]

    valor_final = float(y[-1])
    ymax = float(np.max(y_pos))
    overshoot_pct = max(0.0, (ymax - 1.0)) * 100.0

    faixa = 0.02
    tempo_acomodacao = np.nan
    for k in range(y_pos.size):
        if np.all(np.abs(y_pos[k:] - 1.0) <= faixa):
            tempo_acomodacao = float(t_pos[k] - cfg.t_step)
            break

    return {
        "t": t,
        "r": r,
        "y": y,
        "u": u,
        "e": e,
        "e_pp": e_pp,
        "k_e": k_e,
        "estado_id": estado_id,
        "estado_nome": estado_nome,
        "idx_lut": idx_lut,
        "Gc": gc,
        "Gct": gct,
        "mu1": mu1,
        "lambda2": lambda2,
        "xI": x_i,
        "xF": x_f,
        "d_term": d_term,
        "cfg": asdict(cfg),
        "metricas": {
            "valor_final": valor_final,
            "overshoot_pct": overshoot_pct,
            "tempo_acomodacao_2pct": tempo_acomodacao,
        },
    }


def plotar_resultados(
    resultados: Dict[str, Any],
    salvar_em: Optional[str | Path] = None,
    mostrar: bool = False,
) -> None:
    t = resultados["t"]
    r = resultados["r"]
    y = resultados["y"]
    u = resultados["u"]
    e = resultados["e"]
    e_pp = resultados["e_pp"]
    estado_id = resultados["estado_id"]
    k_e = resultados["k_e"]
    gc = resultados["Gc"]
    gct = resultados["Gct"]

    fig, axes = plt.subplots(5, 1, figsize=(12, 14), sharex=True, constrained_layout=True)

    axes[0].plot(t, r, "k--", linewidth=1.3, label="r(t)")
    axes[0].plot(t, y, linewidth=1.5, label="y(t)")
    axes[0].grid(True)
    axes[0].set_ylabel("Saída")
    axes[0].set_title("Referência e saída da planta")
    axes[0].legend(loc="best")

    axes[1].plot(t, u, linewidth=1.3)
    axes[1].grid(True)
    axes[1].set_ylabel("u(t)")
    axes[1].set_title("Sinal de controle")

    axes[2].plot(t, e, linewidth=1.2, label="e(t)")
    axes[2].plot(t, e_pp, linewidth=1.2, label="e'(t)")
    axes[2].grid(True)
    axes[2].set_ylabel("Erro")
    axes[2].set_title("Erro original e erro pré-processado")
    axes[2].legend(loc="best")

    ax4 = axes[3]
    ax4.step(t, estado_id, where="post", linewidth=1.1)
    ax4.set_ylabel("Estado (1..14)")
    ax4.set_ylim(0.5, 14.5)
    ax4.set_yticks(np.arange(1, 15))
    ax4.grid(True)
    ax4.set_title("Estado lógico e ganho da LUT")

    ax4b = ax4.twinx()
    ax4b.plot(t, k_e, linewidth=1.2)
    ax4b.set_ylabel("k_e")

    axes[4].plot(t, gc, linewidth=1.2, label="Gc")
    axes[4].plot(t, gct, linewidth=1.2, label="Gct")
    axes[4].grid(True)
    axes[4].set_xlabel("Tempo (s)")
    axes[4].set_ylabel("Valor")
    axes[4].set_title("Gc e Gct")
    axes[4].legend(loc="best")

    if salvar_em is not None:
        salvar_em = Path(salvar_em)
        salvar_em.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(salvar_em, dpi=200, bbox_inches="tight")

    if mostrar:
        plt.show()
    else:
        plt.close(fig)


def salvar_resultados_csv(resultados: Dict[str, Any], caminho_csv: str | Path) -> None:
    caminho_csv = Path(caminho_csv)
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)

    chaves_series = [
        "t", "r", "y", "u", "e", "e_pp", "k_e", "estado_id",
        "idx_lut", "Gc", "Gct", "mu1", "lambda2", "xI", "xF", "d_term"
    ]
    n = len(resultados["t"])

    with caminho_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(chaves_series + ["estado_nome"])
        for i in range(n):
            row = [resultados[chave][i] for chave in chaves_series]
            row.append(resultados["estado_nome"][i])
            writer.writerow(row)
