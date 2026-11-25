
import streamlit as st
import pandas as pd

from src.database import (
    criar_tabela,
    listar_pesagens_duplas,
    listar_pesagens_pendentes
)

from src.matching import (
    registrar_carne,
    registrar_prato_completo
)


# ==========================================
# CONFIGURACOES
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

st.subheader("Sistema inteligente de pesagem")

st.write(
    "Monitoramento da quantidade de carne nos pratos "
    "por meio de duas balanças independentes."
)

st.info(
    "A churrasqueira registra somente o peso da carne. "
    "O caixa registra o peso total do prato. "
    "O sistema relaciona as informações pela comanda."
)


# ==========================================
# MENU PRINCIPAL
# ==========================================

aba_churrasqueira, aba_caixa, aba_dashboard = st.tabs([
    "🥩 Churrasqueira",
    "⚖️ Caixa",
    "📊 Dashboard"
])


# ==========================================
# TELA 1 - CHURRASQUEIRA
# ==========================================

with aba_churrasqueira:

    st.header("🥩 Registro de carne")

    st.write(
        "Registre o peso exclusivo da carne adicionada ao prato."
    )

    st.markdown("### Como funciona")

    st.write(
        "1. Identifique a comanda.\n"
        "2. Coloque o prato na balança.\n"
        "3. Execute a tara na balança física.\n"
        "4. Adicione a carne.\n"
        "5. Registre o peso apresentado."
    )

    with st.form("form_churrasqueira"):

        comanda_carne = st.text_input(
            "Número da comanda",
            placeholder="Exemplo: 1025"
        )

        peso_carne = st.number_input(
            "Peso da carne (gramas)",
            min_value=0.0,
            value=150.0,
            step=10.0
        )

        enviar_carne = st.form_submit_button(
            "Registrar carne",
            type="primary",
            use_container_width=True
        )

    if enviar_carne:

        try:

            id_pesagem = registrar_carne(
                comanda_carne,
                peso_carne
            )

            st.success(
                f"Carne registrada! "
                f"Comanda: {comanda_carne}. "
                f"ID: {id_pesagem}"
            )

            st.info(
                "Aguardando o registro do peso total no caixa."
            )

        except ValueError as erro:

            st.error(str(erro))


    # ==========================================
    # PESAGENS AGUARDANDO CAIXA
    # ==========================================

    st.divider()

    st.subheader("⏳ Aguardando pesagem no caixa")

    pendentes = listar_pesagens_pendentes()

    if pendentes:

        df_pendentes = pd.DataFrame(
            pendentes,
            columns=[
                "ID",
                "Comanda",
                "Carne (g)",
                "Data/hora"
            ]
        )

        st.dataframe(
            df_pendentes,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Nenhuma pesagem pendente.")


# ==========================================
# TELA 2 - CAIXA
# ==========================================

with aba_caixa:

    st.header("⚖️ Registro do prato completo")

    st.write(
        "Informe a mesma comanda utilizada na churrasqueira "
        "e registre o peso total do prato."
    )

    st.markdown("### Como funciona")

    st.write(
        "1. Identifique a comanda.\n"
        "2. Coloque o prato completo na balança.\n"
        "3. Desconte a tara do prato vazio.\n"
        "4. Registre o peso líquido dos alimentos.\n"
        "5. O sistema localizará o peso da carne automaticamente."
    )

    with st.form("form_caixa"):

        comanda_caixa = st.text_input(
            "Número da comanda",
            placeholder="Exemplo: 1025"
        )

        peso_total = st.number_input(
            "Peso total do prato (gramas)",
            min_value=0.0,
            value=500.0,
            step=10.0
        )

        st.divider()

        st.subheader("💰 Custos dos alimentos")

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

        enviar_caixa = st.form_submit_button(
            "Finalizar pesagem",
            type="primary",
            use_container_width=True
        )

    if enviar_caixa:

        try:

            resultado = registrar_prato_completo(
                comanda_caixa,
                peso_total,
                custo_carne_kg,
                custo_outros_kg
            )

            st.success(
                f"Comanda {resultado['comanda']} finalizada!"
            )

            st.subheader("📊 Composição do prato")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Peso da carne",
                f"{resultado['peso_carne']:.0f} g"
            )

            col2.metric(
                "Outros alimentos",
                f"{resultado['peso_outros']:.0f} g"
            )

            col3.metric(
                "Peso total",
                f"{resultado['peso_total']:.0f} g"
            )

            st.write("**Participação dos alimentos**")

            col1, col2 = st.columns(2)

            col1.metric(
                "Carne",
                f"{resultado['percentual_carne']:.1f}%"
            )

            col2.metric(
                "Outros alimentos",
                f"{resultado['percentual_outros']:.1f}%"
            )

            st.progress(
                resultado["percentual_carne"] / 100
            )

            st.divider()

            st.subheader("💰 Custos estimados")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Custo da carne",
                f"R$ {resultado['custo_carne']:.2f}"
            )

            col2.metric(
                "Custo dos outros",
                f"R$ {resultado['custo_outros']:.2f}"
            )

            col3.metric(
                "Custo total",
                f"R$ {resultado['custo_total']:.2f}"
            )

        except ValueError as erro:

            st.error(str(erro))


# ==========================================
# TELA 3 - DASHBOARD
# ==========================================

with aba_dashboard:

    st.header("📊 Dashboard administrativo")

    registros = listar_pesagens_duplas()

    if registros:

        dados = []

        for registro in registros:

            dados.append({
                "ID": registro[0],
                "Comanda": registro[1],
                "Carne (g)": registro[2],
                "Outros (g)": registro[3],
                "Total (g)": registro[4],
                "Carne (%)": registro[5],
                "Custo carne (R$)": registro[6],
                "Custo outros (R$)": registro[7],
                "Custo total (R$)": registro[8],
                "Data churrasqueira": registro[9],
                "Data caixa": registro[10]
            })

        df = pd.DataFrame(dados)

        st.subheader("📋 Histórico de pesagens")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # ==========================================
        # INDICADORES
        # ==========================================

        st.divider()

        st.subheader("📈 Indicadores gerais")

        quantidade = len(df)

        peso_medio = df["Total (g)"].mean()

        carne_media = df["Carne (g)"].mean()

        percentual_medio = df["Carne (%)"].mean()

        custo_acumulado = df["Custo total (R$)"].sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Pratos analisados",
            quantidade
        )

        col2.metric(
            "Peso médio",
            f"{peso_medio:.1f} g"
        )

        col3.metric(
            "Média de carne",
            f"{carne_media:.1f} g"
        )

        col4.metric(
            "Percentual médio de carne",
            f"{percentual_medio:.1f}%"
        )

        st.metric(
            "Custo estimado acumulado",
            f"R$ {custo_acumulado:.2f}"
        )


        # ==========================================
        # GRAFICOS
        # ==========================================

        st.divider()

        st.subheader("🥩 Participação da carne por comanda")

        grafico_carne = df.set_index("Comanda")[
            ["Carne (%)"]
        ]

        st.bar_chart(grafico_carne)

        st.subheader("💰 Comparação de custos")

        grafico_custos = df.set_index("Comanda")[
            [
                "Custo carne (R$)",
                "Custo outros (R$)"
            ]
        ]

        st.bar_chart(grafico_custos)

        st.subheader("📉 Custo estimado por prato")

        grafico_total = df.set_index("Comanda")[
            ["Custo total (R$)"]
        ]

        st.line_chart(grafico_total)

    else:

        st.info(
            "Ainda não existem pratos concluídos. "
            "Registre uma pesagem na churrasqueira e depois "
            "finalize a mesma comanda no caixa."
        )
