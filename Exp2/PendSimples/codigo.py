from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados.csv'

df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

t_exp = df['t'].values if 't' in df.columns else df['tempo'].values
x_exp = df['x'].values
y_exp = df['y'].values

x0 = 0.0
y0 = 0.0

delta_x = x_exp - x0
delta_y = y0 - y_exp 

theta_exp = np.degrees(np.arctan2(delta_x, delta_y))

D = 0.221         
g = 9.786

T_simples = 2 * np.pi * np.sqrt(D / g)
omega_simples = (2 * np.pi) / T_simples

theta_max = 10.0  
phi0 = 0.0

t_curva = np.linspace(min(t_exp), max(t_exp), 500)
theta_simples = theta_max * np.cos(omega_simples * t_curva + phi0)

plt.figure(figsize=(9.5, 5.5))
plt.plot(t_exp, theta_exp, 'o-', color='navy', markersize=4, linewidth=1, 
         label='Dados Experimentais (Tracker)', zorder=3)

plt.plot(t_curva, theta_simples, color='crimson', linestyle='--', linewidth=2, 
         label=f'Pêndulo Simples ($T_{{simples}} = {T_simples:.2f}$ s)', zorder=2)

plt.xlabel('Tempo $t$ (s)', fontsize=12)
plt.ylabel('Posição Angular $\\theta(t)$ (°)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=10.5, loc='upper right')
plt.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)

texto_info = (f'Parâmetros do Pêndulo Simples:\n'
              f'$D = {D:.3f}$ m\n'
              f'$T_{{simples}} = {T_simples:.3f}$ s\n'
              f'$\\omega_{{simples}} = {omega_simples:.2f}$ rad/s')

plt.gca().text(0.02, 0.08, texto_info, transform=plt.gca().transAxes,
               fontsize=10, bbox=dict(boxstyle='round,pad=0.5', facecolor='linen', alpha=0.9))

plt.tight_layout()
plt.show()