
import sqlite3
from pathlib import Path


# Localização do banco de dados
CAMINHO_BANCO = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "bovinus.db"
)


# Conectar ao banco
def conectar():

    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conexao = sqlite3.connect(CAMINHO_BANCO)

    return conexao


# Criar tabela
def criar_tabela():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pesagens (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso_carne REAL NOT NULL,
            peso_outros REAL NOT NULL,
            peso_total REAL NOT NULL,
            percentual_carne REAL NOT NULL,
            custo_carne REAL NOT NULL,
            custo_outros REAL NOT NULL,
            custo_total REAL NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conexao.commit()
    conexao.close()


# Salvar uma pesagem
def salvar_pesagem(
    peso_carne,
    peso_outros,
    peso_total,
    percentual_carne,
    custo_carne,
    custo_outros,
    custo_total
):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO pesagens (
            peso_carne,
            peso_outros,
            peso_total,
            percentual_carne,
            custo_carne,
            custo_outros,
            custo_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        peso_carne,
        peso_outros,
        peso_total,
        percentual_carne,
        custo_carne,
        custo_outros,
        custo_total
    ))

    id_pesagem = cursor.lastrowid

    conexao.commit()
    conexao.close()

    return id_pesagem


def listar_pesagens():
    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            peso_carne,
            peso_outros,
            peso_total,
            percentual_carne,
            custo_carne,
            custo_outros,
            custo_total,
            data_hora
        FROM pesagens
        ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    conexao.close()

    return registros

