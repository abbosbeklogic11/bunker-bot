"""
Balance engine module for BUNKER game.
Controls ability distribution according to profession affinities and balances game settings.
"""
from typing import Dict, Any, List, Optional
import random
from game.data import ABILITY_DEFINITIONS, CARD_DEFINITIONS, APOCALYPSE_SCENARIOS, BUNKER_CONFIGS


class BalanceEngine:
    @staticmethod
    def select_abilities_for_player(
        profession_name: str,
        character_name: str,
        assigned_ability_ids: List[int],
        max_abilities: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Picks abilities for a player giving preference to profession-affinity abilities.
        """
        chosen = []
        
        # 1. Look for profession affinity match
        matching = [
            a for a in ABILITY_DEFINITIONS
            if any(p.lower() in profession_name.lower() for p in a.get("profession_affinity", []))
            and a["id"] not in assigned_ability_ids
        ]

        if matching:
            chosen.append(random.choice(matching))

        # 2. Fill remaining slots if any
        while len(chosen) < max_abilities:
            available = [a for a in ABILITY_DEFINITIONS if a["id"] not in assigned_ability_ids and a not in chosen]
            if not available:
                available = ABILITY_DEFINITIONS
            chosen.append(random.choice(available))

        return chosen

    @staticmethod
    def get_apocalypse() -> Dict[str, Any]:
        return random.choice(APOCALYPSE_SCENARIOS)

    @staticmethod
    def get_bunker_config() -> Dict[str, Any]:
        return random.choice(BUNKER_CONFIGS)
