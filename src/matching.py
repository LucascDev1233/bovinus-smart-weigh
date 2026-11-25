
from src.database import (
    salvar_peso_carne,
    buscar_pesagem_pendente,
    finalizar_pesagem
)

from src.calculations import (
    calcular_pesagem,
    calcular_custos
)


# ==========================================
# REGISTRO DA CHURRASQUEIRA
# ==========================================

def registrar_carne(comanda, peso_carne):

    comanda = str(comanda).strip()

    if not comanda:
        raise ValueError("Informe o número da comanda.")

    if peso_carne <= 0:
        raise ValueError("O peso da carne deve ser maior que zero.")

    return salvar_peso_carne(
        comanda,
        peso_carne
    )


# ==========================================
# REGISTRO DO CAIXA
# ==========================================

def registrar_prato_completo(
    comanda,
    peso_total,
    custo_carne_kg,
    custo_outros_kg
):

    comanda = str(comanda).strip()

    if not comanda:
        raise ValueError("Informe o número da comanda.")

    if peso_total <= 0:
        raise ValueError("O peso total deve ser maior que zero.")

    if custo_carne_kg < 0 or custo_outros_kg < 0:
        raise ValueError("Os custos não podem ser negativos.")

    # Localiza o peso registrado na churrasqueira.
    registro = buscar_pesagem_pendente(comanda)

    if registro is None:

        raise ValueError(
            "Nenhuma pesagem pendente encontrada para essa comanda."
        )

    id_pesagem = registro[0]
    peso_carne = registro[2]

    # Calcula a composição do prato.
    resultado = calcular_pesagem(
        peso_carne,
        peso_total
    )

    peso_outros = resultado["peso_outros"]

    percentual_carne = resultado["percentual_carne"]

    # Calcula os custos.
    custos = calcular_custos(
        peso_carne,
        peso_outros,
        custo_carne_kg,
        custo_outros_kg
    )

    # Finaliza o registro no banco.
    finalizar_pesagem(
        id_pesagem,
        peso_total,
        peso_outros,
        percentual_carne,
        custos["custo_carne"],
        custos["custo_outros"],
        custos["custo_total"],
        custo_carne_kg,
        custo_outros_kg
    )

    return {
        "id": id_pesagem,
        "comanda": comanda,
        "peso_carne": peso_carne,
        "peso_outros": peso_outros,
        "peso_total": peso_total,
        "percentual_carne": percentual_carne,
        "percentual_outros": resultado["percentual_outros"],
        "custo_carne": custos["custo_carne"],
        "custo_outros": custos["custo_outros"],
        "custo_total": custos["custo_total"]
    }
