import pandas as pd
from analyze_matches import calculate_win_rates, get_champion_stats, check_data_quality, get_champion_recommendations

def create_test_data():
    """Create a small, predictable dataset for testing."""

    return pd.DataFrame({
        "game_date": pd.to_datetime([
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
        ]),
        "champion": ["Yasuo", "Yasuo", "Galio"],
        "win": [True, False, True],
        "kills": [10, 2, 5],
        "deaths": [2, 5, 1],
        "assists": [5, 3, 4],
        "total_cs": [200, 150, 180],
        "game_duration_seconds": [1800, 1500, 1800],
        "gold_earned": [12000, 9000, 11000],
        "damage_to_champions": [25000, 12000, 20000],
    })


def test_cumulative_win_rate():
    df = create_test_data()
    result = calculate_win_rates(df)

    expected = [100.0, 50.0, 100 * 2 / 3]

    for actual, target in zip(
        result["cumulative_win_rate"], expected
    ):
        assert abs(actual - target) < 0.01


def test_champion_game_counts():
    df = create_test_data()
    result = get_champion_stats(df)

    yasuo = result[result["champion"] == "Yasuo"].iloc[0]
    galio = result[result["champion"] == "Galio"].iloc[0]

    assert yasuo["games"] == 2
    assert yasuo["wins"] == 1
    assert galio["games"] == 1
    assert galio["wins"] == 1


def test_champion_win_rates():
    df = create_test_data()
    result = get_champion_stats(df)

    yasuo = result[result["champion"] == "Yasuo"].iloc[0]
    galio = result[result["champion"] == "Galio"].iloc[0]

    assert yasuo["win_rate_pct"] == 50.0
    assert galio["win_rate_pct"] == 100.0
    
def test_champion_with_zero_deaths():
    df = create_test_data()
    df.loc[0, "deaths"] = 0

    result = get_champion_stats(df)
    yasuo = result[result["champion"] == "Yasuo"].iloc[0]

    # (10 kills + 5 assists) / 1 death = 15 KDA
    assert yasuo["avg_kda"] == 8.0
    
def test_rolling_win_rate_with_fewer_than_10_games():
    df = create_test_data()
    result = calculate_win_rates(df)

    # A full 10-game window is required.
    assert result["rolling_win_rate"].isna().all()
    
def test_rolling_win_rate_with_10_games():
    df = pd.DataFrame({
        "win": [
            True, False, True, True, False,
            True, False, True, True, False
        ]
    })

    result = calculate_win_rates(df)

    # 6 wins out of 10 games = 60%
    assert result["rolling_win_rate"].iloc[-1] == 60.0
    
def test_data_quality_detects_duplicate_match_ids(capsys):
    df = pd.DataFrame({
        "match_id": ["NA1_123", "NA1_123", "NA1_456"],
        "win": [True, False, True],
    })

    check_data_quality(df)

    captured = capsys.readouterr()

    assert "Duplicate match IDs: 1" in captured.out
    
def test_data_quality_detects_missing_values(capsys):
    df = pd.DataFrame({
        "match_id": ["NA1_123", "NA1_456"],
        "champion": ["Yasuo", None],
        "win": [True, False],
    })

    check_data_quality(df)

    captured = capsys.readouterr()

    assert "Missing values by column:" in captured.out
    assert "champion" in captured.out
    assert "1" in captured.out
    
def test_champion_recommendations_require_minimum_games(capsys):
    champion_stats = pd.DataFrame({
        "champion": ["Yasuo", "Galio", "Ahri"],
        "games": [10, 3, 6],
        "win_rate_pct": [60.0, 100.0, 50.0],
    })

    get_champion_recommendations(champion_stats)

    captured = capsys.readouterr()

    # Galio has a 100% win rate but only 3 games.
    # It should not qualify for a recommendation.
    assert "Yasuo" in captured.out
    assert "Ahri" in captured.out
    assert "Galio" not in captured.out
    
def test_champion_recommendations_when_no_champion_qualifies(capsys):
    champion_stats = pd.DataFrame({
        "champion": ["Yasuo", "Galio"],
        "games": [2, 4],
        "win_rate_pct": [50.0, 75.0],
    })

    get_champion_recommendations(champion_stats)

    captured = capsys.readouterr()

    assert "No champion has at least 5 games." in captured.out