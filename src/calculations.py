
def calcular_pesagem(peso_carne, peso_outros):
    peso_total = peso_carne + peso_outros

    percentual_carne = (
        peso_carne / peso_total * 100
        if peso_total > 0 else 0
    )

    return {
        "peso_total": peso_total,
        "percentual_carne": percentual_carne
    }


def calcular_custos(
    peso_carne,
    peso_outros,
    custo_carne_kg,
    custo_outros_kg
):
    carne_kg = peso_carne / 1000
    outros_kg = peso_outros / 1000

    custo_carne = carne_kg * custo_carne_kg
    custo_outros = outros_kg * custo_outros_kg

    return {
        "custo_carne": custo_carne,
        "custo_outros": custo_outros,
        "custo_total": custo_carne + custo_outros
    }


def calcular_pesagem_dupla(
    peso_carne,
    peso_total,
    custo_carne_kg,
    custo_outros_kg
):
    if peso_carne < 0 or peso_total <= 0:
        raise ValueError("Os pesos informados são inválidos.")

    if peso_carne > peso_total:
        raise ValueError(
            "O peso da carne não pode ser maior que o peso total."
        )

    peso_outros = peso_total - peso_carne

    percentual_carne = peso_carne / peso_total * 100

    custos = calcular_custos(
        peso_carne,
        peso_outros,
        custo_carne_kg,
        custo_outros_kg
    )

    return {
        "peso_carne": peso_carne,
        "peso_outros": peso_outros,
        "peso_total": peso_total,
        "percentual_carne": percentual_carne,
        "custo_carne": custos["custo_carne"],
        "custo_outros": custos["custo_outros"],
        "custo_total": custos["custo_total"]
    }


def calcular_buffet(
    peso_inicial,
    total_reposicoes,
    sobra_aproveitavel,
    descarte
):
    valores = [
        peso_inicial,
        total_reposicoes,
        sobra_aproveitavel,
        descarte
    ]

    if any(valor < 0 for valor in valores):
        raise ValueError("Os valores não podem ser negativos.")

    disponivel = peso_inicial + total_reposicoes

    if sobra_aproveitavel + descarte > disponivel:
        raise ValueError(
            "Sobra e descarte não podem superar "
            "a quantidade disponibilizada."
        )

    consumido = (
        disponivel
        - sobra_aproveitavel
        - descarte
    )

    percentual_desperdicio = (
        descarte / disponivel * 100
        if disponivel > 0 else 0
    )

    return {
        "disponivel": disponivel,
        "consumido": consumido,
        "sobra": sobra_aproveitavel,
        "descarte": descarte,
        "percentual_desperdicio": percentual_desperdicio
    }
