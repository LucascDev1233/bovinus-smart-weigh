
def calcular_pesagem(peso_carne, peso_total):
    """
    Calcula o peso dos outros alimentos e a participação da carne.
    """

    if peso_carne < 0 or peso_total < 0:
        raise ValueError("Os pesos não podem ser negativos.")

    if peso_total <= 0:
        raise ValueError("O peso total deve ser maior que zero.")

    if peso_carne > peso_total:
        raise ValueError(
            "O peso da carne não pode ser maior que o peso total."
        )

    peso_outros = peso_total - peso_carne

    percentual_carne = (peso_carne / peso_total) * 100

    percentual_outros = (peso_outros / peso_total) * 100

    return {
        "peso_carne": peso_carne,
        "peso_outros": peso_outros,
        "peso_total": peso_total,
        "percentual_carne": percentual_carne,
        "percentual_outros": percentual_outros
    }


def calcular_custos(
    peso_carne,
    peso_outros,
    custo_carne_kg,
    custo_outros_kg
):
    """
    Calcula os custos estimados da carne e dos outros alimentos.
    """

    if min(
        peso_carne,
        peso_outros,
        custo_carne_kg,
        custo_outros_kg
    ) < 0:
        raise ValueError("Pesos e custos não podem ser negativos.")

    carne_kg = peso_carne / 1000
    outros_kg = peso_outros / 1000

    custo_carne = carne_kg * custo_carne_kg
    custo_outros = outros_kg * custo_outros_kg

    custo_total = custo_carne + custo_outros

    return {
        "custo_carne": custo_carne,
        "custo_outros": custo_outros,
        "custo_total": custo_total
    }
