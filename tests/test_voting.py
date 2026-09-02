"""
Tests for voting and event evaluation logic.
"""
import unittest
from game.systems.events import EventSystem


class TestVotingAndEvents(unittest.TestCase):
    def test_event_resolution(self):
        """Verify event resolution detection."""
        mock_event = {
            "name": "Suv filtri buzildi!",
            "required_professions": ["Santexnik", "Muhandis"],
            "required_knowledge": ["Gidrologiya"],
            "required_items": ["Portativ suv filtri"]
        }

        players_with_plumber = [
            {"user_id": 1, "name": "Ali", "profession": "👨‍🔧 Santexnik", "knowledge": "IT", "inventory": "Sham"},
            {"user_id": 2, "name": "Vali", "profession": "👨‍🏫 O'qituvchi", "knowledge": "Tarix", "inventory": "Non"}
        ]

        is_resolved, resolvers, _ = EventSystem.evaluate_event_resolution(mock_event, players_with_plumber)
        self.assertTrue(is_resolved)
        self.assertEqual(len(resolvers), 1)
        self.assertEqual(resolvers[0]["user_id"], 1)

        players_without_fix = [
            {"user_id": 3, "name": "Hasan", "profession": "🎨 Rassom", "knowledge": "San'at", "inventory": "Bo'yoq"},
            {"user_id": 4, "name": "Husan", "profession": "🎤 Qo'shiqchi", "knowledge": "Musiqa", "inventory": "Gitara"}
        ]

        is_resolved_no, resolvers_no, _ = EventSystem.evaluate_event_resolution(mock_event, players_without_fix)
        self.assertFalse(is_resolved_no)
        self.assertEqual(len(resolvers_no), 0)


if __name__ == "__main__":
    unittest.main()
