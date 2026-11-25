def calcular_pesagem(peso_carne, peso_outros):
    peso_total = peso_carne + peso_outros

    if peso_total == 0:
        percentual_carne = 0
    else:
        percentual_carne = (peso_carne / peso_total) * 100

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
    # Converte gramas para quilogramas
    carne_kg = peso_carne / 1000
    outros_kg = peso_outros / 1000

    # Calcula o custo de cada categoria
    custo_carne = carne_kg * custo_carne_kg
    custo_outros = outros_kg * custo_outros_kg

    # Soma os custos
    custo_total = custo_carne + custo_outros

    return {
        "custo_carne": custo_carne,
        "custo_outros": custo_outros,
        "custo_total": custo_total
    }
