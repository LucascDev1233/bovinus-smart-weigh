
# Desenvolvimento do Bovinu's Smart Weigh

## 1. Identificação do problema

Durante a análise da operação do Bovinu's Grill & Beer,
identificamos a dificuldade de visualizar a composição
dos pratos servidos no buffet por quilo.

O peso total é conhecido, mas a participação individual
das carnes e dos demais alimentos não é necessariamente
identificada.

## 2. Ideação da solução

A equipe propôs desenvolver um sistema capaz de registrar
separadamente os pesos das carnes e dos demais alimentos.

A proposta busca transformar esses registros em
informações úteis para análise gerencial.

## 3. Planejamento

Foram definidas as seguintes funcionalidades:

- Registro de pesagem.
- Separação entre carnes e outros alimentos.
- Cálculo do peso total.
- Cálculo do percentual de carne.
- Estimativa de custos.
- Controle diário do buffet.
- Histórico de registros.
- Dashboard operacional.

## 4. Implementação

O sistema foi desenvolvido utilizando Python e Streamlit.

O SQLite foi utilizado para armazenar os registros,
enquanto as funções de cálculo e processamento foram
organizadas em módulos separados.

## 5. Testes e validação

Foram realizadas simulações com diferentes pesos e
composições de pratos para verificar os resultados.

Exemplo:
- Peso da carne: 250 g.
- Peso dos demais alimentos: 250 g.
- Peso total: 500 g.
- Participação da carne: 50%.

Os resultados foram utilizados para conferir
o funcionamento dos cálculos.

## 6. Publicação

O código-fonte foi disponibilizado no GitHub e a
aplicação foi publicada por meio do Streamlit Cloud,
permitindo acessar a demonstração pela internet.
