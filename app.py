
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

# Estados da pesagem
if "etapa_pesagem" not in st.session_state:
    st.session_state.etapa_pesagem = 1

if "peso_outros" not in st.session_state:
    st.session_state.peso_outros = 0.0

if "ultima_pesagem" not in st.session_state:
    st.session_state.ultima_pesagem = None


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
    "Simulação da leitura da balança. Os pesos são informados "
    "manualmente para representar a operação que futuramente "
    "será automatizada."
)

st.divider()


# ==========================================
# RESULTADO DA ULTIMA PESAGEM
# ==========================================

if st.session_state.ultima_pesagem is not None:

    ultima = st.session_state.ultima_pesagem

    st.success(
        f"Pesagem registrada com sucesso! ID: {ultima['id']}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Peso da carne", f"{ultima['carne']:.0f} g")
    col2.metric("Participação da carne", f"{ultima['percentual']:.1f}%")
    col3.metric("Custo estimado", f"R$ {ultima['custo']:.2f}")

    st.divider()


# ==========================================
# SIMULACAO DA BALANCA
# ==========================================

st.header("⚖️ Pesagem na churrasqueira")

st.write(
    "Realize a pesagem em duas etapas: primeiro os alimentos "
    "sem carne e depois a carne, utilizando a função TARA."
)


# ==========================================
# ETAPA 1 - PESO INICIAL
# ==========================================

if st.session_state.etapa_pesagem == 1:

    st.subheader("1️⃣ Pesagem inicial — Prato com alimentos")

    st.write(
        "Coloque o prato com arroz, feijão, salada e outros "
        "alimentos na balança, sem adicionar a carne."
    )

    peso_inicial = st.number_input(
        "Peso dos alimentos antes da carne (gramas)",
        min_value=0.0,
        value=300.0,
        step=10.0,
        key="input_peso_inicial"
    )

    if st.button(
        "Registrar peso inicial",
        type="primary",
        use_container_width=True
    ):

        if peso_inicial <= 0:
            st.error("Informe um peso inicial maior que zero.")

        else:
            st.session_state.peso_outros = peso_inicial
            st.session_state.etapa_pesagem = 2
            st.rerun()


# ==========================================
# ETAPA 2 - TARA
# ==========================================

elif st.session_state.etapa_pesagem == 2:

    st.subheader("2️⃣ Tara — Zerar a balança")

    col1, col2 = st.columns(2)

    col1.metric(
        "Peso registrado anteriormente",
        f"{st.session_state.peso_outros:.0f} g"
    )

    col2.metric(
        "Leitura após a tara",
        "0 g"
    )

    st.info(
        "O peso inicial já foi armazenado. Agora, simule o botão "
        "TARA da balança para zerar a leitura antes de adicionar "
        "a carne."
    )

    if st.button(
        "⚖️ TARAR BALANÇA",
        type="primary",
        use_container_width=True
    ):

        st.session_state.etapa_pesagem = 3
        st.rerun()


# ==========================================
# ETAPA 3 - PESO DA CARNE
# ==========================================

elif st.session_state.etapa_pesagem == 3:

    st.subheader("3️⃣ Pesagem da carne")

    st.success(
        "Balança zerada! Adicione a carne ao prato."
    )

    st.metric(
        "Leitura da balança após a tara",
        "0 g"
    )

    peso_carne = st.number_input(
        "Peso da carne adicionada (gramas)",
        min_value=0.0,
        value=150.0,
        step=10.0,
        key="input_peso_carne"
    )

    st.divider()

    st.subheader("📊 Resultado da captura")

    peso_outros = st.session_state.peso_outros

    peso_total = peso_outros + peso_carne

    if peso_carne > 0:

        percentual_carne = (peso_carne / peso_total) * 100

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
            f"{peso_total:.0f} g"
        )

        st.write("**Composição do prato**")

        st.progress(percentual_carne / 100)

        col1, col2 = st.columns(2)

        col1.metric(
            "Participação da carne",
            f"{percentual_carne:.1f}%"
        )

        col2.metric(
            "Participação dos outros alimentos",
            f"{100 - percentual_carne:.1f}%"
        )

    else:

        st.warning(
            "Adicione a carne e informe seu peso para visualizar "
            "a composição do prato."
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
    # IDENTIFICACAO DO CORTE
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
        "A identificação do corte é opcional. O custo utiliza "
        "o valor médio por kg informado acima."
    )


    # ==========================================
    # REGISTRAR PESAGEM
    # ==========================================

    if st.button(
        "Registrar pesagem",
        type="primary",
        use_container_width=True
    ):

        if peso_carne <= 0:

            st.error("Informe um peso de carne maior que zero.")

        else:

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

            st.session_state.ultima_pesagem = {
                "id": id_pesagem,
                "carne": peso_carne,
                "percentual": percentual_carne,
                "custo": custo_total
            }

            # Reinicia o processo para o próximo prato
            st.session_state.etapa_pesagem = 1
            st.session_state.peso_outros = 0.0

            st.rerun()


    # ==========================================
    # CANCELAR PESAGEM
    # ==========================================

    if st.button(
        "Cancelar e iniciar novamente",
        use_container_width=True
    ):

        st.session_state.etapa_pesagem = 1
        st.session_state.peso_outros = 0.0

        st.rerun()


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
