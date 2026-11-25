
import streamlit as st
import pandas as pd

from src.calculations import calcular_pesagem, calcular_custos
from src.database import criar_tabela, salvar_pesagem, listar_pesagens


# ==========================================
# CONFIGURACOES INICIAIS
# ==========================================

st.set_page_config(
    page_title="Bovinu's Smart Weigh",
    page_icon="🥩",
    layout="wide"
)

criar_tabela()


# ==========================================
# CABECALHO
# ==========================================

st.title("🥩 Bovinu's Smart Weigh")

st.subheader("Balança inteligente na churrasqueira")

st.write(
    "Identifique automaticamente o peso das carnes adicionadas "
    "ao prato e acompanhe sua composição e seus custos estimados."
)

st.info(
    "simulação da leitura da balança. "
    "Os pesos são informados manualmente para representar "
    "a operação que futuramente será automatizada."
)

st.divider()


# ==========================================
# SIMULACAO DA BALANCA
# ==========================================

st.header("⚖️ Pesagem na churrasqueira")

st.write(
    "Informe o peso do prato antes e depois da adição das carnes."
)

col1, col2 = st.columns(2)

with col1:
    peso_inicial = st.number_input(
        "Peso inicial do prato (gramas)",
        min_value=0.0,
        value=300.0,
        step=10.0,
        help="Peso dos alimentos servidos antes de chegar à churrasqueira."
    )

with col2:
    peso_final = st.number_input(
        "Peso final do prato (gramas)",
        min_value=0.0,
        value=500.0,
        step=10.0,
        help="Peso do prato depois que as carnes foram adicionadas."
    )


# ==========================================
# CALCULO DO PESO DA CARNE
# ==========================================

peso_outros = peso_inicial
peso_carne = peso_final - peso_inicial

st.divider()

st.subheader("📊 Resultado da captura")

if peso_final < peso_inicial:

    st.error(
        "O peso final não pode ser menor que o peso inicial. "
        "Verifique os valores informados."
    )

elif peso_final == peso_inicial:

    st.warning(
        "Nenhum peso adicional foi identificado. "
        "Informe o peso depois de adicionar as carnes."
    )

else:

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Outros alimentos",
        f"{peso_outros:.0f} g"
    )

    col2.metric(
        "Carne identificada",
        f"{peso_carne:.0f} g"
    )

    col3.metric(
        "Peso total do prato",
        f"{peso_final:.0f} g"
    )

    percentual_carne = (
        peso_carne / peso_final
    ) * 100

    st.write("**Composição do prato**")

    st.progress(
        min(max(percentual_carne / 100, 0.0), 1.0)
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Participação da carne",
        f"{percentual_carne:.1f}%"
    )

    col2.metric(
        "Participação dos outros alimentos",
        f"{100 - percentual_carne:.1f}%"
    )


    # ==========================================
    # CUSTOS DOS ALIMENTOS
    # ==========================================

    st.divider()

    st.header("💰 Estimativa de custos")

    col1, col2 = st.columns(2)

    with col1:
        custo_carne_kg = st.number_input(
            "Custo da carne por kg (R$)",
            min_value=0.0,
            value=40.0,
            step=1.0
        )

    with col2:
        custo_outros_kg = st.number_input(
            "Custo dos outros alimentos por kg (R$)",
            min_value=0.0,
            value=12.0,
            step=1.0
        )


    # ==========================================
    # IDENTIFICACAO OPCIONAL DO CORTE
    # ==========================================

    st.subheader("🥩 Identificação da carne")

    tipo_corte = st.selectbox(
        "Tipo de corte servido",
        [
            "Não identificado",
            "Picanha",
            "Alcatra",
            "Fraldinha",
            "Contra-filé",
            "Maminha",
            "Costela",
            "Outros"
        ]
    )

    st.caption(
        "A identificação do corte é opcional nesta versão. "
        "O custo ainda utiliza o valor médio por kg informado acima."
    )


    # ==========================================
    # CALCULAR E SALVAR PESAGEM
    # ==========================================

    if st.button(
        "Registrar pesagem",
        type="primary",
        use_container_width=True
    ):

        resultado = calcular_pesagem(
            peso_carne,
            peso_outros
        )

        custos = calcular_custos(
            peso_carne,
            peso_outros,
            custo_carne_kg,
            custo_outros_kg
        )

        peso_total = resultado["peso_total"]
        percentual_carne = resultado["percentual_carne"]

        custo_carne = custos["custo_carne"]
        custo_outros = custos["custo_outros"]
        custo_total = custos["custo_total"]

        id_pesagem = salvar_pesagem(
            peso_carne,
            peso_outros,
            peso_total,
            percentual_carne,
            custo_carne,
            custo_outros,
            custo_total
        )

        st.success(
            f"Pesagem registrada com sucesso! ID: {id_pesagem}"
        )

        st.subheader("Resumo da pesagem registrada")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Peso da carne",
            f"{peso_carne:.0f} g"
        )

        col2.metric(
            "Percentual de carne",
            f"{percentual_carne:.1f}%"
        )

        col3.metric(
            "Custo estimado total",
            f"R$ {custo_total:.2f}"
        )

        st.write("**Detalhamento dos custos**")

        col1, col2 = st.columns(2)

        col1.metric(
            "Custo da carne",
            f"R$ {custo_carne:.2f}"
        )

        col2.metric(
            "Custo dos outros alimentos",
            f"R$ {custo_outros:.2f}"
        )


# ==========================================
# HISTORICO DE PESAGENS
# ==========================================

st.divider()

st.header("📋 Histórico de pesagens")

registros = listar_pesagens()

if registros:

    dados = []

    for registro in registros:

        dados.append({
            "ID": registro[0],
            "Carne (g)": registro[1],
            "Outros (g)": registro[2],
            "Total (g)": registro[3],
            "Carne (%)": registro[4],
            "Custo carne (R$)": registro[5],
            "Custo outros (R$)": registro[6],
            "Custo total (R$)": registro[7],
            "Data/hora": registro[8]
        })

    df = pd.DataFrame(dados)

    df["ID"] = pd.to_numeric(df["ID"])

    df = df.sort_values(
        by="ID",
        ascending=True
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # ==========================================
    # INDICADORES GERAIS
    # ==========================================

    st.divider()

    st.header("📈 Indicadores gerais")

    quantidade_pesagens = len(df)

    peso_medio = df["Total (g)"].mean()

    percentual_medio = df["Carne (%)"].mean()

    carne_media = df["Carne (g)"].mean()

    custo_acumulado = df["Custo total (R$)"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total de pesagens",
        quantidade_pesagens
    )

    col2.metric(
        "Peso médio por prato",
        f"{peso_medio:.1f} g"
    )

    col3.metric(
        "Média de carne",
        f"{percentual_medio:.1f}%"
    )

    col4.metric(
        "Custo estimado acumulado",
        f"R$ {custo_acumulado:.2f}"
    )

    st.metric(
        "Quantidade média de carne por prato",
        f"{carne_media:.1f} g"
    )


    # ==========================================
    # DASHBOARD ANALITICO
    # ==========================================

    st.divider()

    st.header("📊 Dashboard analítico")

    st.subheader("Participação da carne por prato")

    grafico_carne = df.set_index("ID")[
        ["Carne (%)"]
    ]

    st.bar_chart(grafico_carne)

    st.subheader("Comparação dos custos por prato")

    grafico_custos = df.set_index("ID")[
        [
            "Custo carne (R$)",
            "Custo outros (R$)"
        ]
    ]

    st.bar_chart(grafico_custos)

    st.subheader("Custo estimado por pesagem")

    grafico_total = df.set_index("ID")[
        ["Custo total (R$)"]
    ]

    st.line_chart(grafico_total)


else:

    st.info(
        "Ainda não existem pesagens registradas. "
        "Realize uma pesagem para construir seu histórico."
    )
