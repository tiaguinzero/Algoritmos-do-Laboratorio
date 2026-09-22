from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados_tracker.csv'

df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

D = df['D'].values       # Distância do eixo ao CM (m)
u_D = df['u_D'].values   # Incerteza de D (m)
T = df['T'].values       # Período de oscilação (s)
u_T = df['u_T'].values   # Incerteza de T (s)

X = D**2
Y = (T**2) * D
u_Y = np.sqrt(((2 * T * D) * u_T)**2 + ((T**2) * u_D)**2)

coef = np.polyfit(X, Y, 1, w=1/u_Y)
A, B = coef

g_exp = (4 * np.pi**2) / A
k_exp = np.sqrt(B / A)

D_min = 0.01
D_max = 1.0    
D_curva = np.linspace(D_min, D_max, 500)

# Modelo 1: Pêndulo Simples T = 2*pi * sqrt(D / g)
T_simples = 2 * np.pi * np.sqrt(D_curva / g_exp)

# Modelo 2: Pêndulo Físico T = 2*pi * sqrt((D + k^2/D) / g)
T_fisico = 2 * np.pi * np.sqrt((D_curva + (k_exp**2) / D_curva) / g_exp)

plt.figure(figsize=(9.5, 6))

plt.errorbar(D, T, xerr=u_D, yerr=u_T, fmt='o', color='black', 
             ecolor='dimgray', elinewidth=1.2, capsize=3, capthick=1, ms=6, 
             label='Dados Experimentais Brutos', zorder=4)

plt.plot(D_curva, T_fisico, color='crimson', linewidth=2, linestyle='-',
         label=f'Modelo Pêndulo Físico ($g = {g_exp:.2f}$ m/s², $k = {k_exp*100:.1f}$ cm)', zorder=3)

plt.plot(D_curva, T_simples, color='royalblue', linewidth=1.8, linestyle='--',
         label=f'Modelo Pêndulo Simples ($g = {g_exp:.2f}$ m/s²)', zorder=2)

D_min_periodo = k_exp
T_min_periodo = 2 * np.pi * np.sqrt((2 * k_exp) / g_exp)
plt.plot(D_min_periodo, T_min_periodo, '^', color='darkred', ms=8, 
         label=f'Mínimo teórico ($D = k = {k_exp*100:.1f}$ cm)', zorder=5)

plt.xlim(0, 1.02)
plt.ylim(0, 2.3)
plt.xlabel('Distância ao Centro de Massa $D$ (m)', fontsize=12)
plt.ylabel('Período de Oscilação $T$ (s)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=10.5, loc='lower right')

plt.tight_layout()
plt.show()