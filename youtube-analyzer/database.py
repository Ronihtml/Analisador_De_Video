import sqlite3
import os
import datetime

# Caminho para o banco de dados
DB_PATH = os.path.join(os.getcwd(), 'database', 'youtube_analyzer.db')

def inicializar_banco():
    """Inicializa o banco de dados criando a tabela se não existir."""
    # Garantir que o diretório existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de análises
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        titulo TEXT,
        data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resumo TEXT,
        duracao_video TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Banco de dados inicializado em: {DB_PATH}")

def salvar_analise(url, titulo, resumo, duracao_video=None):
    """Salva uma análise no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO analises (url, titulo, resumo, duracao_video, data_analise)
    VALUES (?, ?, ?, ?, ?)
    ''', (url, titulo, resumo, duracao_video, datetime.datetime.now()))
    
    analise_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return analise_id

def obter_analise(analise_id):
    """Recupera uma análise específica pelo ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM analises WHERE id = ?', (analise_id,))
    analise = cursor.fetchone()
    
    conn.close()
    
    if analise:
        return dict(analise)
    return None

def listar_analises(limite=10):
    """Lista as análises mais recentes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM analises 
    ORDER BY data_analise DESC 
    LIMIT ?
    ''', (limite,))
    
    analises = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return analises

def buscar_analises(termo_busca):
    """Busca análises por termo no título ou resumo."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM analises 
    WHERE titulo LIKE ? OR resumo LIKE ? 
    ORDER BY data_analise DESC
    ''', (f'%{termo_busca}%', f'%{termo_busca}%'))
    
    analises = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return analises

def excluir_analise(analise_id):
    """Exclui uma análise do banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM analises WHERE id = ?', (analise_id,))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0
