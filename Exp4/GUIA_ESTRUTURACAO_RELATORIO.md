# Guia de Planejamento e Estruturação do Relatório do Experimento IV
**Disciplina:** F 259 – Introdução à Física Experimental II (IFGW / Unicamp)  
**Experimento IV:** Capacitor e Circuitos RC  
**Arquivo Principal:** `relatorio_final/relatorio4_capacitor.tex`  
**Extensão Máxima:** 5 páginas de corpo principal (excluindo Capa e Apêndices)

---
 
## 1. Diretrizes Fundamentais e Restrições do Projeto

1. **Limite Estrito de Páginas:**
   - O corpo do relatório (do **Resumo** à **Conclusão**) deve ter **no máximo 5 páginas**.
   - A **Capa** e os **Apêndices** (fotos, deduções, planilhas de incerteza e códigos-fonte) não contam para esse limite.
2. **Localização dos Arquivos:**
   - Scripts Python de análise e ajustes: `Exp4/codigos/`
   - Figuras e gráficos gerados: `Exp4/graficos/` (e linkados em `relatorio_final/`)
   - Fotos da bancada e equipamentos: `relatorio_final/fotos/`
   - Documento LaTeX: `relatorio_final/relatorio4_capacitor.tex`
3. **Referenciação dos Códigos:**
   - Todos os scripts em `Exp4/codigos/` deverão ser incluídos integralmente nos Apêndices (usando formatação apropriada como `listings` ou `verbatim`/`minted`) e expressamente citados no corpo do texto (ex.: *"conforme o script implementado no Apêndice D"*).
4. **Alinhamento com a Rubrica da Disciplina:**
   - *Fundamentação e Objetivos (Peso 1):* Modelo teórico claro, equações fundamentais e parâmetros alvo explícitos ($\tau$, $C$).
   - *Materiais e Métodos (Peso 2):* Descrição reprodutível, diagrama do circuito RC e especificações dos instrumentos.
   - *Execução e Apresentação dos Resultados (Peso 3):* Dados bem apresentados em tabelas e gráficos de alta qualidade com barras de incerteza e curvas de ajuste.
   - *Análise de Dados e Incertezas (Peso 4):* Ajustes linear e não-linear, propagação analítica por derivadas parciais, orçamentos de incerteza do osciloscópio (leitura + calibração tipo B) e algarismos significativos rigorosos.
   - *Síntese Crítica (Peso 2):* Comparação física aprofundada entre linearização e ajuste exponencial, discussão do efeito de amostragem digital (resolução de 8 bits do osciloscópio), corte da varredura no modo *Scan* e compatibilidade estatística com valores nominais.

---

## 2. Diagnóstico Físico e Tratamento dos Dados Experimentais

### A. Ensaio 1: Circuito RC de Tempo Longo — Capacitor Eletrolítico
* **Componentes:** Resistor nominal $R = (1000 \pm 50)\ \Omega$ ($5\%$ tolerância); Capacitor eletrolítico nominal $C = (1{,}0 \pm 0{,}2)\text{ mF}$ ($20\%$ tolerância).
* **Constante de tempo teórica:** $\tau_{\text{teo}} = R \times C = (1{,}00 \pm 0{,}21)\text{ s}$.
* **Tratamento dos Dados do Osciloscópio (`dados/capacitor_eletronico/F0000CH1.CSV`):**
  1. *Remoção do Blanking de Scan:* O osciloscópio TBS 1062 gravou em modo `Scan` (1,00 s/div). Ao salvar a tela a $t \approx 8\text{ s}$, gerou 250 pontos sentinela de $-10{,}24\text{ V}$ entre $t = 7{,}996\text{ s}$ e $t = 8{,}992\text{ s}$, além do resíduo da varredura anterior para $t > 8{,}992\text{ s}$. Esses pontos devem ser filtrados.
  2. *Trecho Útil de Descarga:* $t \in [6{,}976\text{ s}, 7{,}996\text{ s}]$ ($\Delta t \approx 1{,}02\text{ s}$, 255 pontos). Esse intervalo cobre $\approx 1{,}0\tau$ de decaimento ($63\%$ de queda), permitindo um ajuste preciso ($\tau_{\text{exp}} \approx 1{,}06\text{ s}$, $R^2 = 0{,}9975$).
  3. *Trecho de Carga Complementar:* $t \in [1{,}988\text{ s}, 6{,}392\text{ s}]$ ($\Delta t \approx 4{,}4\text{ s} > 4\tau$, 1100 pontos). Fornece $\tau_{\text{carga}} \approx 1{,}12\text{ s}$, servindo como excelente elemento de validação cruzada na discussão.
  4. *Correção de Nível de Referência ($V_{\infty}$):* A tensão oscila entre $-1{,}89\text{ V}$ e $+2{,}00\text{ V}$. Para linearização e ajuste, usa-se a tensão transladada:
     $$V(t) - V_{\infty} = \Delta V \, e^{-t/\tau} \implies \ln(V(t) - V_{\infty}) = \ln(\Delta V) - \frac{t}{\tau}$$

### B. Ensaio 2: Circuito RC de Tempo Curto — Capacitor Cerâmico
* **Componentes:** Resistor nominal $R = (1000 \pm 50)\ \Omega$; Capacitor cerâmico nominal $C = (1{,}0 \pm 0{,}1)\ \mu\text{F}$ ($10\%$ tolerância).
* **Constante de tempo teórica:** $\tau_{\text{teo}} = R \times C = (1{,}00 \pm 0{,}11)\text{ ms}$.
* **Tratamento dos Dados do Osciloscópio (`dados/capacitor_ceramico/F0000CH1.CSV`):**
  1. O sinal está perfeitamente periódico a $f = 99{,}98\text{ Hz}$ ($T \approx 10\text{ ms}$).
  2. Isola-se um semiciclo completo de descarga de $5\text{ ms}$ ($\approx 5\tau$, $\sim 500$ pontos, de $t = -6{,}49\text{ ms}$ a $-1{,}49\text{ ms}$).
  3. Ajuste preliminar realizado: $\tau_{\text{exp}} \approx 1{,}026\text{ ms}$ (desvio de apenas $2{,}6\%$ em relação ao nominal).

---

## 3. Planejamento Passo a Passo da Execução

```
[Etapa 1: Scripts Python]
 ├── codigos/analise_eletrolitico.py  --> Gera graficos/eletrolitico_ajustes.pdf/.png
 └── codigos/analise_ceramico.py      --> Gera graficos/ceramico_ajustes.pdf/.png

[Etapa 2: Redação LaTeX e Controle de Espaço]
 ├── Página 1: Resumo, Introdução e Objetivos
 ├── Página 2: Modelo Teórico, Suposições, Materiais e Métodos (Diagrama RC)
 ├── Página 3: Resultados Parte I (Eletrolítico: Tabelas, Gráficos Linear e Não-Linear)
 ├── Página 4: Resultados Parte II (Cerâmico: Tabelas, Gráficos Linear e Não-Linear, Síntese)
 └── Página 5: Síntese Crítica, Discussão Aprofundada e Conclusões

[Etapa 3: Apêndices]
 ├── Apêndice A: Fotos do Aparato Experimental (Bancada, Osciloscópio, Gerador)
 ├── Apêndice B: Dedução Matemática da EDO do Circuito RC
 ├── Apêndice C: Tabelas e Fórmulas de Incerteza (Tipo B, Propagação Analítica)
 └── Apêndice D e E: Códigos Python Completos e Documentados
```

---

## 4. Roteiro Detalhado do Conteúdo por Página (Corpo Principal $\le 5$ Páginas)

### **Página 1: Introdução e Fundamentação Inicial**
* **Resumo:**
  * Contexto: estudo de circuitos RC em série sob excitação de onda contínua e pulsada.
  * Metodologia: aquisição digital de dados temporais de tensão com osciloscópio Tektronix TBS 1062.
  * Resultados principais: constantes de tempo $\tau$ obtidas por ajuste linear ($\ln$) e ajuste exponencial direto para ambos os capacitores (eletrolítico de $1\text{ mF}$ e cerâmico de $1\ \mu\text{F}$), e capacitâncias experimentais correspondentes.
  * Conclusão sucinta: validação dos modelos teóricos e grau de compatibilidade estatística.
* **1. Introdução:**
  * O papel do capacitor como acumulador de energia eletrostática e sua evolução histórica (Garrafa de Leiden).
  * O comportamento transiente de circuitos resistivo-capacitivos (RC) regido pelo tempo característico $\tau = RC$.
  * Importância prática em filtros de sinal, circuitos temporizadores e acoplamentos.
* **2. Objetivos:**
  * Determinar experimentalmente as constantes de tempo $\tau$ e as capacitâncias $C$ em duas escalas temporais distintas: longa ($\sim 1\text{ s}$) e curta ($\sim 1\text{ ms}$).
  * Confrontar e avaliar comparativamente os métodos de regressão linear ponderada via linearização logarítmica e ajuste direto não-linear.
  * Investigar limitações instrumentais decorrentes da digitalização em osciloscópios digitais.

---

### **Página 2: Modelo Teórico, Suposições e Procedimento Experimental**
* **3. Modelo Teórico e Suposições:**
  * Aplicação da Lei das Malhas de Kirchhoff ao circuito em série: $\varepsilon(t) = V_R(t) + V_C(t)$.
  * Relações constitutivas: $I(t) = \frac{dq}{dt} = C \frac{dV_C}{dt}$ e $V_R(t) = R I(t)$.
  * Equação diferencial ordinária (EDO):
    $$\frac{dV_C}{dt} + \frac{1}{RC} V_C(t) = \frac{\varepsilon(t)}{RC}$$
  * Soluções analíticas para carga e descarga com nível assintótico $V_{\infty}$:
    $$V_C(t) = V_{\infty} + \Delta V \, e^{-t/\tau}$$
  * Suposições do modelo ideal:
    1. Componentes lineares e ôhmicos (resistores e capacitores ideais sem perdas dielétricas).
    2. Resistência interna dos cabos e indutâncias parasitas desprezíveis.
    3. Impedância de entrada do osciloscópio ($1\text{ M}\Omega$) ordens de grandeza superior à resistência do circuito ($1\text{ k}\Omega$), não sobrecarregando o sistema.
* **4. Materiais e Métodos:**
  * Equipamentos: Osciloscópio Digital Tektronix TBS 1062 (60 MHz, 1 GS/s), Gerador de Funções, Protoboard, Resistor de $1\text{ k}\Omega \pm 5\%$, Capacitores ($1\text{ mF}$ e $1\ \mu\text{F}$).
  * Diagrama esquemático do circuito RC montado (ilustrado de forma compacta).
  * Descrição dos procedimentos para o ensaio de tempo longo (chaveamento e varredura em 1 s/div) e tempo curto (onda quadrada de 100 Hz e varredura em 2,5 ms/div).

---

### **Página 3: Resultados e Análises — Parte I (Capacitor Eletrolítico)**
* **Tabela 1:** Especificações nominais dos componentes e valores teóricos previstos ($\tau_{\text{teo}}$, tolerâncias).
* **Tratamento dos Dados do Ensaio I:**
  * Amostra tabulada dos dados de descarga (Tabela compacta com tempo, tensão e incerteza $u_V$).
  * **Figura 1 (Gráficos lado a lado em `minipage`):**
    * *(a) Curva de Descarga e Ajuste Exponencial Direto:* Dados com barras de incerteza e curva $V(t) = V_{\infty} + \Delta V e^{-t/\tau}$.
    * *(b) Linearização Logarítmica:* Gráfico de $\ln(V(t) - V_{\infty})$ versus $t$, com a reta ajustada por MMQ ponderado.
  * Coeficientes obtidos: coeficiente angular $A \pm u_A$, constante de tempo $\tau_{\text{lin}} \pm u_\tau$ e $\tau_{\text{exp}} \pm u_\tau$.
  * Cálculo da capacitância:
    $$C_{\text{exp}} = \frac{\tau}{R}, \quad u_C = C_{\text{exp}} \sqrt{\left(\frac{u_\tau}{\tau}\right)^2 + \left(\frac{u_R}{R}\right)^2}$$
  * Compatibilidade do capacitor eletrolítico com o valor nominal.

---

### **Página 4: Resultados e Análises — Parte II (Capacitor Cerâmico) e Síntese**
* **Tratamento dos Dados do Ensaio II:**
  * Amostra tabulada de um ciclo completo de descarga ($5\text{ ms}$, $\sim 5\tau$).
  * **Figura 2 (Gráficos lado a lado em `minipage`):**
    * *(a) Queda Exponencial Direta:* Dados amostrados e curva de regressão não-linear.
    * *(b) Linearização Logarítmica:* Dispersão dos pontos transformados e reta do MMQ ponderado.
  * Coeficientes e parâmetros determinados: $\tau_{\text{lin}}$, $\tau_{\text{exp}}$ e $C_{\text{cerâmico}}$.
* **Tabela 2 (Síntese Global dos Resultados):**
  * Tabela consolidada contendo: Componente, $\tau_{\text{teórico}}$, $\tau_{\text{linear}}$, $\tau_{\text{exponencial}}$, $C_{\text{nominal}}$ e $C_{\text{estimado}}$ com as respectivas incertezas absolutas e relativas.
  * Discrepância normalizada ($Z = \frac{|\tau_{\text{exp}} - \tau_{\text{teo}}|}{\sqrt{u_{\text{exp}}^2 + u_{\text{teo}}^2}}$).

---

### **Página 5: Discussão Aprofundada (Síntese Crítica) e Conclusão**
* **6. Discussão:**
  * *Ajuste Linear vs. Ajuste Não-Linear:* Análise de por que o ajuste linear logarítmico tende a supervalorizar os pontos de menor tensão na cauda (onde as incertezas relativas do logaritmo $\frac{u_V}{V - V_{\infty}}$ crescem exponencialmente).
  * *Efeito da Digitalização do Osciloscópio:* O conversor A/D de 8 bits do osciloscópio gera discretização da tensão (degraus de $80\text{ mV}$ na escala de 2 V/div). Na linearização logarítmica, essa discretização se manifesta como "degraus horizontais" próximos ao piso de tensão.
  * *Análise do Modo Scan e Comparação Descarga vs. Carga:* Explicação do corte em $t \approx 8\text{ s}$ devido ao período de varredura do osciloscópio e confronto com a constante de tempo da curva de carga ($\tau_{\text{carga}} \approx 1{,}12\text{ s}$), demonstrando a simetria física da constante de tempo.
  * *Validação dos Componentes:* Comparação das capacitâncias obtidas com os limites de tolerância industrial (eletrolítico $\pm 20\%$, cerâmico $\pm 10\%$).
* **7. Conclusões:**
  * Resumo das conclusões experimentais: objetivos plenamente alcançados dentro do escopo de 5 páginas.
  * Validação experimental das soluções da equação diferencial do circuito RC.

---

### **Apêndices (Após a Página 5 — Sem Limite de Páginas)**
* **Referências Bibliográficas:** Halliday, Resnick & Walker (Vol. 3, Caps. 25 e 27), manuais técnicos Tektronix TBS 1000 e normas ABNT.
* **Apêndice A: Fotos do Arranjo Experimental:**
  * Inclusão das fotos reais da bancada (`foto_bancada.jpg`), do osciloscópio (`foto_osciloscopio.jpg`) e do gerador de funções (`foto_gerador_de_funcoes.jpg`).
* **Apêndice B: Dedução Matemática Detalhada:**
  * Passo a passo completo da integração da EDO de separação de variáveis para carga e descarga.
* **Apêndice C: Tratamento Completo de Incertezas:**
  * Tabelas de incerteza do osciloscópio (resolução digital tipo B, incerteza de calibração $3\% + 10\%\text{ escala} + 1\text{ mV}$).
  * Dedução algébrica das derivadas parciais para propagação em $\ln(V)$ e em $C = \tau / R$.
* **Apêndice D: Código Python — Ensaio do Capacitor Eletrolítico:**
  * Listagem integral do script `codigos/analise_eletrolitico.py`.
* **Apêndice E: Código Python — Ensaio do Capacitor Cerâmico:**
  * Listagem integral do script `codigos/analise_ceramico.py`.

---

## 5. Estratégias Rigorosas de Controle de Tamanho (Garantia de $\le 5$ Páginas)

Para assegurar que o corpo não exceda 5 páginas em hipótese alguma:
1. **Dimensionamento dos Gráficos:** Utilização obrigatória de `\begin{minipage}{0.48\textwidth}` para dispor os gráficos linear e não-linear lado a lado em uma única linha vertical por experimento.
2. **Espaçamento Controlado:** Configurar margens ABNT adequadas (`left=2cm, right=1.5cm, top=1.5cm, bottom=2cm`), entrelinhamento simples no corpo (`\singlespacing` ou `1.15`) e ajustes pontuais de `\vspace` antes e após tabelas e figuras.
3. **Quebra de Página Forçada para Apêndices:** Inserir `\clearpage` logo após a seção de Conclusões, iniciando as Referências e Apêndices a partir da página 6.
4. **Verificação de Compilação:** Inspeção minuciosa da contagem de páginas para garantir que a última linha da Conclusão termine precisamente no final da página 5.

