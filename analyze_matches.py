import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
from pathlib import Path
from config import SELECTED_ROLE

project_folder = Path(__file__).resolve().parent


def load_matches(csv_path):
    """Load match data and sort it chronologically."""
    df = pd.read_csv(csv_path)
    df["game_date"] = pd.to_datetime(df["game_date"])
    df = df.sort_values("game_date").reset_index(drop=True)
    return df


def load_matches_from_mysql():
    """Load ranked matches directly from MySQL."""

    load_dotenv()

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database="lol_analytics"
    )


    query = """
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
        FROM matches
        WHERE queue_id = 420
        ORDER BY game_date
    """

    try:
        df = pd.read_sql(query, connection)
    finally:
        connection.close()

    df["game_date"] = pd.to_datetime(df["game_date"])

    # Remove records with invalid or missing game durations
    df = df[
        df["game_duration_seconds"].notna()
        & (df["game_duration_seconds"] > 0)
    ].copy()

    return df.reset_index(drop=True)


def calculate_win_rates(df):
    """Add cumulative and rolling 10-game win rates."""
    df = df.copy()

    df["cumulative_win_rate"] = (
        df["win"].expanding().mean() * 100
    )

    df["rolling_win_rate"] = (
        df["win"].rolling(window=10, min_periods=10).mean() * 100
    )

    return df


def get_champion_stats(df):
    """Calculate performance metrics for each champion."""
    df = df.copy()

    # Calculate KDA for each match
    df["kda"] = (
        (df["kills"] + df["assists"]) / df["deaths"].clip(lower=1)
    )

    # Calculate CS per minute for each match
    df["cs_per_min"] = (
        df["total_cs"] / (df["game_duration_seconds"] / 60)
    )

    df["gold_per_min"] = (
        df["gold_earned"] / (df["game_duration_seconds"] / 60)
    )

    df["damage_per_min"] = (
        df["damage_to_champions"] / (df["game_duration_seconds"] / 60)
    )
    
    # Summarize performance by champion
    stats = df.groupby("champion").agg(
        games=("win", "count"),
        wins=("win", "sum"),
        avg_kda=("kda", "mean"),
        avg_cs_per_min=("cs_per_min", "mean"),
        avg_gold=("gold_earned", "mean"),
        avg_gold_per_min=("gold_per_min", "mean"),
        avg_damage=("damage_to_champions", "mean"),
        avg_damage_per_min=("damage_per_min", "mean")
    ).reset_index()

    stats["win_rate_pct"] = (
        stats["wins"] / stats["games"] * 100
    )

    stats["avg_kda"] = stats["avg_kda"].round(2)
    stats["avg_cs_per_min"] = stats["avg_cs_per_min"].round(2)
    stats["avg_gold"] = stats["avg_gold"].round(0).astype(int)
    stats["avg_gold_per_min"] = stats["avg_gold_per_min"].round(0).astype(int)
    stats["avg_damage"] = stats["avg_damage"].round(0).astype(int)
    stats["avg_damage_per_min"] = stats["avg_damage_per_min"].round(0).astype(int)
    stats["win_rate_pct"] = stats["win_rate_pct"].round(1)
    stats["win_rate_reliable"] = stats["games"] >= 5

    return stats.sort_values(
        ["games", "win_rate_pct"],
        ascending=[False, False]
).reset_index(drop=True)

def get_champion_recommendations(champion_stats, min_games=5):
    """Identify strongest and weakest champions with enough games."""

    reliable_stats = champion_stats[
        champion_stats["games"] >= min_games
    ].copy()

    if reliable_stats.empty:
        print(
            f"\nNot enough champion data yet. "
            f"No champion has at least {min_games} games."
        )
        return

    strongest = reliable_stats.sort_values(
        ["win_rate_pct", "games"],
        ascending=[False, False]
    ).iloc[0]

    weakest = reliable_stats.sort_values(
        ["win_rate_pct", "games"],
        ascending=[True, False]
    ).iloc[0]

    print(f"\nStrongest champion (minimum {min_games} games):")
    print(
        f"{strongest['champion']}: "
        f"{strongest['win_rate_pct']}% win rate "
        f"across {int(strongest['games'])} games"
    )

    print(f"\nWeakest champion (minimum {min_games} games):")
    print(
        f"{weakest['champion']}: "
        f"{weakest['win_rate_pct']}% win rate "
        f"across {int(weakest['games'])} games"
    )

def get_role_stats(df):
    """Summarize ranked performance by role."""

    df = df.copy()

    df["kda"] = (
        (df["kills"] + df["assists"])
        / df["deaths"].clip(lower=1)
    )

    stats = df.groupby("role").agg(
        games=("win", "count"),
        wins=("win", "sum"),
        avg_kda=("kda", "mean"),
        avg_cs_per_min=(
            "total_cs",
            lambda cs: (
                cs / (df.loc[cs.index, "game_duration_seconds"] / 60)
            ).mean()
        ),
        avg_gold=("gold_earned", "mean"),
        avg_damage=("damage_to_champions", "mean")
    ).reset_index()

    stats["win_rate_pct"] = (
        stats["wins"] / stats["games"] * 100
    ).round(1)

    stats["avg_kda"] = stats["avg_kda"].round(2)
    stats["avg_cs_per_min"] = stats["avg_cs_per_min"].round(2)
    stats["avg_gold"] = stats["avg_gold"].round(0).astype(int)
    stats["avg_damage"] = stats["avg_damage"].round(0).astype(int)

    return stats.sort_values(
        ["games", "win_rate_pct"],
        ascending=[False, False]
    ).reset_index(drop=True)

def get_recent_form(df):
    """Compare win rate across the last 5 and last 20 games."""

    if df.empty:
        print("\nNo games available for recent-form analysis.")
        return

    # Ensure games are in chronological order
    df = df.sort_values("game_date").reset_index(drop=True)

    last_5 = df.tail(5)
    last_20 = df.tail(20)

    last_5_win_rate = last_5["win"].mean() * 100
    last_20_win_rate = last_20["win"].mean() * 100

    print("\nRecent form:")
    print(
        f"Last {len(last_5)} games: "
        f"{last_5_win_rate:.1f}% win rate"
    )
    print(
        f"Last {len(last_20)} games: "
        f"{last_20_win_rate:.1f}% win rate"
    )

    difference = last_5_win_rate - last_20_win_rate

    if difference > 0:
        print(f"Recent win rate is up {difference:.1f} percentage points.")
    elif difference < 0:
        print(
            f"Recent win rate is down {abs(difference):.1f} "
            "percentage points."
        )
    else:
        print("Recent win rate matches your last-20-game rate.")

def compare_wins_and_losses(df):
    """Compare average performance in wins versus losses."""

    if df.empty:
        print("\nNo matches available for win/loss comparison.")
        return

    df = df.copy()

    df["kda"] = (
        (df["kills"] + df["assists"])
        / df["deaths"].clip(lower=1)
    )

    df["cs_per_min"] = (
        df["total_cs"] / (df["game_duration_seconds"] / 60)
    )

    df["gold_per_min"] = (
        df["gold_earned"] / (df["game_duration_seconds"] / 60)
    )

    df["damage_per_min"] = (
        df["damage_to_champions"]
        / (df["game_duration_seconds"] / 60)
    )

    comparison = df.groupby("win").agg(
        games=("win", "count"),
        avg_kda=("kda", "mean"),
        avg_cs_per_min=("cs_per_min", "mean"),
        avg_gold_per_min=("gold_per_min", "mean"),
        avg_damage_per_min=("damage_per_min", "mean")
    ).reset_index()

    comparison["result"] = comparison["win"].map({
        True: "Win",
        False: "Loss"
    })

    comparison = comparison.drop(columns=["win"])

    numeric_columns = [
        "avg_kda",
        "avg_cs_per_min",
        "avg_gold_per_min",
        "avg_damage_per_min"
    ]

    comparison[numeric_columns] = (
        comparison[numeric_columns].round(2)
    )

    print("\nWin vs. Loss Comparison:")
    print(comparison.to_string(index=False))

    return comparison

def check_data_quality(df):
    """Report missing values and duplicate match IDs."""

    print("\nData Quality Report:")
    print(f"Total records loaded: {len(df)}")

    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]

    if missing_values.empty:
        print("Missing values: None")
    else:
        print("Missing values by column:")
        print(missing_values.to_string())

    if "match_id" in df.columns:
        duplicate_count = df["match_id"].duplicated().sum()
        print(f"Duplicate match IDs: {duplicate_count}")
    else:
        print("Duplicate match IDs: Not checked (match_id not loaded)")

if __name__ == "__main__":
    all_matches = load_matches_from_mysql()
    check_data_quality(all_matches)
    # Export the match-level dataset
    matches_report_path = project_folder / "ranked_match_history.csv"

    all_matches.to_csv(matches_report_path, index=False)

    print(f"Match history saved to: {matches_report_path}")

    # Summarize every role before applying the role filter
    role_stats = get_role_stats(all_matches)
    # Export role performance to a CSV report
    role_report_path = project_folder / "role_performance_report.csv"

    role_stats.to_csv(role_report_path, index=False)

    print(f"Role report saved to: {role_report_path}")

    # Choose which role to analyze: MIDDLE, TOP, JUNGLE,
    # BOTTOM, UTILITY, or ALL
    selected_role = SELECTED_ROLE

    matches = all_matches.copy()

    if selected_role != "ALL":
        matches = matches[matches["role"] == selected_role].copy()

    matches = calculate_win_rates(matches)
    champion_stats = get_champion_stats(matches)
    win_loss_stats = compare_wins_and_losses(matches)

    if win_loss_stats is not None:
        win_loss_report_path = (
            project_folder / "win_loss_comparison_report.csv"
        )

        win_loss_stats.to_csv(win_loss_report_path, index=False)

        print(
            f"Win/loss report saved to: {win_loss_report_path}"
        )
        
    # Export champion statistics to a CSV report
    report_path = project_folder / "champion_performance_report.csv"

    champion_stats.to_csv(report_path, index=False)

    print(f"\nChampion report saved to: {report_path}")
    get_recent_form(matches)

    print(f"\nOverall ranked performance ({selected_role}):")
    print(f"Games analyzed: {len(matches)}")
    print(f"Wins: {int(matches['win'].sum())}")
    print(f"Win rate: {matches['win'].mean() * 100:.1f}%"
          if len(matches) > 0 else "Win rate: N/A")

    print("\nRole performance:")
    print(role_stats.to_string(index=False))

    print(f"\nChampion performance ({selected_role}):")
    print(champion_stats.to_string(index=False))
    get_champion_recommendations(champion_stats)