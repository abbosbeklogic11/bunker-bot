"""
Balance checker module for BUNKER game.
Ensures fairness across all generated players and prevents overpowered/underpowered outliers.
"""
from typing import Dict, Any, List, Tuple
import statistics


class BalanceChecker:
    @staticmethod
    def evaluate_game_balance(players_scores: Dict[int, int]) -> Dict[str, Any]:
        """
        Evaluates the distribution of survival scores.
        Returns metrics and whether rebalancing is advised.
        """
        if not players_scores:
            return {"balanced": True, "mean": 0, "std_dev": 0, "outliers": []}

        scores = list(players_scores.values())
        mean_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0

        outliers = []
        for uid, score in players_scores.items():
            if score > mean_score + 2 * std_dev:
                outliers.append({"user_id": uid, "score": score, "type": "OVERPOWERED"})
            elif score < mean_score - 2 * std_dev:
                outliers.append({"user_id": uid, "score": score, "type": "UNDERPOWERED"})

        is_balanced = len(outliers) <= (len(players_scores) * 0.1)  # max 10% outliers

        return {
            "balanced": is_balanced,
            "mean": round(mean_score, 1),
            "std_dev": round(std_dev, 1),
            "min_score": min(scores),
            "max_score": max(scores),
            "outliers": outliers
        }
