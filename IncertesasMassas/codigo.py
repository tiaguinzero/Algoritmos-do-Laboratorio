import pandas as pd
import numpy as np
import math

# ====================================================================
# 1. FUNÇÃO DE ARREDONDAMENTO AUTOMÁTICO (REGRA DO GUIA)
# ====================================================================
def formatar_resultado(valor, incerteza):
    """
    Arredonda a incerteza para 1 algarismo significativo e o valor central
    para a mesma casa decimal, retornando a string formatada.
    """
    if incerteza == 0:
        return f"({valor} ± 0)"
        
    # Encontra a posição do 1º algarismo significativo (ex: 0.00125 -> -3)
    casas_decimais = -int(math.floor(math.log10(abs(incerteza))))
    
    # Arredonda a incerteza para 1 algarismo significativo
    u_arr = round(incerteza, casas_decimais)
    
    # Prevenção extra: se o arredondamento mudou a casa decimal (ex: 0.098 vira 0.1)
    if u_arr != 0:
        casas_decimais = -int(math.floor(math.log10(abs(u_arr))))
        
    # Arredonda o valor medido para acompanhar a incerteza
    v_arr = round(valor, casas_decimais)
    
    # Garante que o Python exiba os zeros à direita (ex: 0.500 em vez de 0.5)
    casas_formatacao = max(0, casas_decimais)
    
    return f"({v_arr:.{casas_formatacao}f} ± {u_arr:.{casas_formatacao}f})"


# ====================================================================
# 2. PARÂMETROS DA BALANÇA (Ajuste conforme o seu manual)
# ====================================================================
resolucao = 0.001  # Exemplo: 1 grama

def calcular_incerteza(massa):
    """Calcula a incerteza de uma medição na balança."""
    u_leitura = resolucao / (2 * np.sqrt(3))
    erro_calibracao = (0.001 * massa) + (2 * resolucao) 
    u_calibracao = erro_calibracao / np.sqrt(3)
    return np.sqrt(u_leitura**2 + u_calibracao**2)


# ====================================================================
# 3. LEITURA DO ARQUIVO E PROCESSAMENTO
# ====================================================================
nome_arquivo = 'massas.csv'

try:
    # Lê o arquivo. Lembre-se: 'numero;massa' e decimais com vírgula!
    tabela = pd.read_csv(nome_arquivo, sep=';', decimal=',')
    
    massa_total = 0.0
    soma_variancias = 0.0 
    
    print("=== Massas Individuais ===")
    
    for index, row in tabela.iterrows():
        num = int(row['numero'])
        m = row['massa']
        
        # Calcula a incerteza individual longa
        u_m = calcular_incerteza(m)
        
        # Acumula os valores "crus" para a massa total (evita perda de dados)
        massa_total += m
        soma_variancias += u_m**2 
        
        # Aplica a formatação de algarismos significativos e imprime
        resultado_texto = formatar_resultado(m, u_m)
        print(f"{num} - {resultado_texto} kg")
        
    # Calcula a incerteza da massa total (Raiz da soma em quadratura)
    u_massa_total = np.sqrt(soma_variancias)
    
    print("\n=== Resultado Final ===")
    
    # Formata a massa total obedecendo as mesmas regras
    resultado_total_texto = formatar_resultado(massa_total, u_massa_total)
    print(f"Massa Total - {resultado_total_texto} kg\n")
            
except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
except KeyError:
    print("Erro: Verifique se o cabeçalho do arquivo CSV contém exatamente 'numero;massa'.")