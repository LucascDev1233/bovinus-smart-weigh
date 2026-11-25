
import sqlite3
from pathlib import Path


CAMINHO_BANCO = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "bovinus.db"
)


def conectar():
    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    # Tabela antiga: preservada para não perder dados anteriores.
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

    # Pesagens vinculadas pela comanda.
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

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_comanda_pendente
        ON pesagens_duplas(comanda)
        WHERE status = 'aguardando_caixa'
    """)

    # Controle diário do buffet.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buffet_controle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            alimento TEXT NOT NULL,
            peso_inicial REAL NOT NULL,
            sobra_aproveitavel REAL,
            descarte REAL,
            status TEXT NOT NULL DEFAULT 'aberto',
            data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_fechamento TIMESTAMP,
            UNIQUE(data, alimento)
        )
    """)

    # Reposições individuais de cada alimento.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buffet_reposicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            controle_id INTEGER NOT NULL,
            quantidade REAL NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(controle_id)
                REFERENCES buffet_controle(id)
        )
    """)

    conexao.commit()
    conexao.close()


# ==========================================
# PESAGENS ANTIGAS
# ==========================================

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
        SELECT *
        FROM pesagens
        ORDER BY id DESC
    """)

    registros = [dict(row) for row in cursor.fetchall()]

    conexao.close()

    return registros


# ==========================================
# DUAS BALANCAS
# ==========================================

def salvar_pesagem_carne(comanda, peso_carne):
    comanda = str(comanda).strip()

    if not comanda:
        raise ValueError("Informe o número da comanda.")

    if peso_carne <= 0:
        raise ValueError("O peso da carne deve ser maior que zero.")

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
        """, (comanda, peso_carne))

        id_pesagem = cursor.lastrowid
        conexao.commit()

        return id_pesagem

    except sqlite3.IntegrityError:
        conexao.rollback()
        raise ValueError(
            "Já existe uma pesagem de carne aguardando "
            "o peso total para essa comanda."
        )

    finally:
        conexao.close()


def finalizar_pesagem_caixa(
    comanda,
    peso_total,
    custo_carne_kg,
    custo_outros_kg,
    resultado
):
    comanda = str(comanda).strip()

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT id
            FROM pesagens_duplas
            WHERE comanda = ?
              AND status = 'aguardando_caixa'
            ORDER BY id DESC
            LIMIT 1
        """, (comanda,))

        registro = cursor.fetchone()

        if registro is None:
            raise ValueError(
                "Não foi encontrada uma pesagem pendente "
                "para essa comanda."
            )

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
            resultado["peso_outros"],
            resultado["percentual_carne"],
            resultado["custo_carne"],
            resultado["custo_outros"],
            resultado["custo_total"],
            custo_carne_kg,
            custo_outros_kg,
            registro["id"]
        ))

        if cursor.rowcount == 0:
            raise ValueError("Não foi possível finalizar a pesagem.")

        conexao.commit()

        return registro["id"]

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def listar_pesagens_duplas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM pesagens_duplas
        WHERE status = 'concluida'
        ORDER BY id DESC
    """)

    registros = [dict(row) for row in cursor.fetchall()]

    conexao.close()

    return registros


def listar_pesagens_pendentes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM pesagens_duplas
        WHERE status = 'aguardando_caixa'
        ORDER BY id DESC
    """)

    registros = [dict(row) for row in cursor.fetchall()]

    conexao.close()

    return registros


# ==========================================
# BUFFET - ABERTURA
# ==========================================

def criar_controle_buffet(data, alimento, peso_inicial):
    alimento = str(alimento).strip()

    if not alimento:
        raise ValueError("Informe o nome do alimento.")

    if peso_inicial <= 0:
        raise ValueError(
            "A quantidade inicial deve ser maior que zero."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            INSERT INTO buffet_controle (
                data,
                alimento,
                peso_inicial
            )
            VALUES (?, ?, ?)
        """, (data, alimento, peso_inicial))

        id_controle = cursor.lastrowid
        conexao.commit()

        return id_controle

    except sqlite3.IntegrityError:
        conexao.rollback()
        raise ValueError(
            "Esse alimento já foi cadastrado nessa data."
        )

    finally:
        conexao.close()


# ==========================================
# BUFFET - REPOSICOES
# ==========================================

def adicionar_reposicao_buffet(controle_id, quantidade):
    if quantidade <= 0:
        raise ValueError(
            "A quantidade da reposição deve ser maior que zero."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT status
            FROM buffet_controle
            WHERE id = ?
        """, (controle_id,))

        registro = cursor.fetchone()

        if registro is None:
            raise ValueError("Alimento não encontrado.")

        if registro["status"] != "aberto":
            raise ValueError(
                "Esse controle já foi finalizado."
            )

        cursor.execute("""
            INSERT INTO buffet_reposicoes (
                controle_id,
                quantidade
            )
            VALUES (?, ?)
        """, (controle_id, quantidade))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


# ==========================================
# BUFFET - CONSULTA
# ==========================================

def listar_controles_buffet(data):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            b.id,
            b.alimento,
            b.peso_inicial,
            COALESCE(SUM(r.quantidade), 0) AS total_reposicoes,
            b.sobra_aproveitavel,
            b.descarte,
            b.status,
            b.data_abertura,
            b.data_fechamento

        FROM buffet_controle b

        LEFT JOIN buffet_reposicoes r
            ON b.id = r.controle_id

        WHERE b.data = ?

        GROUP BY b.id

        ORDER BY b.alimento
    """, (data,))

    registros = [dict(row) for row in cursor.fetchall()]

    conexao.close()

    return registros


def listar_reposicoes_buffet(controle_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            quantidade,
            data_hora
        FROM buffet_reposicoes
        WHERE controle_id = ?
        ORDER BY id ASC
    """, (controle_id,))

    registros = [dict(row) for row in cursor.fetchall()]

    conexao.close()

    return registros


# ==========================================
# BUFFET - FECHAMENTO
# ==========================================

def finalizar_controle_buffet(
    controle_id,
    sobra_aproveitavel,
    descarte
):
    if sobra_aproveitavel < 0 or descarte < 0:
        raise ValueError(
            "Sobra e descarte não podem ser negativos."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT
                peso_inicial,
                status
            FROM buffet_controle
            WHERE id = ?
        """, (controle_id,))

        registro = cursor.fetchone()

        if registro is None:
            raise ValueError("Alimento não encontrado.")

        if registro["status"] != "aberto":
            raise ValueError(
                "Esse alimento já foi finalizado."
            )

        cursor.execute("""
            SELECT COALESCE(SUM(quantidade), 0) AS total
            FROM buffet_reposicoes
            WHERE controle_id = ?
        """, (controle_id,))

        total_reposicoes = cursor.fetchone()["total"]

        disponivel = registro["peso_inicial"] + total_reposicoes

        if sobra_aproveitavel + descarte > disponivel:
            raise ValueError(
                "A soma da sobra e do descarte não pode "
                "ser maior que o total disponibilizado."
            )

        cursor.execute("""
            UPDATE buffet_controle
            SET
                sobra_aproveitavel = ?,
                descarte = ?,
                status = 'fechado',
                data_fechamento = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status = 'aberto'
        """, (
            sobra_aproveitavel,
            descarte,
            controle_id
        ))

        if cursor.rowcount == 0:
            raise ValueError(
                "Não foi possível finalizar o controle."
            )

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
