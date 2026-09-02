"""
Database connection manager.
Supports both PostgreSQL (via asyncpg) and transparent SQLite fallback (bunker.db)
with WAL mode and autocommit so the bot runs out of the box with zero external dependencies.
"""
from __future__ import annotations
import os
import re
import sqlite3
import asyncio
from typing import Any, Optional, List, Dict
import logging

try:
    from loguru import logger
except ImportError:
    logger = logging.getLogger("bunker_db")

_pool: Any = None


class SQLiteRecord(dict):
    """Dict subclass that allows attribute-style access like asyncpg.Record."""
    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"No such column: {name}")


class SQLiteConnectionAdapter:
    def __init__(self, db_path: str = "bunker.db"):
        self.db_path = db_path
        # Use isolation_level=None for autocommit (prevents transaction lock issues)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False, isolation_level=None, timeout=30.0)
        self._conn.row_factory = sqlite3.Row
        self._lock = asyncio.Lock()
        
        # Optimize SQLite for multi-threaded/async access
        cur = self._conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.close()
        
        self._init_schema()

    def _init_schema(self):
        cur = self._conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT NOT NULL,
            is_bot_started INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 0,
            diamonds INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0,
            mvp_count INTEGER DEFAULT 0,
            eliminations_count INTEGER DEFAULT 0,
            survival_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_chat_id INTEGER NOT NULL,
            dashboard_message_id INTEGER,
            state TEXT DEFAULT 'LOBBY',
            current_round INTEGER DEFAULT 0,
            current_attribute_index INTEGER DEFAULT 0,
            apocalypse_type TEXT,
            bunker_capacity INTEGER DEFAULT 4,
            bunker_food_days INTEGER DEFAULT 180,
            bunker_water_days INTEGER DEFAULT 150,
            bunker_power_days INTEGER DEFAULT 90,
            bunker_has_farm INTEGER DEFAULT 0,
            bunker_has_medical INTEGER DEFAULT 0,
            bunker_has_workshop INTEGER DEFAULT 0,
            bunker_has_radio INTEGER DEFAULT 0,
            phase_started_at TIMESTAMP,
            phase_ends_at TIMESTAMP,
            config TEXT DEFAULT '{}',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS game_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            status TEXT DEFAULT 'ACTIVE',
            survival_score INTEGER DEFAULT 0,
            is_protected INTEGER DEFAULT 0,
            protected_until_round INTEGER,
            join_order INTEGER,
            elimination_round INTEGER,
            elimination_votes INTEGER DEFAULT 0,
            votes_received_total INTEGER DEFAULT 0,
            votes_given_total INTEGER DEFAULT 0,
            abilities_used INTEGER DEFAULT 0,
            cards_used INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(game_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS player_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            attribute_type TEXT NOT NULL,
            attribute_value TEXT NOT NULL,
            attribute_metadata TEXT DEFAULT '{}',
            is_revealed INTEGER DEFAULT 0,
            is_fake INTEGER DEFAULT 0,
            revealed_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            rarity TEXT NOT NULL,
            power INTEGER DEFAULT 50,
            card_type TEXT NOT NULL,
            effect_data TEXT DEFAULT '{}',
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS player_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            card_id INTEGER,
            is_used INTEGER DEFAULT 0,
            used_at TIMESTAMP,
            used_on_user_id INTEGER,
            obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            ability_type TEXT NOT NULL,
            trigger_condition TEXT DEFAULT 'MANUAL',
            power INTEGER DEFAULT 50,
            uses_per_game INTEGER DEFAULT 1,
            effect_data TEXT DEFAULT '{}',
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS player_abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            ability_id INTEGER,
            uses_remaining INTEGER DEFAULT 1,
            is_blocked INTEGER DEFAULT 0,
            blocked_until_round INTEGER
        );

        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            round_number INTEGER NOT NULL,
            voter_id INTEGER,
            target_id INTEGER,
            vote_weight INTEGER DEFAULT 1,
            is_valid INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(game_id, round_number, voter_id)
        );

        CREATE TABLE IF NOT EXISTS game_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            round_number INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT DEFAULT '{}',
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved INTEGER DEFAULT 0,
            resolved_by INTEGER
        );

        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            round_number INTEGER,
            actor_id INTEGER,
            action_type TEXT NOT NULL,
            action_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            reward_coins INTEGER DEFAULT 0,
            reward_diamonds INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER,
            achievement_id INTEGER,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            user_id INTEGER,
            place INTEGER,
            coins_reward INTEGER DEFAULT 0,
            diamonds_reward INTEGER DEFAULT 0,
            bonus_type TEXT,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR IGNORE INTO achievements (code, name, description, icon, reward_coins, reward_diamonds) VALUES
        ('first_win', 'Birinchi g''alaba', 'Bunkerda birinchi marta g''olib bo''ldingiz', '🏆', 100, 20),
        ('five_wins', '5 ta g''alaba', '5 marta bunkerda omon qoldingiz', '🔥', 250, 50),
        ('ten_wins', '10 ta g''alaba', '10 marta bunkerda g''alaba qozondingiz', '💎', 500, 100),
        ('twenty_five_wins', '25 ta g''alaba', 'Afsonaviy Bunker faxriysi', '👑', 1000, 250),
        ('mvp_first', 'Birinchi MVP', 'O''yinda eng yuqori survival ball to''pladingiz', '⭐', 150, 30),
        ('survivor', 'Survivor', '10 ta o''yinda omon qoldingiz', '⚔️', 200, 40);
        """)
        cur.close()

    def _convert_query(self, query: str) -> tuple[str, bool]:
        """Converts postgres query ($1, $2, NOW(), RETURNING) to SQLite format."""
        q = re.sub(r'\$\d+', '?', query)
        q = re.sub(r'\bNOW\(\)', 'CURRENT_TIMESTAMP', q, flags=re.IGNORECASE)
        q = re.sub(r'\bTIMESTAMPTZ\b', 'TIMESTAMP', q, flags=re.IGNORECASE)
        q = re.sub(r'\bBOOLEAN\b', 'INTEGER', q, flags=re.IGNORECASE)
        q = re.sub(r'\bTRUE\b', '1', q, flags=re.IGNORECASE)
        q = re.sub(r'\bFALSE\b', '0', q, flags=re.IGNORECASE)
        
        has_returning = "RETURNING" in q.upper()
        return q, has_returning

    def acquire(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def transaction(self):
        class _Tx:
            def __init__(self, parent):
                self.p = parent
            async def __aenter__(self):
                return self.p
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        return _Tx(self)

    async def execute(self, query: str, *args) -> None:
        async with self._lock:
            q, _ = self._convert_query(query)
            clean_args = [int(a) if isinstance(a, bool) else a for a in args]
            cur = self._conn.cursor()
            cur.execute(q, clean_args)
            cur.close()

    async def fetchval(self, query: str, *args) -> Any:
        async with self._lock:
            q, has_ret = self._convert_query(query)
            clean_args = [int(a) if isinstance(a, bool) else a for a in args]
            cur = self._conn.cursor()
            
            if has_ret and q.strip().upper().startswith("INSERT"):
                q_no_ret = re.sub(r'\s+RETURNING\s+.*$', '', q, flags=re.IGNORECASE)
                cur.execute(q_no_ret, clean_args)
                last_id = cur.lastrowid
                cur.close()
                return last_id

            if has_ret and q.strip().upper().startswith("UPDATE"):
                match = re.search(r'RETURNING\s+(\w+)', q, flags=re.IGNORECASE)
                ret_col = match.group(1) if match else "id"
                q_no_ret = re.sub(r'\s+RETURNING\s+.*$', '', q, flags=re.IGNORECASE)
                cur.execute(q_no_ret, clean_args)
                cur.close()
                return args[0] if args else 1

            cur.execute(q, clean_args)
            row = cur.fetchone()
            val = row[0] if row else None
            cur.close()
            return val

    async def fetchrow(self, query: str, *args) -> Optional[SQLiteRecord]:
        async with self._lock:
            q, has_ret = self._convert_query(query)
            clean_args = [int(a) if isinstance(a, bool) else a for a in args]
            cur = self._conn.cursor()

            if has_ret and q.strip().upper().startswith("INSERT"):
                table_match = re.search(r'INSERT\s+INTO\s+(\w+)', q, flags=re.IGNORECASE)
                table_name = table_match.group(1) if table_match else ""
                q_no_ret = re.sub(r'\s+RETURNING\s+.*$', '', q, flags=re.IGNORECASE)
                cur.execute(q_no_ret, clean_args)
                row_id = cur.lastrowid
                cur.close()
                
                if table_name and row_id:
                    cur2 = self._conn.cursor()
                    cur2.execute(f"SELECT * FROM {table_name} WHERE id = ?", (row_id,))
                    row = cur2.fetchone()
                    res = SQLiteRecord(dict(row)) if row else None
                    cur2.close()
                    return res
                return None

            cur.execute(q, clean_args)
            row = cur.fetchone()
            res = SQLiteRecord(dict(row)) if row else None
            cur.close()
            return res

    async def fetch(self, query: str, *args) -> List[SQLiteRecord]:
        async with self._lock:
            q, _ = self._convert_query(query)
            clean_args = [int(a) if isinstance(a, bool) else a for a in args]
            cur = self._conn.cursor()
            cur.execute(q, clean_args)
            rows = cur.fetchall()
            res = [SQLiteRecord(dict(r)) for r in rows]
            cur.close()
            return res

    async def close(self) -> None:
        self._conn.close()


async def create_pool(dsn: Optional[str] = None, **kwargs) -> Any:
    global _pool
    db_url = dsn or os.getenv("DATABASE_URL", "")

    if "postgres" in db_url.lower() and not "sqlite" in db_url.lower():
        try:
            import asyncpg
            clean_dsn = db_url.replace("postgresql+asyncpg://", "postgresql://")
            logger.info("Connecting to PostgreSQL database...")
            _pool = await asyncpg.create_pool(dsn=clean_dsn, min_size=1, max_size=10, command_timeout=10)
            logger.info("PostgreSQL connection pool established!")
            return _pool
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database...")

    logger.info("Initializing local SQLite database (bunker.db)...")
    _pool = SQLiteConnectionAdapter("bunker.db")
    logger.info("SQLite database (bunker.db) is ready and initialized!")
    return _pool


def get_pool() -> Any:
    global _pool
    if _pool is None:
        raise RuntimeError("Database pool is not initialised.")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
