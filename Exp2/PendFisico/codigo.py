from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados.csv'

df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

t_exp = df['t'].values  # Tempo em segundos (s)
x_exp = df['x'].values  # Posição X em metros (m)
y_exp = df['y'].values  # Posição Y em metros (m)

x0 = 0.0
y0 = 0.0

delta_x = x_exp - x0
delta_y = y0 - y_exp  # Distância vertical para baixo

theta_exp = np.degrees(np.arctan2(delta_x, delta_y))

theta_max = np.max(np.abs(theta_exp[:15]))  # Primeiro pico inicial

picos_idx = []
for i in range(1, len(theta_exp) - 1):
    if theta_exp[i] > theta_exp[i-1] and theta_exp[i] > theta_exp[i+1] and theta_exp[i] > 0.5 * theta_max:
        picos_idx.append(i)

if len(picos_idx) >= 2:
    T_exp = t_exp[picos_idx[1]] - t_exp[picos_idx[0]]
else:
    T_exp = 1.102

omega_exp = (2 * np.pi) / T_exp  # Frequência angular (rad/s)

t_curva = np.linspace(min(t_exp), max(t_exp), 500)
theta_teorico = theta_max * np.cos(omega_exp * t_curva)

plt.figure(figsize=(10, 5.5))

plt.plot(t_exp, theta_exp, 'o-', color='navy', markersize=4, linewidth=1,
         label='Dados Experimentais (Tracker)', zorder=3)

plt.plot(t_curva, theta_teorico, color='crimson', linestyle='--', linewidth=2,
         label=f'Oscilador Ideal: $\\theta(t) = {theta_max:.1f}^\\circ \\cos({omega_exp:.2f} t)$', zorder=2)

plt.xlabel('Tempo $t$ (s)', fontsize=12)
plt.ylabel('Posição Angular $\\theta$ (°)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=10.5, loc='upper right')

plt.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)

texto_info = (f'$\\theta_{{max}} = {theta_max:.1f}^\\circ$\n'
              f'$T = {T_exp:.3f}$ s\n'
              f'$\\omega = {omega_exp:.2f}$ rad/s')

plt.gca().text(0.02, 0.08, texto_info, transform=plt.gca().transAxes,
               fontsize=10.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85))

plt.tight_layout()
plt.show()