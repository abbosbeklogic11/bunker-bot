"""
Unit tests for BUNKER Game Engine scoring, randomizers, and state machine.
"""
import unittest
from game.state_machine import StateMachine, GamePhase
from game.randomizer import AttributeRandomizer, CardRandomizer, BalanceChecker
from game.systems import ScoringSystem, RewardSystem
from game.data import PROFESSIONS, APOCALYPSE_SCENARIOS, BUNKER_CONFIGS, CARD_DEFINITIONS, ABILITY_DEFINITIONS


class TestBunkerEngine(unittest.TestCase):
    def test_data_integrity(self):
        """Verify all game data lists are populated with required minimum counts."""
        self.assertGreaterEqual(len(PROFESSIONS), 50)
        self.assertGreaterEqual(len(APOCALYPSE_SCENARIOS), 10)
        self.assertGreaterEqual(len(BUNKER_CONFIGS), 5)
        self.assertGreaterEqual(len(CARD_DEFINITIONS), 25)
        self.assertGreaterEqual(len(ABILITY_DEFINITIONS), 15)

    def test_state_machine_transitions(self):
        """Verify FSM transition logic."""
        sm = StateMachine()

        # Valid transitions
        self.assertTrue(sm.can_transition(GamePhase.LOBBY, GamePhase.STARTING))
        self.assertTrue(sm.can_transition(GamePhase.STARTING, GamePhase.DEAL_CARDS))
        self.assertTrue(sm.can_transition(GamePhase.DISCUSSION, GamePhase.ABILITY_PHASE))
        self.assertTrue(sm.can_transition(GamePhase.ABILITY_PHASE, GamePhase.VOTING))
        self.assertTrue(sm.can_transition(GamePhase.VOTING, GamePhase.ELIMINATION))
        self.assertTrue(sm.can_transition(GamePhase.VOTING, GamePhase.DUEL))
        self.assertTrue(sm.can_transition(GamePhase.LOBBY, GamePhase.FINISHED))  # On cancel

        # Invalid transitions
        self.assertFalse(sm.can_transition(GamePhase.DISCUSSION, GamePhase.FINAL))
        self.assertFalse(sm.can_transition(GamePhase.VOTING, GamePhase.LOBBY))

    def test_attribute_randomizer_20_players(self):
        """Verify 20 distinct players can be generated without errors."""
        existing_profs = []
        players_attrs = []
        
        for i in range(20):
            attrs = AttributeRandomizer.generate_player_attributes(
                player_index=i,
                total_players=20,
                existing_professions=existing_profs,
                apocalypse_type="nuclear"
            )
            self.assertIn("profession", attrs)
            self.assertIn("age", attrs)
            self.assertIn("health", attrs)
            self.assertIn("character", attrs)
            self.assertIn("hobby", attrs)
            self.assertIn("inventory", attrs)
            
            prof_name = attrs["profession"]["value"]
            existing_profs.append(prof_name)
            players_attrs.append(attrs)

        # All 20 should have unique professions
        self.assertEqual(len(set(existing_profs)), 20)

    def test_card_distribution_balance(self):
        """Verify 20 players get balanced card distribution without violating legendary limits."""
        player_ids = list(range(1001, 1021))  # 20 players
        dist = CardRandomizer.distribute_cards_for_game(player_ids, cards_per_player=3)

        self.assertEqual(len(dist), 20)
        
        legendary_count = 0
        for uid, cards in dist.items():
            self.assertEqual(len(cards), 3)
            for c in cards:
                if c["rarity"] == "LEGENDARY":
                    legendary_count += 1

        # Should not exceed game limit
        self.assertLessEqual(legendary_count, 2)

    def test_scoring_system(self):
        """Verify survival score calculation produces realistic values."""
        mock_attrs = {
            "profession": "👨‍⚕️ Shifokor",
            "health": "🌟 A'lo",
            "knowledge": "🩺 Tibbiyot",
            "physical": "💪 Kuchli",
            "inventory": "🧰 Tibbiy sumka to'liq",
            "character": "🤝 Jamoaviy"
        }
        bunker = BUNKER_CONFIGS[0]
        
        score_virus = ScoringSystem.calculate_survival_score(mock_attrs, "virus", bunker)
        score_ice = ScoringSystem.calculate_survival_score(mock_attrs, "ice_age", bunker)

        # Doctor should score higher in virus scenario than ice age
        self.assertGreater(score_virus, score_ice)
        self.assertGreater(score_virus, 0)

    def test_reward_system(self):
        """Verify 4 winners and MVP awards calculation."""
        winners = [
            {"user_id": 1, "name": "Ali", "survival_score": 500},
            {"user_id": 2, "name": "Vali", "survival_score": 600},
            {"user_id": 3, "name": "Hasan", "survival_score": 450},
            {"user_id": 4, "name": "Husan", "survival_score": 400},
        ]
        all_p = [{"user_id": i, "status": "ACTIVE"} for i in range(1, 11)]
        
        calc = RewardSystem.calculate_game_rewards(winners, all_p, [])
        self.assertEqual(len(calc["winners"]), 4)
        self.assertEqual(calc["mvp"]["user_id"], 2)  # Highest score
        
        # 4 place rewards + 1 MVP reward
        self.assertGreaterEqual(len(calc["rewards"]), 5)


if __name__ == "__main__":
    unittest.main()
