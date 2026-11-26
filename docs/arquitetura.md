
# 🏗️ Arquitetura do Bovinu's Smart Weigh

## 1. Visão geral

O Bovinu's Smart Weigh foi desenvolvido como uma
aplicação web para auxiliar o gerenciamento da
composição dos pratos e o controle operacional
do buffet no Bovinu's Grill & Beer — Unidade Augusta.

A arquitetura foi organizada para permitir o registro,
processamento, armazenamento e visualização dos dados
por meio de uma interface acessível pelo navegador.

## 2. Tecnologias utilizadas

| Tecnologia | Responsabilidade |
|---|---|
| Python | Lógica e processamento do sistema |
| Streamlit | Interface web e interação com o usuário |
| SQLite | Armazenamento dos registros |
| Pandas | Manipulação e análise de dados |
| Git | Controle de versões |
| GitHub | Hospedagem do código-fonte |
| Streamlit Cloud | Publicação da aplicação |

## 3. Organização dos componentes

A aplicação é dividida em componentes responsáveis
por diferentes funções:

- Interface: apresenta as telas e recebe informações.
- Processamento: realiza cálculos e regras de negócio.
- Banco de dados: armazena os registros.
- Dashboard: apresenta indicadores e resultados.

## 4. Fluxo de funcionamento

1. O usuário acessa a aplicação pelo navegador.
2. A interface recebe os dados informados.
3. O sistema processa os pesos e realiza os cálculos.
4. Os registros são armazenados no banco de dados.
5. Os dados são consultados e apresentados no dashboard.

## 5. Banco de dados

O SQLite é utilizado para armazenar os registros
da aplicação.

A estrutura permite manter informações utilizadas
pelas funcionalidades de pesagem e controle do buffet.

## 6. Hospedagem e publicação

O código-fonte é mantido no GitHub.

A aplicação é publicada pelo Streamlit Cloud,
permitindo seu acesso por meio de um endereço web.

## 7. Diagrama da arquitetura

Usuário
   ↓
Interface Streamlit
   ↓
Lógica de processamento Python
   ↓
Banco de dados SQLite
   ↓
Consulta e visualização dos indicadores
