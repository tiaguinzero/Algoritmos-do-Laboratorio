import numpy as np
import matplotlib.pyplot as plt
import pandas as pd  # NOVA BIBLIOTECA: Importando o pandas para ler o CSV

# 1. LEITURA AUTOMÁTICA DO ARQUIVO CSV
# Substitua 'dados_tracker.csv' pelo nome exato do seu arquivo.
# Certifique-se de que o arquivo Python e o CSV estão na mesma pasta.
nome_do_arquivo = 'dados_tracker.csv'

# Lendo o arquivo. 
# sep=';' -> Define que as colunas são separadas por ponto e vírgula. 
# decimal=',' -> Converte as vírgulas dos números brasileiros para os pontos do Python.
# skiprows=1 -> Pula a primeira linha se ela contiver texto inútil (ajuste se necessário).
tabela = pd.read_csv(nome_do_arquivo, sep=';', decimal=',')

# Extraindo as colunas para o formato do numpy
# Importante: verifique se os cabeçalhos no seu CSV se chamam 't' e 'y'. 
# Se o Tracker chamou de 'x' a coluna de queda, mude 'y' para 'x' abaixo.
tempo = tabela['t'].values
posicao = tabela['y'].values 

# 2. AJUSTE POLINOMIAL DE 2º GRAU
# O comando polyfit retorna os coeficientes da parábola [a2, a1, a0] e a matriz
coeficientes, matriz_cov = np.polyfit(tempo, posicao, 2, cov=True)
a2, a1, a0 = coeficientes

# 3. CÁLCULO DA ACELERAÇÃO FÍSICA E SUA INCERTEZA
a_fisica = 2 * a2

# Calculando a incerteza de a2 a partir da matriz de covariância
u_a2 = np.sqrt(matriz_cov[0, 0])
u_a_fisica = 2 * u_a2 # Propagação da incerteza

# 4. CRIANDO A CURVA PARA O GRÁFICO
t_ajuste = np.linspace(min(tempo), max(tempo), 100)
h_ajuste = a0 + a1 * t_ajuste + a2 * (t_ajuste**2)

# 5. EXIBINDO OS RESULTADOS NO TERMINAL
print("=== Resultados do Ajuste Polinomial ===")
print(f"a0 (Posição inicial): {a0:.4f} m")
print(f"a1 (Velocidade inicial): {a1:.4f} m/s")
print(f"a2 (Metade da aceleração): {a2:.4f} m/s²")
print(f"\nAceleração real (a): {a_fisica:.4f} ± {u_a_fisica:.4f} m/s²\n")

# 6. PLOTAGEM DO GRÁFICO
plt.figure(figsize=(8, 5))
plt.scatter(tempo, posicao, color='red', label='Dados do Tracker', zorder=2)
plt.plot(t_ajuste, h_ajuste, color='blue', label=f'Ajuste: $h(t) = {a2:.2f}t^2 {a1:+.2f}t {a0:+.2f}$')

plt.title('Ajuste Polinomial: Posição vs Tempo (Queda Livre)', fontweight='bold')
plt.xlabel('Tempo $t$ (s)')
plt.ylabel('Posição $h$ (m)')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.show()