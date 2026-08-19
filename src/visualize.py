"""Render the charts for the Netflix ELT project.

    python src/visualize.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import viz_theme as T  # noqa: E402
from config import CHARTS_DIR, RESULTS_DIR, WAREHOUSE  # noqa: E402

SOURCE = ("Source: Netflix titles catalogue, 7,787 titles | "
          "netflix-elt-data-cleaning")


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / f"{name}.csv")


# ---------------------------------------------------------------- chart 1 ---
def chart_cleaning_impact() -> None:
    """The headline: what a naive GROUP BY reports vs what is actually there."""
    df = load("01_cleaning_impact")
    fig, ax = plt.subplots(figsize=(9.5, 4.6))

    y = np.arange(len(df))
    h = 0.34
    T.rounded_bars(ax, y + h / 2, df["naive_distinct_count"], T.NEG,
                   thickness=h, horizontal=True)
    T.rounded_bars(ax, y - h / 2, df["true_distinct_count"], T.BLUE,
                   thickness=h, horizontal=True)

    ax.set_yticks(y, df["field"])
    ax.set_xlabel("Distinct values reported")
    ax.set_xlim(0, df["naive_distinct_count"].max() * 1.34)
    ax.grid(axis="y", visible=False)

    for yi, row in zip(y, df.itertuples()):
        ax.annotate(f"{row.naive_distinct_count:,}",
                    (row.naive_distinct_count + 12, yi + h / 2), va="center",
                    fontsize=9.5, fontweight="600", color=T.NEG)
        ax.annotate(f"{row.true_distinct_count:,}   "
                    f"({row.naive_distinct_count/row.true_distinct_count:.1f}x overcount)",
                    (row.true_distinct_count + 12, yi - h / 2), va="center",
                    fontsize=9.5, fontweight="600", color=T.BLUE)

    handles = [plt.Line2D([], [], marker="s", ls="", ms=10, color=T.NEG,
                          label="Naive COUNT(DISTINCT) on the raw column"),
               plt.Line2D([], [], marker="s", ls="", ms=10, color=T.BLUE,
                          label="After exploding and normalising")]
    ax.legend(handles=handles, loc="lower right", fontsize=9.5)

    T.title_block(
        ax,
        "The raw columns report 5.8x more countries than actually exist",
        "`country` and `listed_in` pack multiple values into one cell, so "
        "'United States, India' counts as a country of its own. Exploding to "
        "one row per value takes 681 apparent countries down to 117 real ones.",
        wrap=100,
    )
    T.save(fig, CHARTS_DIR / "01_cleaning_impact.png", SOURCE)


# ---------------------------------------------------------------- chart 2 ---
def chart_completeness() -> None:
    df = load("02_completeness").set_index("title_type")
    fields = ["director", "cast", "country", "date_added", "rating"]
    cols = [f"pct_missing_{f}" for f in fields]

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(fields))
    h = 0.34

    T.rounded_bars(ax, x - h / 2, df.loc["Movie", cols].values, T.BLUE,
                   thickness=h, horizontal=False)
    T.rounded_bars(ax, x + h / 2, df.loc["TV Show", cols].values, T.ORANGE,
                   thickness=h, horizontal=False)

    ax.set_xticks(x, [f.replace("_", " ") for f in fields])
    ax.set_ylabel("% of titles with the field missing")
    ax.set_ylim(0, 108)
    ax.set_xlabel("Source field")
    ax.grid(axis="x", visible=False)

    for xi, f in zip(x, cols):
        for off, tt, col in [(-h / 2, "Movie", T.BLUE), (h / 2, "TV Show", T.ORANGE)]:
            v = df.loc[tt, f]
            ax.annotate(f"{v:.1f}%", (xi + off, v), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=9,
                        fontweight="600" if v > 50 else "normal",
                        color=T.INK if v > 50 else T.INK_SECONDARY)

    handles = [plt.Line2D([], [], marker="s", ls="", ms=10, color=T.BLUE,
                          label="Movies (5,377)"),
               plt.Line2D([], [], marker="s", ls="", ms=10, color=T.ORANGE,
                          label="TV Shows (2,410)")]
    ax.legend(handles=handles, loc="upper right", fontsize=9.5)

    T.title_block(
        ax,
        "92% of TV shows have no director, so missingness is not random",
        "Movies are 3% missing on the same field. Any 'top directors' analysis "
        "that ignores this silently answers a question about films only, while "
        "appearing to describe the whole catalogue.",
        wrap=100,
    )
    T.save(fig, CHARTS_DIR / "02_completeness.png", SOURCE)


# ---------------------------------------------------------------- chart 3 ---
def chart_growth() -> None:
    df = load("03_catalogue_growth")
    df = df[df["year_added"] <= 2020]      # 2021 is a partial year in this extract

    fig, ax = plt.subplots(figsize=(10, 5.2))
    x = df["year_added"]
    ax.plot(x, df["movies_added"], color=T.BLUE, marker="o", label="Movies")
    ax.plot(x, df["shows_added"], color=T.ORANGE, marker="o", label="TV Shows")

    ax.set_xlabel("Year added to Netflix")
    ax.set_ylabel("Titles added")
    ax.set_xticks(x)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", fontsize=9.5)
    ax.set_ylim(0, df["movies_added"].max() * 1.22)

    peak = df.loc[df["movies_added"].idxmax()]
    ax.annotate(f"{int(peak['movies_added']):,} films in {int(peak['year_added'])}",
                (peak["year_added"], peak["movies_added"]),
                textcoords="offset points", xytext=(-10, 12), ha="right",
                fontsize=9.5, color=T.INK_SECONDARY)

    last = df.iloc[-1]
    T.title_block(
        ax,
        "Netflix's acquisition rate peaked in 2019, then films fell while TV held",
        f"By {int(last['year_added'])}, TV was {last['pct_tv']:.0f}% of everything "
        f"added, up from {df.iloc[3]['pct_tv']:.0f}% in {int(df.iloc[3]['year_added'])}. "
        f"2021 is excluded here: the extract stops partway through it.",
        wrap=100,
    )
    T.save(fig, CHARTS_DIR / "03_catalogue_growth.png", SOURCE)


# ---------------------------------------------------------------- chart 4 ---
def chart_countries() -> None:
    df = load("04_country_production").head(15).sort_values("titles")

    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    y = np.arange(len(df))
    T.rounded_bars(ax, y, df["titles"], T.BLUE, thickness=0.64)
    ax.set_yticks(y, df["country"])
    ax.set_xlabel("Titles produced (including co-productions)")
    ax.set_xlim(0, df["titles"].max() * 1.36)
    ax.grid(axis="y", visible=False)

    for yi, row in zip(y, df.itertuples()):
        ax.annotate(f"{row.titles:,}   ({row.pct_tv:.0f}% TV, "
                    f"{row.co_produced_titles:,} co-produced)",
                    (row.titles + df["titles"].max() * 0.012, yi), va="center",
                    fontsize=8.8, color=T.INK_SECONDARY)

    jp = df[df["country"] == "Japan"]
    T.title_block(
        ax,
        "The US dominates, but the TV/film mix per country is the real story",
        f"Japan is {jp['pct_tv'].iloc[0]:.0f}% television (the anime catalogue) "
        f"against 26% for the US. These per-country splits only exist because "
        f"co-productions were exploded into one row per country.",
        wrap=100,
    )
    T.save(fig, CHARTS_DIR / "04_countries.png", SOURCE)


# ---------------------------------------------------------------- chart 5 ---
def chart_runtime_distribution() -> None:
    """Read straight from the warehouse: a histogram needs the raw values, and
    binning them in the analysis layer would bake the bin width into the CSV."""
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    mins = con.execute(
        "SELECT duration_minutes FROM dim_title WHERE duration_minutes IS NOT NULL"
    ).fetchdf()["duration_minutes"]
    seasons = con.execute(
        "SELECT seasons FROM dim_title WHERE seasons IS NOT NULL"
    ).fetchdf()["seasons"]
    con.close()

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1.7, 1], "wspace": 0.22}
    )

    ax1.hist(mins, bins=range(0, 210, 5), color=T.BLUE, edgecolor=T.SURFACE, lw=0.6)
    ax1.axvline(mins.median(), color=T.NEG, lw=1.8, ls=(0, (5, 3)))
    ax1.annotate(f"median {mins.median():.0f} min", (mins.median(), 0),
                 xycoords=("data", "axes fraction"), textcoords="offset points",
                 xytext=(8, 195), fontsize=9.5, color=T.NEG, fontweight="600")
    ax1.set_xlabel("Runtime (minutes)")
    ax1.set_ylabel("Films")
    ax1.grid(axis="x", visible=False)
    T.title_block(ax1, "Film runtimes cluster hard at 90–100 minutes",
                  f"{len(mins):,} films. Range {mins.min():.0f}–{mins.max():.0f} min.",
                  wrap=60)

    counts = seasons.value_counts().sort_index()
    keep = counts[counts.index <= 10]
    T.rounded_bars(ax2, keep.index, keep.values, T.ORANGE, thickness=0.62,
                   horizontal=False)
    ax2.set_xlabel("Seasons")
    ax2.set_ylabel("TV shows")
    ax2.set_xticks(range(1, 11))
    ax2.grid(axis="x", visible=False)
    ax2.set_ylim(0, keep.values.max() * 1.20)
    pct1 = 100 * (seasons == 1).mean()
    ax2.annotate(f"{pct1:.0f}% never get\na second season",
                 (1, keep.values.max()), textcoords="offset points",
                 xytext=(20, -12), fontsize=9.5, color=T.INK_SECONDARY)
    T.title_block(ax2, "Most shows are one and done",
                  f"{len(seasons):,} shows, up to {seasons.max():.0f} seasons.",
                  wrap=44)

    T.save(fig, CHARTS_DIR / "05_duration_distributions.png", SOURCE)


def main() -> None:
    T.apply_theme()
    for fn in (chart_cleaning_impact, chart_completeness, chart_growth,
               chart_countries, chart_runtime_distribution):
        fn()
    print(f"\nCharts written to {CHARTS_DIR}")


if __name__ == "__main__":
    main()
