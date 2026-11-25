
import streamlit as st
import pandas as pd

from datetime import date

from src.database import (
    criar_tabela,
    listar_pesagens_duplas,
    listar_pesagens_pendentes,
    criar_controle_buffet,
    adicionar_reposicao_buffet,
    listar_controles_buffet,
    listar_reposicoes_buffet,
    finalizar_controle_buffet
)

from src.matching import (
    registrar_carne,
    registrar_prato_completo
)

from src.calculations import calcular_buffet


# ==========================================
# CONFIGURACAO
# ==========================================

st.set_page_config(
    page_title="Bovinu's Smart Weigh",
    page_icon="🥩",
    layout="wide"
)

criar_tabela()

st.title("🥩 Bovinu's Smart Weigh")

st.caption(
    "Sistema de controle de pesagem, composição dos pratos "
    "e desperdício do buffet."
)


# ==========================================
# ABAS DO SISTEMA
# ==========================================

aba_churrasqueira, aba_caixa, aba_dashboard, aba_buffet = st.tabs([
    "🥩 Churrasqueira",
    "⚖️ Caixa",
    "📊 Dashboard",
    "🥗 Buffet"
])


# ==========================================
# ABA 1 - CHURRASQUEIRA
# ==========================================

with aba_churrasqueira:

    st.header("Registro de carne")

    st.write(
        "Registre o peso da carne adicionada ao prato. "
        "Utilize o número da comanda para relacionar "
        "essa pesagem com a pesagem total realizada no caixa."
    )

    with st.form("form_churrasqueira"):

        comanda_carne = st.text_input(
            "Número da comanda",
            placeholder="Exemplo: 1025"
        )

        peso_carne = st.number_input(
            "Peso da carne (gramas)",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        enviar_carne = st.form_submit_button(
            "Registrar carne",
            type="primary",
            use_container_width=True
        )

    if enviar_carne:

        try:

            id_registro = registrar_carne(
                comanda_carne,
                peso_carne
            )

            st.success(
                f"Carne registrada! Código do registro: {id_registro}"
            )

            st.info(
                f"Comanda {comanda_carne}: "
                f"{peso_carne:.1f} g de carne aguardando pesagem no caixa."
            )

        except ValueError as erro:

            st.error(str(erro))

    st.divider()

    st.subheader("Pesagens aguardando o caixa")

    pendentes = listar_pesagens_pendentes()

    if pendentes:

        df_pendentes = pd.DataFrame([
            {
                "Comanda": item["comanda"],
                "Peso da carne (g)": item["peso_carne"],
                "Registro": item["data_churrasqueira"]
            }
            for item in pendentes
        ])

        st.dataframe(
            df_pendentes,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Nenhuma pesagem aguardando o caixa.")


# ==========================================
# ABA 2 - CAIXA
# ==========================================

with aba_caixa:

    st.header("Registro do peso total")

    st.write(
        "Informe a mesma comanda utilizada na churrasqueira "
        "e registre o peso total líquido do prato, "
        "com a tara do prato já descontada."
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

        st.subheader("Custos estimados")

        custo_carne_kg = st.number_input(
            "Custo da carne por kg (R$)",
            min_value=0.0,
            value=20.0,
            step=1.0
        )

        custo_outros_kg = st.number_input(
            "Custo dos outros alimentos por kg (R$)",
            min_value=0.0,
            value=8.0,
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

            st.success("Pesagem finalizada com sucesso!")

            st.divider()

            st.subheader("Resultado do prato")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Peso total",
                f"{resultado['peso_total']:.1f} g"
            )

            col2.metric(
                "Peso da carne",
                f"{resultado['peso_carne']:.1f} g"
            )

            col3.metric(
                "Outros alimentos",
                f"{resultado['peso_outros']:.1f} g"
            )

            st.metric(
                "Participação da carne",
                f"{resultado['percentual_carne']:.1f}%"
            )

            st.divider()

            st.subheader("Estimativa de custos")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Custo da carne",
                f"R$ {resultado['custo_carne']:.2f}"
            )

            col2.metric(
                "Custo dos outros alimentos",
                f"R$ {resultado['custo_outros']:.2f}"
            )

            col3.metric(
                "Custo total estimado",
                f"R$ {resultado['custo_total']:.2f}"
            )

        except ValueError as erro:

            st.error(str(erro))


# ==========================================
# ABA 3 - DASHBOARD
# ==========================================

with aba_dashboard:

    st.header("Dashboard operacional")

    registros = listar_pesagens_duplas()

    if registros:

        df = pd.DataFrame(registros)

        total_pratos = len(df)

        peso_total_kg = df["peso_total"].sum() / 1000
        peso_carne_kg = df["peso_carne"].sum() / 1000
        peso_outros_kg = df["peso_outros"].sum() / 1000

        percentual_medio_carne = (
            peso_carne_kg / peso_total_kg * 100
            if peso_total_kg > 0 else 0
        )

        custo_total = df["custo_total"].sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Pratos registrados",
            total_pratos
        )

        col2.metric(
            "Peso total",
            f"{peso_total_kg:.2f} kg"
        )

        col3.metric(
            "Carne utilizada",
            f"{peso_carne_kg:.2f} kg"
        )

        col4.metric(
            "Participação da carne",
            f"{percentual_medio_carne:.1f}%"
        )

        st.metric(
            "Custo estimado total",
            f"R$ {custo_total:.2f}"
        )

        st.divider()

        st.subheader("Composição dos pratos")

        df_composicao = pd.DataFrame({
            "Categoria": ["Carne", "Outros alimentos"],
            "Peso (kg)": [peso_carne_kg, peso_outros_kg]
        })

        st.bar_chart(
            df_composicao.set_index("Categoria")
        )

        st.divider()

        st.subheader("Histórico de pesagens")

        colunas_historico = [
            "id",
            "comanda",
            "peso_carne",
            "peso_outros",
            "peso_total",
            "percentual_carne",
            "custo_carne",
            "custo_outros",
            "custo_total",
            "data_caixa"
        ]

        df_historico = df[colunas_historico].copy()

        df_historico.columns = [
            "ID",
            "Comanda",
            "Carne (g)",
            "Outros alimentos (g)",
            "Total (g)",
            "Carne (%)",
            "Custo carne (R$)",
            "Custo outros (R$)",
            "Custo total (R$)",
            "Data/hora"
        ]

        st.dataframe(
            df_historico,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Ainda não existem pesagens concluídas "
            "para apresentar no Dashboard."
        )


# ==========================================
# ABA 4 - BUFFET
# ==========================================

with aba_buffet:

    st.header("🥗 Controle diário do buffet")

    st.write(
        "Registre os alimentos colocados no buffet, "
        "as reposições realizadas e o resultado no fechamento."
    )

    data_buffet = st.date_input(
        "Data de operação",
        value=date.today(),
        key="data_buffet"
    )

    data_texto = data_buffet.isoformat()

    st.divider()

    # ------------------------------------------
    # ABERTURA
    # ------------------------------------------

    st.subheader("1. Abertura do buffet")

    with st.form("form_abertura_buffet"):

        alimento = st.text_input(
            "Nome do alimento",
            placeholder="Exemplo: Arroz"
        )

        peso_inicial = st.number_input(
            "Quantidade inicial (kg)",
            min_value=0.0,
            value=5.0,
            step=0.5
        )

        cadastrar_alimento = st.form_submit_button(
            "Cadastrar alimento",
            type="primary",
            use_container_width=True
        )

    if cadastrar_alimento:

        try:

            criar_controle_buffet(
                data_texto,
                alimento,
                peso_inicial
            )

            st.success(
                f"{alimento} cadastrado no buffet!"
            )

            st.rerun()

        except ValueError as erro:

            st.error(str(erro))

    registros_buffet = listar_controles_buffet(data_texto)

    abertos = [
        registro for registro in registros_buffet
        if registro["status"] == "aberto"
    ]

    fechados = [
        registro for registro in registros_buffet
        if registro["status"] == "fechado"
    ]

    # ------------------------------------------
    # REPOSICOES
    # ------------------------------------------

    st.divider()

    st.subheader("2. Registrar reposições")

    if abertos:

        opcoes_reposicao = {
            f"{registro['alimento']} — Controle #{registro['id']}":
                registro["id"]
            for registro in abertos
        }

        with st.form("form_reposicao_buffet"):

            alimento_reposicao = st.selectbox(
                "Selecione o alimento",
                list(opcoes_reposicao.keys())
            )

            quantidade_reposicao = st.number_input(
                "Quantidade reposta (kg)",
                min_value=0.0,
                value=1.0,
                step=0.5
            )

            registrar_reposicao = st.form_submit_button(
                "Registrar reposição",
                use_container_width=True
            )

        if registrar_reposicao:

            try:

                adicionar_reposicao_buffet(
                    opcoes_reposicao[alimento_reposicao],
                    quantidade_reposicao
                )

                st.success("Reposição registrada!")

                st.rerun()

            except ValueError as erro:

                st.error(str(erro))

    else:

        st.info(
            "Não existem alimentos abertos para receber reposições."
        )

    # ------------------------------------------
    # FECHAMENTO
    # ------------------------------------------

    st.divider()

    st.subheader("3. Fechamento do buffet")

    if abertos:

        opcoes_fechamento = {
            f"{registro['alimento']} — Controle #{registro['id']}":
                registro["id"]
            for registro in abertos
        }

        with st.form("form_fechamento_buffet"):

            alimento_fechamento = st.selectbox(
                "Selecione o alimento para finalizar",
                list(opcoes_fechamento.keys())
            )

            sobra_aproveitavel = st.number_input(
                "Sobra aproveitável (kg)",
                min_value=0.0,
                value=0.0,
                step=0.5
            )

            descarte = st.number_input(
                "Quantidade descartada (kg)",
                min_value=0.0,
                value=0.0,
                step=0.5
            )

            fechar_alimento = st.form_submit_button(
                "Finalizar alimento",
                type="primary",
                use_container_width=True
            )

        if fechar_alimento:

            try:

                finalizar_controle_buffet(
                    opcoes_fechamento[alimento_fechamento],
                    sobra_aproveitavel,
                    descarte
                )

                st.success(
                    "Controle do alimento finalizado!"
                )

                st.rerun()

            except ValueError as erro:

                st.error(str(erro))

    else:

        st.info(
            "Todos os alimentos cadastrados já foram finalizados "
            "ou ainda não existem alimentos para fechar."
        )

    # ------------------------------------------
    # HISTORICO E RELATORIO
    # ------------------------------------------

    st.divider()

    st.subheader("4. Histórico e relatório do buffet")

    if registros_buffet:

        dados_relatorio = []

        for registro in registros_buffet:

            id_controle = registro["id"]
            nome = registro["alimento"]
            inicial = registro["peso_inicial"]
            total_reposicoes = registro["total_reposicoes"]
            sobra = registro["sobra_aproveitavel"]
            descarte_atual = registro["descarte"]
            status = registro["status"]

            disponivel = inicial + total_reposicoes

            if status == "fechado":

                resultado = calcular_buffet(
                    inicial,
                    total_reposicoes,
                    sobra,
                    descarte_atual
                )

                consumido = resultado["consumido"]
                percentual = resultado["percentual_desperdicio"]

            else:

                consumido = None
                percentual = None

            dados_relatorio.append({
                "ID": id_controle,
                "Alimento": nome,
                "Inicial (kg)": inicial,
                "Reposições (kg)": total_reposicoes,
                "Disponível (kg)": disponivel,
                "Consumo estimado (kg)": consumido,
                "Sobra aproveitável (kg)": sobra,
                "Descarte (kg)": descarte_atual,
                "Desperdício (%)": percentual,
                "Status": status
            })

        df_buffet = pd.DataFrame(dados_relatorio)

        st.dataframe(
            df_buffet,
            use_container_width=True,
            hide_index=True
        )

        # Histórico individual de reposições.

        st.subheader("Histórico individual de reposições")

        for registro in registros_buffet:

            with st.expander(
                f"{registro['alimento']} — Controle #{registro['id']}"
            ):

                historico_reposicoes = listar_reposicoes_buffet(
                    registro["id"]
                )

                if historico_reposicoes:

                    df_reposicoes = pd.DataFrame([
                        {
                            "Quantidade (kg)": item["quantidade"],
                            "Data/hora": item["data_hora"]
                        }
                        for item in historico_reposicoes
                    ])

                    st.dataframe(
                        df_reposicoes,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.write("Nenhuma reposição registrada.")

        # Indicadores somente dos alimentos fechados.

        if fechados:

            df_fechados = df_buffet[
                df_buffet["Status"] == "fechado"
            ]

            total_disponivel = df_fechados[
                "Disponível (kg)"
            ].sum()

            total_consumido = df_fechados[
                "Consumo estimado (kg)"
            ].sum()

            total_descarte = df_fechados[
                "Descarte (kg)"
            ].sum()

            total_sobra = df_fechados[
                "Sobra aproveitável (kg)"
            ].sum()

            percentual_geral = (
                total_descarte / total_disponivel * 100
                if total_disponivel > 0 else 0
            )

            st.divider()

            st.subheader("Indicadores do buffet")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Disponibilizado",
                f"{total_disponivel:.2f} kg"
            )

            col2.metric(
                "Consumo estimado",
                f"{total_consumido:.2f} kg"
            )

            col3.metric(
                "Descarte",
                f"{total_descarte:.2f} kg"
            )

            col4.metric(
                "Sobra aproveitável",
                f"{total_sobra:.2f} kg"
            )

            st.metric(
                "Percentual de desperdício",
                f"{percentual_geral:.2f}%"
            )

            st.subheader("Consumo e desperdício por alimento")

            grafico_buffet = df_fechados.set_index("Alimento")[
                [
                    "Consumo estimado (kg)",
                    "Sobra aproveitável (kg)",
                    "Descarte (kg)"
                ]
            ]

            st.bar_chart(grafico_buffet)

    else:

        st.info(
            "Nenhum alimento cadastrado para essa data."
        )
