from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PARÂMETROS GEOMÉTRICOS DO TUBO DE PVC (Aberto-Fechado)
# ==============================================================================
L_tubo = 0.501        # Comprimento físico do tubo L (m)
u_L = 0.001           # Incerteza do comprimento u_L (m)
r_tubo = 0.02215      # Raio interno do tubo r (m)
u_r = 0.0005          # Incerteza do raio u_r (m)

# Para tubo Aberto-Fechado, há apenas 1 extremidade aberta (m = 1)
# Comprimento efetivo acústico: L' = L + 0.6 * r
m_extremidades = 1
L_efetivo = L_tubo + 0.6 * m_extremidades * r_tubo
u_L_efetivo = np.sqrt(u_L**2 + (0.6 * u_r)**2)

# ==============================================================================
# 2. LEITURA DOS DADOS EXPERIMENTAIS
# ==============================================================================
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados_tuboaf.csv'

# Lê o arquivo CSV contendo os harmônicos ímpares e suas frequências
df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

n = df['n'].values       # Número do harmônico ímpar (n = 1, 3, 5, 7, ...)
f_n = df['f_n'].values   # Frequência medida no topo do pico (Hz)
u_fn = df['u_fn'].values # Incerteza da frequência (Hz)

# ==============================================================================
# 3. LINEARIZAÇÃO DO TUBO ABERTO-FECHADO: f_n = (v / (4 * L')) * n
# Linearização: Y = f_n  vs  X = n
# ==============================================================================
X = n                    # Eixo X = n (números ímpares: 1, 3, 5, ...)
Y = f_n                  # Eixo Y = f_n (frequência medida em Hz)
u_Y = u_fn

# Ajuste Linear Ponderado por MMQ (Y = A*X + B)
coef, cov = np.polyfit(X, Y, 1, w=1/u_Y, cov=True)
A, B = coef

u_A = np.sqrt(cov[0, 0])   # Incerteza do coeficiente angular A
u_B = np.sqrt(cov[1, 1])   # Incerteza do coeficiente linear B

# ==============================================================================
# 4. CÁLCULO DA VELOCIDADE DO SOM (v) E INCERTEZA PROPAGADA
# A = v / (4 * L')  =&gt;  v = 4 * L' * A
# ==============================================================================
v = 4 * L_efetivo * A

# Propagação combinada da velocidade do som v = f(L', A)
u_v = v * np.sqrt((u_L_efetivo / L_efetivo)**2 + (u_A / A)**2)

print("="*55)
print("RESULTADOS DA ANÁLISE POR MMQ (TUBO ABERTO-FECHADO)")
print("="*55)
print(f"Coeficiente Angular (A): {A:.2f} ± {u_A:.2f} Hz")
print(f"Coeficiente Linear  (B): {B:.2f} ± {u_B:.2f} Hz")
print("-" * 55)
print(f"Comprimento Efetivo L' : {L_efetivo*100:.2f} ± {u_L_efetivo*100:.2f} cm")
print(f"Velocidade do Som (v)  : {v:.2f} ± {u_v:.2f} m/s")
print("="*55)

# ==============================================================================
# 5. CONSTRUÇÃO DO GRÁFICO (Y vs X)
# ==============================================================================
x_ajuste = np.linspace(0.8, max(X) + 0.2, 100)
y_ajuste = A * x_ajuste + B

plt.figure(figsize=(9, 6))

plt.errorbar(X, Y, yerr=u_Y, fmt='o', color='navy', 
             ecolor='blue', elinewidth=1, capsize=3, capthick=1, ms=6, 
             label='Dados Experimentais ($Y = f_n$, $X = n$)', zorder=3)

plt.plot(x_ajuste, y_ajuste, color='red', linewidth=1.8, 
         label=f'Ajuste MMQ: $Y = ({A:.2f} \\pm {u_A:.2f})X + ({B:.2f} \\pm {u_B:.2f})$')

plt.xlabel('Número do Harmônico Ímpar $n$ (Adimensional)', fontsize=12)
plt.ylabel('Frequência de Ressonância $f_n$ (Hz)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11, loc='upper left')

texto_resultados = (f'$v_{{exp}} = ({v:.2f} \\pm {u_v:.2f})$ m/s\n'
                    f'$L\' = ({L_efetivo*100:.2f} \\pm {u_L_efetivo*100:.2f})$ cm')

plt.gca().text(0.62, 0.12, texto_resultados, transform=plt.gca().transAxes,
               fontsize=11, bbox=dict(boxstyle='round,pad=0.5', facecolor='whitesmoke', alpha=0.85))

plt.tight_layout()
plt.show()
