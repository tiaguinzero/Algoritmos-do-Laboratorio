"""
analise_ceramico.py -- Parte II: circuito RC com tempo curto (capacitor cerâmico).

Dados: dados/capacitor_ceramico/F0000CH1.CSV (Tektronix TBS 1062, 2,5 ms/div, 2 V/div).
Circuito: gerador BK 4052 (onda quadrada de 4 Vpp, offset 0 V, f = 99,98 Hz medida pelo
osciloscópio) -> resistor de 1 kOhm -> capacitor cerâmico de 1 uF; CH1 sobre o capacitor.

Etapas:
  1. Isola um semiciclo completo de descarga (~5 ms ~ 5 tau).
  2. Ajuste não linear V(t) = V_inf + dV exp(-t/tau).
  3. Linearização ln(V - V_inf) = ln(dV) - t/tau e MMQ ponderado.
  4. Verificações: segundo semiciclo de descarga e semiciclo de carga.
  5. Capacitância C = tau / (R + R_ger) e comparação com os valores nominais.
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/mplconfig')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils_rc import (PASTA_DADOS, PASTA_GRAFICOS, R_EQ, U_REQ, ler_csv_tek,
                      incerteza_tensao, ajuste_exponencial, modelo_exp, ajuste_linear,
                      linearizar, tau_do_linear, capacitancia, compatibilidade, fmt, fmt_br,
                      detectar_borda, eixos_com_virgula)

ESCALA_V = 2.0                      # V/div
F_ONDA = 99.9834                    # Hz (contador de frequência do osciloscópio)
T_ONDA = 1.0 / F_ONDA               # s
LIMIAR_LN = 0.20                    # V
C_NOM, U_C_NOM = 1.0e-6, 0.10 * 1.0e-6 / np.sqrt(3)   # 1 uF, tolerância 10 %

t, v = ler_csv_tek(PASTA_DADOS / 'capacitor_ceramico' / 'F0000CH1.CSV')
u_v = incerteza_tensao(v, ESCALA_V)


def janela(t_borda):
    """Semiciclo que começa na borda (descarta 2 % finais para não incluir a borda seguinte)."""
    return (t >= t_borda) & (t < t_borda + 0.98 * T_ONDA / 2)


# ----------------------------------------------------------------- descarga principal
t_d1 = detectar_borda(t, v, -6.8e-3, descendo=True, escala_v=ESCALA_V)
m1 = janela(t_d1)
td, vd, ud = t[m1] - t_d1, v[m1], u_v[m1]
p, cov, chi2 = ajuste_exponencial(td, vd, ud, [-2.0, 4.0, 1e-3])
u_p = np.sqrt(np.diag(cov))
v_inf, dv, tau_exp = p
u_vinf, u_dv, u_tau_exp = u_p
print(f'Borda de descida: {t_d1 * 1e3:.2f} ms | período T = {T_ONDA * 1e3:.3f} ms')
print('\n=== DESCARGA: ajuste exponencial (3 parâmetros) ===')
print(f'N = {len(td)}, chi2_red = {chi2 / (len(td) - 3):.3f}')
print(f'V_inf = {fmt(v_inf, u_vinf)} V | dV = {fmt(dv, u_dv)} V | '
      f'tau = {fmt(tau_exp * 1e3, u_tau_exp * 1e3)} ms')

# ----------------------------------------------------------------- linearização
t_l, y_l, u_y_l, _ = linearizar(td, vd, ud, v_inf, LIMIAR_LN)
A, B, u_A, u_B, cov_l, chi2_l = ajuste_linear(t_l, y_l, u_y_l)
tau_lin, u_tau_lin_est = tau_do_linear(A, u_A)
taus_vinf = []
for vi in (v_inf - u_vinf, v_inf + u_vinf):
    t2, y2, u2, _ = linearizar(td, vd, ud, vi, LIMIAR_LN)
    taus_vinf.append(tau_do_linear(ajuste_linear(t2, y2, u2)[0], 1.0)[0])
u_tau_vinf = abs(taus_vinf[1] - taus_vinf[0]) / 2
u_tau_lin = np.hypot(u_tau_lin_est, u_tau_vinf)
print('\n=== DESCARGA: linearização ln(V - V_inf) x t ===')
print(f'N = {len(t_l)}, chi2_red = {chi2_l / (len(t_l) - 2):.3f}')
print(f'A = {fmt(A, u_A)} 1/s | B = {fmt(B, u_B)} | ln(dV) esperado = {np.log(dv):.3f}')
print(f'tau_lin = {fmt(tau_lin * 1e3, u_tau_lin * 1e3)} ms (estatística '
      f'{u_tau_lin_est * 1e3:.4f} ms, devida a V_inf {u_tau_vinf * 1e3:.4f} ms)')

# ----------------------------------------------------------------- verificações
t_d2 = detectar_borda(t, v, 3.2e-3, descendo=True, escala_v=ESCALA_V)
m2 = janela(t_d2)
p2, cov2, _ = ajuste_exponencial(t[m2] - t_d2, v[m2], u_v[m2], [-2.0, 4.0, 1e-3])
print('\n=== Verificação: segundo semiciclo de descarga ===')
print(f'borda {t_d2 * 1e3:.2f} ms, N = {m2.sum()}, '
      f'tau = {fmt(p2[2] * 1e3, np.sqrt(cov2[2, 2]) * 1e3)} ms')

t_s = detectar_borda(t, v, -2.0e-3, descendo=False, escala_v=ESCALA_V)
ms = janela(t_s)
pq, covq, chi2q = ajuste_exponencial(t[ms] - t_s, v[ms], u_v[ms], [2.0, -4.0, 1e-3])
tau_carga, u_tau_carga = pq[2], np.sqrt(covq[2, 2])
print('\n=== Verificação: semiciclo de carga ===')
print(f'borda {t_s * 1e3:.2f} ms, N = {ms.sum()}, chi2_red = {chi2q / (ms.sum() - 3):.3f}, '
      f'V_sup = {fmt(pq[0], np.sqrt(covq[0, 0]))} V, '
      f'tau_carga = {fmt(tau_carga * 1e3, u_tau_carga * 1e3)} ms')
print(f'meio período medido entre bordas: {(t_s - t_d1) * 1e3:.2f} ms')

# ----------------------------------------------------------------- capacitância e teoria
tau_teo = R_EQ * C_NOM
u_tau_teo = tau_teo * np.hypot(U_REQ / R_EQ, U_C_NOM / C_NOM)
C_exp, u_C_exp = capacitancia(tau_exp, u_tau_exp)
C_lin, u_C_lin = capacitancia(tau_lin, u_tau_lin)
print('\n=== Comparação com o modelo ===')
print(f'tau_teo = (R + R_ger) C_nom = {fmt(tau_teo * 1e3, u_tau_teo * 1e3)} ms')
print(f'Z(tau_exp, teo) = {compatibilidade(tau_exp, u_tau_exp, tau_teo, u_tau_teo):.2f} | '
      f'Z(tau_lin, teo) = {compatibilidade(tau_lin, u_tau_lin, tau_teo, u_tau_teo):.2f} | '
      f'Z(exp, lin) = {compatibilidade(tau_exp, u_tau_exp, tau_lin, u_tau_lin):.2f} | '
      f'Z(exp, carga) = {compatibilidade(tau_exp, u_tau_exp, tau_carga, u_tau_carga):.2f}')
print(f'C (exp) = {fmt(C_exp * 1e6, u_C_exp * 1e6)} uF | C (lin) = {fmt(C_lin * 1e6, u_C_lin * 1e6)} uF'
      f' | C_nom = {fmt(C_NOM * 1e6, U_C_NOM * 1e6)} uF')
print(f'Z(C_exp, C_nom) = {compatibilidade(C_exp, u_C_exp, C_NOM, U_C_NOM):.2f} | '
      f'Z(C_lin, C_nom) = {compatibilidade(C_lin, u_C_lin, C_NOM, U_C_NOM):.2f}')

# ----------------------------------------------------------------- tabela (apêndice)
print('\n=== Tabela (amostra a cada 0,25 ms) para o apêndice ===')
for alvo in np.arange(0, 4.9e-3, 0.25e-3):
    i = np.argmin(abs(td - alvo))
    dif = vd[i] - v_inf
    ln_txt = f'{np.log(dif):.3f} & {ud[i] / dif:.3f}' if dif >= LIMIAR_LN else '-- & --'
    print(f'{td[i] * 1e3:.2f} & {vd[i]:.2f} & {ud[i]:.2f} & {ln_txt} \\\\')

# ----------------------------------------------------------------- gráfico
plt.rcParams.update({'font.size': 8, 'axes.labelsize': 8, 'legend.fontsize': 6.5})
fig, ax = plt.subplots(2, 2, figsize=(7.0, 3.6), sharex='col',
                       gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.08, 'wspace': 0.28})
tms = td * 1e3
sel = np.arange(len(td))[::15]
ax[0, 0].plot(tms, vd, '.', ms=1.5, color='tab:blue', label='dados (osciloscópio)')
ax[0, 0].errorbar(tms[sel], vd[sel], yerr=ud[sel], fmt='none', ecolor='tab:blue',
                  elinewidth=0.6, capsize=1.5, alpha=0.7)
t_mod = np.linspace(0, td.max(), 400)
ax[0, 0].plot(t_mod * 1e3, modelo_exp(t_mod, p), 'r-', lw=1.2,
              label=fr'ajuste: $\tau$ = {fmt_br(tau_exp * 1e3, u_tau_exp * 1e3)} ms')
ax[0, 0].set_ylabel('$V_C$ (V)')
ax[0, 0].legend(loc='upper right', frameon=False)
ax[0, 0].set_title('(a) Ajuste exponencial direto', fontsize=8)
banda = incerteza_tensao(modelo_exp(t_mod, p), ESCALA_V)
ax[1, 0].fill_between(t_mod * 1e3, -banda, banda, color='gray', alpha=0.25, lw=0)
ax[1, 0].plot(tms, vd - modelo_exp(td, p), '.', ms=1.2, color='tab:blue')
ax[1, 0].axhline(0, color='r', lw=0.8)
ax[1, 0].set_ylabel('resíduo (V)')
ax[1, 0].set_xlabel('tempo desde o início da descarga, $t$ (ms)')

sel = np.arange(len(t_l))[::10]
ax[0, 1].plot(t_l * 1e3, y_l, '.', ms=1.5, color='tab:blue', label='dados linearizados')
ax[0, 1].errorbar(t_l[sel] * 1e3, y_l[sel], yerr=u_y_l[sel], fmt='none', ecolor='tab:blue',
                  elinewidth=0.6, capsize=1.5, alpha=0.7)
x_mod = np.linspace(0, t_l.max(), 100)
ax[0, 1].plot(x_mod * 1e3, A * x_mod + B, 'r-', lw=1.2,
              label=fr'MMQ: $A$ = {fmt_br(A, u_A)} s$^{{-1}}$')
ax[0, 1].set_ylabel(r'$\ln[(V_C - V_\infty)/1\,\mathrm{V}]$')
ax[0, 1].legend(loc='upper right', frameon=False)
ax[0, 1].set_title('(b) Linearização', fontsize=8)
ax[1, 1].errorbar(t_l[sel] * 1e3, (y_l - (A * t_l + B))[sel], yerr=u_y_l[sel], fmt='.', ms=2,
                  color='tab:blue', elinewidth=0.5, capsize=1)
ax[1, 1].axhline(0, color='r', lw=0.8)
ax[1, 1].set_ylabel('resíduo')
ax[1, 1].set_xlabel('$t$ (ms)')
eixos_com_virgula(ax.flat)
for a in ax.flat:
    a.grid(alpha=0.3)
fig.align_ylabels(ax[:, 0])
PASTA_GRAFICOS.mkdir(exist_ok=True)
fig.savefig(PASTA_GRAFICOS / 'ceramico_descarga.pdf', bbox_inches='tight')
fig.savefig(PASTA_GRAFICOS / 'ceramico_descarga.png', dpi=200, bbox_inches='tight')
print('\nFiguras salvas em', PASTA_GRAFICOS)
