import numpy as np
import matplotlib.pyplot as plt

# 1. Identificação dos experimentos (1 a 10)
experimentos = np.arange(1, 11)

# ==========================================
# DADOS DE TEMPO DE QUEDA (Das suas 10 coletas)
# ==========================================
# Tempo do Tracker (T_track) e sua incerteza associada (30 FPS)
t_track = np.array([0.70, 0.90, 0.87, 0.73, 0.97, 1.17, 0.93, 1.07, 1.17, 1.63])
u_t_track = np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]) # u = 0.01 s combinado

# Tempo do Cronômetro Manual (T_cron) e suas respectivas incertezas brutas
t_cron = np.array([0.603, 0.683, 0.880, 0.747, 0.790, 0.747, 0.830, 1.027, 1.120, 1.463])
u_t_cron = np.array([0.062, 0.118, 0.121, 0.022, 0.040, 0.055, 0.076, 0.130, 0.130, 0.221])

# ==========================================
# PROCESSAMENTO E TRATAMENTO DOS DADOS (Metrologia)
# ==========================================
# Diferença de tempo: delta_T = T_track - T_cron
delta_T = t_track - t_cron

# Propagação da incerteza-padrão combinada de delta_T (em quadratura)
u_delta_T = np.sqrt(u_t_track**2 + u_t_cron**2)

# Estatística descritiva da amostra (Média e Desvio Padrão Amostral)
media_delta_T = np.mean(delta_T)
desvio_padrao_delta_T = np.std(delta_T, ddof=1) # ddof=1 para desvio amostral

# Print dos parâmetros para conferência (e para colocar no texto)
print(f"Atraso sistemático médio: {media_delta_T:.3f} s")
print(f"Flutuação estatística (1-sigma): ± {desvio_padrao_delta_T:.3f} s")

# ==========================================
# CONSTRUÇÃO DO GRÁFICO DE RESÍDUOS
# ==========================================
plt.figure(figsize=(9, 6))

# Plotagem das diferenças individuais com barras de incerteza combinadas
plt.errorbar(experimentos, delta_T, yerr=u_delta_T, fmt='o', color='blue', 
             ecolor='darkblue', elinewidth=1.5, capsize=4, capthick=1.5, ms=6, 
             label='Diferença Individual ($\Delta T_i = T_{\\text{track}} - T_{\\text{cron}}$)')

# Linha horizontal vermelha para o valor médio (desvio sistemático médio)
plt.axhline(y=media_delta_T, color='red', linestyle='-', linewidth=2, 
            label=f'Atraso Médio: $\\overline{{\\Delta T}} = {media_delta_T:.3f}$ s')

# Faixa sombreada vermelha clara representando a dispersão de 1 desvio padrão (flutuação humana)
plt.axhspan(media_delta_T - desvio_padrao_delta_T, media_delta_T + desvio_padrao_delta_T, 
            color='red', alpha=0.12, 
            label=f'Flutuação Esperada ($\pm 1\\sigma$): $\pm {desvio_padrao_delta_T:.3f}$ s')

# Linha de referência no zero (caso a reação humana fosse perfeitamente instantânea)
plt.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1, label='Referência (Sem atraso)')

# Configurações visuais e eixos
plt.xlabel('Número do Experimento (Medição)', fontsize=12)
plt.ylabel('Diferença de Tempo $\Delta T$ (s)', fontsize=12)
plt.xticks(experimentos) # Mostra números inteiros de 1 a 10 no eixo X
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(fontsize=10, loc='upper left')

plt.tight_layout()
plt.show()