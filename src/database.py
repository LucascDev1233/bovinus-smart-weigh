
import sqlite3
from pathlib import Path


# ==========================================
# LOCALIZACAO DO BANCO
# ==========================================

CAMINHO_BANCO = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "bovinus.db"
)


# ==========================================
# CONEXAO
# ==========================================

def conectar():

    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conexao = sqlite3.connect(
        CAMINHO_BANCO,
        timeout=10
    )

    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


# ==========================================
# CRIAR TABELAS
# ==========================================

def criar_tabela():

    conexao = conectar()

    cursor = conexao.cursor()

    # Mantem a tabela antiga, sem apagar os registros.
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

    # Nova tabela para as duas balancas.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pesagens_duplas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            comanda TEXT NOT NULL,

            peso_carne REAL NOT NULL,

            peso_total REAL,

            peso_outros REAL,

            percentual_carne REAL,

            custo_carne REAL,

            custo_outros REAL,

            custo_total REAL,

            custo_carne_kg REAL,

            custo_outros_kg REAL,

            status TEXT NOT NULL DEFAULT 'aguardando_caixa',

            data_churrasqueira TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            data_caixa TIMESTAMP

        )
    """)

    # Impede duas comandas pendentes com o mesmo numero.
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_comanda_pendente
        ON pesagens_duplas(comanda)
        WHERE status = 'aguardando_caixa'
    """)

    conexao.commit()
    conexao.close()


# ==========================================
# REGISTRAR PESO DA CARNE
# ==========================================

def salvar_peso_carne(comanda, peso_carne):

    conexao = conectar()

    cursor = conexao.cursor()

    try:

        cursor.execute("""
            INSERT INTO pesagens_duplas (
                comanda,
                peso_carne,
                status
            )
            VALUES (?, ?, 'aguardando_caixa')
        """, (
            comanda,
            peso_carne
        ))

        id_pesagem = cursor.lastrowid

        conexao.commit()

        return id_pesagem

    except sqlite3.IntegrityError:

        conexao.rollback()

        raise ValueError(
            "Já existe uma pesagem aguardando o caixa "
            "para essa comanda."
        )

    finally:

        conexao.close()


# ==========================================
# BUSCAR PESAGEM PENDENTE
# ==========================================

def buscar_pesagem_pendente(comanda):

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            comanda,
            peso_carne,
            status
        FROM pesagens_duplas
        WHERE comanda = ?
        AND status = 'aguardando_caixa'
        ORDER BY id DESC
        LIMIT 1
    """, (comanda,))

    registro = cursor.fetchone()

    conexao.close()

    return registro


# ==========================================
# FINALIZAR PESAGEM NO CAIXA
# ==========================================

def finalizar_pesagem(
    id_pesagem,
    peso_total,
    peso_outros,
    percentual_carne,
    custo_carne,
    custo_outros,
    custo_total,
    custo_carne_kg,
    custo_outros_kg
):

    conexao = conectar()

    cursor = conexao.cursor()

    try:

        cursor.execute("""
            UPDATE pesagens_duplas

            SET
                peso_total = ?,
                peso_outros = ?,
                percentual_carne = ?,
                custo_carne = ?,
                custo_outros = ?,
                custo_total = ?,
                custo_carne_kg = ?,
                custo_outros_kg = ?,
                status = 'concluida',
                data_caixa = CURRENT_TIMESTAMP

            WHERE id = ?
            AND status = 'aguardando_caixa'

        """, (
            peso_total,
            peso_outros,
            percentual_carne,
            custo_carne,
            custo_outros,
            custo_total,
            custo_carne_kg,
            custo_outros_kg,
            id_pesagem
        ))

        if cursor.rowcount == 0:

            raise ValueError(
                "Pesagem não encontrada ou já finalizada."
            )

        conexao.commit()

    except Exception:

        conexao.rollback()
        raise

    finally:

        conexao.close()


# ==========================================
# LISTAR PESAGENS CONCLUIDAS
# ==========================================

def listar_pesagens_duplas():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            comanda,
            peso_carne,
            peso_outros,
            peso_total,
            percentual_carne,
            custo_carne,
            custo_outros,
            custo_total,
            data_churrasqueira,
            data_caixa

        FROM pesagens_duplas

        WHERE status = 'concluida'

        ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    conexao.close()

    return registros


# ==========================================
# LISTAR PESAGENS PENDENTES
# ==========================================

def listar_pesagens_pendentes():

    conexao = conectar()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            comanda,
            peso_carne,
            data_churrasqueira

        FROM pesagens_duplas

        WHERE status = 'aguardando_caixa'

        ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    conexao.close()

    return registros


# ==========================================
# HISTORICO ANTIGO
# ==========================================

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
