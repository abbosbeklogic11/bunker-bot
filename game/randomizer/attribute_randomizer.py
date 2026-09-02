"""
Attribute randomizer module.
Generates balanced, believable, and varied attributes for players in a BUNKER game.
"""
from typing import Dict, Any, List, Optional
import random
from game.data import (
    PROFESSIONS, HEALTH_STATES, CHARACTERS, HOBBIES,
    KNOWLEDGE_DOMAINS, GENETICS_TRAITS, INVENTORY_ITEMS, PHYSICAL_STATES
)


class AttributeRandomizer:
    @staticmethod
    def generate_player_attributes(
        player_index: int,
        total_players: int,
        existing_professions: List[str],
        apocalypse_type: str = "nuclear"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generates a balanced set of attributes for a player.
        Ensures unique professions per game where possible, realistic age/hobby/knowledge coupling.
        """
        # 1. Unique profession (checks name or full value with emoji)
        available_professions = [
            p for p in PROFESSIONS
            if not any(p["name"].lower() in ep.lower() for ep in existing_professions)
        ]
        if not available_professions:
            available_professions = PROFESSIONS
        profession = random.choice(available_professions)

        # 2. Age (18 - 75)
        # Age distribution: 60% young/middle (22-45), 25% mature (46-60), 15% elder/young (18-21 or 61-75)
        r = random.random()
        if r < 0.60:
            age = random.randint(22, 45)
        elif r < 0.85:
            age = random.randint(46, 60)
        elif r < 0.93:
            age = random.randint(18, 21)
        else:
            age = random.randint(61, 75)

        # 3. Health
        health = random.choice(HEALTH_STATES)

        # 4. Character
        character = random.choice(CHARACTERS)

        # 5. Hobby
        hobby = random.choice(HOBBIES)

        # 6. Knowledge
        knowledge = random.choice(KNOWLEDGE_DOMAINS)

        # 7. Genetics
        genetics = random.choice(GENETICS_TRAITS)

        # 8. Physical state
        if age > 65:
            physical_pool = [p for p in PHYSICAL_STATES if p["value_score"] <= 75]
        else:
            physical_pool = PHYSICAL_STATES
        physical = random.choice(physical_pool if physical_pool else PHYSICAL_STATES)

        # 9. Inventory item
        inventory = random.choice(INVENTORY_ITEMS)

        # 10. Special feature
        special_notes = [
            "Qon guruhi: O(I) Rh+", "Qon guruhi: A(II) Rh+", "Qon guruhi: B(III) Rh+", "Qon guruhi: AB(IV) Rh+",
            "Universal donor (O-)", "Ko'zi 100% o'tkir", "Ikkinchi til: Ingliz tili mukammal",
            "Haydovchilik guvohnomasi (B, C, D toifalari)", "Gipnozga tushmaydi", "Suv ostida 3 daqiqa nafas ushlay oladi",
            "Fotografik xotira sohibi", "Hissiyotlarini yashira oladi", "Tug'ma strategik intuitsiya"
        ]
        special = random.choice(special_notes)

        return {
            "profession": {"value": f"{profession['emoji']} {profession['name']}", "metadata": profession},
            "age": {"value": f"🎂 {age} yosh", "metadata": {"age": age}},
            "health": {"value": f"{health['emoji']} {health['name']}", "metadata": health},
            "character": {"value": f"{character['emoji']} {character['name']}", "metadata": character},
            "hobby": {"value": f"{hobby['emoji']} {hobby['name']}", "metadata": hobby},
            "knowledge": {"value": f"{knowledge['emoji']} {knowledge['name']}", "metadata": knowledge},
            "genetics": {"value": f"{genetics['emoji']} {genetics['name']}", "metadata": genetics},
            "physical": {"value": f"{physical['emoji']} {physical['name']}", "metadata": physical},
            "inventory": {"value": f"{inventory['emoji']} {inventory['name']}", "metadata": inventory},
            "special": {"value": f"🔬 {special}", "metadata": {"note": special}},
        }
