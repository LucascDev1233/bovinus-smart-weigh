
# Bovinu's Smart Weigh

Sistema de pesagem inteligente desenvolvido para o Hackathon.

## Sobre o projeto

O Bovinu's Smart Weigh busca solucionar a falta de visibilidade sobre a quantidade de carne consumida pelos clientes durante o almoço por quilo.

A proposta é separar a medição das carnes dos demais alimentos do buffet, utilizando uma balança inteligente integrada à estação da churrasqueira.

## Problema identificado

Atualmente, o restaurante consegue identificar o peso total do prato, mas não sabe exatamente quanto desse peso corresponde às carnes.

Isso dificulta o acompanhamento do consumo e dos custos dos alimentos.

## Solução proposta

O sistema registra:

- Peso dos alimentos servidos antes da churrasqueira;
- Peso da carne adicionada;
- Percentual de carne no prato;
- Identificação dos diferentes cortes;
- Estimativa de custos;
- Histórico de pesagens;
- Indicadores e gráficos para análise.

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- SQLite

## Como executar

1. Clone este repositório.
2. Crie um ambiente virtual.
3. Instale as dependências:

   pip install -r requirements.txt

4. Execute:

   streamlit run app.py

## Status do projeto

MVP em desenvolvimento. A versão atual simula as leituras da balança por meio de entradas manuais.
