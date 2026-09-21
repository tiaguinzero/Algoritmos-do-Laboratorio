from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. LEITURA DOS DADOS EXPERIMENTAIS
# ==============================================================================
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados.csv'

df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

D = df['D'].values       # Distância ao Centro de Massa (m)
u_D = df['u_D'].values   # Incerteza de D (m)
T = df['T'].values       # Período de oscilação (s)
u_T = df['u_T'].values   # Incerteza do período T (s)

# ==============================================================================
# 2. LINEARIZAÇÃO DO PÊNDULO SIMPLES: T² = (4*pi²/g) * D
# Linearização: Y = T²  vs  X = D
# ==============================================================================
X_simples = D
Y_simples = T**2

# Propagação de incerteza para Y: u_Y = |d(T²)/dT| * u_T = 2 * T * u_T
u_Y_simples = 2 * T * u_T

# Ajuste Linear Ponderado (Y = A*X + B)
coef_simples, cov_simples = np.polyfit(X_simples, Y_simples, 1, w=1/u_Y_simples, cov=True)
A_sim, B_sim = coef_simples

u_A_sim = np.sqrt(cov_simples[0, 0])
u_B_sim = np.sqrt(cov_simples[1, 1])

# Cálculo da Gravidade pelo Pêndulo Simples: A = 4*pi² / g =&gt; g = 4*pi² / A
g_simples = (4 * np.pi**2) / A_sim
u_g_simples = abs(g_simples * (u_A_sim / A_sim))

print("="*60)
print("RESULTADOS DO AJUSTE POR MMQ - MODELO PÊNDULO SIMPLES")
print("="*60)
print(f"Coeficiente Angular (A): {A_sim:.4f} ± {u_A_sim:.4f} s²/m")
print(f"Coeficiente Linear  (B): {B_sim:.4f} ± {u_B_sim:.4f} s²")
print(f"Gravidade Resultante (g): {g_simples:.2f} ± {u_g_simples:.2f} m/s²")
print("="*60)

# ==============================================================================
# 3. GRÁFICO DA LINEARIZAÇÃO DO PÊNDULO SIMPLES (Y vs X)
# ==============================================================================
x_curva = np.linspace(0, max(D) * 1.1, 100)
y_curva = A_sim * x_curva + B_sim

plt.figure(figsize=(9, 5.5))

# Pontos experimentais
plt.errorbar(X_simples, Y_simples, xerr=u_D, yerr=u_Y_simples, fmt='o', 
             color='royalblue', ecolor='blue', elinewidth=1.2, capsize=3, ms=6, 
             label='Dados Experimentais ($Y = T^2$, $X = D$)', zorder=3)

# Reta do ajuste linear
plt.plot(x_curva, y_curva, color='black', linestyle='--', linewidth=1.8,
         label=f'Ajuste Linear: $Y = ({A_sim:.2f} \\pm {u_A_sim:.2f})X + ({B_sim:.2f} \\pm {u_B_sim:.2f})$')

plt.xlabel('Distância ao Centro de Massa $D$ (m)', fontsize=12)
plt.ylabel('Quadrado do Período $T^2$ (s²)', fontsize=12)
plt.title('Linearização Inadequada pelo Modelo do Pêndulo Simples', fontsize=13, fontweight='bold')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=10.5, loc='upper right')

# Caixa explicativa mostrando o resultado discrepante de g
texto_box = (f'Resultado pelo Pêndulo Simples:\n'
             f'$g_{{simples}} = ({g_simples:.2f} \\pm {u_g_simples:.2f})$ m/s²\n'
             f'*(Modelo Inadequado: valor não-físico)*')

plt.gca().text(0.05, 0.12, texto_box, transform=plt.gca().transAxes,
               fontsize=10.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='linen', alpha=0.9))

plt.tight_layout()
plt.show()