import os
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# INPUT YOUR STATS HERE:

WIN_PROBABILITY = 0.5231
LOSE_PROBABILITY = 0.4769

AVERAGE_WIN = 0.011635
AVERAGE_LOSS = -0.012596

TRADES_PER_RUN = 800
NUM_RUNS = 1000

STARTING_CAPITAL = 10000

# Number of equity curves shown in the background
CURVES_TO_PLOT = 100

# Random seed
# None = different results every run
# Example: 42 = reproducible results
RANDOM_SEED = None


# ================================================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FOLDER = Path(f"MONTE_CARLO_REPORT_{timestamp}")
OUTPUT_FOLDER.mkdir(parents=True,exist_ok=True)


# RANDOM GENERATOR
rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# VALIDATION

if not np.isclose(WIN_PROBABILITY + LOSE_PROBABILITY,1.0):
    raise ValueError("WIN_PROBABILITY + LOSE_PROBABILITY must equal 1.0")

if WIN_PROBABILITY < 0 or WIN_PROBABILITY > 1:
    raise ValueError("WIN_PROBABILITY must be between 0 and 1")

if LOSE_PROBABILITY < 0 or LOSE_PROBABILITY > 1:
    raise ValueError("LOSE_PROBABILITY must be between 0 and 1")

if TRADES_PER_RUN <= 0:
    raise ValueError("TRADES_PER_RUN must be greater than 0")

if NUM_RUNS <= 0:
    raise ValueError("NUM_RUNS must be greater than 0")

if STARTING_CAPITAL <= 0:
    raise ValueError("STARTING_CAPITAL must be greater than 0")

if AVERAGE_LOSS <= -1:
    raise ValueError("AVERAGE_LOSS must be greater than -100%")


# ============================================================
# TRADE AXIS
trades = np.arange(TRADES_PER_RUN + 1)


# ============================================================
# EXPECTANCY
EXPECTED_RETURN_PER_TRADE = (WIN_PROBABILITY * AVERAGE_WIN + LOSE_PROBABILITY * AVERAGE_LOSS)
EXPECTED_RETURN_PERCENT = (EXPECTED_RETURN_PER_TRADE * 100)


# ============================================================
# PRINT INITIAL INFORMATION

print("=" * 70)
print("MONTE CARLO SIMULATION")
print("=" * 70)

print(f"Runs:             {NUM_RUNS:,}")
print(f"Trades per run:   {TRADES_PER_RUN:,}")
print(f"Total trades:     "f"{NUM_RUNS * TRADES_PER_RUN:,}")
print()

print(f"Win probability:  "f"{WIN_PROBABILITY * 100:.4f}%")
print(f"Loss probability: "f"{LOSE_PROBABILITY * 100:.4f}%")
print(f"Average win:      "f"{AVERAGE_WIN * 100:.4f}%")
print(f"Average loss:     "f"{AVERAGE_LOSS * 100:.4f}%")
print()

print(f"Expected return/trade: "f"{EXPECTED_RETURN_PERCENT:.6f}%")
print()

print("Starting simulation...")


# ============================================================
# MONTE CARLO SIMULATION

# ------------------------------------------------------------
# Generate random numbers
#
# Shape:
#
#       rows    = trades
#       columns = simulations
#
# ------------------------------------------------------------

random_numbers = rng.random((TRADES_PER_RUN,NUM_RUNS))


# ------------------------------------------------------------
# Determine wins/losses
#
# True  = win
# False = loss
# ------------------------------------------------------------

wins = (random_numbers < WIN_PROBABILITY)


# ============================================================
# ACTUAL TRADE RETURNS

trade_returns = np.where(wins,AVERAGE_WIN,AVERAGE_LOSS)


# ============================================================
# EQUITY CURVES

# Each column = one simulation
#
# Row 0 = starting capital
# Row 1 = after trade 1
# Row 2 = after trade 2
# ...
# Row N = after final trade

growth_factors = (1 + trade_returns)

equity_curves = np.empty((TRADES_PER_RUN + 1, NUM_RUNS))

equity_curves[0, :] = (STARTING_CAPITAL)

equity_curves[1:, :] = (STARTING_CAPITAL * np.cumprod(growth_factors, axis=0))


# ============================================================
# THEORETICAL EXPECTED CURVE

theoretical_curve = (STARTING_CAPITAL * (1 + EXPECTED_RETURN_PER_TRADE) ** trades)

theoretical_final = (theoretical_curve[-1])


# ============================================================
# FINAL RESULTS

final_capital = (equity_curves[-1, :])

final_return = (final_capital / STARTING_CAPITAL) - 1


# ============================================================
# ACTUAL WIN RATE

actual_wins = (wins.sum(axis=0))

actual_losses = (TRADES_PER_RUN - actual_wins)

actual_win_rate = (actual_wins / TRADES_PER_RUN)


# ============================================================
# MAXIMUM DRAWDOWN

running_peak = np.maximum.accumulate(equity_curves, axis=0)

drawdown = (equity_curves / running_peak) - 1

max_drawdown = (drawdown.min(axis=0))


# ============================================================
# MAXIMUM LOSING STREAK

def calculate_max_losing_streak(win_array):

    max_streak = 0
    current_streak = 0

    for is_win in win_array:

        if is_win:

            current_streak = 0

        else:

            current_streak += 1

            if current_streak > max_streak:

                max_streak = (current_streak)

    return max_streak


max_losing_streak = np.array([
    calculate_max_losing_streak(
        wins[:, i]
    )
    for i in range(NUM_RUNS)
])


# ============================================================
# PROFITABLE / LOSING SIMULATIONS

profitable = (final_capital > STARTING_CAPITAL)

losing = (final_capital < STARTING_CAPITAL)

breakeven = np.isclose(final_capital, STARTING_CAPITAL)

profit_probability = (profitable.mean())

loss_probability = (losing.mean())

breakeven_probability = (breakeven.mean())


# ============================================================
# BASIC STATISTICS

average_final = np.mean(final_capital)

median_final = np.median(final_capital)

std_final = np.std(final_capital)

best_final = np.max(final_capital)

worst_final = np.min(final_capital)

return_mean = np.mean(final_return)

return_median = np.median(final_return)

return_std = np.std(final_return)

best_return = np.max(final_return)

worst_return = np.min(final_return)


# ============================================================
# PERCENTILES

capital_p5 = np.percentile(final_capital, 5)

capital_p10 = np.percentile(final_capital, 10)

capital_p25 = np.percentile(final_capital, 25)

capital_p50 = np.percentile(final_capital, 50)

capital_p75 = np.percentile(final_capital, 75)

capital_p90 = np.percentile(final_capital, 90)

capital_p95 = np.percentile(final_capital, 95)

drawdown_p5 = np.percentile(max_drawdown, 5)

drawdown_p25 = np.percentile(max_drawdown, 25)

drawdown_p50 = np.percentile(max_drawdown, 50)

drawdown_p75 = np.percentile(max_drawdown, 75)

drawdown_p95 = np.percentile(max_drawdown, 95)


# ============================================================
# FIND REPRESENTATIVE RUNS

# ------------------------------------------------------------
# Median run
#
# We select the ACTUAL simulation whose final capital
# is closest to the statistical median.
# ------------------------------------------------------------

median_index = np.argmin(np.abs(final_capital - median_final))

# ------------------------------------------------------------
# Best run
# ------------------------------------------------------------

best_index = np.argmax(final_capital)


# ------------------------------------------------------------
# Worst run
# ------------------------------------------------------------

worst_index = np.argmin(final_capital)


# ============================================================
# REPRESENTATIVE CURVES

median_curve = (equity_curves[:, median_index])

best_curve = (equity_curves[:, best_index])

worst_curve = (equity_curves[:, worst_index])


# ============================================================
# PRINT SUMMARY

print()
print("Simulation finished.")
print()

print("=" * 70)
print("RESULT SUMMARY")
print("=" * 70)
print()

print(f"Expected return/trade:     "f"{EXPECTED_RETURN_PERCENT:.6f}%")
print(f"Theoretical final value:   "f"${theoretical_final:,.2f}")
print()

print(f"Average final capital:     "f"${average_final:,.2f}")
print(f"Median final capital:      "f"${median_final:,.2f}")
print(f"Best final capital:        "f"${best_final:,.2f}")
print(f"Worst final capital:       "f"${worst_final:,.2f}")
print()

print(f"Probability of profit:     "f"{profit_probability * 100:.2f}%")
print(f"Probability of loss:       "f"{loss_probability * 100:.2f}%")
print(f"Probability of break-even: "f"{breakeven_probability * 100:.2f}%")
print()

print(f"Average max drawdown:      "f"{np.mean(max_drawdown) * 100:.2f}%")
print(f"Worst max drawdown:        "f"{np.min(max_drawdown) * 100:.2f}%")
print()

print(f"Average max losing streak: "f"{np.mean(max_losing_streak):.2f}")
print(f"Worst losing streak:       "f"{np.max(max_losing_streak)}")


# ============================================================
# CHART STYLE HELPER

def save_chart(filename):

    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / filename,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# 01 — EQUITY CURVES

plt.figure(figsize=(16, 9))


# ------------------------------------------------------------
# Background Monte Carlo curves
# ------------------------------------------------------------

number_to_plot = min(CURVES_TO_PLOT, NUM_RUNS)

for i in range(number_to_plot):

    # Don't draw highlighted curves twice
    if i in {
        median_index,
        best_index,
        worst_index
    }:
        continue

    plt.plot(
        trades,
        equity_curves[:, i],
        linewidth=0.7,
        alpha=0.15
    )


# ------------------------------------------------------------
# Theoretical expected curve
# ------------------------------------------------------------

plt.plot(
    trades,
    theoretical_curve,
    linewidth=2.5,
    linestyle=":",
    label=(
        f"THEORETICAL EXPECTATION | "
        f"${theoretical_final:,.2f}"
    )
)


# ------------------------------------------------------------
# Median run
# ------------------------------------------------------------

plt.plot(
    trades,
    median_curve,
    linewidth=3,
    linestyle="-",
    label=(
        f"MEDIAN RUN | "
        f"${median_curve[-1]:,.2f} | "
        f"{final_return[median_index] * 100:+.2f}%"
    )
)


# ------------------------------------------------------------
# Best run
# ------------------------------------------------------------

plt.plot(
    trades,
    best_curve,
    linewidth=3,
    linestyle="-.",
    label=(
        f"BEST RUN | "
        f"${best_curve[-1]:,.2f} | "
        f"{final_return[best_index] * 100:+.2f}%"
    )
)


# ------------------------------------------------------------
# Worst run
# ------------------------------------------------------------

plt.plot(
    trades,
    worst_curve,
    linewidth=3,
    linestyle="--",
    label=(
        f"WORST RUN | "
        f"${worst_curve[-1]:,.2f} | "
        f"{final_return[worst_index] * 100:+.2f}%"
    )
)


# ------------------------------------------------------------
# Starting capital
# ------------------------------------------------------------

plt.axhline(
    STARTING_CAPITAL,
    linestyle=":",
    linewidth=1.5,
    label=(
        f"STARTING CAPITAL | "
        f"${STARTING_CAPITAL:,.2f}"
    )
)


# ------------------------------------------------------------
# Final points
# ------------------------------------------------------------

plt.scatter(
    [TRADES_PER_RUN],
    [median_curve[-1]],
    s=80,
    zorder=5
)

plt.scatter(
    [TRADES_PER_RUN],
    [best_curve[-1]],
    s=80,
    zorder=5
)

plt.scatter(
    [TRADES_PER_RUN],
    [worst_curve[-1]],
    s=80,
    zorder=5
)


# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

plt.title(
    f"Monte Carlo Equity Curves\n"
    f"{NUM_RUNS:,} Runs × "
    f"{TRADES_PER_RUN:,} Trades"
)

plt.xlabel(
    "Trade Number"
)

plt.ylabel(
    "Account Value ($)"
)

plt.grid(
    alpha=0.25
)

plt.legend(
    loc="best",
    frameon=True
)

save_chart(
    "01_equity_curves.png"
)


# ============================================================
# PRINT HIGHLIGHTED RUNS

print()
print("=" * 70)
print("HIGHLIGHTED EQUITY CURVES")
print("=" * 70)

print()

print(
    f"MEDIAN RUN\n"
    f"  Simulation: #{median_index + 1:,}\n"
    f"  Final:      ${final_capital[median_index]:,.2f}\n"
    f"  Return:     {final_return[median_index] * 100:+.2f}%\n"
    f"  Max DD:     {max_drawdown[median_index] * 100:.2f}%\n"
    f"  Win Rate:   {actual_win_rate[median_index] * 100:.2f}%\n"
    f"  Max Loss Streak: "
    f"{max_losing_streak[median_index]}\n"
)

print(
    f"BEST RUN\n"
    f"  Simulation: #{best_index + 1:,}\n"
    f"  Final:      ${final_capital[best_index]:,.2f}\n"
    f"  Return:     {final_return[best_index] * 100:+.2f}%\n"
    f"  Max DD:     {max_drawdown[best_index] * 100:.2f}%\n"
    f"  Win Rate:   {actual_win_rate[best_index] * 100:.2f}%\n"
    f"  Max Loss Streak: "
    f"{max_losing_streak[best_index]}\n"
)

print(
    f"WORST RUN\n"
    f"  Simulation: #{worst_index + 1:,}\n"
    f"  Final:      ${final_capital[worst_index]:,.2f}\n"
    f"  Return:     {final_return[worst_index] * 100:+.2f}%\n"
    f"  Max DD:     {max_drawdown[worst_index] * 100:.2f}%\n"
    f"  Win Rate:   {actual_win_rate[worst_index] * 100:.2f}%\n"
    f"  Max Loss Streak: "
    f"{max_losing_streak[worst_index]}\n"
)


# ============================================================
# 02 — FINAL CAPITAL DISTRIBUTION

plt.figure(figsize=(13, 8))

plt.hist(
    final_capital,
    bins=50,
    alpha=0.75
)

plt.axvline(
    STARTING_CAPITAL,
    linestyle="--",
    linewidth=2,
    label="Starting Capital"
)

plt.axvline(
    median_final,
    linestyle="-",
    linewidth=2,
    label=(
        f"Median: "
        f"${median_final:,.0f}"
    )
)

plt.axvline(
    average_final,
    linestyle=":",
    linewidth=2,
    label=(
        f"Average: "
        f"${average_final:,.0f}"
    )
)

plt.axvline(
    best_final,
    linestyle="-.",
    linewidth=1.5,
    label=(
        f"Best: "
        f"${best_final:,.0f}"
    )
)

plt.axvline(
    worst_final,
    linestyle="-.",
    linewidth=1.5,
    label=(
        f"Worst: "
        f"${worst_final:,.0f}"
    )
)

plt.title("Final Capital Distribution")

plt.xlabel("Final Capital ($)")

plt.ylabel("Number of Simulations")

plt.legend()

plt.grid(alpha=0.25)

save_chart("02_final_capital_distribution.png")


# ============================================================
# 03 — RETURN DISTRIBUTION

plt.figure(figsize=(13, 8))

plt.hist(
    final_return * 100,
    bins=50,
    alpha=0.75
)

plt.axvline(
    0,
    linestyle="--",
    linewidth=2,
    label="Break-even"
)

plt.axvline(
    return_median * 100,
    linestyle="-",
    linewidth=2,
    label=(
        f"Median: "
        f"{return_median * 100:.2f}%"
    )
)

plt.axvline(
    best_return * 100,
    linestyle="-.",
    linewidth=1.5,
    label=(
        f"Best: "
        f"{best_return * 100:.2f}%"
    )
)

plt.axvline(
    worst_return * 100,
    linestyle="-.",
    linewidth=1.5,
    label=(
        f"Worst: "
        f"{worst_return * 100:.2f}%"
    )
)

plt.title("Final Return Distribution")

plt.xlabel("Total Return (%)")

plt.ylabel("Number of Simulations")

plt.legend()

plt.grid(alpha=0.25)

save_chart("03_return_distribution.png")


# ============================================================
# 04 — MAXIMUM DRAWDOWN DISTRIBUTION

plt.figure(figsize=(13, 8))

plt.hist(
    max_drawdown * 100,
    bins=40,
    alpha=0.75
)

plt.axvline(
    drawdown_p50 * 100,
    linestyle="-",
    linewidth=2,
    label=(
        f"Median: "
        f"{drawdown_p50 * 100:.2f}%"
    )
)

plt.axvline(
    np.mean(max_drawdown) * 100,
    linestyle=":",
    linewidth=2,
    label=(
        f"Average: "
        f"{np.mean(max_drawdown) * 100:.2f}%"
    )
)

plt.title("Maximum Drawdown Distribution")

plt.xlabel("Maximum Drawdown (%)")

plt.ylabel("Number of Simulations")

plt.legend()

plt.grid(alpha=0.25)

save_chart("04_drawdown_distribution.png")


# ============================================================
# 05 — PERCENTILE FAN CHART

percentile_5 = np.percentile(
    equity_curves,
    5,
    axis=1
)

percentile_25 = np.percentile(
    equity_curves,
    25,
    axis=1
)

percentile_50 = np.percentile(
    equity_curves,
    50,
    axis=1
)

percentile_75 = np.percentile(
    equity_curves,
    75,
    axis=1
)

percentile_95 = np.percentile(
    equity_curves,
    95,
    axis=1
)


plt.figure(figsize=(14, 8))

plt.fill_between(
    trades,
    percentile_5,
    percentile_95,
    alpha=0.15,
    label="5th–95th percentile"
)

plt.fill_between(
    trades,
    percentile_25,
    percentile_75,
    alpha=0.25,
    label="25th–75th percentile"
)

plt.plot(
    trades,
    percentile_50,
    linewidth=2,
    label="Median"
)

plt.plot(
    trades,
    theoretical_curve,
    linewidth=2,
    linestyle=":",
    label="Theoretical expectation"
)

plt.axhline(
    STARTING_CAPITAL,
    linestyle="--",
    linewidth=1,
    label="Starting capital"
)

plt.title("Monte Carlo Percentile Fan Chart")

plt.xlabel("Trade Number")

plt.ylabel("Account Value ($)")

plt.legend()

plt.grid(alpha=0.25)

save_chart("05_percentile_fan_chart.png")


# ============================================================
# 06 — LOSING STREAK DISTRIBUTION

plt.figure(figsize=(13, 8))

max_streak_value = int(
    np.max(max_losing_streak)
)

bins = np.arange(
    0.5,
    max_streak_value + 1.5,
    1
)

plt.hist(
    max_losing_streak,
    bins=bins,
    rwidth=0.8,
    alpha=0.75
)

plt.axvline(
    np.mean(max_losing_streak),
    linestyle="--",
    linewidth=2,
    label=(
        f"Average: "
        f"{np.mean(max_losing_streak):.2f}"
    )
)

plt.axvline(
    np.median(max_losing_streak),
    linestyle=":",
    linewidth=2,
    label=(
        f"Median: "
        f"{np.median(max_losing_streak):.0f}"
    )
)

plt.title("Maximum Losing Streak Distribution")

plt.xlabel("Longest Consecutive Losing Trades")

plt.ylabel("Number of Simulations")

plt.legend()

plt.grid(alpha=0.25)

save_chart("06_losing_streak_distribution.png")


# ============================================================
# 07 — PROBABILITY OF BEING PROFITABLE

profitable_by_trade = (equity_curves > STARTING_CAPITAL).mean(axis=1)

plt.figure(figsize=(14, 8))

plt.plot(
    trades,
    profitable_by_trade * 100,
    linewidth=2
)

plt.axhline(
    50,
    linestyle="--",
    linewidth=1,
    label="50%"
)

plt.title("Probability of Being Above Starting Capital")

plt.xlabel("Trade Number")

plt.ylabel("Probability (%)")

plt.ylim(0, 100)

plt.legend()

plt.grid(alpha=0.25)

save_chart("07_profit_probability_by_trade.png")


# ============================================================
# 08 — ACTUAL WIN RATE VS FINAL CAPITAL

plt.figure(figsize=(12, 8))

plt.scatter(
    actual_win_rate * 100,
    final_capital,
    alpha=0.35,
    s=20
)

plt.axvline(
    WIN_PROBABILITY * 100,
    linestyle="--",
    linewidth=2,
    label=(
        f"Expected win rate: "
        f"{WIN_PROBABILITY * 100:.2f}%"
    )
)

plt.axhline(
    STARTING_CAPITAL,
    linestyle="--",
    linewidth=1,
    label="Starting capital"
)

plt.title("Actual Win Rate vs Final Capital")

plt.xlabel("Actual Win Rate (%)")

plt.ylabel("Final Capital ($)")

plt.legend()

plt.grid(alpha=0.25)

save_chart("08_final_capital_vs_win_rate.png")


# ============================================================
# 09 — FINAL CAPITAL BOX PLOT

plt.figure(figsize=(10, 7))

plt.boxplot(
    final_capital,
    vert=True,
    patch_artist=False
)

plt.axhline(
    STARTING_CAPITAL,
    linestyle="--",
    linewidth=2,
    label="Starting capital"
)

plt.axhline(
    median_final,
    linestyle=":",
    linewidth=2,
    label=(
        f"Median: "
        f"${median_final:,.0f}"
    )
)

plt.title("Final Capital Box Plot")

plt.ylabel("Final Capital ($)")

plt.legend()

plt.grid(alpha=0.25)

save_chart("09_final_capital_boxplot.png")


# ============================================================
# 10 — DISTRIBUTION OF ACTUAL WIN RATES

plt.figure(figsize=(13, 8))

plt.hist(
    actual_win_rate * 100,
    bins=30,
    alpha=0.75
)

plt.axvline(
    WIN_PROBABILITY * 100,
    linestyle="--",
    linewidth=2,
    label=(
        f"Expected: "
        f"{WIN_PROBABILITY * 100:.2f}%"
    )
)

plt.axvline(
    np.mean(actual_win_rate) * 100,
    linestyle=":",
    linewidth=2,
    label=(
        f"Simulation mean: "
        f"{np.mean(actual_win_rate) * 100:.2f}%"
    )
)

plt.title("Distribution of Actual Win Rates")

plt.xlabel("Actual Win Rate (%)")

plt.ylabel("Number of Simulations")

plt.legend()

plt.grid(alpha=0.25)

save_chart("10_actual_win_rate_distribution.png")


# ============================================================
# 11 — THEORETICAL VS MEDIAN EQUITY

plt.figure(figsize=(14, 8))

plt.plot(
    trades,
    theoretical_curve,
    linewidth=2.5,
    linestyle=":",
    label="Theoretical expectation"
)

plt.plot(
    trades,
    percentile_50,
    linewidth=2.5,
    label="Monte Carlo median"
)

plt.plot(
    trades,
    median_curve,
    linewidth=1.5,
    linestyle="--",
    label="Actual median-selected run"
)

plt.axhline(
    STARTING_CAPITAL,
    linestyle="--",
    linewidth=1,
    label="Starting capital"
)

plt.title("Theoretical Expectation vs Monte Carlo Median")

plt.xlabel("Trade Number")

plt.ylabel("Account Value ($)")

plt.legend()

plt.grid(alpha=0.25)

save_chart("11_theoretical_vs_median.png")


# ============================================================
# SAVE INDIVIDUAL SIMULATION RESULTS

results_df = pd.DataFrame({

    "simulation":
        np.arange(
            1,
            NUM_RUNS + 1
        ),

    "wins":
        actual_wins,

    "losses":
        actual_losses,

    "actual_win_rate":
        actual_win_rate,

    "final_capital":
        final_capital,

    "total_return":
        final_return,

    "max_drawdown":
        max_drawdown,

    "max_losing_streak":
        max_losing_streak,

    "profitable":
        profitable
})


results_df.to_csv(OUTPUT_FOLDER / "simulation_results.csv", index=False)


# ============================================================
# COMPREHENSIVE TEXT REPORT

report = f"""
==============================================================
                 MONTE CARLO TESTING REPORT
==============================================================

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


--------------------------------------------------------------
INPUT PARAMETERS
--------------------------------------------------------------

Starting Capital:
${STARTING_CAPITAL:,.2f}

Win Probability:
{WIN_PROBABILITY * 100:.4f}%

Loss Probability:
{LOSE_PROBABILITY * 100:.4f}%

Average Win:
{AVERAGE_WIN * 100:.4f}%

Average Loss:
{AVERAGE_LOSS * 100:.4f}%

Trades per Run:
{TRADES_PER_RUN:,}

Number of Runs:
{NUM_RUNS:,}

Total Simulated Trades:
{NUM_RUNS * TRADES_PER_RUN:,}


--------------------------------------------------------------
EXPECTED VALUE
--------------------------------------------------------------

Expected Return / Trade:
{EXPECTED_RETURN_PER_TRADE * 100:.6f}%

Theoretical Final Capital:
${theoretical_final:,.2f}


--------------------------------------------------------------
FINAL CAPITAL
--------------------------------------------------------------

Average Final Capital:
${average_final:,.2f}

Median Final Capital:
${median_final:,.2f}

Standard Deviation:
${std_final:,.2f}

Best Result:
${best_final:,.2f}

Worst Result:
${worst_final:,.2f}


--------------------------------------------------------------
FINAL RETURN
--------------------------------------------------------------

Average Return:
{return_mean * 100:.2f}%

Median Return:
{return_median * 100:.2f}%

Standard Deviation:
{return_std * 100:.2f}%

Best Return:
{best_return * 100:.2f}%

Worst Return:
{worst_return * 100:.2f}%


--------------------------------------------------------------
PROBABILITY
--------------------------------------------------------------

Probability of Profit:
{profit_probability * 100:.2f}%

Probability of Loss:
{loss_probability * 100:.2f}%

Probability of Break-even:
{breakeven_probability * 100:.2f}%


--------------------------------------------------------------
FINAL CAPITAL PERCENTILES
--------------------------------------------------------------

5th Percentile:
${capital_p5:,.2f}

10th Percentile:
${capital_p10:,.2f}

25th Percentile:
${capital_p25:,.2f}

50th Percentile:
${capital_p50:,.2f}

75th Percentile:
${capital_p75:,.2f}

90th Percentile:
${capital_p90:,.2f}

95th Percentile:
${capital_p95:,.2f}


--------------------------------------------------------------
MAXIMUM DRAWDOWN
--------------------------------------------------------------

Average Maximum Drawdown:
{np.mean(max_drawdown) * 100:.2f}%

Median Maximum Drawdown:
{drawdown_p50 * 100:.2f}%

Best Maximum Drawdown:
{np.max(max_drawdown) * 100:.2f}%

Worst Maximum Drawdown:
{np.min(max_drawdown) * 100:.2f}%


Drawdown Percentiles:

5th:
{drawdown_p5 * 100:.2f}%

25th:
{drawdown_p25 * 100:.2f}%

50th:
{drawdown_p50 * 100:.2f}%

75th:
{drawdown_p75 * 100:.2f}%

95th:
{drawdown_p95 * 100:.2f}%


--------------------------------------------------------------
LOSING STREAK
--------------------------------------------------------------

Average Maximum Losing Streak:
{np.mean(max_losing_streak):.2f} trades

Median Maximum Losing Streak:
{np.median(max_losing_streak):.0f} trades

Worst Maximum Losing Streak:
{np.max(max_losing_streak)} trades


--------------------------------------------------------------
ACTUAL WIN RATE
--------------------------------------------------------------

Expected Win Rate:
{WIN_PROBABILITY * 100:.4f}%

Average Actual Win Rate:
{np.mean(actual_win_rate) * 100:.4f}%

Minimum Actual Win Rate:
{np.min(actual_win_rate) * 100:.4f}%

Maximum Actual Win Rate:
{np.max(actual_win_rate) * 100:.4f}%


--------------------------------------------------------------
HIGHLIGHTED SIMULATIONS
--------------------------------------------------------------

MEDIAN RUN
Simulation:
#{median_index + 1:,}

Final Capital:
${final_capital[median_index]:,.2f}

Return:
{final_return[median_index] * 100:+.2f}%

Actual Win Rate:
{actual_win_rate[median_index] * 100:.2f}%

Maximum Drawdown:
{max_drawdown[median_index] * 100:.2f}%

Maximum Losing Streak:
{max_losing_streak[median_index]} trades


BEST RUN
Simulation:
#{best_index + 1:,}

Final Capital:
${final_capital[best_index]:,.2f}

Return:
{final_return[best_index] * 100:+.2f}%

Actual Win Rate:
{actual_win_rate[best_index] * 100:.2f}%

Maximum Drawdown:
{max_drawdown[best_index] * 100:.2f}%

Maximum Losing Streak:
{max_losing_streak[best_index]} trades


WORST RUN
Simulation:
#{worst_index + 1:,}

Final Capital:
${final_capital[worst_index]:,.2f}

Return:
{final_return[worst_index] * 100:+.2f}%

Actual Win Rate:
{actual_win_rate[worst_index] * 100:.2f}%

Maximum Drawdown:
{max_drawdown[worst_index] * 100:.2f}%

Maximum Losing Streak:
{max_losing_streak[worst_index]} trades


--------------------------------------------------------------
INTERPRETATION
--------------------------------------------------------------

The strategy has a theoretical expected return per trade of:

{EXPECTED_RETURN_PER_TRADE * 100:.6f}%


The theoretical compound final capital after
{TRADES_PER_RUN:,} trades is:

${theoretical_final:,.2f}


The Monte Carlo simulation contains:

{NUM_RUNS:,} independent simulations

with:

{TRADES_PER_RUN:,} trades per simulation.


The results represent different possible sequences
of wins and losses while keeping the specified
probability and average trade return constant.


TOOL LIMITATION
--------------------------------------------------------------

Because no standard deviation or historical distribution
of individual winning and losing trades was provided,
every win is modeled as exactly average value:

{AVERAGE_WIN * 100:.4f}%


and every loss is modeled as exactly:

{AVERAGE_LOSS * 100:.4f}%


Therefore this simulation primarily measures:

- Robustness of the edge when
- Sequence risk
- Win-rate variation
- Losing streak risk
- Compounding effects
- Maximum drawdown
- Outcome dispersion


It does NOT model the real variation in individual
trade sizes.

==============================================================
END OF REPORT
==============================================================
"""


# ============================================================
# SAVE TEXT REPORT
# ============================================================

with open(OUTPUT_FOLDER / "monte_carlo_report.txt", "w", encoding="utf-8") as f:
    f.write(report)


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 70)
print("REPORT COMPLETE")
print("=" * 70)

print()

print(f"Output folder:\n"f"{OUTPUT_FOLDER.resolve()}")
print()

print("Files created:")

for file in sorted(OUTPUT_FOLDER.iterdir()):

    print(f"  {file.name}")
print()
print("Finished.")