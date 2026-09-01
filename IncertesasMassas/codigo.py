import pandas as pd
import numpy as np

# ====================================================================
# 1. PARÂMETROS DA BALANÇA (Ajuste conforme o seu manual)
# ====================================================================
resolucao = 0.001  # Exemplo: 1 grama

def calcular_incerteza(massa):
    """Calcula a incerteza de uma medição na balança."""
    u_leitura = resolucao / (2 * np.sqrt(3))
    erro_calibracao = (0.001 * massa) + (2 * resolucao) 
    u_calibracao = erro_calibracao / np.sqrt(3)
    return np.sqrt(u_leitura**2 + u_calibracao**2)

# ====================================================================
# 2. LEITURA DO ARQUIVO E PROCESSAMENTO
# ====================================================================
nome_arquivo = 'massas.csv'

try:
    # Lê o arquivo com o separador ponto e vírgula
    tabela = pd.read_csv(nome_arquivo, sep=';', decimal=',')
    
    massa_total = 0.0
    soma_variancias = 0.0 # Guardará a soma dos quadrados das incertezas
    
    print("=== Massas Individuais ===")
    
    for index, row in tabela.iterrows():
        # Lê a linha atual
        num = int(row['numero'])
        m = row['massa']
        
        # Calcula a incerteza individual
        u_m = calcular_incerteza(m)
        
        # Acumula os valores para o total
        massa_total += m
        soma_variancias += u_m**2 # Soma em quadratura
        
        # Imprime no formato solicitado: número - (valor medido ± incerteza)
        print(f"{num} - ({m:.5f} ± {u_m:.5f}) kg")
        
    # Calcula a incerteza da massa total (Raiz da soma em quadratura)
    u_massa_total = np.sqrt(soma_variancias)
    
    print("\n=== Resultado Final ===")
    print(f"Massa Total - ({massa_total:.5f} ± {u_massa_total:.5f}) kg")
            
except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
except KeyError:
    print("Erro: Verifique se o cabeçalho do arquivo CSV contém exatamente 'numero;massa'.")