from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PARÂMETROS GEOMÉTRICOS DO TUBO DE PVC (Altere com suas medidas)
# ==============================================================================
# Medidas físicas do tubo e suas incertezas (em metros)
L_tubo = 0.501        # Comprimento físico do tubo L (m) [Ex: 40,0 cm = 0,400 m]
u_L = 0.001           # Incerteza do comprimento u_L (m) [Ex: 1 mm]
r_tubo = 0.02215          # Raio interno do tubo r (m) [Ex: 1,5 cm = 0,015 m]
u_r = 0.0005          # Incerteza do raio u_r (m) [Ex: 0,5 mm]

# Para tubo Aberto-Aberto, há 2 extremidades abertas expostas ao meio externo (m = 2)
# Comprimento efetivo acústico: L' = L + 0.6 * m * r = L + 1.2 * r
m_extremidades = 2
L_efetivo = L_tubo + 0.6 * m_extremidades * r_tubo
u_L_efetivo = np.sqrt(u_L**2 + (1.2 * u_r)**2)

# ==============================================================================
# 2. LEITURA DOS DADOS EXPERIMENTAIS
# ==============================================================================
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados_tuboaa.csv'

# Lê o arquivo CSV contendo os harmônicos e suas frequências medidas
df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

n = df['n'].values       # Número do harmônico (n = 1, 2, 3, 4, ...)
f_n = df['f_n'].values   # Frequência medida no topo do pico (Hz)
u_fn = df['u_fn'].values # Incerteza da frequência (Hz)

# ==============================================================================
# 3. LINEARIZAÇÃO DO TUBO ABERTO-ABERTO: f_n = (v / (2 * L')) * n
# Linearização: Y = f_n  vs  X = n
# ==============================================================================
X = n                    # Eixo X = n (número do harmônico, exato)
Y = f_n                  # Eixo Y = f_n (frequência medida em Hz)

# Como o índice do harmônico n é uma contagem inteira exata (u_X = 0),
# a incerteza de Y é a própria incerteza da medição de frequência
u_Y = u_fn

# Ajuste Linear Ponderado por MMQ (Y = A*X + B)
coef, cov = np.polyfit(X, Y, 1, w=1/u_Y, cov=True)
A, B = coef

u_A = np.sqrt(cov[0, 0])   # Incerteza do coeficiente angular A
u_B = np.sqrt(cov[1, 1])   # Incerteza do coeficiente linear B

# ==============================================================================
# 4. CÁLCULO DA VELOCIDADE DO SOM (v) E INCERTEZA PROPAGADA
# A = v / (2 * L')  =&gt;  v = 2 * L' * A
# ==============================================================================
v = 2 * L_efetivo * A

# Propagação combinada da velocidade do som v = f(L', A)
u_v = v * np.sqrt((u_L_efetivo / L_efetivo)**2 + (u_A / A)**2)

print("="*55)
print("RESULTADOS DA ANÁLISE POR MMQ (TUBO ABERTO-ABERTO)")
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

plt.xlabel('Número do Harmônico $n$ (Adimensional)', fontsize=12)
plt.ylabel('Frequência de Ressonância $f_n$ (Hz)', fontsize=12)
#plt.title('Regressão Linear dos Harmônicos — Tubo Aberto–Aberto', fontsize=13, fontweight='bold')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11, loc='upper left')

texto_resultados = (f'$v_{{exp}} = ({v:.2f} \\pm {u_v:.2f})$ m/s\n'
                    f'$L\' = ({L_efetivo*100:.2f} \\pm {u_L_efetivo*100:.2f})$ cm')

plt.gca().text(0.62, 0.12, texto_resultados, transform=plt.gca().transAxes,
               fontsize=11, bbox=dict(boxstyle='round,pad=0.5', facecolor='whitesmoke', alpha=0.85))

plt.tight_layout()
plt.show()