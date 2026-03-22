from cp_lut import ConfigC04, pre_processa_erro_c04, simula_pid_c04_malha_fechada


def test_preprocessamento_retorna_info():
    e_pp, info = pre_processa_erro_c04(r=1.0, y=0.3)
    assert isinstance(e_pp, float)
    assert "Gc" in info
    assert "Gct" in info
    assert "estado_id" in info


def test_simulacao_smoke():
    cfg = ConfigC04(tf=2.0, dt=0.05, t_step=0.5)
    resultados = simula_pid_c04_malha_fechada(cfg)
    assert len(resultados["t"]) > 0
    assert "metricas" in resultados
