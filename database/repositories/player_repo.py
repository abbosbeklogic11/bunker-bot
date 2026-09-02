from typing import Optional, List, Dict, Any, Tuple
import asyncpg
import json
from datetime import datetime, timezone
from models.game import GamePlayerModel, PlayerStatus, PlayerAttributeModel, AttributeType


class PlayerRepository:
    def __init__(self, pool: Any):
        self.pool = pool

    async def add_player(self, game_id: int, user_id: int, join_order: int) -> GamePlayerModel:
        async with self.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT * FROM game_players WHERE game_id = $1 AND user_id = $2;",
                game_id, user_id
            )
            if existing:
                await conn.execute(
                    "UPDATE game_players SET status = 'ACTIVE' WHERE game_id = $1 AND user_id = $2;",
                    game_id, user_id
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO game_players (game_id, user_id, status, join_order, joined_at)
                    VALUES ($1, $2, 'ACTIVE', $3, NOW());
                    """,
                    game_id, user_id, join_order
                )

            row = await conn.fetchrow(
                "SELECT * FROM game_players WHERE game_id = $1 AND user_id = $2;",
                game_id, user_id
            )
            return GamePlayerModel.from_row(row)

    async def get_player(self, game_id: int, user_id: int) -> Optional[GamePlayerModel]:
        query = "SELECT * FROM game_players WHERE game_id = $1 AND user_id = $2;"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, game_id, user_id)
            return GamePlayerModel.from_row(row) if row else None

    async def get_all_players(self, game_id: int) -> List[GamePlayerModel]:
        query = "SELECT * FROM game_players WHERE game_id = $1 ORDER BY join_order ASC;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id)
            return [GamePlayerModel.from_row(r) for r in rows]

    async def get_alive_players(self, game_id: int) -> List[GamePlayerModel]:
        query = """
            SELECT * FROM game_players 
            WHERE game_id = $1 AND status IN ('ACTIVE', 'PROTECTED') 
            ORDER BY join_order ASC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id)
            return [GamePlayerModel.from_row(r) for r in rows]

    async def get_player_count(self, game_id: int) -> int:
        query = "SELECT COUNT(*) FROM game_players WHERE game_id = $1 AND status != 'LEFT';"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, game_id)

    async def eliminate_player(self, game_id: int, user_id: int, round_number: int, votes_received: int) -> None:
        query = """
            UPDATE game_players 
            SET status = 'ELIMINATED', elimination_round = $1, elimination_votes = $2 
            WHERE game_id = $3 AND user_id = $4;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, round_number, votes_received, game_id, user_id)

    async def protect_player(self, game_id: int, user_id: int, until_round: int) -> None:
        query = """
            UPDATE game_players 
            SET is_protected = TRUE, protected_until_round = $1, status = 'PROTECTED'
            WHERE game_id = $2 AND user_id = $3;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, until_round, game_id, user_id)

    async def remove_protection(self, game_id: int, user_id: int) -> None:
        query = """
            UPDATE game_players 
            SET is_protected = FALSE, protected_until_round = NULL,
                status = CASE WHEN status = 'PROTECTED' THEN 'ACTIVE' ELSE status END
            WHERE game_id = $1 AND user_id = $2;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, game_id, user_id)

    async def update_status(self, game_id: int, user_id: int, status: PlayerStatus) -> None:
        status_str = status.value if isinstance(status, PlayerStatus) else str(status)
        query = "UPDATE game_players SET status = $1 WHERE game_id = $2 AND user_id = $3;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, status_str, game_id, user_id)

    async def update_survival_score(self, game_id: int, user_id: int, score: int) -> None:
        query = "UPDATE game_players SET survival_score = $1 WHERE game_id = $2 AND user_id = $3;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, score, game_id, user_id)

    async def increment_stats(
        self,
        game_id: int,
        user_id: int,
        votes_received: int = 0,
        votes_given: int = 0,
        abilities_used: int = 0,
        cards_used: int = 0
    ) -> None:
        query = """
            UPDATE game_players 
            SET votes_received_total = votes_received_total + $1,
                votes_given_total = votes_given_total + $2,
                abilities_used = abilities_used + $3,
                cards_used = cards_used + $4
            WHERE game_id = $5 AND user_id = $6;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, votes_received, votes_given, abilities_used, cards_used, game_id, user_id)

    # === ATTRIBUTES ===
    async def add_player_attribute(
        self,
        game_id: int,
        user_id: int,
        attr_type: str,
        attr_value: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PlayerAttributeModel:
        query = """
            INSERT INTO player_attributes (game_id, user_id, attribute_type, attribute_value, attribute_metadata, is_revealed)
            VALUES ($1, $2, $3, $4, $5, 0)
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, game_id, user_id, attr_type, attr_value, json.dumps(metadata or {}))
            return PlayerAttributeModel.from_row(row)

    async def get_player_attributes(self, game_id: int, user_id: int) -> List[PlayerAttributeModel]:
        query = "SELECT * FROM player_attributes WHERE game_id = $1 AND user_id = $2 ORDER BY id ASC;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, user_id)
            return [PlayerAttributeModel.from_row(r) for r in rows]

    async def get_attribute_by_type(self, game_id: int, user_id: int, attr_type: str) -> Optional[PlayerAttributeModel]:
        query = "SELECT * FROM player_attributes WHERE game_id = $1 AND user_id = $2 AND attribute_type = $3;"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, game_id, user_id, attr_type)
            return PlayerAttributeModel.from_row(row) if row else None

    async def reveal_player_attribute(self, game_id: int, user_id: int, attr_type: str) -> Optional[PlayerAttributeModel]:
        """Reveals a specific unrevealed attribute for a single player. Returns None if already revealed or not found."""
        async with self.pool.acquire() as conn:
            # 1. Verify attribute exists and is UNREVEALED (is_revealed = 0)
            row = await conn.fetchrow(
                "SELECT * FROM player_attributes WHERE game_id = $1 AND user_id = $2 AND attribute_type = $3 AND is_revealed = 0;",
                game_id, user_id, attr_type
            )
            if not row:
                return None

            # 2. Update to revealed
            await conn.execute(
                "UPDATE player_attributes SET is_revealed = 1, revealed_at = NOW() WHERE game_id = $1 AND user_id = $2 AND attribute_type = $3;",
                game_id, user_id, attr_type
            )
            updated = await conn.fetchrow(
                "SELECT * FROM player_attributes WHERE game_id = $1 AND user_id = $2 AND attribute_type = $3;",
                game_id, user_id, attr_type
            )
            return PlayerAttributeModel.from_row(updated) if updated else None

    async def get_unrevealed_player_attributes(self, game_id: int, user_id: int) -> List[PlayerAttributeModel]:
        """Returns list of unrevealed attributes for a player."""
        query = """
            SELECT * FROM player_attributes 
            WHERE game_id = $1 AND user_id = $2 AND is_revealed = 0 
            ORDER BY id ASC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, user_id)
            return [PlayerAttributeModel.from_row(r) for r in rows]

    async def get_revealed_player_count(self, game_id: int, user_id: int) -> int:
        """Counts how many attributes a player has already revealed."""
        query = """
            SELECT COUNT(*) FROM player_attributes 
            WHERE game_id = $1 AND user_id = $2 AND is_revealed = 1;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, game_id, user_id) or 0

    async def reveal_attribute(self, game_id: int, attr_type: str) -> None:
        query = """
            UPDATE player_attributes 
            SET is_revealed = 1, revealed_at = NOW() 
            WHERE game_id = $1 AND attribute_type = $2;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, game_id, attr_type)

    async def get_revealed_attributes_by_type(self, game_id: int, attr_type: str) -> List[Tuple[int, str, bool, str, Optional[str]]]:
        query = """
            SELECT pa.user_id, pa.attribute_value, pa.is_fake, u.first_name, u.username
            FROM player_attributes pa
            JOIN users u ON pa.user_id = u.id
            WHERE pa.game_id = $1 AND pa.attribute_type = $2 AND pa.is_revealed = 1
            ORDER BY pa.id ASC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, attr_type)
            return [(r['user_id'], r['attribute_value'], bool(r['is_fake']), r['first_name'], r['username']) for r in rows]

    async def get_all_revealed_attributes(self, game_id: int) -> List[Dict[str, Any]]:
        """Returns all currently revealed attributes for all players with user details."""
        query = """
            SELECT pa.user_id, pa.attribute_type, pa.attribute_value, pa.is_fake, u.first_name, u.username
            FROM player_attributes pa
            JOIN users u ON pa.user_id = u.id
            WHERE pa.game_id = $1 AND pa.is_revealed = 1
            ORDER BY u.first_name ASC, pa.id ASC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id)
            return [dict(r) for r in rows]

    async def set_fake_attribute(self, game_id: int, user_id: int, attr_type: str, fake_value: str) -> None:
        query = """
            UPDATE player_attributes 
            SET attribute_value = $1, is_fake = 1 
            WHERE game_id = $2 AND user_id = $3 AND attribute_type = $4;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, fake_value, game_id, user_id, attr_type)

    async def swap_attributes(self, game_id: int, user1_id: int, user2_id: int, attr_type: str) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                row1 = await conn.fetchrow(
                    "SELECT attribute_value, attribute_metadata FROM player_attributes WHERE game_id=$1 AND user_id=$2 AND attribute_type=$3",
                    game_id, user1_id, attr_type
                )
                row2 = await conn.fetchrow(
                    "SELECT attribute_value, attribute_metadata FROM player_attributes WHERE game_id=$1 AND user_id=$2 AND attribute_type=$3",
                    game_id, user2_id, attr_type
                )
                if not row1 or not row2:
                    return False

                await conn.execute(
                    "UPDATE player_attributes SET attribute_value=$1, attribute_metadata=$2 WHERE game_id=$3 AND user_id=$4 AND attribute_type=$5",
                    row2['attribute_value'], row2['attribute_metadata'], game_id, user1_id, attr_type
                )
                await conn.execute(
                    "UPDATE player_attributes SET attribute_value=$1, attribute_metadata=$2 WHERE game_id=$3 AND user_id=$4 AND attribute_type=$5",
                    row1['attribute_value'], row1['attribute_metadata'], game_id, user2_id, attr_type
                )
                return True

    # === CARDS ===
    async def assign_card(self, game_id: int, user_id: int, card_id: int) -> int:
        query = """
            INSERT INTO player_cards (game_id, user_id, card_id, is_used, obtained_at)
            VALUES ($1, $2, $3, 0, NOW())
            RETURNING id;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, game_id, user_id, card_id)

    async def get_player_cards(self, game_id: int, user_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT pc.id as player_card_id, pc.is_used, pc.used_at, pc.used_on_user_id,
                   c.id as card_id, c.name, c.description, c.rarity, c.power, c.card_type, c.effect_data
            FROM player_cards pc
            JOIN cards c ON pc.card_id = c.id
            WHERE pc.game_id = $1 AND pc.user_id = $2
            ORDER BY pc.id ASC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, user_id)
            return [dict(r) for r in rows]

    async def use_card(self, player_card_id: int, used_on_user_id: Optional[int] = None) -> None:
        query = """
            UPDATE player_cards 
            SET is_used = 1, used_at = NOW(), used_on_user_id = $1 
            WHERE id = $2;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, used_on_user_id, player_card_id)

    # === ABILITIES ===
    async def assign_ability(self, game_id: int, user_id: int, ability_id: int, uses: int = 1) -> int:
        query = """
            INSERT INTO player_abilities (game_id, user_id, ability_id, uses_remaining, is_blocked)
            VALUES ($1, $2, $3, $4, 0)
            RETURNING id;
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, game_id, user_id, ability_id, uses)

    async def get_player_abilities(self, game_id: int, user_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT pa.id as player_ability_id, pa.uses_remaining, pa.is_blocked, pa.blocked_until_round,
                   a.id as ability_id, a.name, a.description, a.ability_type, a.trigger_condition, a.power, a.effect_data
            FROM player_abilities pa
            JOIN abilities a ON pa.ability_id = a.id
            WHERE pa.game_id = $1 AND pa.user_id = $2
            ORDER BY pa.id ASC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, user_id)
            return [dict(r) for r in rows]

    async def use_ability(self, game_id: int, user_id: int, ability_id: int) -> bool:
        query = """
            UPDATE player_abilities 
            SET uses_remaining = uses_remaining - 1 
            WHERE game_id = $1 AND user_id = $2 AND ability_id = $3 AND uses_remaining > 0
            RETURNING id;
        """
        async with self.pool.acquire() as conn:
            res = await conn.fetchval(query, game_id, user_id, ability_id)
            return res is not None

    async def block_ability(self, game_id: int, user_id: int, ability_id: int, until_round: int) -> None:
        query = """
            UPDATE player_abilities 
            SET is_blocked = 1, blocked_until_round = $1 
            WHERE game_id = $2 AND user_id = $3 AND ability_id = $4;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, until_round, game_id, user_id, ability_id)

    async def unblock_abilities(self, game_id: int, current_round: int) -> None:
        query = """
            UPDATE player_abilities 
            SET is_blocked = 0, blocked_until_round = NULL 
            WHERE game_id = $1 AND is_blocked = 1 AND blocked_until_round <= $2;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, game_id, current_round)
