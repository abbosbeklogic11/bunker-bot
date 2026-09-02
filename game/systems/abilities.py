"""
game/systems/abilities.py
Special ability system for BUNKER.

All user-facing messages are in Uzbek.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AbilityEffectType(Enum):
    HEAL = "HEAL"
    DETECT = "DETECT"
    DOUBLE_VOTE = "DOUBLE_VOTE"
    CANCEL_VOTE = "CANCEL_VOTE"
    RANDOM_REVEAL = "RANDOM_REVEAL"
    PROTECT = "PROTECT"
    RANDOM_ABILITY = "RANDOM_ABILITY"
    SWAP_ATTRIBUTE = "SWAP_ATTRIBUTE"
    BLOCK = "BLOCK"
    OBSERVE = "OBSERVE"
    EXTRA_INFO = "EXTRA_INFO"


@dataclass
class AbilityResult:
    """Outcome of :meth:`AbilitySystem.use_ability`."""

    success: bool
    message_to_user: str  # private, in Uzbek
    public_event: str | None = None  # shown to group if not None
    effect: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ability definitions (ability_id -> metadata)
# ---------------------------------------------------------------------------
ABILITY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "heal": {
        "id": "heal",
        "name": "Shifo",
        "effect": AbilityEffectType.HEAL,
        "max_uses": 1,
        "requires_target": True,
        "rarity": "RARE",
        "description": "Maqsadli o'yinchini bu turda ovozdan himoya qiladi.",
    },
    "detect": {
        "id": "detect",
        "name": "Aniqlash",
        "effect": AbilityEffectType.DETECT,
        "max_uses": 2,
        "requires_target": True,
        "rarity": "UNCOMMON",
        "description": "Maqsadli o'yinchining yashirin atributlaridan birini ko'rsatadi.",
    },
    "double_vote": {
        "id": "double_vote",
        "name": "Ikki ovoz",
        "effect": AbilityEffectType.DOUBLE_VOTE,
        "max_uses": 2,
        "requires_target": False,
        "rarity": "UNCOMMON",
        "description": "Bu turda sizning ovozingiz 2 ta hisoblanaudi.",
    },
    "cancel_vote": {
        "id": "cancel_vote",
        "name": "Ovozni bekor qilish",
        "effect": AbilityEffectType.CANCEL_VOTE,
        "max_uses": 1,
        "requires_target": False,
        "rarity": "EPIC",
        "description": "Kelayotgan ovoz berish turini bekor qiladi.",
    },
    "random_reveal": {
        "id": "random_reveal",
        "name": "Tasodifiy oshkor",
        "effect": AbilityEffectType.RANDOM_REVEAL,
        "max_uses": 2,
        "requires_target": False,
        "rarity": "COMMON",
        "description": "Tasodifiy o'yinchining bir atributini oshkor qiladi.",
    },
    "protect": {
        "id": "protect",
        "name": "Himoya",
        "effect": AbilityEffectType.PROTECT,
        "max_uses": 1,
        "requires_target": True,
        "rarity": "RARE",
        "description": "Maqsad keyingi tur ovoz berish siyosatidan immunitetga ega bo'ladi.",
    },
    "random_ability": {
        "id": "random_ability",
        "name": "Tasodifiy qobiliyat",
        "effect": AbilityEffectType.RANDOM_ABILITY,
        "max_uses": 1,
        "requires_target": False,
        "rarity": "EPIC",
        "description": "Foydalanilmagan tasodifiy qobiliyat oladi.",
    },
    "swap_attribute": {
        "id": "swap_attribute",
        "name": "Atribut almashtirish",
        "effect": AbilityEffectType.SWAP_ATTRIBUTE,
        "max_uses": 1,
        "requires_target": True,
        "rarity": "LEGENDARY",
        "description": "O'zingizning bir atributingizni maqsad bilan almashtiradi.",
    },
    "block": {
        "id": "block",
        "name": "Bloklash",
        "effect": AbilityEffectType.BLOCK,
        "max_uses": 2,
        "requires_target": True,
        "rarity": "UNCOMMON",
        "description": "Bu turda maqsad qobiliyat ishlatishini oldini oladi.",
    },
    "observe": {
        "id": "observe",
        "name": "Kuzatish",
        "effect": AbilityEffectType.OBSERVE,
        "max_uses": 2,
        "requires_target": True,
        "rarity": "COMMON",
        "description": "Bu turda maqsad qaysi qobiliyatdan foydalanganini ko'radi.",
    },
    "extra_info": {
        "id": "extra_info",
        "name": "Qo'shimcha ma'lumot",
        "effect": AbilityEffectType.EXTRA_INFO,
        "max_uses": 2,
        "requires_target": True,
        "rarity": "UNCOMMON",
        "description": "Maqsadning omon qolish reytingini ko'radi (aniq ball emas).",
    },
}


class AbilitySystem:
    """
    Manages ability activation, usage tracking, and effect application.

    State is kept in memory per game.  Persisting used_abilities and
    blocked status to DB is the caller's responsibility via the effect dict.
    """

    def __init__(self) -> None:
        # {game_id -> {user_id -> {ability_id -> uses_remaining}}}
        self._uses: dict[int, dict[int, dict[str, int]]] = {}
        # {game_id -> {user_id -> set of ability_ids blocked this round}}
        self._blocked: dict[int, dict[int, set[str]]] = {}
        # {game_id -> {user_id -> ability_id used this round}} (for OBSERVE)
        self._used_this_round: dict[int, dict[int, str]] = {}

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_player_ability(
        self, game_id: int, user_id: int, ability_id: str
    ) -> None:
        """Register an ability for a player with its full uses."""
        defn = ABILITY_DEFINITIONS.get(ability_id)
        if defn is None:
            return
        self._uses.setdefault(game_id, {}).setdefault(user_id, {})[ability_id] = defn[
            "max_uses"
        ]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_available_abilities(
        self, game_id: int, user_id: int
    ) -> list[dict[str, Any]]:
        """Return ability dicts for abilities the player still has uses for."""
        player_uses = self._uses.get(game_id, {}).get(user_id, {})
        result: list[dict[str, Any]] = []
        for ability_id, remaining in player_uses.items():
            if remaining > 0:
                defn = ABILITY_DEFINITIONS.get(ability_id)
                if defn:
                    result.append({**defn, "remaining_uses": remaining})
        return result

    def has_remaining_uses(
        self, game_id: int, user_id: int, ability_id: str
    ) -> bool:
        return self._uses.get(game_id, {}).get(user_id, {}).get(ability_id, 0) > 0

    def is_ability_blocked(
        self, game_id: int, user_id: int, ability_id: str
    ) -> bool:
        return ability_id in self._blocked.get(game_id, {}).get(user_id, set())

    # ------------------------------------------------------------------
    # Core use
    # ------------------------------------------------------------------

    def use_ability(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        """
        Attempt to activate *ability_id* for *user_id* against *target_id*.

        *context* must include:
        * ``alive_players``: list[dict] with ``user_id`` and ``attributes``
        * ``round_num``: int
        * ``survival_scores``: dict[user_id, int] (for EXTRA_INFO)
        * ``phase``: str
        """
        defn = ABILITY_DEFINITIONS.get(ability_id)
        if defn is None:
            return AbilityResult(
                success=False,
                message_to_user="❌ Noma'lum qobiliyat.",
            )

        if not self.has_remaining_uses(game_id, user_id, ability_id):
            return AbilityResult(
                success=False,
                message_to_user="❌ Bu qobiliyatning foydalanish limiti tugadi.",
            )

        if self.is_ability_blocked(game_id, user_id, ability_id):
            return AbilityResult(
                success=False,
                message_to_user="❌ Bu turda qobiliyatingiz bloklangan.",
            )

        effect_type: AbilityEffectType = defn["effect"]
        handler = self._effect_handlers.get(effect_type)
        if handler is None:
            return AbilityResult(
                success=False,
                message_to_user="❌ Bu qobiliyat hali amalga oshirilmagan.",
            )

        result = handler(self, game_id, user_id, ability_id, target_id, context)

        if result.success:
            # Consume one use
            self._uses[game_id][user_id][ability_id] -= 1
            # Track for OBSERVE
            self._used_this_round.setdefault(game_id, {})[user_id] = ability_id

        return result

    # ------------------------------------------------------------------
    # Effect handlers
    # ------------------------------------------------------------------

    def _handle_heal(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        return AbilityResult(
            success=True,
            message_to_user=f"✅ O'yinchi #{target_id} bu turda ovozdan himoya qilindi.",
            public_event=None,
            effect={"type": "PROTECT_FROM_VOTE", "target_id": target_id, "rounds": 1},
        )

    def _handle_detect(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        alive_players: list[dict[str, Any]] = context.get("alive_players", [])
        target_data = next(
            (p for p in alive_players if p["user_id"] == target_id), None
        )
        if target_data is None:
            return AbilityResult(
                success=False, message_to_user="❌ Maqsadli o'yinchi topilmadi."
            )

        attrs: dict[str, Any] = target_data.get("attributes", {})
        hidden_keys = [k for k, v in attrs.items() if not target_data.get("revealed", {}).get(k, False)]
        if not hidden_keys:
            return AbilityResult(
                success=False,
                message_to_user="❌ Bu o'yinchining yashirin atributlari yo'q.",
            )

        revealed_key = random.choice(hidden_keys)
        revealed_value = attrs[revealed_key]
        return AbilityResult(
            success=True,
            message_to_user=(
                f"🔍 O'yinchi #{target_id}ning yashirin atributi: "
                f"**{revealed_key}** = {revealed_value}"
            ),
            public_event=None,
            effect={
                "type": "REVEAL_ATTRIBUTE",
                "target_id": target_id,
                "attribute_key": revealed_key,
                "attribute_value": revealed_value,
                "private": True,
            },
        )

    def _handle_double_vote(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        return AbilityResult(
            success=True,
            message_to_user="✅ Bu turda sizning ovozingiz 2 ta hisoblanaudi.",
            public_event=None,
            effect={"type": "DOUBLE_VOTE", "user_id": user_id},
        )

    def _handle_cancel_vote(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        return AbilityResult(
            success=True,
            message_to_user="✅ Kelayotgan ovoz berish turi bekor qilindi.",
            public_event="⚡ Bir o'yinchi bu turning ovoz berish bosqichini bekor qildi!",
            effect={"type": "CANCEL_VOTE", "round": context.get("round_num")},
        )

    def _handle_random_reveal(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        alive_players: list[dict[str, Any]] = context.get("alive_players", [])
        others = [p for p in alive_players if p["user_id"] != user_id]
        if not others:
            return AbilityResult(
                success=False, message_to_user="❌ Boshqa o'yinchilar yo'q."
            )

        victim = random.choice(others)
        attrs = victim.get("attributes", {})
        hidden_keys = list(attrs.keys())
        if not hidden_keys:
            return AbilityResult(
                success=False, message_to_user="❌ Oshkor qilish uchun atribut topilmadi."
            )

        revealed_key = random.choice(hidden_keys)
        revealed_value = attrs[revealed_key]
        victim_id = victim["user_id"]
        public_msg = f"🎲 Tasodifiy oshkor: O'yinchi #{victim_id}ning **{revealed_key}** = {revealed_value}"
        return AbilityResult(
            success=True,
            message_to_user=f"✅ {public_msg}",
            public_event=public_msg,
            effect={
                "type": "REVEAL_ATTRIBUTE",
                "target_id": victim_id,
                "attribute_key": revealed_key,
                "attribute_value": revealed_value,
                "private": False,
            },
        )

    def _handle_protect(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        return AbilityResult(
            success=True,
            message_to_user=f"✅ O'yinchi #{target_id} keyingi tur ovoz berish siyosatidan immunitetga ega.",
            public_event=None,
            effect={"type": "PROTECT_FROM_VOTE", "target_id": target_id, "rounds": 2},
        )

    def _handle_random_ability(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        player_abilities = set(self._uses.get(game_id, {}).get(user_id, {}).keys())
        candidates = [
            aid
            for aid in ABILITY_DEFINITIONS
            if aid != "random_ability" and aid not in player_abilities
        ]
        if not candidates:
            return AbilityResult(
                success=False,
                message_to_user="❌ Olish uchun yangi qobiliyat yo'q.",
            )
        new_ability_id = random.choice(candidates)
        defn = ABILITY_DEFINITIONS[new_ability_id]
        self._uses.setdefault(game_id, {}).setdefault(user_id, {})[new_ability_id] = defn["max_uses"]
        return AbilityResult(
            success=True,
            message_to_user=f"✅ Yangi qobiliyat olindi: **{defn['name']}** — {defn['description']}",
            public_event=None,
            effect={"type": "GRANT_ABILITY", "ability_id": new_ability_id, "user_id": user_id},
        )

    def _handle_swap_attribute(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        alive_players: list[dict[str, Any]] = context.get("alive_players", [])
        self_data = next((p for p in alive_players if p["user_id"] == user_id), None)
        target_data = next((p for p in alive_players if p["user_id"] == target_id), None)
        if not self_data or not target_data:
            return AbilityResult(success=False, message_to_user="❌ O'yinchi topilmadi.")

        self_attrs = self_data.get("attributes", {})
        target_attrs = target_data.get("attributes", {})
        swappable = list(set(self_attrs.keys()) & set(target_attrs.keys()))
        if not swappable:
            return AbilityResult(success=False, message_to_user="❌ Almashtirilishi mumkin atribut yo'q.")

        chosen = random.choice(swappable)
        return AbilityResult(
            success=True,
            message_to_user=f"✅ **{chosen}** atributi o'yinchi #{target_id} bilan almashtirildi.",
            public_event=f"🔄 Ikki o'yinchi o'rtasida atribut almashtirish amalga oshirildi!",
            effect={
                "type": "SWAP_ATTRIBUTE",
                "self_id": user_id,
                "target_id": target_id,
                "attribute_key": chosen,
                "self_value": self_attrs[chosen],
                "target_value": target_attrs[chosen],
            },
        )

    def _handle_block(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        # Block ALL abilities for target this round
        self._blocked.setdefault(game_id, {}).setdefault(target_id, set()).update(
            ABILITY_DEFINITIONS.keys()
        )
        return AbilityResult(
            success=True,
            message_to_user=f"✅ O'yinchi #{target_id} bu turda qobiliyat ishlatishdan bloklandi.",
            public_event=None,
            effect={"type": "BLOCK", "target_id": target_id},
        )

    def _handle_observe(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        used_ability = self._used_this_round.get(game_id, {}).get(target_id)
        if used_ability:
            defn = ABILITY_DEFINITIONS.get(used_ability, {})
            name = defn.get("name", used_ability)
            msg = f"🔭 O'yinchi #{target_id} bu turda **{name}** qobiliyatidan foydalandi."
        else:
            msg = f"🔭 O'yinchi #{target_id} bu turda hech qanday qobiliyat ishlatmadi."
        return AbilityResult(
            success=True,
            message_to_user=msg,
            public_event=None,
            effect={"type": "OBSERVE", "target_id": target_id, "observed_ability": used_ability},
        )

    def _handle_extra_info(
        self,
        game_id: int,
        user_id: int,
        ability_id: str,
        target_id: int,
        context: dict[str, Any],
    ) -> AbilityResult:
        scores: dict[int, int] = context.get("survival_scores", {})
        alive_players: list[dict[str, Any]] = context.get("alive_players", [])
        alive_ids = [p["user_id"] for p in alive_players]
        sorted_ids = sorted(alive_ids, key=lambda uid: scores.get(uid, 0), reverse=True)

        try:
            rank = sorted_ids.index(target_id) + 1
        except ValueError:
            rank = len(sorted_ids)

        total = len(sorted_ids)
        if rank <= total // 3:
            label = "Yuqori"
        elif rank <= 2 * total // 3:
            label = "O'rta"
        else:
            label = "Quyi"

        return AbilityResult(
            success=True,
            message_to_user=(
                f"📊 O'yinchi #{target_id} omon qolish reytingi: **{label}** "
                f"({rank}/{total} o'rinlar orasida)"
            ),
            public_event=None,
            effect={"type": "EXTRA_INFO", "target_id": target_id, "rank": rank},
        )

    # Map effect types to handlers
    _effect_handlers: dict[AbilityEffectType, Any] = {
        AbilityEffectType.HEAL: _handle_heal,
        AbilityEffectType.DETECT: _handle_detect,
        AbilityEffectType.DOUBLE_VOTE: _handle_double_vote,
        AbilityEffectType.CANCEL_VOTE: _handle_cancel_vote,
        AbilityEffectType.RANDOM_REVEAL: _handle_random_reveal,
        AbilityEffectType.PROTECT: _handle_protect,
        AbilityEffectType.RANDOM_ABILITY: _handle_random_ability,
        AbilityEffectType.SWAP_ATTRIBUTE: _handle_swap_attribute,
        AbilityEffectType.BLOCK: _handle_block,
        AbilityEffectType.OBSERVE: _handle_observe,
        AbilityEffectType.EXTRA_INFO: _handle_extra_info,
    }

    # ------------------------------------------------------------------
    # Round reset
    # ------------------------------------------------------------------

    def reset_round(self, game_id: int) -> None:
        """Clear per-round tracking (blocked, used this round)."""
        self._blocked.pop(game_id, None)
        self._used_this_round.pop(game_id, None)
