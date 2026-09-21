import numpy as np
import matplotlib.pyplot as plt

# delta m
delta_m = np.array([0.4525, 0.3539, 0.2923, 0.2727, 0.2515, 0.2299, 0.2213, 0.1801, 0.1429, 0.0839]) 
u_delta_m = np.array([0.000042, 0.000042, 0.000042, 0.000042, 0.000042, 0.000042, 0.000042, 0.000042, 0.000042, 0.000042]) 

# Constantes
M = 0.4525       # Massa total do sistema em kg
u_M = 0.000042   # Incerteza da balança
R = 0.05         # Raio da polia em metros
u_R = 0.0005     # Incerteza do raio
g = 9.7856366    # Gravidade
u_g = 0.0000001  

# acelercao metodo 1
a_m1 = np.array([1.19, 0.72, 0.77, 1.09, 0.62, 0.43, 0.67, 0.51, 0.43, 0.219])
u_a_m1 = np.array([0.04, 0.02, 0.02, 0.03, 0.02, 0.01, 0.02, 0.01, 0.01, 0.003])

coef_m1, cov_m1 = np.polyfit(delta_m, a_m1, 1, w=1/u_a_m1, cov=True)
A1, B1 = coef_m1

# aceleracao metodo 2
a_m2 = np.array([1.22, 0.97, 0.72, 0.67, 0.67, 0.59, 0.62, 0.495, 0.383, 0.213]) 
u_a_m2 = np.array([0.04, 0.01, 0.03, 0.04, 0.02, 0.01, 0.01, 0.002, 0.006, 0.004])

coef_m2, cov_m2 = np.polyfit(delta_m, a_m2, 1, w=1/u_a_m2, cov=True)
A2, B2 = coef_m2

# gráfico
x_ajuste = np.linspace(min(delta_m)*0.9, max(delta_m)*1.05, 100)
y_ajuste_m1 = A1 * x_ajuste + B1
y_ajuste_m2 = A2 * x_ajuste + B2

plt.figure(figsize=(9, 6))

plt.errorbar(delta_m, a_m1, xerr=u_delta_m, yerr=u_a_m1, fmt='o', color='green', 
             ecolor='green', elinewidth=1, capsize=3, capthick=1, ms=5, 
             label='Método 1 (Cinemática)', zorder=3)
plt.plot(x_ajuste, y_ajuste_m1, color='green', linewidth=1.5, 
         label=f'MMQ Mét. 1: $a = {A1:.2f}\\Delta m {B1:+.4f}$')

plt.errorbar(delta_m, a_m2, xerr=u_delta_m, yerr=u_a_m2, fmt='s', color='red', 
             ecolor='red', elinewidth=1, capsize=3, capthick=1, ms=5, 
             label='Método 2 (Tracker)', zorder=4)
plt.plot(x_ajuste, y_ajuste_m2, color='red', linestyle='-', linewidth=2, 
         label=f'MMQ Mét. 2: $a = {A2:.2f}\\Delta m {B2:+.4f}$')

plt.xlabel('Diferença de Massa $\\Delta m$ (kg)', fontsize=12)
plt.ylabel('Aceleração Linear $a$ (m/s²)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11, loc='upper left')

plt.tight_layout()
plt.show()