"""
game/systems/scoring.py
Pure-function survival scoring for BUNKER players.

Score is NEVER shown to players directly — it is only used internally for
balance checking, final ranking, and the admin dashboard.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_APOCALYPSE_PROFESSION_BONUSES: dict[str, dict[str, int]] = {
    "nuclear": {
        "shifokor": 60,
        "jarroh": 60,
        "muhandis": 60,
        "fizik": 80,
        "energetik": 70,
        "harbiy": 50,
        "quruvchi": 40,
    },
    "virus": {
        "shifokor": 90,
        "jarroh": 85,
        "biolog": 80,
        "feldsher": 70,
        "kimyogar": 60,
        "veterinar": 50,
    },
    "flood": {
        "dengizchi": 80,
        "suvchi": 85,
        "gidrogeolog": 80,
        "santexnik": 70,
        "baliqchi": 60,
        "muhandis": 50,
    },
    "ice_age": {
        "energetik": 85,
        "elektrik": 80,
        "tikuvchi": 70,
        "mexanik": 65,
        "alpinist": 60,
        "oshpaz": 50,
    },
    "volcano": {
        "geolog": 80,
        "kimyogar": 75,
        "ekolog": 65,
        "quruvchi": 60,
    },
    "ai_takeover": {
        "dasturchi": 90,
        "it": 85,
        "elektrik": 65,
        "harbiy": 60,
    }
}


class ScoringSystem:
    """
    Calculates a deterministic survival score for a player.
    """

    @classmethod
    def calculate_survival_score(
        cls,
        player_attrs: dict[str, Any],
        apocalypse_type: str,
        bunker_config: dict[str, Any],
    ) -> int:
        breakdown = cls.get_score_breakdown(player_attrs, apocalypse_type, bunker_config)
        total = sum(breakdown.values())
        return max(0, min(1000, total))

    @classmethod
    def get_score_breakdown(
        cls,
        player_attrs: dict[str, Any],
        apocalypse_type: str,
        bunker_config: dict[str, Any],
    ) -> dict[str, int]:
        profession = str(player_attrs.get("profession", "")).lower()
        health = str(player_attrs.get("health", "")).lower()
        knowledge = str(player_attrs.get("knowledge", "")).lower()
        inventory = str(player_attrs.get("inventory", "")).lower()

        # 1. Profession score (50 - 200)
        prof_score = 100
        bonuses = _APOCALYPSE_PROFESSION_BONUSES.get(apocalypse_type, {})
        for key, bonus in bonuses.items():
            if key in profession:
                prof_score += bonus
                break

        # 2. Health score (20 - 150)
        health_score = 100
        if "a'lo" in health or "alo" in health:
            health_score = 150
        elif "yaxshi" in health:
            health_score = 120
        elif "o'rtacha" in health or "ortacha" in health:
            health_score = 80
        elif "zaif" in health:
            health_score = 40
        elif "virus" in health or "kasallik" in health:
            health_score = 20

        # 3. Knowledge score (30 - 100)
        know_score = 70
        if "tibbiyot" in knowledge:
            know_score = 95
        elif "texnika" in knowledge or "energetika" in knowledge:
            know_score = 90
        elif "qishloq" in knowledge or "biologiya" in knowledge:
            know_score = 85

        # 4. Inventory score (30 - 150)
        inv_score = 80
        if "to'liq" in inventory or "filtr" in inventory or "generator" in inventory or "noutbuk" in inventory:
            inv_score = 140
        elif "sumka" in inventory or "dori" in inventory or "urug'" in inventory:
            inv_score = 110

        # 5. Apocalypse fit (20 - 200)
        fit_score = 80
        if apocalypse_type == "virus" and "shifokor" in profession:
            fit_score = 180
        elif apocalypse_type == "nuclear" and ("fizik" in profession or "radiatsiya" in knowledge):
            fit_score = 180
        elif apocalypse_type == "flood" and ("dengizchi" in profession or "suv" in knowledge):
            fit_score = 180

        return {
            "profession_score": min(200, prof_score),
            "health_score": min(150, health_score),
            "knowledge_score": min(100, know_score),
            "inventory_score": min(150, inv_score),
            "apocalypse_fit": min(200, fit_score)
        }
