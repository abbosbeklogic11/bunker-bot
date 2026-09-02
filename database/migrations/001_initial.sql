-- =============================================================
-- Migration 001: Initial schema for BUNKER Telegram game
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- USERS
CREATE TABLE IF NOT EXISTS users (
    id                  BIGINT          PRIMARY KEY,
    username            VARCHAR(64),
    first_name          VARCHAR(128)    NOT NULL DEFAULT '',
    is_bot_started      BOOLEAN         NOT NULL DEFAULT FALSE,
    is_banned           BOOLEAN         NOT NULL DEFAULT FALSE,
    is_admin            BOOLEAN         NOT NULL DEFAULT FALSE,
    coins               INT             NOT NULL DEFAULT 0,
    diamonds            INT             NOT NULL DEFAULT 0,
    level               INT             NOT NULL DEFAULT 1,
    experience          INT             NOT NULL DEFAULT 0,
    reputation          INT             NOT NULL DEFAULT 0,
    games_played        INT             NOT NULL DEFAULT 0,
    games_won           INT             NOT NULL DEFAULT 0,
    games_lost          INT             NOT NULL DEFAULT 0,
    mvp_count           INT             NOT NULL DEFAULT 0,
    eliminations_count  INT             NOT NULL DEFAULT 0,
    survival_count      INT             NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- GAMES
CREATE TABLE IF NOT EXISTS games (
    id                      SERIAL          PRIMARY KEY,
    group_chat_id           BIGINT          NOT NULL,
    dashboard_message_id    BIGINT,
    state                   VARCHAR(32)     NOT NULL DEFAULT 'LOBBY',
    current_round           INT             NOT NULL DEFAULT 0,
    current_attribute_index INT             NOT NULL DEFAULT 0,
    apocalypse_type         VARCHAR(128),
    bunker_capacity         INT             NOT NULL DEFAULT 4,
    bunker_food_days        INT,
    bunker_water_days       INT,
    bunker_power_days       INT,
    bunker_has_farm         BOOLEAN         NOT NULL DEFAULT FALSE,
    bunker_has_medical      BOOLEAN         NOT NULL DEFAULT FALSE,
    bunker_has_workshop     BOOLEAN         NOT NULL DEFAULT FALSE,
    bunker_has_radio        BOOLEAN         NOT NULL DEFAULT FALSE,
    phase_started_at        TIMESTAMPTZ,
    phase_ends_at           TIMESTAMPTZ,
    config                  JSONB           NOT NULL DEFAULT '{}',
    created_by              BIGINT          REFERENCES users(id) ON DELETE SET NULL,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    finished_at             TIMESTAMPTZ
);

-- GAME PLAYERS
CREATE TABLE IF NOT EXISTS game_players (
    id                      SERIAL,
    game_id                 INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id                 BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status                  VARCHAR(32)     NOT NULL DEFAULT 'ACTIVE',
    survival_score          INT             NOT NULL DEFAULT 0,
    is_protected            BOOLEAN         NOT NULL DEFAULT FALSE,
    protected_until_round   INT,
    join_order              INT             NOT NULL DEFAULT 0,
    elimination_round       INT,
    elimination_votes       INT,
    votes_received_total    INT             NOT NULL DEFAULT 0,
    votes_given_total       INT             NOT NULL DEFAULT 0,
    abilities_used          INT             NOT NULL DEFAULT 0,
    cards_used              INT             NOT NULL DEFAULT 0,
    joined_at               TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    UNIQUE (game_id, user_id)
);

-- PLAYER ATTRIBUTES
CREATE TABLE IF NOT EXISTS player_attributes (
    id                  SERIAL          PRIMARY KEY,
    game_id             INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id             BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    attribute_type      VARCHAR(32)     NOT NULL,
    attribute_value     VARCHAR(256)    NOT NULL,
    attribute_metadata  JSONB           NOT NULL DEFAULT '{}',
    is_revealed         BOOLEAN         NOT NULL DEFAULT FALSE,
    is_fake             BOOLEAN         NOT NULL DEFAULT FALSE,
    revealed_at         TIMESTAMPTZ
);

-- CARDS (catalogue)
CREATE TABLE IF NOT EXISTS cards (
    id          SERIAL          PRIMARY KEY,
    name        VARCHAR(128)    NOT NULL,
    description TEXT            NOT NULL DEFAULT '',
    rarity      VARCHAR(16)     NOT NULL DEFAULT 'COMMON',
    power       INT             NOT NULL DEFAULT 1,
    card_type   VARCHAR(32)     NOT NULL,
    effect_data JSONB           NOT NULL DEFAULT '{}',
    is_active   BOOLEAN         NOT NULL DEFAULT TRUE
);

-- PLAYER CARDS (instances dealt to players)
CREATE TABLE IF NOT EXISTS player_cards (
    id              SERIAL          PRIMARY KEY,
    game_id         INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id         BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id         INT             NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    is_used         BOOLEAN         NOT NULL DEFAULT FALSE,
    used_at         TIMESTAMPTZ,
    used_on_user_id BIGINT          REFERENCES users(id) ON DELETE SET NULL,
    obtained_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ABILITIES (catalogue)
CREATE TABLE IF NOT EXISTS abilities (
    id                  SERIAL          PRIMARY KEY,
    name                VARCHAR(128)    NOT NULL,
    description         TEXT            NOT NULL DEFAULT '',
    ability_type        VARCHAR(32)     NOT NULL,
    trigger_condition   VARCHAR(32)     NOT NULL DEFAULT 'manual',
    power               INT             NOT NULL DEFAULT 1,
    uses_per_game       INT             NOT NULL DEFAULT 1,
    effect_data         JSONB           NOT NULL DEFAULT '{}',
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE
);

-- PLAYER ABILITIES
CREATE TABLE IF NOT EXISTS player_abilities (
    id                  SERIAL          PRIMARY KEY,
    game_id             INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id             BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ability_id          INT             NOT NULL REFERENCES abilities(id) ON DELETE CASCADE,
    uses_remaining      INT             NOT NULL DEFAULT 1,
    is_blocked          BOOLEAN         NOT NULL DEFAULT FALSE,
    blocked_until_round INT
);

-- VOTES
CREATE TABLE IF NOT EXISTS votes (
    id              SERIAL          PRIMARY KEY,
    game_id         INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    round_number    INT             NOT NULL,
    voter_id        BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_id       BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vote_weight     INT             NOT NULL DEFAULT 1,
    is_valid        BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (game_id, round_number, voter_id)
);

-- GAME EVENTS
CREATE TABLE IF NOT EXISTS game_events (
    id              SERIAL          PRIMARY KEY,
    game_id         INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    round_number    INT             NOT NULL DEFAULT 0,
    event_type      VARCHAR(64)     NOT NULL,
    event_data      JSONB           NOT NULL DEFAULT '{}',
    triggered_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    resolved        BOOLEAN         NOT NULL DEFAULT FALSE,
    resolved_by     BIGINT          REFERENCES users(id) ON DELETE SET NULL
);

-- ACTIONS (audit log)
CREATE TABLE IF NOT EXISTS actions (
    id              SERIAL          PRIMARY KEY,
    game_id         INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    round_number    INT             NOT NULL DEFAULT 0,
    actor_id        BIGINT          REFERENCES users(id) ON DELETE SET NULL,
    action_type     VARCHAR(64)     NOT NULL,
    action_data     JSONB           NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ACHIEVEMENTS (catalogue)
CREATE TABLE IF NOT EXISTS achievements (
    id              SERIAL          PRIMARY KEY,
    code            VARCHAR(64)     NOT NULL UNIQUE,
    name            VARCHAR(128)    NOT NULL,
    description     TEXT            NOT NULL DEFAULT '',
    icon            VARCHAR(16)     NOT NULL DEFAULT '',
    reward_coins    INT             NOT NULL DEFAULT 0,
    reward_diamonds INT             NOT NULL DEFAULT 0
);

-- USER ACHIEVEMENTS
CREATE TABLE IF NOT EXISTS user_achievements (
    user_id         BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id  INT             NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, achievement_id)
);

-- REWARDS
CREATE TABLE IF NOT EXISTS rewards (
    id              SERIAL          PRIMARY KEY,
    game_id         INT             NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id         BIGINT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    place           INT,
    coins_reward    INT             NOT NULL DEFAULT 0,
    diamonds_reward INT             NOT NULL DEFAULT 0,
    bonus_type      VARCHAR(64),
    granted_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_users_username         ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_is_banned        ON users (is_banned);
CREATE INDEX IF NOT EXISTS idx_users_is_admin         ON users (is_admin);
CREATE INDEX IF NOT EXISTS idx_games_group_chat_id    ON games (group_chat_id);
CREATE INDEX IF NOT EXISTS idx_games_state            ON games (state);
CREATE INDEX IF NOT EXISTS idx_games_created_by       ON games (created_by);
CREATE INDEX IF NOT EXISTS idx_games_created_at       ON games (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_gp_game_id             ON game_players (game_id);
CREATE INDEX IF NOT EXISTS idx_gp_user_id             ON game_players (user_id);
CREATE INDEX IF NOT EXISTS idx_gp_status              ON game_players (game_id, status);
CREATE INDEX IF NOT EXISTS idx_pa_game_user           ON player_attributes (game_id, user_id);
CREATE INDEX IF NOT EXISTS idx_pa_attr_type           ON player_attributes (game_id, attribute_type);
CREATE INDEX IF NOT EXISTS idx_pa_revealed            ON player_attributes (game_id, is_revealed);
CREATE INDEX IF NOT EXISTS idx_pc_game_user           ON player_cards (game_id, user_id);
CREATE INDEX IF NOT EXISTS idx_pc_card_id             ON player_cards (card_id);
CREATE INDEX IF NOT EXISTS idx_pab_game_user          ON player_abilities (game_id, user_id);
CREATE INDEX IF NOT EXISTS idx_votes_game_round       ON votes (game_id, round_number);
CREATE INDEX IF NOT EXISTS idx_votes_voter            ON votes (voter_id);
CREATE INDEX IF NOT EXISTS idx_votes_target           ON votes (target_id);
CREATE INDEX IF NOT EXISTS idx_votes_valid            ON votes (game_id, round_number, is_valid);
CREATE INDEX IF NOT EXISTS idx_ge_game_id             ON game_events (game_id);
CREATE INDEX IF NOT EXISTS idx_ge_resolved            ON game_events (game_id, resolved);
CREATE INDEX IF NOT EXISTS idx_actions_game_id        ON actions (game_id);
CREATE INDEX IF NOT EXISTS idx_actions_actor          ON actions (actor_id);
CREATE INDEX IF NOT EXISTS idx_actions_type           ON actions (action_type);
CREATE INDEX IF NOT EXISTS idx_rewards_game_id        ON rewards (game_id);
CREATE INDEX IF NOT EXISTS idx_rewards_user_id        ON rewards (user_id);
CREATE INDEX IF NOT EXISTS idx_ua_user_id             ON user_achievements (user_id);
