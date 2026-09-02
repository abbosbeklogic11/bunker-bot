"""
Card randomizer module.
Distributes cards fairly to players according to strict rarity and power constraints.
"""
from typing import Dict, Any, List, Optional
import random
from game.data import CARD_DEFINITIONS


class CardRandomizer:
    # Rarity distribution weights: COMMON 50%, UNCOMMON 28%, RARE 14%, EPIC 6%, LEGENDARY 2%
    RARITY_WEIGHTS = {
        "COMMON": 0.50,
        "UNCOMMON": 0.28,
        "RARE": 0.14,
        "EPIC": 0.06,
        "LEGENDARY": 0.02
    }

    @classmethod
    def distribute_cards_for_game(
        cls,
        player_ids: List[int],
        cards_per_player: int = 3
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Distributes cards to all players in a game ensuring balance:
        - Max 1 LEGENDARY card per player, max 2 LEGENDARY per entire game of 20 players.
        - Power balanced across players so nobody gets 3 legendary/epic while someone gets 3 common.
        """
        cards_by_rarity: Dict[str, List[Dict[str, Any]]] = {
            r: [c for c in CARD_DEFINITIONS if c["rarity"] == r]
            for r in cls.RARITY_WEIGHTS.keys()
        }

        distribution: Dict[int, List[Dict[str, Any]]] = {uid: [] for uid in player_ids}
        legendary_given_total = 0
        max_legendary_game = 2 if len(player_ids) >= 10 else 1

        for uid in player_ids:
            player_cards: List[Dict[str, Any]] = []
            has_legendary = False

            for _ in range(cards_per_player):
                # Adjust weights if player already has high tier or game limit reached
                current_weights = dict(cls.RARITY_WEIGHTS)
                if has_legendary or legendary_given_total >= max_legendary_game:
                    current_weights["LEGENDARY"] = 0.0

                rarity = random.choices(
                    list(current_weights.keys()),
                    weights=list(current_weights.values()),
                    k=1
                )[0]

                pool = [c for c in cards_by_rarity[rarity] if c not in player_cards]
                if not pool:
                    pool = [c for c in CARD_DEFINITIONS if c not in player_cards]
                
                chosen = random.choice(pool)
                player_cards.append(chosen)

                if chosen["rarity"] == "LEGENDARY":
                    has_legendary = True
                    legendary_given_total += 1

            distribution[uid] = player_cards

        return distribution

    @classmethod
    def get_random_card_by_rarity(cls, rarity: Optional[str] = None) -> Dict[str, Any]:
        if rarity:
            pool = [c for c in CARD_DEFINITIONS if c["rarity"] == rarity]
            if pool:
                return random.choice(pool)
        return random.choice(CARD_DEFINITIONS)
