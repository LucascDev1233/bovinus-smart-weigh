
from src.database import (
    salvar_pesagem_carne,
    finalizar_pesagem_caixa
)

from src.calculations import calcular_pesagem_dupla


def registrar_carne(comanda, peso_carne):
    return salvar_pesagem_carne(
        comanda,
        peso_carne
    )


def registrar_prato_completo(
    comanda,
    peso_total,
    custo_carne_kg,
    custo_outros_kg
):
    if peso_total <= 0:
        raise ValueError(
            "O peso total deve ser maior que zero."
        )

    if custo_carne_kg < 0 or custo_outros_kg < 0:
        raise ValueError(
            "Os custos por kg não podem ser negativos."
        )

    # Localiza a pesagem de carne pendente.
    from src.database import listar_pesagens_pendentes

    comanda_texto = str(comanda).strip()

    pendentes = listar_pesagens_pendentes()

    pesagem = next(
        (
            item for item in pendentes
            if item["comanda"] == comanda_texto
        ),
        None
    )

    if pesagem is None:
        raise ValueError(
            "Não existe pesagem de carne aguardando "
            "para essa comanda."
        )

    resultado = calcular_pesagem_dupla(
        pesagem["peso_carne"],
        peso_total,
        custo_carne_kg,
        custo_outros_kg
    )

    id_pesagem = finalizar_pesagem_caixa(
        comanda_texto,
        peso_total,
        custo_carne_kg,
        custo_outros_kg,
        resultado
    )

    return {
        "id": id_pesagem,
        **resultado
    }
