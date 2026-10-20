CREATE DATABASE IF NOT EXISTS lol_analytics;
USE lol_analytics;

-- =====================================================
-- 1. Create the matches table if it does not exist
-- =====================================================

CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(30) PRIMARY KEY,
    puuid VARCHAR(100) NOT NULL,
    game_date DATETIME NOT NULL,
    game_duration_seconds INT NOT NULL,
    queue_id INT,
    champion VARCHAR(50) NOT NULL,
    role VARCHAR(30),
    win BOOLEAN NOT NULL,
    kills INT NOT NULL,
    deaths INT NOT NULL,
    assists INT NOT NULL,
    total_cs INT NOT NULL,
    gold_earned INT NOT NULL,
    damage_to_champions INT NOT NULL
);

-- =====================================================
-- 2. Select the 100 most recent Ranked Solo/Duo games
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    match_id,
    game_date,
    champion,
    win,
    kills,
    deaths,
    assists,
    total_cs,
    queue_id
FROM latest_100
ORDER BY game_date DESC, match_id DESC;

-- =====================================================
-- 3. Overall ranked statistics for the latest 100 games
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    COUNT(*) AS ranked_games,
    SUM(win) AS wins,
    SUM(CASE WHEN win = 0 THEN 1 ELSE 0 END) AS losses,
    ROUND(100 * AVG(win), 2) AS win_rate_pct
FROM latest_100;

-- =====================================================
-- 4. Champion win-rate analysis
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    champion,
    COUNT(*) AS games,
    SUM(win) AS wins,
    ROUND(100 * AVG(win), 1) AS win_rate_pct
FROM latest_100
GROUP BY champion
ORDER BY win_rate_pct DESC, games DESC;

-- =====================================================
-- 5. Champion performance: win rate, KDA, and CS/min
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    champion,
    COUNT(*) AS games,
    SUM(win) AS wins,
    ROUND(100 * AVG(win), 1) AS win_rate_pct,
    ROUND(
        AVG((kills + assists) * 1.0 / GREATEST(deaths, 1)),
        2
    ) AS avg_kda,
    ROUND(
        SUM(total_cs) / NULLIF(SUM(game_duration_seconds) / 60.0, 0),
        2
    ) AS cs_per_min
FROM latest_100
GROUP BY champion
ORDER BY games DESC, win_rate_pct DESC;

-- =====================================================
-- 6. Cumulative and rolling 20-game win-rate trends
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
),
ranked_games AS (
    SELECT
        match_id,
        game_date,
        champion,
        win,
        ROW_NUMBER() OVER (
            ORDER BY game_date, match_id
        ) AS game_number,
        AVG(win) OVER (
            ORDER BY game_date, match_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) * 100 AS cumulative_win_rate,
        AVG(win) OVER (
            ORDER BY game_date, match_id
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) * 100 AS rolling_20_game_win_rate,
        COUNT(*) OVER (
            ORDER BY game_date, match_id
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS games_in_window
    FROM latest_100
)
SELECT
    game_number,
    game_date,
    champion,
    CASE
        WHEN win = 1 THEN 'Win'
        ELSE 'Loss'
    END AS result,
    ROUND(cumulative_win_rate, 1) AS cumulative_win_rate_pct,
    CASE
        WHEN games_in_window = 20
        THEN ROUND(rolling_20_game_win_rate, 1)
        ELSE NULL
    END AS rolling_20_game_win_rate_pct
FROM ranked_games
ORDER BY game_number;

-- =====================================================
-- 7. Match history for analysis and visualization
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    match_id,
    game_date,
    champion,
    role,
    win,
    kills,
    deaths,
    assists,
    total_cs,
    game_duration_seconds,
    gold_earned,
    damage_to_champions
FROM latest_100
ORDER BY game_date, match_id;

-- =====================================================
-- 8. Date range covered by the latest 100 ranked games
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    COUNT(*) AS total_matches,
    MIN(game_date) AS oldest_match,
    MAX(game_date) AS newest_match
FROM latest_100;

-- =====================================================
-- 9. Ranked games by role
-- =====================================================

WITH latest_100 AS (
    SELECT *
    FROM matches
    WHERE queue_id = 420
    ORDER BY game_date DESC, match_id DESC
    LIMIT 100
)
SELECT
    role,
    COUNT(*) AS games,
    SUM(win) AS wins,
    SUM(CASE WHEN win = 0 THEN 1 ELSE 0 END) AS losses,
    ROUND(100 * AVG(win), 1) AS win_rate_pct
FROM latest_100
GROUP BY role
ORDER BY games DESC;

-- =====================================================
-- 10. Export the latest 100 ranked matches for Tableau
-- =====================================================

SELECT
    match_id,
    game_date,
    game_duration_seconds,
    champion,
    role,
    win,
    kills,
    deaths,
    assists,
    total_cs,
    gold_earned,
    damage_to_champions
FROM matches
WHERE queue_id = 420
ORDER BY game_date DESC, match_id DESC
LIMIT 100;
