"""
Competitor Review Scraper for VeloIntel Market Research
========================================================
Scrapes App Store and Google Play reviews for fitness/training apps.

Install dependencies:
    pip install app-store-scraper google-play-scraper pandas

Usage:
    python scripts/scrape_competitor_reviews.py

Output:
    data/research/competitor_reviews.csv
    data/research/review_insights.md
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import time
import json

# App Store scraper
try:
    from app_store_scraper import AppStore
    HAS_APP_STORE = True
except ImportError:
    print("⚠️  Install app-store-scraper: pip install app-store-scraper")
    HAS_APP_STORE = False

# Google Play scraper
try:
    from google_play_scraper import reviews, Sort
    HAS_GOOGLE_PLAY = True
except ImportError:
    print("⚠️  Install google-play-scraper: pip install google-play-scraper")
    HAS_GOOGLE_PLAY = False


# =============================================================================
# TARGET APPS - Add/modify as needed
# =============================================================================

APP_STORE_APPS = [
    {"app_name": "strava-run-ride-hike", "app_id": 426826309, "display_name": "Strava"},
    {"app_name": "trainingpeaks", "app_id": 455468457, "display_name": "TrainingPeaks"},
    {"app_name": "whoop-performance-optimization", "app_id": 933944389, "display_name": "WHOOP"},
    {"app_name": "oura-ring", "app_id": 1043837948, "display_name": "Oura"},
    {"app_name": "garmin-connect", "app_id": 583446403, "display_name": "Garmin Connect"},
    {"app_name": "trainerroad-indoor-cycling", "app_id": 453209186, "display_name": "TrainerRoad"},
    {"app_name": "intervals-pro", "app_id": 957586850, "display_name": "Intervals.icu"},
]

GOOGLE_PLAY_APPS = [
    {"app_id": "com.strava", "display_name": "Strava"},
    {"app_id": "com.peaksware.trainingpeaks", "display_name": "TrainingPeaks"},
    {"app_id": "com.whoop.android", "display_name": "WHOOP"},
    {"app_id": "com.ouraring.oura", "display_name": "Oura"},
    {"app_id": "com.garmin.android.apps.connectmobile", "display_name": "Garmin Connect"},
    {"app_id": "com.trainerroad.trainerroad", "display_name": "TrainerRoad"},
]


# =============================================================================
# SCRAPING FUNCTIONS
# =============================================================================

def scrape_app_store(apps: list, reviews_per_app: int = 100, country: str = "us") -> pd.DataFrame:
    """Scrape App Store reviews."""
    if not HAS_APP_STORE:
        return pd.DataFrame()

    all_reviews = []

    for app_info in apps:
        print(f"📱 Scraping App Store: {app_info['display_name']}...")
        try:
            app = AppStore(
                country=country,
                app_name=app_info["app_name"],
                app_id=app_info["app_id"]
            )
            app.review(how_many=reviews_per_app)

            for review in app.reviews:
                all_reviews.append({
                    "store": "App Store",
                    "app": app_info["display_name"],
                    "rating": review.get("rating"),
                    "title": review.get("title", ""),
                    "content": review.get("review", ""),
                    "date": review.get("date"),
                    "developer_response": review.get("developerResponse", {}).get("body", "") if review.get("developerResponse") else "",
                })

            print(f"   ✓ Got {len(app.reviews)} reviews")
            time.sleep(2)  # Rate limiting

        except Exception as e:
            print(f"   ✗ Error: {e}")

    return pd.DataFrame(all_reviews)


def scrape_google_play(apps: list, reviews_per_app: int = 100, country: str = "us") -> pd.DataFrame:
    """Scrape Google Play reviews."""
    if not HAS_GOOGLE_PLAY:
        return pd.DataFrame()

    all_reviews = []

    for app_info in apps:
        print(f"🤖 Scraping Google Play: {app_info['display_name']}...")
        try:
            result, _ = reviews(
                app_info["app_id"],
                lang="en",
                country=country,
                sort=Sort.NEWEST,
                count=reviews_per_app,
            )

            for review in result:
                all_reviews.append({
                    "store": "Google Play",
                    "app": app_info["display_name"],
                    "rating": review.get("score"),
                    "title": "",  # Google Play doesn't have titles
                    "content": review.get("content", ""),
                    "date": review.get("at"),
                    "developer_response": review.get("replyContent", ""),
                })

            print(f"   ✓ Got {len(result)} reviews")
            time.sleep(2)  # Rate limiting

        except Exception as e:
            print(f"   ✗ Error: {e}")

    return pd.DataFrame(all_reviews)


def filter_actionable_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Filter for 1-3 star reviews with substantive content."""
    # Focus on critical reviews (1-3 stars)
    critical = df[df["rating"] <= 3].copy()

    # Filter for reviews with enough content to be useful
    critical = critical[critical["content"].str.len() > 50]

    return critical


def extract_themes(df: pd.DataFrame) -> dict:
    """Extract common themes from reviews using keyword matching."""
    themes = {
        "sync_issues": ["sync", "connect", "import", "export", "integration"],
        "complexity": ["complicated", "confusing", "difficult", "hard to", "overwhelming"],
        "missing_features": ["wish", "need", "want", "missing", "should have", "please add"],
        "accuracy": ["inaccurate", "wrong", "incorrect", "doesn't match", "off by"],
        "price_complaints": ["expensive", "overpriced", "not worth", "too much", "subscription"],
        "recommendations": ["recommendation", "suggest", "advice", "coach", "tell me what"],
        "data_issues": ["data", "lost", "disappeared", "deleted", "missing data"],
        "ui_ux": ["interface", "ui", "ux", "design", "layout", "cluttered"],
        "notifications": ["notification", "alert", "reminder", "push"],
        "battery": ["battery", "drain", "power"],
    }

    theme_counts = {}
    theme_examples = {}

    for theme, keywords in themes.items():
        mask = df["content"].str.lower().apply(
            lambda x: any(kw in x for kw in keywords)
        )
        theme_counts[theme] = mask.sum()
        theme_examples[theme] = df[mask]["content"].head(3).tolist()

    return {"counts": theme_counts, "examples": theme_examples}


def generate_insights_report(df: pd.DataFrame, themes: dict, output_path: Path):
    """Generate a markdown report with insights."""

    report = f"""# Competitor Review Analysis
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Reviews:** {len(df)}
**Critical Reviews (1-3 stars):** {len(df[df['rating'] <= 3])}

---

## Reviews by App

| App | Total | ⭐1 | ⭐2 | ⭐3 | ⭐4 | ⭐5 | Avg |
|-----|-------|-----|-----|-----|-----|-----|-----|
"""

    for app in df["app"].unique():
        app_df = df[df["app"] == app]
        row = f"| {app} | {len(app_df)} | "
        for star in [1, 2, 3, 4, 5]:
            row += f"{len(app_df[app_df['rating'] == star])} | "
        row += f"{app_df['rating'].mean():.1f} |"
        report += row + "\n"

    report += """
---

## Pain Point Themes (from 1-3 star reviews)

"""

    # Sort themes by count
    sorted_themes = sorted(themes["counts"].items(), key=lambda x: x[1], reverse=True)

    for theme, count in sorted_themes:
        if count > 0:
            report += f"### {theme.replace('_', ' ').title()} ({count} mentions)\n\n"
            for example in themes["examples"][theme][:2]:
                # Truncate long examples
                example_short = example[:300] + "..." if len(example) > 300 else example
                report += f"> {example_short}\n\n"

    report += """
---

## VeloIntel Opportunity Analysis

Based on the review analysis, here are potential differentiators:

"""

    # Add opportunity analysis based on theme counts
    if themes["counts"].get("sync_issues", 0) > 5:
        report += "- **Multi-source fusion**: Users frustrated with sync issues → unified data layer is valuable\n"
    if themes["counts"].get("complexity", 0) > 5:
        report += "- **Simplicity**: Users find apps overwhelming → simple daily recommendation wins\n"
    if themes["counts"].get("recommendations", 0) > 3:
        report += "- **Actionable advice**: Users want to be told what to do → proactive coach agent\n"
    if themes["counts"].get("accuracy", 0) > 3:
        report += "- **Explainability**: Users don't trust black-box recommendations → show reasoning\n"
    if themes["counts"].get("price_complaints", 0) > 5:
        report += "- **Value clarity**: Price sensitivity exists → clear ROI messaging needed\n"

    report += """
---

## Raw Data

See `competitor_reviews.csv` for full review dataset.

## Next Steps

1. Deep-dive into "recommendations" theme reviews
2. Identify specific language users use to describe pain points
3. Use insights to refine VeloIntel value proposition
4. Pull quotes for landing page social proof (pain-focused)
"""

    output_path.write_text(report)
    print(f"\n📊 Report saved to: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    # Setup output directory
    output_dir = Path("data/research")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🔍 VeloIntel Competitor Review Scraper")
    print("=" * 60)

    # Scrape reviews
    reviews_per_app = 100  # Adjust as needed (max ~200 for rate limits)

    app_store_df = scrape_app_store(APP_STORE_APPS, reviews_per_app)
    google_play_df = scrape_google_play(GOOGLE_PLAY_APPS, reviews_per_app)

    # Combine
    all_reviews = pd.concat([app_store_df, google_play_df], ignore_index=True)

    if len(all_reviews) == 0:
        print("\n❌ No reviews scraped. Check dependencies and try again.")
        return

    print(f"\n📥 Total reviews scraped: {len(all_reviews)}")

    # Save raw data
    csv_path = output_dir / "competitor_reviews.csv"
    all_reviews.to_csv(csv_path, index=False)
    print(f"💾 Raw data saved to: {csv_path}")

    # Filter for actionable reviews
    critical_reviews = filter_actionable_reviews(all_reviews)
    print(f"🎯 Critical reviews (1-3 stars, >50 chars): {len(critical_reviews)}")

    # Extract themes
    themes = extract_themes(critical_reviews)

    # Generate report
    report_path = output_dir / "review_insights.md"
    generate_insights_report(all_reviews, themes, report_path)

    # Quick summary
    print("\n" + "=" * 60)
    print("📈 QUICK INSIGHTS")
    print("=" * 60)
    print(f"\nTop pain point themes:")
    for theme, count in sorted(themes["counts"].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {theme.replace('_', ' ').title()}: {count} mentions")

    print("\n✅ Done! Check data/research/ for full analysis.")


if __name__ == "__main__":
    main()
