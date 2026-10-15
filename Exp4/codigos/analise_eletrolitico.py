"""
analise_eletrolitico.py -- Parte I: circuito RC com tempo longo (capacitor eletrolítico).

Dados: dados/capacitor_eletronico/F0000CH1.CSV (Tektronix TBS 1062, 1 s/div, 2 V/div,
modo Scan). Circuito: gerador BK 4052 (onda quadrada de 4 Vpp, offset 0 V, período 10 s)
-> resistor de 1 kOhm -> capacitor eletrolítico de 1 mF; CH1 sobre o capacitor.

Etapas:
  1. Remove os pontos sem aquisição (código mínimo do A/D, -10,24 V) deixados pelo modo Scan.
  2. Monta a descarga completa por "dobramento de fase": como a tela (10 div x 1 s/div)
     corresponde a exatamente um período da onda quadrada, o tempo desde o início da
     descarga é s = (t - t_desc) mod T.
  3. Ajuste não linear V(s) = V_inf + dV exp(-s/tau).
  4. Linearização ln(V - V_inf) = ln(dV) - s/tau e MMQ ponderado.
  5. Verificações: ajuste só do trecho contínuo e ajuste da curva de carga.
  6. Capacitância C = tau / (R + R_ger) e comparação com os valores nominais.
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

ESCALA_V = 2.0          # V/div
T_ONDA = 10.0           # s, período da onda quadrada (0,1 Hz) = largura da tela
LIMIAR_LN = 0.20        # V, só linearizamos pontos com V - V_inf >= 0,20 V
C_NOM, U_C_NOM = 1.0e-3, 0.20 * 1.0e-3 / np.sqrt(3)   # 1 mF, tolerância 20 %

# ----------------------------------------------------------------- leitura e limpeza
t, v = ler_csv_tek(PASTA_DADOS / 'capacitor_eletronico' / 'F0000CH1.CSV')
sem_aquisicao = v <= -10.0                       # -10,24 V = código -128 do A/D
t_gap = t[sem_aquisicao]
print(f'Pontos sem aquisição: {sem_aquisicao.sum()} entre {t_gap[0]:.3f} s e {t_gap[-1]:.3f} s')

t_sub = detectar_borda(t, v, 1.0, descendo=False, escala_v=ESCALA_V)
t_desc = detectar_borda(t, v, 6.3, descendo=True, escala_v=ESCALA_V)
print(f'Borda de subida: {t_sub:.3f} s | borda de descida: {t_desc:.3f} s | '
      f'meio período: {t_desc - t_sub:.3f} s')

u_v = incerteza_tensao(v, ESCALA_V)

# ----------------------------------------------------------------- descarga (dobrada)
s = np.mod(t - t_desc, T_ONDA)
# exclui o semiciclo de carga e 30 ms antes da borda de subida (a carga já começa ali)
desc = (~sem_aquisicao) & (s < T_ONDA / 2) & ~((t > t_sub - 0.03) & (t < t_desc))
seg_atual = desc & (t >= t_desc) & (t < t_gap[0])          # varredura atual, contínuo
seg_anterior = desc & (t > t_gap[-1])                      # varredura anterior (Scan)
seg_pre = desc & (t < t_sub)                               # antes da borda de subida

p, cov, chi2 = ajuste_exponencial(s[desc], v[desc], u_v[desc], [-2.0, 4.0, 1.0])
u_p = np.sqrt(np.diag(cov))
v_inf, dv, tau_exp = p
u_vinf, u_dv, u_tau_exp = u_p
n_exp = desc.sum()
print('\n=== DESCARGA: ajuste exponencial (3 parâmetros) ===')
print(f'N = {n_exp}, chi2_red = {chi2 / (n_exp - 3):.3f}')
print(f'V_inf = {fmt(v_inf, u_vinf)} V | dV = {fmt(dv, u_dv)} V | tau = {fmt(tau_exp, u_tau_exp)} s')

# ----------------------------------------------------------------- linearização
s_l, y_l, u_y_l, m_l = linearizar(s[desc], v[desc], u_v[desc], v_inf, LIMIAR_LN)
A, B, u_A, u_B, cov_l, chi2_l = ajuste_linear(s_l, y_l, u_y_l)
tau_lin, u_tau_lin_est = tau_do_linear(A, u_A)
# efeito sistemático da incerteza de V_inf (comum a todos os pontos)
taus_vinf = []
for vi in (v_inf - u_vinf, v_inf + u_vinf):
    s2, y2, u2, _ = linearizar(s[desc], v[desc], u_v[desc], vi, LIMIAR_LN)
    taus_vinf.append(tau_do_linear(ajuste_linear(s2, y2, u2)[0], 1.0)[0])
u_tau_vinf = abs(taus_vinf[1] - taus_vinf[0]) / 2
u_tau_lin = np.hypot(u_tau_lin_est, u_tau_vinf)
print('\n=== DESCARGA: linearização ln(V - V_inf) x s ===')
print(f'N = {len(s_l)}, chi2_red = {chi2_l / (len(s_l) - 2):.3f}')
print(f'A = {fmt(A, u_A)} 1/s | B = {fmt(B, u_B)} | ln(dV) esperado = {np.log(dv):.3f}')
print(f'tau_lin = {fmt(tau_lin, u_tau_lin)} s  (estatística {u_tau_lin_est:.4f} s, '
      f'devida a V_inf {u_tau_vinf:.4f} s)')

# ----------------------------------------------------------------- verificações
pc, covc, chi2c = ajuste_exponencial(s[seg_atual], v[seg_atual], u_v[seg_atual],
                                     [-2.0, 4.0, 1.0])
print('\n=== Verificação: só o trecho contínuo da varredura atual ===')
print(f'N = {seg_atual.sum()}, tau = {fmt(pc[2], np.sqrt(covc[2, 2]))} s, '
      f'V_inf = {fmt(pc[0], np.sqrt(covc[0, 0]))} V')

carga = (t >= t_sub) & (t < t_desc)
pq, covq, chi2q = ajuste_exponencial(t[carga] - t_sub, v[carga], u_v[carga], [2.0, -4.0, 1.0])
tau_carga, u_tau_carga = pq[2], np.sqrt(covq[2, 2])
print('\n=== Verificação: curva de carga ===')
print(f'N = {carga.sum()}, chi2_red = {chi2q / (carga.sum() - 3):.3f}, '
      f'V_sup = {fmt(pq[0], np.sqrt(covq[0, 0]))} V, tau_carga = {fmt(tau_carga, u_tau_carga)} s')

# ----------------------------------------------------------------- capacitância e teoria
tau_teo = R_EQ * C_NOM
u_tau_teo = tau_teo * np.hypot(U_REQ / R_EQ, U_C_NOM / C_NOM)
C_exp, u_C_exp = capacitancia(tau_exp, u_tau_exp)
C_lin, u_C_lin = capacitancia(tau_lin, u_tau_lin)
print('\n=== Comparação com o modelo ===')
print(f'tau_teo = (R + R_ger) C_nom = {fmt(tau_teo, u_tau_teo)} s '
      f'(sem R_ger: {1000 * C_NOM:.2f} s)')
print(f'Z(tau_exp, teo) = {compatibilidade(tau_exp, u_tau_exp, tau_teo, u_tau_teo):.2f} | '
      f'Z(tau_lin, teo) = {compatibilidade(tau_lin, u_tau_lin, tau_teo, u_tau_teo):.2f} | '
      f'Z(exp, lin) = {compatibilidade(tau_exp, u_tau_exp, tau_lin, u_tau_lin):.2f} | '
      f'Z(exp, carga) = {compatibilidade(tau_exp, u_tau_exp, tau_carga, u_tau_carga):.2f}')
print(f'C (exp) = {fmt(C_exp * 1e3, u_C_exp * 1e3)} mF | C (lin) = {fmt(C_lin * 1e3, u_C_lin * 1e3)} mF'
      f' | C_nom = {fmt(C_NOM * 1e3, U_C_NOM * 1e3)} mF')
print(f'Z(C_exp, C_nom) = {compatibilidade(C_exp, u_C_exp, C_NOM, U_C_NOM):.2f}')

# ----------------------------------------------------------------- tabela (apêndice)
print('\n=== Tabela (amostra a cada ~0,25 s) para o apêndice ===')
ordem = np.argsort(s[desc])
s_o, v_o, u_o = s[desc][ordem], v[desc][ordem], u_v[desc][ordem]
for alvo in np.arange(0, 5.0, 0.25):
    i = np.argmin(abs(s_o - alvo))
    if abs(s_o[i] - alvo) > 0.05:
        continue
    dif = v_o[i] - v_inf
    ln_txt = f'{np.log(dif):.3f} & {u_o[i] / dif:.3f}' if dif >= LIMIAR_LN else '-- & --'
    print(f'{s_o[i]:.3f} & {v_o[i]:.2f} & {u_o[i]:.2f} & {ln_txt} \\\\')

# ----------------------------------------------------------------- gráfico
plt.rcParams.update({'font.size': 8, 'axes.labelsize': 8, 'legend.fontsize': 6.5})
fig, ax = plt.subplots(2, 2, figsize=(7.0, 3.6), sharex='col',
                       gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.08, 'wspace': 0.28})
cores = {'atual': 'tab:blue', 'anterior': 'tab:orange', 'pre': 'tab:green'}
rotulos = {'atual': 'varredura atual', 'anterior': 'varredura anterior (modo Scan)',
           'pre': 'antes da borda de subida'}
s_mod = np.linspace(0, T_ONDA / 2, 400)
for nome, m in (('atual', seg_atual), ('anterior', seg_anterior), ('pre', seg_pre)):
    ax[0, 0].plot(s[m], v[m], '.', ms=1.5, color=cores[nome], label=rotulos[nome])
    sel = np.where(m)[0][::20]
    ax[0, 0].errorbar(s[sel], v[sel], yerr=u_v[sel], fmt='none', ecolor=cores[nome],
                      elinewidth=0.6, capsize=1.5, alpha=0.7)
    res = v[m] - modelo_exp(s[m], p)
    ax[1, 0].plot(s[m], res, '.', ms=1.2, color=cores[nome])
ax[0, 0].plot(s_mod, modelo_exp(s_mod, p), 'r-', lw=1.2,
              label=fr'ajuste: $\tau$ = {fmt_br(tau_exp, u_tau_exp)} s')
ax[0, 0].set_ylabel('$V_C$ (V)')
ax[0, 0].legend(loc='upper right', frameon=False)
ax[0, 0].set_title('(a) Ajuste exponencial direto', fontsize=8)
banda = incerteza_tensao(modelo_exp(s_mod, p), ESCALA_V)
ax[1, 0].fill_between(s_mod, -banda, banda, color='gray', alpha=0.25, lw=0)
ax[1, 0].axhline(0, color='r', lw=0.8)
ax[1, 0].set_ylabel('resíduo (V)')
ax[1, 0].set_xlabel('tempo desde o início da descarga, $t$ (s)')

sel = np.arange(len(s_l))[::10]
ax[0, 1].plot(s_l, y_l, '.', ms=1.5, color='tab:blue', label='dados linearizados')
ax[0, 1].errorbar(s_l[sel], y_l[sel], yerr=u_y_l[sel], fmt='none', ecolor='tab:blue',
                  elinewidth=0.6, capsize=1.5, alpha=0.7)
x_mod = np.linspace(0, s_l.max(), 100)
ax[0, 1].plot(x_mod, A * x_mod + B, 'r-', lw=1.2,
              label=fr'MMQ: $A$ = {fmt_br(A, u_A)} s$^{{-1}}$')
ax[0, 1].set_ylabel(r'$\ln[(V_C - V_\infty)/1\,\mathrm{V}]$')
ax[0, 1].legend(loc='upper right', frameon=False)
ax[0, 1].set_title('(b) Linearização', fontsize=8)
ax[1, 1].errorbar(s_l[sel], (y_l - (A * s_l + B))[sel], yerr=u_y_l[sel], fmt='.', ms=2,
                  color='tab:blue', elinewidth=0.5, capsize=1)
ax[1, 1].axhline(0, color='r', lw=0.8)
ax[1, 1].set_ylabel('resíduo')
ax[1, 1].set_xlabel('$t$ (s)')
eixos_com_virgula(ax.flat)
for a in ax.flat:
    a.grid(alpha=0.3)
fig.align_ylabels(ax[:, 0])
PASTA_GRAFICOS.mkdir(exist_ok=True)
fig.savefig(PASTA_GRAFICOS / 'eletrolitico_descarga.pdf', bbox_inches='tight')
fig.savefig(PASTA_GRAFICOS / 'eletrolitico_descarga.png', dpi=200, bbox_inches='tight')
print('\nFiguras salvas em', PASTA_GRAFICOS)
