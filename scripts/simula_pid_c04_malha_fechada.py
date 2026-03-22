from __future__ import annotations

import argparse
from pathlib import Path

from cp_lut import ConfigC04, plotar_resultados, salvar_resultados_csv, simula_pid_c04_malha_fechada


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa a simulação do exemplo CP-LUT.")
    parser.add_argument("--tf", type=float, default=100.0, help="Tempo final da simulação.")
    parser.add_argument("--dt", type=float, default=0.01, help="Passo de amostragem usado para saída.")
    parser.add_argument("--t-step", type=float, default=10.0, help="Instante do degrau de referência.")
    parser.add_argument("--show", action="store_true", help="Mostra a figura em janela interativa.")
    parser.add_argument("--save-dir", type=str, default="results", help="Diretório para PNG e CSV.")
    args = parser.parse_args()

    cfg = ConfigC04(tf=args.tf, dt=args.dt, t_step=args.t_step)
    resultados = simula_pid_c04_malha_fechada(cfg)

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    png_path = save_dir / "cp_lut_resposta.png"
    csv_path = save_dir / "cp_lut_resultados.csv"

    plotar_resultados(resultados, salvar_em=png_path, mostrar=args.show)
    salvar_resultados_csv(resultados, csv_path)

    metricas = resultados["metricas"]
    print("\n=== SIMULAÇÃO C04: PID + LUT DO ESTADO LÓGICO ===")
    print("Planta: G(s) = 1/(s+1)")
    print(f"Tempo total: {cfg.tf:.2f} s")
    print(f"Degrau unitário em: {cfg.t_step:.2f} s")
    print(f"Valor final y(Tf): {metricas['valor_final']:.6f}")
    print(f"Overshoot: {metricas['overshoot_pct']:.4f} %")
    print(f"Tempo de acomodação (2%): {metricas['tempo_acomodacao_2pct']}")
    print(f"PNG salvo em: {png_path}")
    print(f"CSV salvo em: {csv_path}")


if __name__ == "__main__":
    main()
