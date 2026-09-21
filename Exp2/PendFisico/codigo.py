from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. LOCALIZAÇÃO AUTOMÁTICA DO ARQUIVO CSV
# ==============================================================================
# Encontra o caminho absoluto da pasta onde este arquivo codigo.py está salvo
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT / 'dados.csv'

# Lê o CSV no caminho correto
df = pd.read_csv(CAMINHO_CSV, sep=';', decimal=',')

t_exp = df['t'].values  # Tempo em segundos (s)
x_exp = df['x'].values  # Posição X em metros (m)
y_exp = df['y'].values  # Posição Y em metros (m)

# ==============================================================================
# 2. CÁLCULO DA POSIÇÃO ANGULAR THETA(t)
# ==============================================================================
# Coordenadas do Eixo de Rotação (Pivô) no Tracker
x0 = 0.0
y0 = 0.0

delta_x = x_exp - x0
delta_y = y0 - y_exp  # Distância vertical para baixo

# Cálculo do ângulo theta em graus: theta = arctan(delta_x / delta_y)
theta_exp = np.degrees(np.arctan2(delta_x, delta_y))

# ==============================================================================
# 3. PARÂMETROS PARA A CURVA TEÓRICA DO OSCILADOR IDEAL
# ==============================================================================
# 1. Amplitude Máxima (theta_max): Pega o valor máximo absoluto no início
theta_max = np.max(np.abs(theta_exp[:15]))  # Primeiro pico inicial

# 2. Determinação do Período (T) e Frequência Angular (omega):
picos_idx = []
for i in range(1, len(theta_exp) - 1):
    if theta_exp[i] > theta_exp[i-1] and theta_exp[i] > theta_exp[i+1] and theta_exp[i] > 0.5 * theta_max:
        picos_idx.append(i)

if len(picos_idx) >= 2:
    T_exp = t_exp[picos_idx[1]] - t_exp[picos_idx[0]]  # Diferença do tempo entre os 2 primeiros picos
else:
    # Caso não detecte picos automaticamente, informe o período medido manualmente
    T_exp = 1.14  # Substitua pelo valor de T medido para este furo

omega_exp = (2 * np.pi) / T_exp  # Frequência angular (rad/s)

# 3. Constante de Fase (phi0)
#phi0 = 0.0 

# ==============================================================================
# 4. GERAÇÃO DA CURVA TEÓRICA IDEAL: theta(t) = theta_max * cos(omega * t + phi0)
# ==============================================================================
t_curva = np.linspace(min(t_exp), max(t_exp), 500)
theta_teorico = theta_max * np.cos(omega_exp * t_curva)

# ==============================================================================
# 5. CONSTRUÇÃO DO GRÁFICO 3 (theta vs t)
# ==============================================================================
plt.figure(figsize=(10, 5.5))

# Dados Reais Calculados a partir de (x, y) do Tracker
plt.plot(t_exp, theta_exp, 'o-', color='navy', markersize=4, linewidth=1,
         label='Dados Experimentais (Tracker)', zorder=3)

# Curva Teórica Ideal do Oscilador Harmônico
plt.plot(t_curva, theta_teorico, color='crimson', linestyle='--', linewidth=2,
         label=f'Oscilador Ideal: $\\theta(t) = {theta_max:.1f}^\\circ \\cos({omega_exp:.2f} t)$', zorder=2)

# Configurações de eixos, títulos e legenda
plt.xlabel('Tempo $t$ (s)', fontsize=12)
plt.ylabel('Posição Angular $\\theta$ (°)', fontsize=12)
#plt.title('Gráfico 3: Posição Angular em Função do Tempo (Rastreamento vs Teoria)', fontsize=13, fontweight='bold')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=10.5, loc='upper right')

# Linha de referência horizontal em theta = 0 (Posição de equilíbrio)
plt.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)

# Caixa com informações dos parâmetros da oscilação
texto_info = (f'$\\theta_{{max}} = {theta_max:.1f}^\\circ$\n'
              f'$T = {T_exp:.3f}$ s\n'
              f'$\\omega = {omega_exp:.2f}$ rad/s')

plt.gca().text(0.02, 0.08, texto_info, transform=plt.gca().transAxes,
               fontsize=10.5, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85))

plt.tight_layout()
plt.show()