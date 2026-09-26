from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PARÂMETROS GEOMÉTRICOS DO GARGALO DA GARRAFA (Altere com suas medidas)
# ==============================================================================
# Medidas físicas do gargalo e suas incertezas (em metros)
L_gargalo = 0.076      # Comprimento físico do gargalo L (m)
u_L = 0.001           # Incerteza do comprimento u_L (m)
r_gargalo = 0.01045     # Raio interno do gargalo r (m)
u_r = 0.00005           # Incerteza do raio u_r (m)

# Área da seção reta S = pi * r²
S = np.pi * (r_gargalo**2)
u_S = 2 * np.pi * r_gargalo * u_r

# Comprimento efetivo com correção de terminação: L' = L + 1.45 * r
L_efetivo = L_gargalo + 1.45 * r_gargalo
u_L_efetivo = np.sqrt(u_L**2 + (1.45 * u_r)**2)

# ==============================================================================
# 2. LEITURA DOS DADOS EXPERIMENTAIS
# ==============================================================================
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados_garrafa.csv'

df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

V = df['V'].values       # Volume de ar útil dentro da garrafa (m³)
u_V = df['u_V'].values   # Incerteza do volume (m³)
f0 = df['f0'].values     # Frequência de ressonância fundamental (Hz)
u_f0 = df['u_f0'].values # Incerteza da frequência (Hz)

# ==============================================================================
# 3. LINEARIZAÇÃO DO RESSONADOR DE HELMHOLTZ: f0² = (v² * S / (4*pi² * L')) * (1/V)
# Linearização: Y = f0²  vs  X = 1/V
# ==============================================================================
X = 1 / V                # Eixo X = 1/V (m⁻³)
Y = f0**2                # Eixo Y = f0² (Hz²)

# Propagação de incertezas por derivada parcial:
# u_X = |-1/V²| * u_V
u_X = u_V / (V**2)

# u_Y = |2 * f0| * u_f0
u_Y = 2 * f0 * u_f0

# Ajuste Linear Ponderado por MMQ (Y = A*X + B)
coef, cov = np.polyfit(X, Y, 1, w=1/u_Y, cov=True)
A, B = coef

u_A = np.sqrt(cov[0, 0])   # Incerteza do coeficiente angular A
u_B = np.sqrt(cov[1, 1])   # Incerteza do coeficiente linear B
cov_AB = cov[0, 1]         # Covariância entre A e B

# ==============================================================================
# 4. CÁLCULO DA VELOCIDADE DO SOM (v) E INSERTEZA PROPAGADA
# A = (v² * S) / (4 * pi² * L')  =&gt;  v = 2 * pi * sqrt( (L' * A) / S )
# ==============================================================================
v = 2 * np.pi * np.sqrt((L_efetivo * A) / S)

# Propagação combinada da velocidade do som v = f(L', A, S)
u_v = v * 0.5 * np.sqrt((u_L_efetivo / L_efetivo)**2 + (u_A / A)**2 + (u_S / S)**2)

print("="*55)
print("RESULTADOS DA ANÁLISE POR MMQ (RESSONADOR DE HELMHOLTZ)")
print("="*55)
print(f"Coeficiente Angular (A): {A:.4e} ± {u_A:.4e} Hz²·m³")
print(f"Coeficiente Linear  (B): {B:.2f} ± {u_B:.2f} Hz²")
print("-" * 55)
print(f"Comprimento Efetivo L' : {L_efetivo*100:.2f} ± {u_L_efetivo*100:.2f} cm")
print(f"Área da Seção Reta S   : {S*1e4:.3f} ± {u_S*1e4:.3f} cm²")
print(f"Velocidade do Som (v)  : {v:.2f} ± {u_v:.2f} m/s")
print("="*55)

# ==============================================================================
# 5. CONSTRUÇÃO DO GRÁFICO (Y vs X)
# ==============================================================================
x_ajuste = np.linspace(min(X) * 0.9, max(X) * 1.1, 100)
y_ajuste = A * x_ajuste + B

plt.figure(figsize=(9, 6))

plt.errorbar(X, Y, xerr=u_X, yerr=u_Y, fmt='o', color='navy', 
             ecolor='blue', elinewidth=1, capsize=3, capthick=1, ms=6, 
             label='Dados Experimentais Transformados ($Y = f_0^2$, $X = 1/V$)', zorder=3)

plt.plot(x_ajuste, y_ajuste, color='red', linewidth=1.8, 
         label=f'Ajuste MMQ: $Y = ({A:.2e} \\pm {u_A:.2e})X + ({B:.1f} \\pm {u_B:.1f})$')

plt.xlabel('Inverso do Volume $X = 1/V$ (m⁻³)', fontsize=12)
plt.ylabel('Quadrado da Frequência $Y = f_0^2$ (Hz²)', fontsize=12)
#plt.title('Linearização do Ressonador de Helmholtz', fontsize=13, fontweight='bold')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=11, loc='upper left')

texto_resultados = (f'$v_{{exp}} = ({v:.2f} \\pm {u_v:.2f})$ m/s\n'
                    f'$L\' = ({L_efetivo*100:.2f} \\pm {u_L_efetivo*100:.2f})$ cm')

plt.gca().text(0.62, 0.12, texto_resultados, transform=plt.gca().transAxes,
               fontsize=11, bbox=dict(boxstyle='round,pad=0.5', facecolor='whitesmoke', alpha=0.85))

plt.tight_layout()
plt.show()