"""
utils/validators.py
BUNKER o'yini uchun amal va callback validatsiya funksiyalari.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.repositories.game_repository import GameRepository
    from core.repositories.player_repository import PlayerRepository


@dataclass(frozen=True)
class ValidationResult:
    """Validatsiya natijasi."""

    is_valid: bool
    error_message: str | None = None
    game: dict | None = None
    player: dict | None = None


async def validate_game_action(
    game_id: int,
    user_id: int,
    expected_phase: str | None,
    game_repo: "GameRepository",
    player_repo: "PlayerRepository",
) -> ValidationResult:
    """O'yin amalini tekshiradi: o'yin mavjudligi, o'yinchi holati, faza.

    Args:
        game_id: O'yin identifikatori.
        user_id: Foydalanuvchi identifikatori.
        expected_phase: Kutilgan o'yin fazasi (None = tekshirmaslik).
        game_repo: O'yin repository'si.
        player_repo: O'yinchi repository'si.

    Returns:
        ValidationResult with is_valid flag and optional error message.
    """
    game = await game_repo.get_by_id(game_id)
    if game is None:
        return ValidationResult(is_valid=False, error_message="O'yin topilmadi.")

    if game.get("status") not in ("ACTIVE", "LOBBY"):
        return ValidationResult(
            is_valid=False,
            error_message="O'yin hozir faol emas.",
        )

    player = await player_repo.get_player_in_game(user_id=user_id, game_id=game_id)
    if player is None:
        return ValidationResult(
            is_valid=False,
            error_message="Siz bu o'yinda qatnashmayapsiz.",
        )

    if player.get("status") == "ELIMINATED":
        return ValidationResult(
            is_valid=False,
            error_message="Siz o'yindan chiqarilgansiz.",
        )

    if expected_phase is not None and game.get("phase") != expected_phase:
        return ValidationResult(
            is_valid=False,
            error_message=f"Bu amal hozir bajarib bo'lmaydi. Joriy faza: {game.get('phase')}",
        )

    return ValidationResult(is_valid=True, game=game, player=player)


async def validate_callback_ownership(
    callback_user_id: int,
    target_user_id: int,
) -> bool:
    """Callback o'z egasiga tegishliligini tekshiradi.

    Args:
        callback_user_id: Callback'ni bosgan foydalanuvchi ID'si.
        target_user_id: Callback kutilayotgan foydalanuvchi ID'si.

    Returns:
        True agar callback to'g'ri foydalanuvchiga tegishli bo'lsa.
    """
    return callback_user_id == target_user_id


async def check_player_in_game(
    user_id: int,
    player_repo: "PlayerRepository",
) -> int | None:
    """Foydalanuvchi faol o'yinda qatnashayotganini tekshiradi.

    Args:
        user_id: Foydalanuvchi identifikatori.
        player_repo: O'yinchi repository'si.

    Returns:
        game_id agar o'yinchi faol o'yinda bo'lsa, aks holda None.
    """
    player = await player_repo.get_active_player(user_id=user_id)
    if player is None:
        return None
    return player.get("game_id")
