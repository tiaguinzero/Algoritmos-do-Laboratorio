"""
utils_rc.py -- Funções auxiliares comuns às análises do Experimento IV (Circuitos RC).

Contém:
  * leitura dos arquivos CSV gravados pelo osciloscópio Tektronix TBS 1062;
  * incerteza-padrão de cada leitura de tensão do osciloscópio (leitura + calibração);
  * ajuste não linear (Levenberg-Marquardt) do modelo V(t) = V_inf + dV * exp(-t/tau);
  * ajuste linear ponderado (MMQ) da forma linearizada ln(V - V_inf) = ln(dV) - t/tau;
  * formatação de resultados com o número correto de algarismos significativos.

Apenas numpy e matplotlib são necessários (não depende de scipy/pandas).
"""
import csv
from pathlib import Path

import numpy as np

PASTA_EXP4 = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_EXP4 / 'dados'
PASTA_GRAFICOS = PASTA_EXP4 / 'graficos'

# Resistor (código de cores marrom-preto-vermelho-dourado) e resistência de saída do gerador
R_NOM = 1000.0                      # Ohm
U_R = 0.05 * R_NOM / np.sqrt(3)     # tolerância de 5 %, distribuição retangular
R_GER = 50.0                        # Ohm, resistência de saída do gerador BK 4052 (manual)
R_EQ = R_NOM + R_GER                # resistência total na malha de carga/descarga
U_REQ = U_R                         # incerteza da resistência equivalente

# Osciloscópio: conversor A/D de 8 bits -> 25 níveis por divisão
NIVEIS_POR_DIV = 25.0


def ler_csv_tek(caminho):
    """Lê o CSV do TBS 1062 (colunas 4 e 5 = tempo, tensão) e retorna arrays numpy."""
    t, v = [], []
    with open(caminho, 'r') as f:
        for linha in csv.reader(f):
            if len(linha) >= 5:
                try:
                    t.append(float(linha[3]))
                    v.append(float(linha[4]))
                except ValueError:
                    pass
    return np.array(t), np.array(v)


def incerteza_tensao(v, escala_v):
    """Incerteza-padrão combinada de uma leitura de tensão do osciloscópio.

    Leitura: resolução = escala/25 (8 bits), distribuição retangular -> d / (2*sqrt(3)).
    Calibração: (3 % |leitura| + 10 % da escala + 1 mV), distribuição retangular -> / sqrt(3).
    """
    d = escala_v / NIVEIS_POR_DIV
    u_leit = d / (2 * np.sqrt(3))
    u_cal = (0.03 * np.abs(v) + 0.10 * escala_v + 0.001) / np.sqrt(3)
    return np.sqrt(u_leit**2 + u_cal**2)


# ---------------------------------------------------------------- modelo exponencial
def modelo_exp(t, p):
    v_inf, dv, tau = p
    return v_inf + dv * np.exp(-t / tau)


def _jacobiano(t, p):
    v_inf, dv, tau = p
    e = np.exp(-t / tau)
    return np.column_stack([np.ones_like(t), e, dv * t * e / tau**2])


def ajuste_exponencial(t, v, u_v, p0, max_iter=500):
    """Ajuste não linear de V(t) = V_inf + dV exp(-t/tau) por Levenberg-Marquardt.

    Retorna (parâmetros, matriz de covariância, chi2). A covariância é calculada
    com as incertezas absolutas u_v (sem reescalonar pelo chi2 reduzido).
    """
    p = np.array(p0, dtype=float)
    lam = 1e-3

    def chi2(q):
        return np.sum(((v - modelo_exp(t, q)) / u_v) ** 2)

    c = chi2(p)
    for _ in range(max_iter):
        J = _jacobiano(t, p) / u_v[:, None]
        r = (v - modelo_exp(t, p)) / u_v
        A = J.T @ J
        g = J.T @ r
        dp = np.linalg.solve(A + lam * np.diag(np.diag(A)), g)
        c_novo = chi2(p + dp)
        if c_novo < c:
            p = p + dp
            lam /= 10
            convergiu = abs(c - c_novo) < 1e-12 * c
            c = c_novo
            if convergiu:
                break
        else:
            lam *= 10
    J = _jacobiano(t, p) / u_v[:, None]
    cov = np.linalg.inv(J.T @ J)
    return p, cov, c


def ajuste_linear(x, y, u_y):
    """MMQ ponderado y = A x + B (pesos 1/u_y^2). Retorna A, B, u_A, u_B, cov, chi2."""
    coef, cov = np.polyfit(x, y, 1, w=1 / u_y, cov='unscaled')
    A, B = coef
    chi2 = np.sum(((y - (A * x + B)) / u_y) ** 2)
    return A, B, np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1]), cov, chi2


def linearizar(t, v, u_v, v_inf, limiar):
    """Transforma (t, V) em (t, ln(V - V_inf)) mantendo só os pontos com V - V_inf >= limiar.

    Propagação: y = ln(V - V_inf)  ->  u_y = |dy/dV| u_V = u_V / (V - V_inf).
    """
    dif = v - v_inf
    m = dif >= limiar
    y = np.log(dif[m])
    u_y = u_v[m] / dif[m]
    return t[m], y, u_y, m


def tau_do_linear(A, u_A):
    """tau = -1/A  ->  u_tau = |dtau/dA| u_A = u_A / A^2."""
    return -1.0 / A, u_A / A**2


def capacitancia(tau, u_tau, r=R_EQ, u_r=U_REQ):
    """C = tau / R, com propagação por derivadas parciais."""
    c = tau / r
    u_c = c * np.sqrt((u_tau / tau) ** 2 + (u_r / r) ** 2)
    return c, u_c


def compatibilidade(a, u_a, b, u_b):
    """Discrepância normalizada |a - b| / sqrt(u_a^2 + u_b^2)."""
    return abs(a - b) / np.sqrt(u_a**2 + u_b**2)


def fmt(valor, incerteza):
    """Formata 'valor ± incerteza' com 2 algarismos significativos na incerteza
    se ela começar por 1 ou 2, e 1 algarismo caso contrário."""
    ordem = int(np.floor(np.log10(abs(incerteza))))
    primeiro = int(abs(incerteza) / 10**ordem)
    casas = -(ordem - 1) if primeiro < 3 else -ordem
    casas = max(casas, 0)
    return f'({valor:.{casas}f} ± {incerteza:.{casas}f})'


def fmt_br(valor, incerteza):
    """Igual a fmt, mas com vírgula decimal (para legendas dos gráficos)."""
    return fmt(valor, incerteza).replace('.', ',').replace('-', '\u2212')


def eixos_com_virgula(eixos):
    """Troca o separador decimal dos rótulos dos eixos de ponto para vírgula."""
    from matplotlib.ticker import FuncFormatter
    f = FuncFormatter(lambda x, pos: f'{x:g}'.replace('.', ',').replace('-', '\u2212'))
    for a in eixos:
        a.xaxis.set_major_formatter(f)
        a.yaxis.set_major_formatter(f)


def detectar_borda(t, v, t_inicio, descendo, escala_v=2.0):
    """Instante da borda da onda quadrada: primeiro ponto, após t_inicio, em que a tensão
    se afasta mais de 1,5 nível de quantização do patamar (mediana dos 20 pontos iniciais).
    Obs.: a escolha da origem t0 só altera a amplitude dV do ajuste, nunca tau."""
    d = escala_v / NIVEIS_POR_DIV
    i0 = np.searchsorted(t, t_inicio)
    patamar = np.median(v[i0:i0 + 20])
    if descendo:
        idx = np.where((t > t[i0]) & (v < patamar - 1.5 * d))[0][0]
    else:
        idx = np.where((t > t[i0]) & (v > patamar + 1.5 * d))[0][0]
    return t[idx - 1]
