"""
game/systems/cards.py
Card system for BUNKER.

All user-facing messages are in Uzbek.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CardEffectType(Enum):
    PROTECT_SELF = "PROTECT_SELF"
    NULLIFY_VOTE = "NULLIFY_VOTE"
    REVEAL_ATTRIBUTE = "REVEAL_ATTRIBUTE"
    BLOCK_ABILITY = "BLOCK_ABILITY"
    SHIELD_NEXT_ROUND = "SHIELD_NEXT_ROUND"
    FAKE_ATTRIBUTE = "FAKE_ATTRIBUTE"
    SPY_VOTE = "SPY_VOTE"
    SWAP_ATTRIBUTE = "SWAP_ATTRIBUTE"
    REVENGE = "REVENGE"
    REVIVE = "REVIVE"
    DOUBLE_VOTE = "DOUBLE_VOTE"
    STEAL_CARD = "STEAL_CARD"
    EXPOSE_CARD = "EXPOSE_CARD"
    VOTE_IMMUNITY = "VOTE_IMMUNITY"
    EXTRA_ROUND = "EXTRA_ROUND"
    AMNESIA = "AMNESIA"
    TRANSFER_ATTRIBUTE = "TRANSFER_ATTRIBUTE"


@dataclass
class CardResult:
    """Outcome of :meth:`CardSystem.use_card`."""

    success: bool
    message_to_user: str
    effect: dict[str, Any] = field(default_factory=dict)
    public_event: str | None = None


# ---------------------------------------------------------------------------
# Card definitions  card_id -> metadata
# ---------------------------------------------------------------------------
CARD_DEFINITIONS: dict[str, dict[str, Any]] = {
    "protect_self": {
        "id": "protect_self",
        "name": "O'z-o'zini himoya qilish",
        "effect": CardEffectType.PROTECT_SELF,
        "rarity": "COMMON",
        "requires_target": False,
        "description": "Bu ovoz berish turida siz eliminatsiya qilinmaysiz.",
    },
    "nullify_vote": {
        "id": "nullify_vote",
        "name": "Ovozni nolga tushirish",
        "effect": CardEffectType.NULLIFY_VOTE,
        "rarity": "RARE",
        "requires_target": False,
        "description": "Bu tur uchun ovoz berish qaytadan boshlanadi.",
    },
    "reveal_attribute": {
        "id": "reveal_attribute",
        "name": "Atributni oshkor qilish",
        "effect": CardEffectType.REVEAL_ATTRIBUTE,
        "rarity": "COMMON",
        "requires_target": True,
        "description": "Maqsadning bitta atributini ko'rish imkoniyati.",
    },
    "block_ability": {
        "id": "block_ability",
        "name": "Qobiliyatni bloklash",
        "effect": CardEffectType.BLOCK_ABILITY,
        "rarity": "UNCOMMON",
        "requires_target": True,
        "description": "Maqsad 1 tur davomida qobiliyat ishlatishdan mahrum bo'ladi.",
    },
    "shield_next_round": {
        "id": "shield_next_round",
        "name": "Keyingi tur qalqoni",
        "effect": CardEffectType.SHIELD_NEXT_ROUND,
        "rarity": "UNCOMMON",
        "requires_target": False,
        "description": "Keyingi tur ovoz berish siyosatidan himoyalanasiz.",
    },
    "fake_attribute": {
        "id": "fake_attribute",
        "name": "Soxta atribut",
        "effect": CardEffectType.FAKE_ATTRIBUTE,
        "rarity": "RARE",
        "requires_target": False,
        "description": "Bitta atributingiz uchun boshqa o'yinchilarga soxta qiymat ko'rsatiladi.",
    },
    "spy_vote": {
        "id": "spy_vote",
        "name": "Ovozlarni kuzatish",
        "effect": CardEffectType.SPY_VOTE,
        "rarity": "UNCOMMON",
        "requires_target": False,
        "description": "Bu turda kim kimga ovoz berganini ko'rish imkoniyati.",
    },
    "swap_attribute": {
        "id": "swap_attribute",
        "name": "Atribut almashtirish",
        "effect": CardEffectType.SWAP_ATTRIBUTE,
        "rarity": "EPIC",
        "requires_target": True,
        "description": "O'zingizning bir atributingizni maqsad bilan almashtiradi.",
    },
    "revenge": {
        "id": "revenge",
        "name": "Qasos",
        "effect": CardEffectType.REVENGE,
        "rarity": "RARE",
        "requires_target": True,
        "description": "Agar siz eliminatsiya qilingan bo'lsangiz, maqsad 2 ta omon qolish ballini yo'qotadi.",
    },
    "revive": {
        "id": "revive",
        "name": "Tirilish",
        "effect": CardEffectType.REVIVE,
        "rarity": "LEGENDARY",
        "requires_target": False,
        "description": "Oxirgi eliminatsiya qilingan o'yinchini o'yinga qaytaradi.",
    },
    "double_vote": {
        "id": "double_vote",
        "name": "Ikki ovoz",
        "effect": CardEffectType.DOUBLE_VOTE,
        "rarity": "UNCOMMON",
        "requires_target": False,
        "description": "Bu turda sizning ovozingiz 2 ta hisoblanaudi.",
    },
    "steal_card": {
        "id": "steal_card",
        "name": "Karta o'g'irlash",
        "effect": CardEffectType.STEAL_CARD,
        "rarity": "EPIC",
        "requires_target": True,
        "description": "Maqsadning tasodifiy kartasini o'g'irlaydi.",
    },
    "expose_card": {
        "id": "expose_card",
        "name": "Kartani oshkor qilish",
        "effect": CardEffectType.EXPOSE_CARD,
        "rarity": "UNCOMMON",
        "requires_target": True,
        "description": "Maqsad o'z kartalaridan birini guruhga oshkor qilishga majbur bo'ladi.",
    },
    "vote_immunity": {
        "id": "vote_immunity",
        "name": "Ovoz immunitetи",
        "effect": CardEffectType.VOTE_IMMUNITY,
        "rarity": "RARE",
        "requires_target": False,
        "description": "Bu turda ovoz berish orqali eliminatsiya qilinmaysiz.",
    },
    "extra_round": {
        "id": "extra_round",
        "name": "Qo'shimcha tur",
        "effect": CardEffectType.EXTRA_ROUND,
        "rarity": "RARE",
        "requires_target": False,
        "description": "Ovoz berishdan oldin yana bir muhokama turi qo'shiladi.",
    },
    "amnesia": {
        "id": "amnesia",
        "name": "Amneziya",
        "effect": CardEffectType.AMNESIA,
        "rarity": "UNCOMMON",
        "requires_target": True,
        "description": "Maqsad bu turda hech qanday karta ishlatishdan mahrum bo'ladi.",
    },
    "transfer_attribute": {
        "id": "transfer_attribute",
        "name": "Atribut uzatish",
        "effect": CardEffectType.TRANSFER_ATTRIBUTE,
        "rarity": "LEGENDARY",
        "requires_target": True,
        "description": "O'zingizning bir atributingizni maqsadga doimiy ravishda berasiz.",
    },
}


class CardSystem:
    """
    Manages card assignment, usage, and effect application.

    Cards are referenced by ``player_card_id`` (unique per player per game),
    which maps to a ``card_id`` from CARD_DEFINITIONS.
    """

    def __init__(self) -> None:
        # {game_id -> {player_card_id -> {user_id, card_id, is_used}}}
        self._cards: dict[int, dict[int, dict[str, Any]]] = {}
        # {game_id -> {user_id -> set of card_ids blocked by AMNESIA}}
        self._amnesia: dict[int, dict[int, bool]] = {}
        # Counter for player_card_id generation
        self._next_pcid: dict[int, int] = {}
        # {game_id -> {user_id -> list of player_card_ids}}
        self._player_index: dict[int, dict[int, list[int]]] = {}

    # ------------------------------------------------------------------
    # Card assignment
    # ------------------------------------------------------------------

    def assign_card(self, game_id: int, user_id: int, card_id: str) -> int:
        """
        Assign *card_id* to *user_id* and return the unique ``player_card_id``.
        """
        pcid = self._next_pcid.get(game_id, 1)
        self._next_pcid[game_id] = pcid + 1
        self._cards.setdefault(game_id, {})[pcid] = {
            "player_card_id": pcid,
            "user_id": user_id,
            "card_id": card_id,
            "is_used": False,
        }
        self._player_index.setdefault(game_id, {}).setdefault(user_id, []).append(pcid)
        return pcid

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_player_cards(
        self, game_id: int, user_id: int
    ) -> list[dict[str, Any]]:
        """Return all card dicts for *user_id* in *game_id*."""
        pcids = self._player_index.get(game_id, {}).get(user_id, [])
        result = []
        for pcid in pcids:
            card_rec = self._cards.get(game_id, {}).get(pcid)
            if card_rec:
                defn = CARD_DEFINITIONS.get(card_rec["card_id"], {})
                result.append({**card_rec, **defn})
        return result

    def get_card_by_player_card_id(
        self, game_id: int, player_card_id: int
    ) -> dict[str, Any] | None:
        card_rec = self._cards.get(game_id, {}).get(player_card_id)
        if card_rec is None:
            return None
        defn = CARD_DEFINITIONS.get(card_rec["card_id"], {})
        return {**card_rec, **defn}

    # ------------------------------------------------------------------
    # Core use
    # ------------------------------------------------------------------

    def use_card(
        self,
        game_id: int,
        user_id: int,
        player_card_id: int,
        context: dict[str, Any],
        target_id: int | None = None,
    ) -> CardResult:
        """
        Attempt to use *player_card_id* on behalf of *user_id*.

        *context* must include:
        * ``phase``: str
        * ``alive_players``: list[dict]
        * ``vote_map``: dict[voter_id, target_id]
        * ``last_eliminated_id``: int | None
        """
        card = self.get_card_by_player_card_id(game_id, player_card_id)
        if card is None:
            return CardResult(success=False, message_to_user="❌ Karta topilmadi.")

        if card["user_id"] != user_id:
            return CardResult(success=False, message_to_user="❌ Bu karta sizniki emas.")

        if card["is_used"]:
            return CardResult(success=False, message_to_user="❌ Bu karta allaqachon ishlatilgan.")

        phase: str = context.get("phase", "")
        if phase in ("LOBBY", "FINISHED", "STARTING"):
            return CardResult(
                success=False, message_to_user="❌ Hozirgi bosqichda karta ishlatib bo'lmaydi."
            )

        # Amnesia check
        if self._amnesia.get(game_id, {}).get(user_id, False):
            return CardResult(
                success=False,
                message_to_user="❌ Bu turda amneziya tufayli karta ishlata olmaysiz.",
            )

        effect_type: CardEffectType = card["effect"]
        handler = self._effect_handlers.get(effect_type)
        if handler is None:
            return CardResult(
                success=False,
                message_to_user="❌ Bu karta effekti hali amalga oshirilmagan.",
            )

        result = handler(self, game_id, user_id, player_card_id, target_id, card, context)
        if result.success:
            self._cards[game_id][player_card_id]["is_used"] = True

        return result

    # ------------------------------------------------------------------
    # Effect handlers
    # ------------------------------------------------------------------

    def _handle_protect_self(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Bu ovoz berish turida siz eliminatsiya qilinmaysiz.",
            effect={"type": "PROTECT_FROM_VOTE", "target_id": user_id, "rounds": 1},
        )

    def _handle_nullify_vote(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Bu tur uchun ovoz berish qaytadan boshlanadi.",
            public_event="🔄 Bir o'yinchi ovoz berish turini bekor qildi! Qaytadan boshlanmoqda…",
            effect={"type": "NULLIFY_VOTE"},
        )

    def _handle_reveal_attribute(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        alive_players: list[dict] = context.get("alive_players", [])
        target_data = next((p for p in alive_players if p["user_id"] == target_id), None)
        if not target_data:
            return CardResult(success=False, message_to_user="❌ Maqsadli o'yinchi topilmadi.")
        attrs = target_data.get("attributes", {})
        if not attrs:
            return CardResult(success=False, message_to_user="❌ Ko'rinadigan atribut yo'q.")
        key = random.choice(list(attrs.keys()))
        val = attrs[key]
        return CardResult(
            success=True,
            message_to_user=f"🔍 O'yinchi #{target_id}: **{key}** = {val}",
            effect={"type": "REVEAL_ATTRIBUTE", "target_id": target_id, "key": key, "value": val, "private": True},
        )

    def _handle_block_ability(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        return CardResult(
            success=True,
            message_to_user=f"✅ O'yinchi #{target_id} 1 tur qobiliyat ishlatishdan mahrum.",
            effect={"type": "BLOCK_ABILITY", "target_id": target_id, "rounds": 1},
        )

    def _handle_shield_next_round(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Keyingi tur ovoz berish siyosatidan himoyalanasiz.",
            effect={"type": "PROTECT_FROM_VOTE", "target_id": user_id, "rounds": 2},
        )

    def _handle_fake_attribute(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Bir atributingiz uchun soxta qiymat ko'rsatiladi.",
            effect={"type": "FAKE_ATTRIBUTE", "user_id": user_id},
        )

    def _handle_spy_vote(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        vote_map: dict = context.get("vote_map", {})
        if not vote_map:
            return CardResult(
                success=True,
                message_to_user="🕵️ Hali hech kim ovoz bermagan.",
                effect={"type": "SPY_VOTE", "vote_map": {}},
            )
        lines = [f"O'yinchi #{v} → #{t}" for v, t in vote_map.items()]
        msg = "🕵️ Ovozlar:\n" + "\n".join(lines)
        return CardResult(
            success=True,
            message_to_user=msg,
            effect={"type": "SPY_VOTE", "vote_map": vote_map},
        )

    def _handle_swap_attribute(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        alive_players = context.get("alive_players", [])
        self_data = next((p for p in alive_players if p["user_id"] == user_id), None)
        target_data = next((p for p in alive_players if p["user_id"] == target_id), None)
        if not self_data or not target_data:
            return CardResult(success=False, message_to_user="❌ O'yinchi topilmadi.")
        common = list(set(self_data.get("attributes", {}).keys()) & set(target_data.get("attributes", {}).keys()))
        if not common:
            return CardResult(success=False, message_to_user="❌ Almashtirilishi mumkin atribut yo'q.")
        chosen = random.choice(common)
        return CardResult(
            success=True,
            message_to_user=f"✅ **{chosen}** atributi o'yinchi #{target_id} bilan almashtirildi.",
            public_event="🔄 Ikki o'yinchi o'rtasida atribut almashtirish amalga oshirildi!",
            effect={
                "type": "SWAP_ATTRIBUTE",
                "self_id": user_id,
                "target_id": target_id,
                "attribute_key": chosen,
                "self_value": self_data["attributes"][chosen],
                "target_value": target_data["attributes"][chosen],
            },
        )

    def _handle_revenge(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        return CardResult(
            success=True,
            message_to_user=f"⚔️ Agar siz eliminatsiya qilingan bo'lsangiz, #{target_id} 2 ball yo'qotadi.",
            effect={"type": "REVENGE", "user_id": user_id, "target_id": target_id, "penalty": 2},
        )

    def _handle_revive(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        last_elim: int | None = context.get("last_eliminated_id")
        if last_elim is None:
            return CardResult(
                success=False,
                message_to_user="❌ Tiriltirilishi mumkin o'yinchi yo'q.",
            )
        return CardResult(
            success=True,
            message_to_user=f"✨ O'yinchi #{last_elim} o'yinga qaytarildi!",
            public_event=f"✨ Mo''jiza! O'yinchi #{last_elim} o'yinga qaytdi!",
            effect={"type": "REVIVE", "target_id": last_elim},
        )

    def _handle_double_vote(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Bu turda sizning ovozingiz 2 ta hisoblanaudi.",
            effect={"type": "DOUBLE_VOTE", "user_id": user_id},
        )

    def _handle_steal_card(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        target_pcids = self._player_index.get(game_id, {}).get(target_id, [])
        unused = [
            p for p in target_pcids
            if not self._cards.get(game_id, {}).get(p, {}).get("is_used", True)
        ]
        if not unused:
            return CardResult(
                success=False,
                message_to_user=f"❌ O'yinchi #{target_id}ning foydalanilmagan kartasi yo'q.",
            )
        stolen_pcid = random.choice(unused)
        # Transfer ownership
        self._cards[game_id][stolen_pcid]["user_id"] = user_id
        self._player_index[game_id].setdefault(user_id, []).append(stolen_pcid)
        self._player_index[game_id][target_id].remove(stolen_pcid)
        stolen_card_id = self._cards[game_id][stolen_pcid]["card_id"]
        defn = CARD_DEFINITIONS.get(stolen_card_id, {})
        return CardResult(
            success=True,
            message_to_user=f"✅ O'yinchi #{target_id}dan **{defn.get('name', stolen_card_id)}** kartasi o'g'irlandi!",
            effect={"type": "STEAL_CARD", "from_id": target_id, "stolen_pcid": stolen_pcid},
        )

    def _handle_expose_card(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        target_pcids = self._player_index.get(game_id, {}).get(target_id, [])
        unused = [
            p for p in target_pcids
            if not self._cards.get(game_id, {}).get(p, {}).get("is_used", True)
        ]
        if not unused:
            return CardResult(
                success=False,
                message_to_user=f"❌ O'yinchi #{target_id}ning oshkor qilish uchun kartasi yo'q.",
            )
        expose_pcid = random.choice(unused)
        exposed_card_id = self._cards[game_id][expose_pcid]["card_id"]
        defn = CARD_DEFINITIONS.get(exposed_card_id, {})
        public_msg = f"🃏 O'yinchi #{target_id}ning kartasi: **{defn.get('name', exposed_card_id)}** — {defn.get('description', '')}"
        return CardResult(
            success=True,
            message_to_user=f"✅ {public_msg}",
            public_event=public_msg,
            effect={"type": "EXPOSE_CARD", "target_id": target_id, "exposed_card_id": exposed_card_id},
        )

    def _handle_vote_immunity(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Bu turda ovoz berish orqali eliminatsiya qilinmaysiz.",
            effect={"type": "PROTECT_FROM_VOTE", "target_id": user_id, "rounds": 1},
        )

    def _handle_extra_round(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        return CardResult(
            success=True,
            message_to_user="✅ Ovoz berishdan oldin yana bir muhokama turi qo'shildi.",
            public_event="⏳ Qo'shimcha muhokama turi boshlanmoqda!",
            effect={"type": "EXTRA_ROUND"},
        )

    def _handle_amnesia(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        self._amnesia.setdefault(game_id, {})[target_id] = True
        return CardResult(
            success=True,
            message_to_user=f"✅ O'yinchi #{target_id} bu turda karta ishlatishdan mahrum.",
            effect={"type": "AMNESIA", "target_id": target_id},
        )

    def _handle_transfer_attribute(
        self, game_id, user_id, pcid, target_id, card, context
    ) -> CardResult:
        if target_id is None:
            return CardResult(success=False, message_to_user="❌ Maqsad ko'rsatilmagan.")
        alive_players = context.get("alive_players", [])
        self_data = next((p for p in alive_players if p["user_id"] == user_id), None)
        if not self_data or not self_data.get("attributes"):
            return CardResult(success=False, message_to_user="❌ Berilishi mumkin atribut yo'q.")
        chosen = random.choice(list(self_data["attributes"].keys()))
        value = self_data["attributes"][chosen]
        return CardResult(
            success=True,
            message_to_user=f"✅ **{chosen}** atributi doimiy ravishda o'yinchi #{target_id}ga berildi.",
            effect={
                "type": "TRANSFER_ATTRIBUTE",
                "from_id": user_id,
                "target_id": target_id,
                "attribute_key": chosen,
                "attribute_value": value,
            },
        )

    _effect_handlers: dict[CardEffectType, Any] = {
        CardEffectType.PROTECT_SELF: _handle_protect_self,
        CardEffectType.NULLIFY_VOTE: _handle_nullify_vote,
        CardEffectType.REVEAL_ATTRIBUTE: _handle_reveal_attribute,
        CardEffectType.BLOCK_ABILITY: _handle_block_ability,
        CardEffectType.SHIELD_NEXT_ROUND: _handle_shield_next_round,
        CardEffectType.FAKE_ATTRIBUTE: _handle_fake_attribute,
        CardEffectType.SPY_VOTE: _handle_spy_vote,
        CardEffectType.SWAP_ATTRIBUTE: _handle_swap_attribute,
        CardEffectType.REVENGE: _handle_revenge,
        CardEffectType.REVIVE: _handle_revive,
        CardEffectType.DOUBLE_VOTE: _handle_double_vote,
        CardEffectType.STEAL_CARD: _handle_steal_card,
        CardEffectType.EXPOSE_CARD: _handle_expose_card,
        CardEffectType.VOTE_IMMUNITY: _handle_vote_immunity,
        CardEffectType.EXTRA_ROUND: _handle_extra_round,
        CardEffectType.AMNESIA: _handle_amnesia,
        CardEffectType.TRANSFER_ATTRIBUTE: _handle_transfer_attribute,
    }

    # ------------------------------------------------------------------
    # Round reset
    # ------------------------------------------------------------------

    def reset_round(self, game_id: int) -> None:
        """Clear per-round amnesia flags."""
        self._amnesia.pop(game_id, None)
