"""
Core Game Engine module for BUNKER game.
Coordinates all game state transitions, repositories, timers, and game systems in a pure business-logic layer.
No Telegram imports. Emits GameEvents to the EventBus.
"""
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from datetime import datetime, timezone, timedelta

from models.game import GameModel, GamePlayerModel, GameState, PlayerStatus
from database.repositories import (
    GameRepository, PlayerRepository, VoteRepository, EventRepository,
    UserRepository, AchievementRepository
)
from game.state_machine import StateMachine, GamePhase
from game.engine_events import EventBus, GameEvent, GameEventType
from game.timers.timer_engine import TimerEngine
from game.randomizer import AttributeRandomizer, CardRandomizer, BalanceChecker
from game.systems import (
    ScoringSystem, VotingSystem, AbilitySystem, CardSystem,
    EventSystem, RewardSystem, BalanceEngine
)
from bot.config.game_config import GameConfig, default_game_config
from game.data import get_apocalypse_by_type


class GameEngine:
    def __init__(
        self,
        game_repo: GameRepository,
        player_repo: PlayerRepository,
        vote_repo: VoteRepository,
        event_repo: EventRepository,
        user_repo: UserRepository,
        achievement_repo: AchievementRepository,
        timer_engine: TimerEngine,
        event_bus: EventBus,
        config: GameConfig = default_game_config
    ):
        self.game_repo = game_repo
        self.player_repo = player_repo
        self.vote_repo = vote_repo
        self.event_repo = event_repo
        self.user_repo = user_repo
        self.achievement_repo = achievement_repo
        self.timer_engine = timer_engine
        self.event_bus = event_bus
        self.config = config
        self.state_machine = StateMachine()

    # ==================== LOBBY ====================

    async def create_game(self, group_chat_id: int, created_by: int) -> Dict[str, Any]:
        """Creates a new game lobby in the given group chat."""
        # 1. Check if an active game already exists
        existing = await self.game_repo.get_active_game_by_group(group_chat_id)
        if existing:
            return {"success": False, "error": "ALREADY_ACTIVE_GAME", "game_id": existing.id}

        # 2. Create game in DB
        game = await self.game_repo.create_game(group_chat_id, created_by)
        
        # 3. Add creator as player 1
        await self.player_repo.add_player(game.id, created_by, join_order=1)
        
        # 4. Set lobby timer
        await self.timer_engine.set_phase_timer(game.id, GamePhase.LOBBY.value, self.config.LOBBY_TIMEOUT)
        
        # 5. Log action and emit event
        await self.game_repo.log_action(game.id, 0, created_by, "GAME_CREATED", {"group_id": group_chat_id})
        await self.event_bus.emit(GameEvent(
            type=GameEventType.LOBBY_UPDATED,
            game_id=game.id,
            data={"action": "created", "player_count": 1}
        ))
        
        return {"success": True, "game": game}

    async def join_game(self, game_id: int, user_id: int) -> Dict[str, Any]:
        """Adds a player to an open lobby."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state != GameState.LOBBY:
            return {"success": False, "error": "NOT_IN_LOBBY"}

        # Check bot started
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_bot_started:
            return {"success": False, "error": "BOT_NOT_STARTED"}

        # Check player count
        current_count = await self.player_repo.get_player_count(game_id)
        if current_count >= self.config.MAX_PLAYERS:
            return {"success": False, "error": "LOBBY_FULL"}

        # Add player
        player = await self.player_repo.add_player(game_id, user_id, join_order=current_count + 1)
        new_count = current_count + 1

        await self.game_repo.log_action(game_id, 0, user_id, "PLAYER_JOINED", {"order": new_count})
        await self.event_bus.emit(GameEvent(
            type=GameEventType.PLAYER_JOINED,
            game_id=game_id,
            data={"user_id": user_id, "player_count": new_count, "max_players": self.config.MAX_PLAYERS}
        ))

        # Auto start if lobby is full
        if new_count >= self.config.MAX_PLAYERS and self.config.AUTO_START_ON_FULL:
            asyncio.create_task(self.start_game(game_id, by_user_id=user_id))

        return {"success": True, "player_count": new_count}

    async def cancel_game(self, game_id: int, by_user_id: int) -> bool:
        """Cancels a game in lobby."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state != GameState.LOBBY:
            return False

        await self.game_repo.finish_game(game_id)
        await self.timer_engine.cancel_timer(game_id)
        await self.event_bus.emit(GameEvent(
            type=GameEventType.GAME_CANCELLED,
            game_id=game_id,
            data={"by_user_id": by_user_id}
        ))
        return True

    # ==================== INITIALIZATION ====================

    async def start_game(self, game_id: int, by_user_id: int) -> Dict[str, Any]:
        """Starts the game from LOBBY."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state != GameState.LOBBY:
            return {"success": False, "error": "INVALID_STATE"}

        players = await self.player_repo.get_all_players(game_id)
        if len(players) < self.config.MIN_PLAYERS:
            return {"success": False, "error": "NOT_ENOUGH_PLAYERS", "count": len(players), "min": self.config.MIN_PLAYERS}

        # 1. Update state
        await self.game_repo.update_state(game_id, GameState.STARTING)
        
        # 2. Pick Apocalypse & Bunker Config
        apocalypse = BalanceEngine.get_apocalypse()
        bunker = BalanceEngine.get_bunker_config()

        # Dynamic capacity based on player count:
        # 5-7 players -> 2 survivors
        # 8-14 players -> 3 survivors
        # 15+ players -> 4 survivors
        if len(players) <= 7:
            bunker_capacity = 2
        elif len(players) <= 14:
            bunker_capacity = 3
        else:
            bunker_capacity = 4

        await self.game_repo.set_apocalypse(game_id, apocalypse["type"])
        await self.game_repo.set_bunker_config(
            game_id=game_id,
            capacity=bunker_capacity,
            food_days=bunker["food_days"],
            water_days=bunker["water_days"],
            power_days=bunker["power_days"],
            has_farm=bunker["has_farm"],
            has_medical=bunker["has_medical"],
            has_workshop=bunker["has_workshop"],
            has_radio=bunker["has_radio"]
        )

        # 3. Generate attributes, cards, and abilities
        await self.deal_cards_and_attributes(game_id, players, apocalypse["type"], bunker)

        # 4. Notify game started
        await self.event_bus.emit(GameEvent(
            type=GameEventType.GAME_STARTED,
            game_id=game_id,
            data={"apocalypse": apocalypse, "bunker": bunker, "player_count": len(players)}
        ))

        # 5. Advance to round 1 attribute reveal
        await self.advance_to_next_round(game_id)
        return {"success": True}

    async def deal_cards_and_attributes(
        self,
        game_id: int,
        players: List[GamePlayerModel],
        apocalypse_type: str,
        bunker_config: Dict[str, Any]
    ) -> None:
        """Generates and persists secret attributes, cards, and abilities for every player."""
        player_ids = [p.user_id for p in players]
        existing_professions: List[str] = []
        assigned_ability_ids: List[int] = []

        # 1. Distribute Cards
        cards_dist = CardRandomizer.distribute_cards_for_game(player_ids, self.config.MAX_CARDS_PER_PLAYER)
        for uid, cards in cards_dist.items():
            for c in cards:
                await self.player_repo.assign_card(game_id, uid, c["id"])

        # 2. Generate attributes & abilities per player
        for idx, player in enumerate(players):
            uid = player.user_id
            attrs = AttributeRandomizer.generate_player_attributes(
                idx, len(players), existing_professions, apocalypse_type
            )
            
            prof_name = attrs["profession"]["value"]
            existing_professions.append(prof_name)
            
            # Save attributes
            for attr_type, attr_data in attrs.items():
                await self.player_repo.add_player_attribute(
                    game_id, uid, attr_type, attr_data["value"], attr_data.get("metadata")
                )

            # Assign abilities
            char_name = attrs["character"]["value"]
            abilities = BalanceEngine.select_abilities_for_player(
                prof_name, char_name, assigned_ability_ids, max_abilities=1
            )
            for ab in abilities:
                assigned_ability_ids.append(ab["id"])
                await self.player_repo.assign_ability(game_id, uid, ab["id"], uses=ab.get("uses_per_game", 1))

            # Calculate and store initial survival score
            raw_attrs = {k: v["value"] for k, v in attrs.items()}
            score = ScoringSystem.calculate_survival_score(raw_attrs, apocalypse_type, bunker_config)
            await self.player_repo.update_survival_score(game_id, uid, score)

        # Emit private cards distribution event (to send private messages)
        await self.event_bus.emit(GameEvent(
            type=GameEventType.CARDS_DISTRIBUTED,
            game_id=game_id,
            data={"player_ids": player_ids}
        ))

    # ==================== ROUND CYCLES ====================

    async def advance_to_next_round(self, game_id: int) -> None:
        """Starts a new round: increments round, enters 15-second attribute reveal phase."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        current_round = await self.game_repo.increment_round(game_id)

        await self.game_repo.update_state(game_id, GameState.REVEAL_ATTRIBUTE)
        await self.timer_engine.set_phase_timer(game_id, GamePhase.REVEAL_ATTRIBUTE.value, self.config.REVEAL_TIME)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.ATTRIBUTE_REVEALED,
            game_id=game_id,
            data={"round": current_round, "duration": self.config.REVEAL_TIME}
        ))
        await self.event_bus.emit(GameEvent(
            type=GameEventType.PHASE_CHANGED,
            game_id=game_id,
            data={"phase": GamePhase.REVEAL_ATTRIBUTE.value, "round": current_round, "duration": self.config.REVEAL_TIME}
        ))

    async def player_reveal_attribute(self, game_id: int, user_id: int, attr_type: str) -> Dict[str, Any]:
        """Reveals a chosen attribute for a specific player."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state not in (GameState.REVEAL_ATTRIBUTE, GameState.DISCUSSION, GameState.ABILITY_PHASE):
            return {"success": False, "error": "NOT_IN_REVEAL", "message": "Xususiyatni faqat xususiyat ochish yoki muhokama bosqichida ochish mumkin."}

        player = await self.player_repo.get_player(game_id, user_id)
        if not player or player.status not in (PlayerStatus.ACTIVE, PlayerStatus.PROTECTED):
            return {"success": False, "error": "NOT_ALIVE", "message": "Siz bu o'yinda tirik emassiz."}

        revealed_count = await self.player_repo.get_revealed_player_count(game_id, user_id)
        if revealed_count >= game.current_round:
            return {"success": False, "error": "ALREADY_REVEALED_THIS_ROUND", "message": f"Siz {game.current_round}-raundda allaqachon xususiyatingizni ochgansiz! Keyingi raundni kuting."}

        revealed = await self.player_repo.reveal_player_attribute(game_id, user_id, attr_type)
        if not revealed:
            return {"success": False, "error": "ALREADY_REVEALED_ATTR", "message": "Bu xususiyatingiz allaqachon ochiq!"}

        u = await self.user_repo.get_by_id(user_id)
        user_name = u.first_name if u else f"O'yinchi #{user_id}"

        await self.event_bus.emit(GameEvent(
            type=GameEventType.PLAYER_ATTRIBUTE_REVEALED,
            game_id=game_id,
            data={
                "user_id": user_id,
                "user_name": user_name,
                "attribute_type": attr_type,
                "attribute_value": revealed.attribute_value,
                "round": game.current_round
            }
        ))

        # Check if all alive players have revealed in REVEAL_ATTRIBUTE phase
        alive = await self.player_repo.get_alive_players(game_id)
        all_revealed = True
        for p in alive:
            cnt = await self.player_repo.get_revealed_player_count(game_id, p.user_id)
            if cnt < game.current_round:
                all_revealed = False
                break

        if all_revealed and game.state == GameState.REVEAL_ATTRIBUTE:
            asyncio.create_task(self.start_discussion_phase(game_id))

        return {"success": True, "attribute": revealed, "user_name": user_name}

    async def auto_reveal_unrevealed_players(self, game_id: int, current_round: int) -> None:
        """Auto reveals 1 random attribute for players who did not manually reveal before timeout."""
        import random
        alive = await self.player_repo.get_alive_players(game_id)
        for p in alive:
            count = await self.player_repo.get_revealed_player_count(game_id, p.user_id)
            if count < current_round:
                unrevealed = await self.player_repo.get_unrevealed_player_attributes(game_id, p.user_id)
                if unrevealed:
                    chosen = random.choice(unrevealed)
                    await self.player_reveal_attribute(game_id, p.user_id, chosen.attribute_type)

    async def start_discussion_phase(self, game_id: int) -> None:
        """Transitions from Attribute Reveal to Discussion Phase with dynamic duration."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state == GameState.DISCUSSION:
            return

        # Auto-reveal any remaining unrevealed player attributes for this round
        await self.auto_reveal_unrevealed_players(game_id, game.current_round)

        alive_players = await self.player_repo.get_alive_players(game_id)
        player_count = len(alive_players)

        # Dynamic discussion duration:
        # 5-8 players: 2 min (120s)
        # 8-10 players: 3 min (180s)
        # 10-15 players: 4 min (240s)
        # 15-20 players: 5 min (300s)
        if player_count <= 8:
            duration = 120
        elif player_count <= 10:
            duration = 180
        elif player_count <= 15:
            duration = 240
        else:
            duration = 300

        await self.game_repo.update_state(game_id, GameState.DISCUSSION)
        await self.timer_engine.set_phase_timer(game_id, GamePhase.DISCUSSION.value, duration)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.PHASE_CHANGED,
            game_id=game_id,
            data={"phase": GamePhase.DISCUSSION.value, "round": game.current_round, "duration": duration}
        ))

    async def start_ability_phase(self, game_id: int) -> None:
        """Transitions from Discussion to Ability Phase."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        await self.game_repo.update_state(game_id, GameState.ABILITY_PHASE)
        await self.timer_engine.set_phase_timer(game_id, GamePhase.ABILITY_PHASE.value, self.config.ABILITY_TIME)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.PHASE_CHANGED,
            game_id=game_id,
            data={"phase": GamePhase.ABILITY_PHASE.value, "round": game.current_round, "duration": self.config.ABILITY_TIME}
        ))

    async def start_voting_phase(self, game_id: int) -> None:
        """Transitions to Voting Phase."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        # Clear any votes from previous rounds
        await self.vote_repo.clear_round_votes(game_id, game.current_round)

        await self.game_repo.update_state(game_id, GameState.VOTING)
        await self.timer_engine.set_phase_timer(game_id, GamePhase.VOTING.value, self.config.VOTING_TIME)

        alive_players = await self.player_repo.get_alive_players(game_id)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.PHASE_CHANGED,
            game_id=game_id,
            data={
                "phase": GamePhase.VOTING.value,
                "round": game.current_round,
                "duration": self.config.VOTING_TIME,
                "alive_count": len(alive_players)
            }
        ))

    # ==================== VOTING & ELIMINATION ====================

    async def submit_vote(
        self,
        game_id: int,
        voter_id: int,
        target_id: int
    ) -> Dict[str, Any]:
        """Submits an elimination vote."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state not in (GameState.VOTING, GameState.DUEL):
            return {"success": False, "error": "NOT_IN_VOTING"}

        # Validate voter is alive
        voter = await self.player_repo.get_player(game_id, voter_id)
        if not voter or voter.status not in (PlayerStatus.ACTIVE, PlayerStatus.PROTECTED):
            return {"success": False, "error": "VOTER_DEAD"}

        # Validate target is alive
        target = await self.player_repo.get_player(game_id, target_id)
        if not target or target.status not in (PlayerStatus.ACTIVE, PlayerStatus.PROTECTED):
            return {"success": False, "error": "TARGET_DEAD"}

        # Check self-voting
        if voter_id == target_id and not self.config.VOTE_CHANGE_ALLOWED:
            return {"success": False, "error": "SELF_VOTE_NOT_ALLOWED"}

        # Submit vote
        submitted = await self.vote_repo.submit_vote(game_id, game.current_round, voter_id, target_id, weight=1)
        if not submitted:
            return {"success": False, "error": "ALREADY_VOTED"}

        # Increment voter stats
        await self.player_repo.increment_stats(game_id, voter_id, votes_given=1)
        await self.player_repo.increment_stats(game_id, target_id, votes_received=1)

        alive_players = await self.player_repo.get_alive_players(game_id)
        total_voters = await self.vote_repo.get_voter_count(game_id, game.current_round)
        vote_counts = await self.vote_repo.get_vote_counts(game_id, game.current_round)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.VOTE_SUBMITTED,
            game_id=game_id,
            data={
                "voter_id": voter_id,
                "voted_count": total_voters,
                "alive_count": len(alive_players),
                "vote_counts": vote_counts
            }
        ))

        # If all alive players have voted, immediately finalize voting
        if total_voters >= len(alive_players):
            asyncio.create_task(self.finalize_voting(game_id))

        return {"success": True, "voted_count": total_voters, "alive_count": len(alive_players)}

    async def finalize_voting(self, game_id: int) -> None:
        """Calculates vote tallies, handles ties/duels or executes elimination."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state not in (GameState.VOTING, GameState.DUEL):
            return

        candidate_id, max_votes, is_tie, tied_ids = await self.vote_repo.get_elimination_candidate(
            game_id, game.current_round
        )

        # 1. Handle Tie -> Duel Phase
        if is_tie and len(tied_ids) > 1:
            await self.start_duel(game_id, tied_ids)
            return

        # 2. Check Protection
        if candidate_id:
            candidate = await self.player_repo.get_player(game_id, candidate_id)
            if candidate and candidate.is_protected:
                # Target is protected! Invalidate and pick second highest or announce protection
                await self.event_bus.emit(GameEvent(
                    type=GameEventType.PLAYER_ELIMINATED,
                    game_id=game_id,
                    data={"saved_by_protection": True, "user_id": candidate_id}
                ))
                await self.player_repo.remove_protection(game_id, candidate_id)
                await self.post_elimination_cycle(game_id)
                return

        # 3. Eliminate player
        if candidate_id and max_votes > 0:
            await self.eliminate_player(game_id, candidate_id, max_votes)
        else:
            # No votes cast at all -> Nobody is eliminated! Round advances with same players
            await self.event_bus.emit(GameEvent(
                type=GameEventType.PHASE_CHANGED,
                game_id=game_id,
                data={"phase": "NO_VOTES", "round": game.current_round}
            ))
            await asyncio.sleep(2)
            await self.advance_to_next_round(game_id)

    async def start_duel(self, game_id: int, tied_ids: List[int]) -> None:
        """Starts a tie-breaker duel between tied candidates."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        await self.game_repo.update_state(game_id, GameState.DUEL)
        await self.timer_engine.set_phase_timer(game_id, GamePhase.DUEL.value, self.config.DUEL_TIME)
        await self.vote_repo.clear_round_votes(game_id, game.current_round)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.DUEL_STARTED,
            game_id=game_id,
            data={"tied_user_ids": tied_ids, "duration": self.config.DUEL_TIME}
        ))

    async def eliminate_player(self, game_id: int, user_id: int, votes_received: int) -> None:
        """Eliminates a player from the game."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        await self.player_repo.eliminate_player(game_id, user_id, game.current_round, votes_received)
        await self.user_repo.update_stats(user_id, eliminations_count=1)
        
        alive_players = await self.player_repo.get_alive_players(game_id)

        await self.game_repo.log_action(game_id, game.current_round, user_id, "PLAYER_ELIMINATED", {"votes": votes_received})
        await self.event_bus.emit(GameEvent(
            type=GameEventType.PLAYER_ELIMINATED,
            game_id=game_id,
            data={"user_id": user_id, "votes": votes_received, "alive_count": len(alive_players)}
        ))

        await self.post_elimination_cycle(game_id)

    async def post_elimination_cycle(self, game_id: int) -> None:
        """Checks win condition and rolls events or advances to next round."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        alive_players = await self.player_repo.get_alive_players(game_id)
        
        # 1. Check Win condition (survivors match dynamic bunker capacity)
        target_capacity = game.bunker_capacity or self.config.WINNERS_COUNT
        if len(alive_players) <= target_capacity:
            await self.finalize_game(game_id)
            return

        # 2. Roll random event
        event = await self.roll_and_apply_event(game_id)
        
        # Short pause before starting next round
        await asyncio.sleep(3)
        await self.advance_to_next_round(game_id)

    # ==================== RANDOM EVENTS ====================

    async def roll_and_apply_event(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Rolls a random event and checks if alive players can resolve it."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None

        past_events = await self.event_repo.get_events_for_game(game_id)
        past_ids = [e.id for e in past_events]

        event = EventSystem.roll_event_for_round(game.current_round, past_ids)
        if not event:
            return None

        # Fetch alive players attributes
        alive_players = await self.player_repo.get_alive_players(game_id)
        players_attrs = []
        for p in alive_players:
            attrs = await self.player_repo.get_player_attributes(game_id, p.user_id)
            u = await self.user_repo.get_by_id(p.user_id)
            attr_dict = {a.attribute_type: a.attribute_value for a in attrs}
            attr_dict["user_id"] = p.user_id
            attr_dict["name"] = u.first_name if u else "O'yinchi"
            players_attrs.append(attr_dict)

        is_resolved, resolvers, consequences = EventSystem.evaluate_event_resolution(event, players_attrs)

        # Save to DB
        saved_event = await self.event_repo.create_event(
            game_id, game.current_round, event["name"],
            {"event": event, "resolved": is_resolved, "resolvers": resolvers, "consequences": consequences}
        )

        if is_resolved and resolvers:
            await self.event_repo.resolve_event(saved_event.id, resolvers[0]["user_id"])

        await self.event_bus.emit(GameEvent(
            type=GameEventType.EVENT_TRIGGERED,
            game_id=game_id,
            data={"event": event, "resolved": is_resolved, "resolvers": resolvers, "consequences": consequences}
        ))
        return event

    # ==================== FINAL & REWARDS ====================

    async def finalize_game(self, game_id: int) -> None:
        """Evaluates survivors against apocalypse, determines rewards, and concludes the game."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        await self.game_repo.update_state(game_id, GameState.FINAL)
        
        alive_players = await self.player_repo.get_alive_players(game_id)
        all_players = await self.player_repo.get_all_players(game_id)
        actions = await self.game_repo.get_game_log(game_id, limit=200)

        # Build winner dicts and profiles for apocalypse evaluation
        from game.systems.evaluation import ApocalypseEvaluator
        from game.data.apocalypse import get_apocalypse_by_type

        ap_data = get_apocalypse_by_type(game.apocalypse_type or "nuclear")

        winners = []
        survivor_profiles = []
        for p in alive_players:
            u = await self.user_repo.get_by_id(p.user_id)
            attrs = await self.player_repo.get_player_attributes(game_id, p.user_id)
            attr_dict = {a.attribute_type: a.attribute_value for a in attrs}
            
            winners.append({
                "user_id": p.user_id,
                "name": u.first_name if u else "O'yinchi",
                "username": u.username if u else "",
                "survival_score": p.survival_score
            })
            survivor_profiles.append({
                "user_id": p.user_id,
                "name": u.first_name if u else "O'yinchi",
                "attributes": attr_dict
            })

        # Evaluate Apocalypse Survival Verdict
        evaluation = ApocalypseEvaluator.evaluate_survival(ap_data, survivor_profiles)

        # Calculate rewards
        raw_all = [{"user_id": p.user_id, "status": p.status, "elimination_round": p.elimination_round} for p in all_players]
        raw_acts = [{"action_type": a.action_type, "actor_id": a.actor_id, "action_data": a.action_data} for a in actions]
        
        calc_results = RewardSystem.calculate_game_rewards(winners, raw_all, raw_acts, self.config)

        # Persist rewards & update stats in DB
        for rew in calc_results["rewards"]:
            uid = rew["user_id"]
            await self.achievement_repo.grant_reward(
                game_id, uid, rew["place"], rew["coins"], rew["diamonds"], rew["bonus_type"]
            )
            await self.user_repo.add_coins(uid, rew["coins"])
            await self.user_repo.add_diamonds(uid, rew["diamonds"])

        # Update winner / loser stats
        for p in all_players:
            is_win = any(w["user_id"] == p.user_id for w in winners)
            if is_win:
                await self.user_repo.update_stats(p.user_id, games_played=1, games_won=1, survival_count=1)
                await self.player_repo.update_status(p.user_id, p.user_id, PlayerStatus.WINNER)
            else:
                await self.user_repo.update_stats(p.user_id, games_played=1, games_lost=1)
                await self.player_repo.update_status(p.user_id, p.user_id, PlayerStatus.LOSER)

            # Check achievements
            u_stats = await self.user_repo.get_by_id(p.user_id)
            if u_stats:
                ach_codes = RewardSystem.evaluate_unlocked_achievements(
                    u_stats.model_dump(), {"is_winner": is_win, "is_mvp": calc_results.get("mvp", {}).get("user_id") == p.user_id}
                )
                for code in ach_codes:
                    ach_obj = await self.achievement_repo.get_achievement_by_code(code)
                    if ach_obj:
                        granted = await self.achievement_repo.grant_achievement(p.user_id, ach_obj.id)
                        if granted:
                            await self.user_repo.add_coins(p.user_id, ach_obj.reward_coins)
                            await self.user_repo.add_diamonds(p.user_id, ach_obj.reward_diamonds)

        # Mark finished
        await self.game_repo.finish_game(game_id)
        await self.timer_engine.cancel_timer(game_id)

        await self.event_bus.emit(GameEvent(
            type=GameEventType.WINNER_DETERMINED,
            game_id=game_id,
            data={
                "winners": winners,
                "rewards": calc_results["rewards"],
                "mvp": calc_results.get("mvp"),
                "evaluation": evaluation
            }
        ))
        await self.event_bus.emit(GameEvent(
            type=GameEventType.GAME_FINISHED,
            game_id=game_id,
            data={"winners": winners}
        ))

    # ==================== ABILITIES & CARDS ====================

    async def use_ability(self, game_id: int, user_id: int, ability_id: int, target_id: Optional[int] = None) -> Dict[str, Any]:
        """Applies a player's ability."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state not in (GameState.ABILITY_PHASE, GameState.DISCUSSION):
            return {"success": False, "message": "Qobiliyatni faqat muhokama yoki qobiliyat bosqichida ishlatish mumkin."}

        # Check uses remaining
        player_abilities = await self.player_repo.get_player_abilities(game_id, user_id)
        target_ab = next((a for a in player_abilities if a["ability_id"] == ability_id), None)
        if not target_ab or target_ab["uses_remaining"] <= 0:
            return {"success": False, "message": "Bu qobiliyatdan foydalanish limiti tugagan."}

        if target_ab.get("is_blocked"):
            return {"success": False, "message": "Sizning qobiliyatingiz bloklangan!"}

        # Execute
        used = await self.player_repo.use_ability(game_id, user_id, ability_id)
        if not used:
            return {"success": False, "message": "Qobiliyatni ishlatishda xatolik."}

        # Handle specific ability effects
        effect_type = target_ab.get("effect_data", {}).get("effect_type", "")
        if not effect_type:
            effect_type = target_ab.get("name", "")

        msg = "Qobiliyat muvaffaqiyatli ishlatildi!"
        
        if "HEAL" in effect_type or "Shifokor" in target_ab["name"]:
            tgt = target_id or user_id
            await self.player_repo.protect_player(game_id, tgt, game.current_round)
            msg = "Tanlangan o'yinchi bu raundda to'liq himoyalandi!"

        elif "PROTECT" in effect_type or "Himoyachi" in target_ab["name"]:
            tgt = target_id or user_id
            await self.player_repo.protect_player(game_id, tgt, game.current_round + 1)
            msg = "Tanlangan o'yinchiga keyingi raund uchun himoya qalqoni berildi!"

        elif "BLOCK" in effect_type or "Bloker" in target_ab["name"]:
            if target_id:
                await self.player_repo.block_ability(game_id, target_id, ability_id=0, until_round=game.current_round + 1)
                msg = "Raqib qobiliyatlari bir raundga bloklandi!"

        await self.player_repo.increment_stats(game_id, user_id, abilities_used=1)
        await self.game_repo.log_action(game_id, game.current_round, user_id, "USE_ABILITY", {"ability_id": ability_id, "target_id": target_id})
        
        await self.event_bus.emit(GameEvent(
            type=GameEventType.ABILITY_USED,
            game_id=game_id,
            data={"user_id": user_id, "ability_name": target_ab["name"], "target_id": target_id}
        ))
        return {"success": True, "message": msg}

    async def use_card(self, game_id: int, user_id: int, player_card_id: int, target_id: Optional[int] = None) -> Dict[str, Any]:
        """Applies a secret card effect."""
        game = await self.game_repo.get_by_id(game_id)
        if not game or game.state in (GameState.LOBBY, GameState.FINISHED):
            return {"success": False, "message": "Kartani bu bosqichda ishlatib bo'lmaydi."}

        cards = await self.player_repo.get_player_cards(game_id, user_id)
        card_entry = next((c for c in cards if c["player_card_id"] == player_card_id and not c["is_used"]), None)
        if not card_entry:
            return {"success": False, "message": "Karta mavjud emas yoki allaqachon ishlatilgan."}

        await self.player_repo.use_card(player_card_id, target_id)
        await self.player_repo.increment_stats(game_id, user_id, cards_used=1)

        # Apply card specific logic
        name = card_entry["name"]
        msg = f"'{name}' kartasi muvaffaqiyatli ishlatildi!"

        if "Qutqaruv" in name or "Qalqon" in name or "Daxlsizlik" in name:
            await self.player_repo.protect_player(game_id, user_id, game.current_round)
            msg = "Sizga ushbu raund uchun daxlsizlik qalqoni berildi!"

        elif "Ikkinchi imkoniyat" in name:
            await self.vote_repo.clear_round_votes(game_id, game.current_round)
            msg = "Joriy raund ovozlari bekor qilindi, qayta ovoz beriladi!"

        elif "Savdo" in name and target_id:
            await self.player_repo.swap_attributes(game_id, user_id, target_id, "profession")
            msg = "Kasblaringiz muvaffaqiyatli almashtirildi!"

        await self.game_repo.log_action(game_id, game.current_round, user_id, "USE_CARD", {"card_name": name, "target_id": target_id})
        await self.event_bus.emit(GameEvent(
            type=GameEventType.CARD_USED,
            game_id=game_id,
            data={"user_id": user_id, "card_name": name}
        ))
        return {"success": True, "message": msg}

    # ==================== TIMEOUT SCHEDULER HANDLER ====================

    async def handle_phase_timeout(self, game_id: int, phase: str) -> None:
        """Handles timer expiration triggers from scheduler."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return

        if phase == GamePhase.LOBBY.value and game.state == GameState.LOBBY:
            # Lobby expired -> start or cancel
            count = await self.player_repo.get_player_count(game_id)
            if count >= self.config.MIN_PLAYERS:
                await self.start_game(game_id, by_user_id=game.created_by or 0)
            else:
                await self.cancel_game(game_id, by_user_id=0)

        elif phase == GamePhase.REVEAL_ATTRIBUTE.value and game.state == GameState.REVEAL_ATTRIBUTE:
            await self.start_discussion_phase(game_id)

        elif phase == GamePhase.DISCUSSION.value and game.state == GameState.DISCUSSION:
            await self.start_voting_phase(game_id)

        elif phase == GamePhase.ABILITY_PHASE.value and game.state == GameState.ABILITY_PHASE:
            await self.start_voting_phase(game_id)

        elif phase == GamePhase.VOTING.value and game.state == GameState.VOTING:
            await self.finalize_voting(game_id)

        elif phase == GamePhase.DUEL.value and game.state == GameState.DUEL:
            await self.finalize_voting(game_id)

    # ==================== DATA GETTERS FOR TELEGRAM ====================

    async def get_game_dashboard_data(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Compiles all data needed to render the rich group chat dashboard."""
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None

        players = await self.player_repo.get_all_players(game_id)
        alive_players = [p for p in players if p.status in (PlayerStatus.ACTIVE, PlayerStatus.PROTECTED)]
        
        # Build player info
        players_data = []
        for p in players:
            u = await self.user_repo.get_by_id(p.user_id)
            players_data.append({
                "user_id": p.user_id,
                "name": u.first_name if u else "O'yinchi",
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "is_protected": p.is_protected
            })

        # Revealed attribute types dynamically from DB
        all_revealed = await self.player_repo.get_all_revealed_attributes(game_id)
        revealed_types = list(dict.fromkeys(a["attribute_type"] for a in all_revealed))

        # Timer remaining
        time_left = await self.timer_engine.get_remaining_time(game_id)
        apocalypse = get_apocalypse_by_type(game.apocalypse_type or "nuclear")

        return {
            "game": game,
            "round": game.current_round,
            "phase": game.state.value if hasattr(game.state, "value") else str(game.state),
            "apocalypse": apocalypse,
            "alive_count": len(alive_players),
            "total_count": len(players),
            "capacity": game.bunker_capacity,
            "time_left": time_left,
            "players": players_data,
            "revealed_types": revealed_types
        }

    async def get_player_private_data(self, game_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Compiles secret cards, abilities, and full attributes for private chat delivery."""
        attrs = await self.player_repo.get_player_attributes(game_id, user_id)
        cards = await self.player_repo.get_player_cards(game_id, user_id)
        abilities = await self.player_repo.get_player_abilities(game_id, user_id)

        return {
            "attributes": {a.attribute_type: a.attribute_value for a in attrs},
            "cards": cards,
            "abilities": abilities
        }
