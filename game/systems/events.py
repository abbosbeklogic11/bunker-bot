"""
Events system module for BUNKER game.
Controls rolling, evaluating resolution, and applying consequences of random bunker events.
"""
from typing import Dict, Any, List, Optional, Tuple
import random
from game.data import EVENT_DEFINITIONS, get_random_event, get_event_by_id


class EventSystem:
    @staticmethod
    def roll_event_for_round(
        round_number: int,
        past_event_ids: List[int],
        chance_percent: float = 0.65
    ) -> Optional[Dict[str, Any]]:
        """
        Determines whether a random crisis/event triggers this round and selects an appropriate one.
        """
        if round_number < 2:
            return None  # No events in round 1 (warmup round)

        if random.random() > chance_percent:
            return None

        # Filter out recently triggered events
        available = [e for e in EVENT_DEFINITIONS if e["id"] not in past_event_ids and e.get("min_round", 1) <= round_number]
        if not available:
            available = EVENT_DEFINITIONS

        return random.choice(available)

    @staticmethod
    def evaluate_event_resolution(
        event: Dict[str, Any],
        alive_players_attrs: List[Dict[str, Any]]
    ) -> Tuple[bool, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Checks if the currently alive players possess the professions, knowledge, or items
        required to resolve the event.
        
        Returns:
            (is_resolved: bool, resolvers: List[dict], consequences: dict)
        """
        req_profs = event.get("required_professions", [])
        req_knows = event.get("required_knowledge", [])
        req_items = event.get("required_items", [])

        resolvers = []

        for p_attrs in alive_players_attrs:
            uid = p_attrs.get("user_id")
            name = p_attrs.get("name", "O'yinchi")
            
            p_prof = p_attrs.get("profession", "")
            p_know = p_attrs.get("knowledge", "")
            p_item = p_attrs.get("inventory", "")

            matched = False
            match_reason = ""

            # Check profession
            for rp in req_profs:
                if rp.lower() in p_prof.lower():
                    matched = True
                    match_reason = f"👨‍💼 Kasbi: {rp}"
                    break
            
            # Check knowledge
            if not matched:
                for rk in req_knows:
                    if rk.lower() in p_know.lower():
                        matched = True
                        match_reason = f"🎓 Bilimi: {rk}"
                        break

            # Check item
            if not matched:
                for ri in req_items:
                    if ri.lower() in p_item.lower():
                        matched = True
                        match_reason = f"🎒 Inventari: {ri}"
                        break

            if matched:
                resolvers.append({
                    "user_id": uid,
                    "name": name,
                    "reason": match_reason
                })

        is_resolved = len(resolvers) > 0
        consequences = event.get("effect_data", {}) if not is_resolved else {}

        return is_resolved, resolvers, consequences
