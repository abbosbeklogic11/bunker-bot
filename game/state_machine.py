"""
game/state_machine.py
Finite-state machine for BUNKER game phases.
"""
from __future__ import annotations

from enum import Enum
from typing import Any


class GamePhase(Enum):
    """All valid phases of a BUNKER game session."""

    LOBBY = "LOBBY"
    STARTING = "STARTING"
    DEAL_CARDS = "DEAL_CARDS"
    REVEAL_ATTRIBUTE = "REVEAL_ATTRIBUTE"
    DISCUSSION = "DISCUSSION"
    ABILITY_PHASE = "ABILITY_PHASE"
    VOTING = "VOTING"
    DUEL = "DUEL"
    ELIMINATION = "ELIMINATION"
    EVENT = "EVENT"
    CHECK_WIN = "CHECK_WIN"
    FINAL = "FINAL"
    REWARDS = "REWARDS"
    FINISHED = "FINISHED"


class StateMachine:
    """
    Validates and suggests phase transitions for a game session.

    ``TRANSITIONS`` maps each phase to the list of phases it is allowed
    to move into.  ``get_next_phase`` uses runtime context (alive count,
    bunker capacity, etc.) to choose the single correct next phase.
    """

    TRANSITIONS: dict[GamePhase, list[GamePhase]] = {
        GamePhase.LOBBY: [GamePhase.STARTING, GamePhase.FINISHED],
        GamePhase.STARTING: [GamePhase.DEAL_CARDS, GamePhase.FINISHED],
        GamePhase.DEAL_CARDS: [GamePhase.REVEAL_ATTRIBUTE, GamePhase.FINISHED],
        GamePhase.REVEAL_ATTRIBUTE: [GamePhase.DISCUSSION, GamePhase.FINISHED],
        GamePhase.DISCUSSION: [GamePhase.ABILITY_PHASE, GamePhase.VOTING, GamePhase.FINISHED],
        GamePhase.ABILITY_PHASE: [GamePhase.VOTING, GamePhase.FINISHED],
        GamePhase.VOTING: [
            GamePhase.DUEL,
            GamePhase.ELIMINATION,
            GamePhase.FINISHED,
        ],
        GamePhase.DUEL: [GamePhase.ELIMINATION, GamePhase.FINISHED],
        GamePhase.ELIMINATION: [GamePhase.EVENT, GamePhase.CHECK_WIN, GamePhase.FINISHED],
        GamePhase.EVENT: [GamePhase.CHECK_WIN, GamePhase.FINISHED],
        GamePhase.CHECK_WIN: [
            GamePhase.REVEAL_ATTRIBUTE,
            GamePhase.FINAL,
            GamePhase.FINISHED,
        ],
        GamePhase.FINAL: [GamePhase.REWARDS],
        GamePhase.REWARDS: [GamePhase.FINISHED],
        GamePhase.FINISHED: [],
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def can_transition(self, current: GamePhase, target: GamePhase) -> bool:
        """Return True if moving from *current* to *target* is allowed."""
        return target in self.TRANSITIONS.get(current, [])

    def get_next_phase(self, current: GamePhase, context: dict[str, Any]) -> GamePhase:
        """
        Determine the single correct next phase given runtime *context*.

        Expected context keys
        ----------------------
        alive_count      : int  – number of surviving players
        bunker_capacity  : int  – how many players can enter the bunker
        has_tie          : bool – voting ended in a tie
        has_event        : bool – an event was rolled this round
        round_number     : int  – current round (1-based)
        """
        alive: int = context.get("alive_count", 0)
        capacity: int = context.get("bunker_capacity", 4)
        has_tie: bool = context.get("has_tie", False)
        has_event: bool = context.get("has_event", False)

        if current == GamePhase.LOBBY:
            return GamePhase.STARTING

        if current == GamePhase.STARTING:
            return GamePhase.DEAL_CARDS

        if current == GamePhase.DEAL_CARDS:
            return GamePhase.REVEAL_ATTRIBUTE

        if current == GamePhase.REVEAL_ATTRIBUTE:
            return GamePhase.DISCUSSION

        if current == GamePhase.DISCUSSION:
            return GamePhase.ABILITY_PHASE

        if current == GamePhase.ABILITY_PHASE:
            return GamePhase.VOTING

        if current == GamePhase.VOTING:
            if has_tie:
                return GamePhase.DUEL
            return GamePhase.ELIMINATION

        if current == GamePhase.DUEL:
            return GamePhase.ELIMINATION

        if current == GamePhase.ELIMINATION:
            if has_event:
                return GamePhase.EVENT
            return GamePhase.CHECK_WIN

        if current == GamePhase.EVENT:
            return GamePhase.CHECK_WIN

        if current == GamePhase.CHECK_WIN:
            if alive <= capacity:
                return GamePhase.FINAL
            return GamePhase.REVEAL_ATTRIBUTE

        if current == GamePhase.FINAL:
            return GamePhase.REWARDS

        if current == GamePhase.REWARDS:
            return GamePhase.FINISHED

        return GamePhase.FINISHED

    def assert_transition(self, current: GamePhase, target: GamePhase) -> None:
        """Raise ``ValueError`` if the transition is not allowed."""
        if not self.can_transition(current, target):
            raise ValueError(
                f"Invalid transition: {current.value} -> {target.value}. "
                f"Allowed: {[p.value for p in self.TRANSITIONS.get(current, [])]}"
            )
