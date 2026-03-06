import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime

# Lock para thread safety
_db_lock = threading.Lock()

def get_connection():
    """Retorna uma conexão SQLite com configurações seguras"""
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
    return conn

@contextmanager
def get_db_connection():
    """Context manager seguro para conexões SQLite"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# ===== FUNÇÕES DE REPUTAÇÃO =====

def get_user(user_id: str) -> Optional[Dict]:
    """Obtém dados do usuário do banco"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Obter dados básicos do usuário
        cursor.execute("SELECT rep_total FROM rep_users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return None
            
        return {
            "rep_total": user_data["rep_total"],
            "history": get_history(user_id),
            "received_from": get_received_from(user_id),
            "given_to": get_given_to(user_id)
        }

def create_user_if_not_exists(user_id: str) -> Dict:
    """Cria usuário se não existir e retorna dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT rep_total FROM rep_users WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            return get_user(user_id)
        
        # Criar usuário
        cursor.execute("INSERT INTO rep_users (user_id, rep_total) VALUES (?, 0)", (user_id,))
        
        return {
            "rep_total": 0,
            "history": [],
            "received_from": {},
            "given_to": {}
        }

def get_rep_total(user_id: str) -> int:
    """Obtém total de reputação do usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rep_total FROM rep_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result["rep_total"] if result else 0

def add_rep(giver_id: str, receiver_id: str, guild_id: str, reason: str = "") -> bool:
    """Adiciona reputação para um usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Garantir que ambos os usuários existam
        create_user_if_not_exists(giver_id)
        create_user_if_not_exists(receiver_id)
        
        current_time = time.time()
        
        # Adicionar ao histórico
        cursor.execute("""
            INSERT INTO rep_history (user_id, giver_id, receiver_id, reason, timestamp, guild_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (receiver_id, giver_id, receiver_id, reason, current_time, guild_id))
        
        # Atualizar received_from
        cursor.execute("""
            INSERT OR REPLACE INTO rep_received_from (user_id, giver_id, timestamp)
            VALUES (?, ?, ?)
        """, (receiver_id, giver_id, current_time))
        
        # Atualizar given_to
        cursor.execute("""
            INSERT OR REPLACE INTO rep_given_to (user_id, receiver_id, timestamp)
            VALUES (?, ?, ?)
        """, (giver_id, receiver_id, current_time))
        
        # Incrementar reputação
        cursor.execute("""
            UPDATE rep_users SET rep_total = rep_total + 1 WHERE user_id = ?
        """, (receiver_id,))
        
        return True

def get_history(user_id: str, limit: int = 50) -> List[Dict]:
    """Obtém histórico de reputações recebidas"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT giver_id, reason, timestamp, guild_id
            FROM rep_history 
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "giver_id": row["giver_id"],
                "reason": row["reason"],
                "timestamp": row["timestamp"],
                "guild_id": row["guild_id"]
            })
        
        return history

def get_received_from(user_id: str) -> Dict:
    """Obtém mapa de quem deu reputação para o usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT giver_id, timestamp FROM rep_received_from WHERE user_id = ?
        """, (user_id,))
        
        return {row["giver_id"]: row["timestamp"] for row in cursor.fetchall()}

def get_given_to(user_id: str) -> Dict:
    """Obtém mapa de para quem o usuário deu reputação"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT receiver_id, timestamp FROM rep_given_to WHERE user_id = ?
        """, (user_id,))
        
        return {row["receiver_id"]: row["timestamp"] for row in cursor.fetchall()}

def get_last_given_timestamp(giver_id: str, receiver_id: str) -> Optional[float]:
    """Obtém o timestamp da última reputação dada de giver -> receiver"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp FROM rep_given_to
            WHERE user_id = ? AND receiver_id = ?
            """,
            (giver_id, receiver_id),
        )
        result = cursor.fetchone()
        return result["timestamp"] if result else None

# ===== FUNÇÕES DE COOLDOWN =====

def update_cooldown(user_id: str, cooldown_type: str, timestamp: float):
    """Atualiza cooldown do usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if cooldown_type == "global":
            cursor.execute("""
                INSERT OR REPLACE INTO cooldowns_global (user_id, timestamp)
                VALUES (?, ?)
            """, (user_id, timestamp))
        # Adicionar outros tipos de cooldown se necessário

def get_cooldown(user_id: str, cooldown_type: str = "global") -> Optional[float]:
    """Obtém timestamp do cooldown do usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if cooldown_type == "global":
            cursor.execute("""
                SELECT timestamp FROM cooldowns_global WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            return result["timestamp"] if result else None
        
        return None

# ===== FUNÇÕES DE MUSHADD =====

def is_mush_enabled(user_id: str) -> bool:
    """Verifica se mushadd está habilitado para o usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT enabled FROM mushadd_usage WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return bool(result["enabled"]) if result else False

def enable_mush(user_id: str):
    """Habilita mushadd para o usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mushadd_usage (user_id, enabled)
            VALUES (?, 1)
        """, (user_id,))

def disable_mush(user_id: str):
    """Desabilita mushadd para o usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mushadd_usage (user_id, enabled)
            VALUES (?, 0)
        """, (user_id,))

# ===== FUNÇÕES DE RANKING (OTIMIZADAS) =====

def get_all_users_rep() -> List[Tuple[str, int]]:
    """Obtém todos os usuários com suas reputações (para ranking)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, rep_total FROM rep_users ORDER BY rep_total DESC")
        return [(row["user_id"], row["rep_total"]) for row in cursor.fetchall()]

def get_top_users(limit: int = 10) -> List[Tuple[str, int]]:
    """Obtém top usuários por reputação"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, rep_total FROM rep_users 
            ORDER BY rep_total DESC 
            LIMIT ?
        """, (limit,))
        return [(row["user_id"], row["rep_total"]) for row in cursor.fetchall()]

def get_user_ranking(user_id: str) -> Tuple[int, int]:
    """Retorna (reputação, posição no ranking)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Obter reputação do usuário
        cursor.execute("SELECT rep_total FROM rep_users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if not result:
            create_user_if_not_exists(user_id)
            return 0, 1
        
        rep_total = result["rep_total"]
        
        # Calcular posição no ranking
        cursor.execute("""
            SELECT COUNT(*) + 1 as position 
            FROM rep_users 
            WHERE rep_total > ?
        """, (rep_total,))
        
        position = cursor.fetchone()["position"]
        return rep_total, position

# ===== FUNÇÕES DE MANUTENÇÃO =====

def cleanup_old_history(days_to_keep: int = 30):
    """Remove histórico antigo para economizar espaço"""
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rep_history WHERE timestamp < ?", (cutoff_time,))
        return cursor.rowcount

def get_database_stats() -> Dict:
    """Retorna estatísticas do banco de dados"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Contagem de usuários
        cursor.execute("SELECT COUNT(*) as count FROM rep_users")
        stats["total_users"] = cursor.fetchone()["count"]
        
        # Contagem de histórico
        cursor.execute("SELECT COUNT(*) as count FROM rep_history")
        stats["total_history"] = cursor.fetchone()["count"]
        
        # Contagem de mushadd enabled
        cursor.execute("SELECT COUNT(*) as count FROM mushadd_usage WHERE enabled = 1")
        stats["mushadd_enabled"] = cursor.fetchone()["count"]
        
        return stats

# ===== FUNÇÕES DE VOICE TRACKING =====

def create_voice_tables():
    """Cria tabelas para sistema de voice tracking se não existirem"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de tempo diário em call
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_time_daily (
                user_id TEXT PRIMARY KEY,
                total_seconds INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Tabela de sessões ativas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_sessions (
                user_id TEXT PRIMARY KEY,
                joined_at REAL NOT NULL
            )
        ''')
        
        # Tabela de controle de ranking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ranking_control (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                last_run_date TEXT
            )
        ''')
        
        # Inserir registro de controle se não existir
        cursor.execute('''
            INSERT OR IGNORE INTO ranking_control (id, last_run_date) VALUES (1, NULL)
        ''')

def start_voice_session(user_id: str, joined_at: float) -> bool:
    """Inicia uma sessão de voice para o usuário"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar se já tem sessão ativa
        cursor.execute("SELECT user_id FROM voice_sessions WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            return False  # Já está em call
        
        # Iniciar nova sessão
        cursor.execute('''
            INSERT INTO voice_sessions (user_id, joined_at)
            VALUES (?, ?)
        ''', (user_id, joined_at))
        
        return True

def end_voice_session(user_id: str, left_at: float) -> Optional[int]:
    """Finaliza sessão de voice e retorna o tempo em segundos"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Buscar sessão ativa
        cursor.execute("SELECT joined_at FROM voice_sessions WHERE user_id = ?", (user_id,))
        session = cursor.fetchone()
        
        if not session:
            return None  # Não tinha sessão ativa
        
        joined_at = session["joined_at"]
        session_duration = int(left_at - joined_at)
        
        if session_duration <= 0:
            session_duration = 0
        
        # Remover sessão ativa
        cursor.execute("DELETE FROM voice_sessions WHERE user_id = ?", (user_id,))
        
        # Adicionar tempo ao total diário
        cursor.execute('''
            INSERT INTO voice_time_daily (user_id, total_seconds)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            total_seconds = total_seconds + excluded.total_seconds
        ''', (user_id, session_duration))
        
        return session_duration

def add_voice_time(user_id: str, seconds: int):
    """Adiciona tempo diretamente ao total diário (para correções manuais)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO voice_time_daily (user_id, total_seconds)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            total_seconds = total_seconds + excluded.total_seconds
        ''', (user_id, seconds))

def get_top_voice_time(limit: int = 10) -> List[Tuple[str, int]]:
    """Retorna top usuários com mais tempo em call no dia"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, total_seconds
            FROM voice_time_daily
            WHERE total_seconds > 0
            ORDER BY total_seconds DESC
            LIMIT ?
        ''', (limit,))
        
        return [(row["user_id"], row["total_seconds"]) for row in cursor.fetchall()]

def get_top5_voice_time() -> List[Tuple[str, int]]:
    """Compatibilidade: retorna top 5 usuários com mais tempo em call no dia"""
    return get_top_voice_time(limit=5)

def reset_daily_voice_time():
    """Reseta o tempo diário de todos os usuários"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM voice_time_daily")
        cursor.execute("UPDATE voice_sessions SET joined_at = ?", (time.time(),))

def get_last_voice_ranking_run() -> Optional[str]:
    """Retorna a data da última execução do ranking de voice"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_run_date FROM ranking_control WHERE id = 1")
        result = cursor.fetchone()
        return result["last_run_date"] if result and result["last_run_date"] else None

def update_last_voice_ranking_run(date: str):
    """Atualiza a data da última execução do ranking de voice"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE ranking_control SET last_run_date = ? WHERE id = 1
        ''', (date,))

def get_active_voice_sessions() -> List[Tuple[str, float]]:
    """Retorna todas as sessões de voice ativas"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, joined_at FROM voice_sessions")
        return [(row["user_id"], row["joined_at"]) for row in cursor.fetchall()]

def format_voice_time(seconds: int) -> str:
    """Formata segundos para 'Xh Ym' ou 'X horas Y minutos'"""
    if seconds < 60:
        return "0h 0m"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours == 0:
        return f"{minutes}m"
    elif minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {minutes}m"

# Funções para ranking message
def create_ranking_message_table():
    conn = get_connection()
    try:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ranking_message (
                    id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')
    except Exception as e:
        print(f"Erro ao criar tabela ranking_message: {e}")

def save_ranking_message(channel_id, message_id):
    conn = get_connection()
    try:
        with conn:
            conn.execute('''
                INSERT OR REPLACE INTO ranking_message (id, channel_id, message_id, last_updated)
                VALUES (1, ?, ?, datetime('now', 'localtime'))
            ''', (channel_id, message_id))
    except Exception as e:
        print(f"Erro ao salvar ranking message: {e}")

def get_ranking_message():
    conn = get_connection()
    try:
        result = conn.execute('''
            SELECT channel_id, message_id FROM ranking_message WHERE id = 1
        ''').fetchone()
        return result
    except Exception as e:
        print(f"Erro ao buscar ranking message: {e}")
        return None

def get_all_voice_times():
    """Obtem todos os usuários com tempo de call ordenados"""
    conn = get_connection()
    try:
        result = conn.execute('''
            SELECT user_id, total_seconds FROM voice_time_daily 
            WHERE total_seconds > 0 
            ORDER BY total_seconds DESC
        ''').fetchall()
        return result
    except Exception as e:
        print(f"Erro ao buscar todos os tempos: {e}")
        return []

def get_user_voice_time(user_id):
    """Obtem tempo de call de um usuário específico"""
    conn = get_connection()
    try:
        result = conn.execute('''
            SELECT total_seconds FROM voice_time_daily WHERE user_id = ?
        ''', (user_id,)).fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Erro ao buscar tempo do usuário {user_id}: {e}")
        return 0

# Atualizar create_tables para incluir ranking_message
def create_tables():
    create_reputation_tables()
    create_mushadd_tables()
    create_voice_tables()
    create_ranking_message_table()
