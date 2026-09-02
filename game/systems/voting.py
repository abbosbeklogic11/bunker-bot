"""
game/systems/voting.py
Voting, duel, and elimination logic for BUNKER.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class VoteResult(Enum):
    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    INVALID_TARGET = "INVALID_TARGET"
    PHASE_ERROR = "PHASE_ERROR"
    SELF_VOTE = "SELF_VOTE"
    BLOCKED = "BLOCKED"


@dataclass
class EliminationResult:
    """Result of a completed voting or duel round."""

    winner: int | None  # user_id of eliminated player, or None if tie unresolved
    vote_count: int
    is_tie: bool
    tied_players: list[int] = field(default_factory=list)


class VotingSystem:
    """
    Manages voting state in memory.

    All vote data is stored in ``_votes`` as::

        {game_id: {round_num: {voter_id: (target_id, weight)}}}

    Duel votes are stored in ``_duel_votes`` as::

        {game_id: {round_num: {voter_id: target_id}}}

    Protected players (set via :meth:`protect_player`) cannot be eliminated
    even if they accumulate the most votes.
    """

    def __init__(self) -> None:
        # {game_id -> {round_num -> {voter_id -> (target_id, weight)}}}
        self._votes: dict[int, dict[int, dict[int, tuple[int, int]]]] = {}
        # {game_id -> {round_num -> {voter_id -> target_id}}}
        self._duel_votes: dict[int, dict[int, dict[int, int]]] = {}
        # {game_id -> set of protected user_ids}
        self._protected: dict[int, set[int]] = {}
        # {game_id -> set of double-vote user_ids for current round}
        self._double_voters: dict[int, set[int]] = {}

    # ------------------------------------------------------------------
    # Protection
    # ------------------------------------------------------------------

    def protect_player(self, game_id: int, user_id: int) -> None:
        self._protected.setdefault(game_id, set()).add(user_id)

    def clear_protection(self, game_id: int, user_id: int) -> None:
        self._protected.get(game_id, set()).discard(user_id)

    def is_protected(self, game_id: int, user_id: int) -> bool:
        return user_id in self._protected.get(game_id, set())

    def set_double_vote(self, game_id: int, user_id: int) -> None:
        self._double_voters.setdefault(game_id, set()).add(user_id)

    # ------------------------------------------------------------------
    # Voting
    # ------------------------------------------------------------------

    def process_vote(
        self,
        game_id: int,
        round_num: int,
        voter_id: int,
        target_id: int,
        alive_players: list[int],
        vote_weight: int = 1,
    ) -> VoteResult:
        """
        Record a vote from *voter_id* targeting *target_id*.

        Returns a :class:`VoteResult` enum value.
        """
        if voter_id == target_id:
            return VoteResult.SELF_VOTE

        if target_id not in alive_players:
            return VoteResult.INVALID_TARGET

        round_votes = self._votes.setdefault(game_id, {}).setdefault(round_num, {})

        if voter_id in round_votes:
            return VoteResult.DUPLICATE

        weight = vote_weight
        if voter_id in self._double_voters.get(game_id, set()):
            weight = 2

        round_votes[voter_id] = (target_id, weight)
        logger.info(
            "Vote recorded: game=%s round=%s voter=%s -> target=%s (weight=%s)",
            game_id,
            round_num,
            voter_id,
            target_id,
            weight,
        )
        return VoteResult.ACCEPTED

    def get_current_results(
        self, game_id: int, round_num: int
    ) -> list[tuple[int, int]]:
        """
        Return list of (target_id, total_votes) sorted descending by vote count.
        """
        round_votes = self._votes.get(game_id, {}).get(round_num, {})
        tally: dict[int, int] = {}
        for _voter, (target, weight) in round_votes.items():
            tally[target] = tally.get(target, 0) + weight
        return sorted(tally.items(), key=lambda x: x[1], reverse=True)

    def get_vote_count(self, game_id: int, round_num: int) -> int:
        """Number of votes cast so far this round."""
        return len(self._votes.get(game_id, {}).get(round_num, {}))

    def finalize_voting(
        self,
        game_id: int,
        round_num: int,
        alive_players: list[int],
    ) -> EliminationResult:
        """
        Finalize the voting round.

        * Skip protected players even if they have the most votes.
        * If the top two have equal votes -> tie.
        """
        results = self.get_current_results(game_id, round_num)

        # Filter out protected players
        protected = self._protected.get(game_id, set())
        unprotected_results = [(uid, cnt) for uid, cnt in results if uid not in protected]

        if not unprotected_results:
            # Everyone is protected or no votes cast
            return EliminationResult(winner=None, vote_count=0, is_tie=False)

        top_count = unprotected_results[0][1]
        top_players = [uid for uid, cnt in unprotected_results if cnt == top_count]

        if len(top_players) > 1:
            return EliminationResult(
                winner=None,
                vote_count=top_count,
                is_tie=True,
                tied_players=top_players,
            )

        winner = top_players[0]
        # Clear double-vote flags for this game after finalization
        self._double_voters.pop(game_id, None)
        return EliminationResult(winner=winner, vote_count=top_count, is_tie=False)

    # ------------------------------------------------------------------
    # Duel
    # ------------------------------------------------------------------

    def process_duel_vote(
        self,
        game_id: int,
        round_num: int,
        voter_id: int,
        target_id: int,
        tied_players: list[int],
        alive_players: list[int],
    ) -> VoteResult:
        """Record a duel vote. Voters must be alive; target must be in tied_players."""
        if voter_id == target_id:
            return VoteResult.SELF_VOTE

        if target_id not in tied_players:
            return VoteResult.INVALID_TARGET

        if voter_id not in alive_players:
            return VoteResult.INVALID_TARGET

        duel_round = self._duel_votes.setdefault(game_id, {}).setdefault(round_num, {})
        if voter_id in duel_round:
            return VoteResult.DUPLICATE

        duel_round[voter_id] = target_id
        return VoteResult.ACCEPTED

    def get_duel_vote_count(self, game_id: int, round_num: int) -> int:
        return len(self._duel_votes.get(game_id, {}).get(round_num, {}))

    def finalize_duel(
        self,
        game_id: int,
        round_num: int,
        tied_players: list[int],
    ) -> EliminationResult:
        """
        Finalize the duel sub-round.

        If still tied, the engine should randomly select an elimination target.
        """
        duel_round = self._duel_votes.get(game_id, {}).get(round_num, {})
        tally: dict[int, int] = {}
        for target in duel_round.values():
            tally[target] = tally.get(target, 0) + 1

        if not tally:
            return EliminationResult(
                winner=None,
                vote_count=0,
                is_tie=True,
                tied_players=tied_players,
            )

        top_count = max(tally.values())
        top_players = [uid for uid, cnt in tally.items() if cnt == top_count]

        if len(top_players) > 1:
            return EliminationResult(
                winner=None,
                vote_count=top_count,
                is_tie=True,
                tied_players=top_players,
            )

        return EliminationResult(
            winner=top_players[0], vote_count=top_count, is_tie=False
        )

    # ------------------------------------------------------------------
    # Admin helpers
    # ------------------------------------------------------------------

    def get_voter_map(
        self, game_id: int, round_num: int
    ) -> dict[int, int]:
        """Return {voter_id: target_id} for current round (admin/spy use)."""
        round_votes = self._votes.get(game_id, {}).get(round_num, {})
        return {voter: target for voter, (target, _) in round_votes.items()}

    def clear_game(self, game_id: int) -> None:
        """Remove all voting state for a finished game."""
        self._votes.pop(game_id, None)
        self._duel_votes.pop(game_id, None)
        self._protected.pop(game_id, None)
        self._double_voters.pop(game_id, None)
