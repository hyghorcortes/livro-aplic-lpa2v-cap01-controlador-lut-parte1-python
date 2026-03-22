from __future__ import annotations

from cp_lut import pre_processa_erro_c04


if __name__ == "__main__":
    e_pp, info = pre_processa_erro_c04(r=1.0, y=0.3)
    print(f"e_pp = {e_pp:.6f}")
    for chave, valor in info.items():
        print(f"{chave}: {valor}")
