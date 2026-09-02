import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# LEITURA AUTOMÁTICA DO ARQUIVO CSV
nome_do_arquivo = 'dados_tracker.csv'

tabela = pd.read_csv(nome_do_arquivo, sep=';', decimal=',')

tempo = tabela['t'].values
posicao = tabela['y'].values 

# AJUSTE POLINOMIAL DE 2º GRAU
coeficientes, matriz_cov = np.polyfit(tempo, posicao, 2, cov=True)
a2, a1, a0 = coeficientes

a_fisica = 2 * a2

u_a2 = np.sqrt(matriz_cov[0, 0])
u_a_fisica = 2 * u_a2 # Propagação da incerteza

# CRIANDO A CURVA PARA O GRÁFICO
t_ajuste = np.linspace(min(tempo), max(tempo), 100)
h_ajuste = a0 + a1 * t_ajuste + a2 * (t_ajuste**2)

# EXIBINDO OS RESULTADOS NO TERMINAL
print("=== Resultados do Ajuste Polinomial ===")
print(f"a0 (Posição inicial): {a0:.4f} m")
print(f"a1 (Velocidade inicial): {a1:.4f} m/s")
print(f"a2 (Metade da aceleração): {a2:.4f} m/s²")
print(f"\nAceleração real (a): {a_fisica:.4f} ± {u_a_fisica:.4f} m/s²\n")

# PLOTAGEM DO GRÁFICO
plt.figure(figsize=(8, 5))
plt.scatter(tempo, posicao, color='red', label='Dados do Tracker', zorder=2)
plt.plot(t_ajuste, h_ajuste, color='blue', label=f'Ajuste: $h(t) = {a2:.2f}t^2 {a1:+.2f}t {a0:+.2f}$')

plt.title('Ajuste Polinomial: Posição vs Tempo (Queda Livre)', fontweight='bold')
plt.xlabel('Tempo $t$ (s)')
plt.ylabel('Posição $h$ (m)')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.show()