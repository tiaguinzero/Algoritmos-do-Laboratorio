from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. LEITURA DOS DADOS (Localização automática na mesma pasta)
# ==============================================================================
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados_tracker.csv'

# Caso seu CSV use ponto e vírgula e vírgula decimal:
df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

D = df['D'].values       # Distância do eixo ao CM (m)
u_D = df['u_D'].values   # Incerteza de D (m)
T = df['T'].values       # Período de oscilação (s)
u_T = df['u_T'].values   # Incerteza do período T (s)

# ==============================================================================
# 2. TRANSFORMAÇÃO DAS VARIÁVEIS (X e Y)
# ==============================================================================
X = D**2                 # Eixo X = D²
Y = (T**2) * D           # Eixo Y = T² * D

# Propagação de Incerteza para X: u_X = 2 * D * u_D
u_X = 2 * D * u_D

# Propagação de Incerteza para Y via Derivadas Parciais:
dY_dT = 2 * T * D
dY_dD = T**2
u_Y = np.sqrt((dY_dT * u_T)**2 + (dY_dD * u_D)**2)

# ==============================================================================
# 3. MÉTODO DOS MÍNIMOS QUADRADOS (MMQ PONDERADO)
# ==============================================================================
# Pesos w = 1 / u_Y para o ajuste ponderado
coef, cov = np.polyfit(X, Y, 1, w=1/u_Y, cov=True)
A, B = coef

u_A = np.sqrt(cov[0, 0])   # Incerteza do coeficiente angular A
u_B = np.sqrt(cov[1, 1])   # Incerteza do coeficiente linear B
cov_AB = cov[0, 1]         # Covariância entre A e B

# ==============================================================================
# 4. CÁLCULO DE g E k COM SUAS INCERTEZAS
# ==============================================================================
# A = 4*pi^2 / g  =&gt;  g = 4*pi^2 / A
g = (4 * np.pi**2) / A
u_g = g * (u_A / A)

# B = A * k^2     =&gt;  k = sqrt(B / A)
k = np.sqrt(B / A)

# Incerteza propagada para k (considerando a covariância entre A e B):
u_k = k * 0.5 * np.sqrt((u_B / B)**2 + (u_A / A)**2 - 2 * (cov_AB / (A * B)))

# Exibição dos resultados numéricos no console
print("="*50)
print("RESULTADOS DA ANÁLISE POR MMQ (PÊNDULO FÍSICO)")
print("="*50)
print(f"Coeficiente Angular (A): {A:.4f} ± {u_A:.4f} s²/m")
print(f"Coeficiente Linear  (B): {B:.4f} ± {u_B:.4f} s²·m")
print("-" * 50)
print(f"Gravidade (g)        : {g:.3f} ± {u_g:.3f} m/s²")
print(f"Raio de Giração (k)  : {k:.4f} ± {u_k:.4f} m  ({k*100:.2f} ± {u_k*100:.2f} cm)")
print("="*50)

# ==============================================================================
# 5. CONSTRUÇÃO DO GRÁFICO 1 (Y vs X)
# ==============================================================================
x_ajuste = np.linspace(min(X) * 0.9, max(X) * 1.1, 100)
y_ajuste = A * x_ajuste + B

plt.figure(figsize=(9, 6))

# Pontos experimentais com barras de incerteza nos dois eixos
plt.errorbar(X, Y, xerr=u_X, yerr=u_Y, fmt='o', color='navy', 
             ecolor='blue', elinewidth=1, capsize=3, capthick=1, ms=6, 
             label='Dados Experimentais Transformados', zorder=3)

# Reta do ajuste linear MMQ
plt.plot(x_ajuste, y_ajuste, color='red', linewidth=1.8, 
         label=f'Ajuste MMQ: $Y = ({A:.2f} \\pm {u_A:.2f})X + ({B:.4f} \\pm {u_B:.4f})$')

# Configurações de eixos, títulos e grade
plt.xlabel('Variável $X = D^2$ (m²)', fontsize=12)
plt.ylabel('Variável $Y = T^2 D$ (s²·m)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11, loc='upper left')

# Caixa de texto com as grandezas físicas finais calculadas
texto_resultados = (f'$g_{{exp}} = ({g:.2f} \\pm {u_g:.2f})$ m/s²\n'
                    f'$k_{{exp}} = ({k*100:.2f} \\pm {u_k*100:.2f})$ cm')

plt.gca().text(0.62, 0.12, texto_resultados, transform=plt.gca().transAxes,
               fontsize=11, bbox=dict(boxstyle='round,pad=0.5', facecolor='whitesmoke', alpha=0.85))

plt.tight_layout()
plt.show()