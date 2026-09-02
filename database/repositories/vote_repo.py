from typing import Optional, List, Dict, Any, Tuple
import asyncpg
from datetime import datetime, timezone
from models.game import VoteModel


class VoteRepository:
    def __init__(self, pool: Any):
        self.pool = pool

    async def submit_vote(
        self,
        game_id: int,
        round_number: int,
        voter_id: int,
        target_id: int,
        vote_weight: int = 1,
        **kwargs: Any
    ) -> bool:
        weight = kwargs.get("weight", vote_weight)
        async with self.pool.acquire() as conn:
            # Check if voter already voted in this round
            existing = await conn.fetchrow(
                "SELECT * FROM votes WHERE game_id = $1 AND round_number = $2 AND voter_id = $3;",
                game_id, round_number, voter_id
            )
            if existing:
                return False

            await conn.execute(
                """
                INSERT INTO votes (game_id, round_number, voter_id, target_id, vote_weight, is_valid, created_at)
                VALUES ($1, $2, $3, $4, $5, 1, NOW());
                """,
                game_id, round_number, voter_id, target_id, weight
            )
            return True

    async def get_votes_for_round(self, game_id: int, round_number: int) -> List[VoteModel]:
        query = "SELECT * FROM votes WHERE game_id = $1 AND round_number = $2 AND is_valid = 1;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, round_number)
            return [VoteModel.from_row(r) for r in rows]

    async def get_vote_counts(self, game_id: int, round_number: int) -> Dict[int, int]:
        query = """
            SELECT target_id, SUM(vote_weight) as total_votes
            FROM votes
            WHERE game_id = $1 AND round_number = $2 AND is_valid = 1
            GROUP BY target_id
            ORDER BY total_votes DESC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, round_number)
            return {r['target_id']: r['total_votes'] for r in rows}

    async def has_voted(self, game_id: int, round_number: int, voter_id: int) -> bool:
        query = """
            SELECT 1 FROM votes 
            WHERE game_id = $1 AND round_number = $2 AND voter_id = $3 AND is_valid = 1;
        """
        async with self.pool.acquire() as conn:
            val = await conn.fetchval(query, game_id, round_number, voter_id)
            return val is not None

    async def get_voter_count(self, game_id: int, round_number: int) -> int:
        query = "SELECT COUNT(*) FROM votes WHERE game_id = $1 AND round_number = $2 AND is_valid = 1;"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, game_id, round_number) or 0

    async def clear_round_votes(self, game_id: int, round_number: int) -> None:
        query = "DELETE FROM votes WHERE game_id = $1 AND round_number = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, game_id, round_number)

    async def get_elimination_candidate(self, game_id: int, round_number: int) -> Tuple[Optional[int], int, bool, List[int]]:
        """
        Returns (candidate_id, max_votes, is_tie, tied_candidate_ids).
        """
        counts = await self.get_vote_counts(game_id, round_number)
        if not counts:
            return None, 0, False, []

        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        max_votes = sorted_counts[0][1]
        
        tied = [uid for uid, v in sorted_counts if v == max_votes]
        is_tie = len(tied) > 1

        return (None if is_tie else tied[0]), max_votes, is_tie, tied
