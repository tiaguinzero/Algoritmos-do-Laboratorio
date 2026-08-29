import numpy as np
import matplotlib.pyplot as plt

# 1. Dados experimentais (atualizados com seus novos valores)
# Variável Independente (X): Diferença de massa (delta_m) em kg
delta_m = np.array([0.3826, 0.2828, 0.1842, 0.848, 0.345]) 

# Variável Dependente (Y): Aceleração linear (a) em m/s^2
a_exp = np.array([-1.09, -0.87, -0.67, -0.33, -0.99]) 

# Constantes do experimento e suas INCERTEZAS
M = 0.500     # Massa total do sistema (m1 + m2) em kg
u_M = 0.001   # Incerteza da balança para a massa total em kg (Substitua pelo valor real)

R = 0.005     # Raio da polia em metros
u_R = 0.204  # Incerteza do instrumento de medida do raio em metros (Substitua pelo valor real)

# Gravidade exata de Campinas
g = 9.7856366  
u_g = 0.0000001 

# 2. Aplicação do MMQ para achar 'A', 'B' e suas respectivas incertezas
# cov=True retorna a matriz de covariância para obtermos u_A e u_B
coeficientes, matriz_cov = np.polyfit(delta_m, a_exp, 1, cov=True)
A, B = coeficientes
u_A = np.sqrt(matriz_cov[0, 0])
u_B = np.sqrt(matriz_cov[1, 1])

# 3. Criar a reta de ajuste usando os coeficientes encontrados
x_ajuste = np.linspace(min(delta_m), max(delta_m), 100)
y_ajuste = A * x_ajuste + B

# 4. Cálculo dos parâmetros físicos a partir dos coeficientes A e B
I = (R**2) * ((g / A) - M)
tau_a = -B * ((g * R) / A)

# 5. PROPAGAÇÃO DE INCERTEZA (Método das Derivadas Parciais)
# Incerteza do Momento de Inércia (u_I)
termo1_I = (-(g * R**2) / (A**2)) * u_A
termo2_I = 2 * R * ((g / A) - M) * u_R
termo3_I = -(R**2) * u_M
termo4_I = (R**2 / A) * u_g  # Derivada em relação à gravidade
u_I = np.sqrt(termo1_I**2 + termo2_I**2 + termo3_I**2 + termo4_I**2)

# Incerteza do Torque de Atrito (u_tau_a)
# Incorporamos (u_g/g)^2 por rigor, embora seja um valor que tenderá a zero.
u_tau_a = abs(tau_a) * np.sqrt((u_B / B)**2 + (u_A / A)**2 + (u_R / R)**2 + (u_g / g)**2)

# 6. Exibe os valores no terminal ANTES de plotar o gráfico
print("=== Coeficientes do Ajuste (MMQ) ===")
print(f"Coeficiente angular (A): {A:.4f} ± {u_A:.4f}")
print(f"Coeficiente linear (B): {B:.4f} ± {u_B:.4f}")
print(f"Equação da reta: a = {A:.4f} * Δm {B:+.4f}\n")

print("=== Resultados Físicos Estimados ===")
print(f"Momento de Inércia (I): {I:.6f} ± {u_I:.6f} kg.m²")
print(f"Torque de Atrito (tau_a): {tau_a:.6f} ± {u_tau_a:.6f} N.m\n")

# 7. Construção do gráfico com Matplotlib
plt.figure(figsize=(8, 5))
plt.scatter(delta_m, a_exp, color='red', marker='s', s=50, label='Dados Experimentais', zorder=2)
plt.plot(x_ajuste, y_ajuste, color='blue', linewidth=2, label=f'Reta MMQ: $a = {A:.2f}\\Delta m {B:+.4f}$')

plt.title('Máquina de Atwood: Aceleração vs Diferença de Massa', fontsize=14, fontweight='bold')
plt.xlabel('Diferença de Massa $\\Delta m$ (kg)', fontsize=12)
plt.ylabel('Aceleração Linear $a$ (m/s²)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11)

plt.show()