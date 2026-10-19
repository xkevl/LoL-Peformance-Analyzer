
import matplotlib.pyplot as plt
from pathlib import Path
from analyze_matches import load_matches_from_mysql
from config import SELECTED_ROLE

# Set up the charts folder
CHARTS_DIR = Path(__file__).resolve().parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# Load ranked match data
df = load_matches_from_mysql()

# Filter by the selected role
selected_role = SELECTED_ROLE

if selected_role != "ALL":
    df = df[df["role"] == selected_role].copy()

# Sort matches chronologically
df = df.sort_values("game_date").reset_index(drop=True)

if df.empty:
    print("No match data available for the selected role.")
else:
    # Ensure dates are in datetime format
    df["game_date"] = plt.matplotlib.dates.date2num(
        df["game_date"].astype("datetime64[ns]")
    )

    # Calculate win-rate trends
    df["cumulative_win_rate"] = df["win"].expanding().mean() * 100
    df["rolling_win_rate"] = (
        df["win"].rolling(window=10, min_periods=10).mean() * 100
    )

    # Create the chart
    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(
        range(1, len(df) + 1),
        df["cumulative_win_rate"],
        label="Cumulative Win Rate",
        linewidth=2
    )

    ax.plot(
        range(1, len(df) + 1),
        df["rolling_win_rate"],
        label="Rolling 10-Game Win Rate",
        marker="o",
        linewidth=2
    )

    ax.axhline(
        y=50,
        linestyle="--",
        linewidth=1,
        label="50% Win Rate"
    )

    role_title = (
        "All Roles"
        if selected_role == "ALL"
        else selected_role.title()
    )

    ax.set_title(f"Ranked Solo/Duo Win Rate Over Time — {role_title}")
    ax.set_xlabel("Game Number (Oldest to Newest)")
    ax.set_ylabel("Win Rate (%)")
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()

    # Save chart to the charts folder
    fig.savefig(
        CHARTS_DIR / "win_rate_trends.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()
