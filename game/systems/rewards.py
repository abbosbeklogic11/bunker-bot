"""
Rewards and achievements calculation system for BUNKER game.
"""
from typing import Dict, Any, List, Optional, Tuple
from bot.config.game_config import GameConfig, default_game_config


class RewardSystem:
    @staticmethod
    def calculate_game_rewards(
        winners: List[Dict[str, Any]],
        all_players: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        config: GameConfig = default_game_config
    ) -> Dict[str, Any]:
        """
        Calculates coin, diamond, and bonus distribution for 4 winners and special award holders.
        """
        rewards_list: List[Dict[str, Any]] = []

        # 1. Place rewards for 4 winners
        for idx, winner in enumerate(winners[:4]):
            place = idx + 1
            place_reward = config.REWARD_PLACES.get(place, {"coins": 200, "diamonds": 30})
            rewards_list.append({
                "user_id": winner["user_id"],
                "place": place,
                "coins": place_reward["coins"],
                "diamonds": place_reward["diamonds"],
                "bonus_type": f"WINNER_PLACE_{place}"
            })

        # 2. Bonus awards
        # A) MVP: Highest survival score among winners
        if winners:
            mvp_winner = max(winners, key=lambda w: w.get("survival_score", 0))
            rewards_list.append({
                "user_id": mvp_winner["user_id"],
                "place": None,
                "coins": config.BONUS_REWARDS["mvp"]["coins"],
                "diamonds": config.BONUS_REWARDS["mvp"]["diamonds"],
                "bonus_type": "MVP"
            })

        # B) Longest Survivor: The last player eliminated before final 4
        eliminated_players = [p for p in all_players if p.get("status") == "ELIMINATED"]
        if eliminated_players:
            last_eliminated = max(eliminated_players, key=lambda p: p.get("elimination_round", 0))
            rewards_list.append({
                "user_id": last_eliminated["user_id"],
                "place": None,
                "coins": config.BONUS_REWARDS["longest_survivor"]["coins"],
                "diamonds": config.BONUS_REWARDS["longest_survivor"]["diamonds"],
                "bonus_type": "LONGEST_SURVIVOR"
            })

        # C) Most Protections: player who used protect abilities/cards most
        protect_counts: Dict[int, int] = {}
        for act in actions:
            if act.get("action_type") in ("USE_ABILITY", "USE_CARD") and "PROTECT" in str(act.get("action_data", {})):
                actor = act.get("actor_id")
                if actor:
                    protect_counts[actor] = protect_counts.get(actor, 0) + 1
        
        if protect_counts:
            top_protector = max(protect_counts, key=protect_counts.get)
            rewards_list.append({
                "user_id": top_protector,
                "place": None,
                "coins": config.BONUS_REWARDS["most_protections"]["coins"],
                "diamonds": config.BONUS_REWARDS["most_protections"]["diamonds"],
                "bonus_type": "MOST_PROTECTIONS"
            })

        return {
            "rewards": rewards_list,
            "winners": winners[:4],
            "mvp": mvp_winner if winners else None
        }

    @staticmethod
    def evaluate_unlocked_achievements(
        user_stats: Dict[str, Any],
        game_result: Dict[str, Any]
    ) -> List[str]:
        """
        Returns codes of achievements that should be unlocked based on stats.
        """
        unlocked = []
        games_won = user_stats.get("games_won", 0)
        games_played = user_stats.get("games_played", 0)
        is_winner = game_result.get("is_winner", False)
        is_mvp = game_result.get("is_mvp", False)

        if is_winner and games_won == 1:
            unlocked.append("first_win")
        if games_won >= 5:
            unlocked.append("five_wins")
        if games_won >= 10:
            unlocked.append("ten_wins")
        if games_won >= 25:
            unlocked.append("twenty_five_wins")
        if is_mvp:
            unlocked.append("mvp_first")
        if user_stats.get("survival_count", 0) >= 10:
            unlocked.append("survivor")

        return unlocked
