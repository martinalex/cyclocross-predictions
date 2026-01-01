#!/usr/bin/env python3
"""
CyclingFlash.com Scraper
Extracts startlists and results from cyclingflash.com event pages.

Usage:
    python scrape_cyclingflash.py <event_url> --series "X2O-Trofee" --race "GP-Sven-Nys" --location "BAAL-BELGIUM" --date "2026-01-01"

Example:
    python scrape_cyclingflash.py https://cyclingflash.com/event/x2o-badkamers-trofee-gp-sven-nys-2026 \
        --series "X2O-Trofee" --race "GP-Sven-Nys" --location "BAAL-BELGIUM" --date "2026-01-01"
"""

import argparse
import csv
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from html.parser import HTMLParser


# Output directories
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "data" / "results"
STARTLISTS_DIR = BASE_DIR / "data" / "startlists"


@dataclass
class RaceInfo:
    """Race metadata for file naming."""
    series: str
    race_name: str
    location: str
    date: str  # YYYY-MM-DD format


@dataclass
class CategoryURLs:
    """URLs for a specific category."""
    category: str  # "Men-Elite" or "Women-Elite"
    startlist_url: str
    results_url: str


class SimpleHTMLParser:
    """Simple HTML parser for extracting data without BeautifulSoup."""

    def __init__(self, html: str):
        self.html = html

    def find_all_links(self) -> list[tuple[str, str]]:
        """Find all links with href and text."""
        links = []
        pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
        for match in re.finditer(pattern, self.html, re.IGNORECASE | re.DOTALL):
            href, text = match.groups()
            links.append((href, text.strip()))
        return links

    def find_links_by_href_pattern(self, pattern: str) -> list[tuple[str, str]]:
        """Find links whose href matches a pattern."""
        all_links = self.find_all_links()
        return [(href, text) for href, text in all_links if pattern in href]

    def extract_table_rows(self) -> list[list[str]]:
        """Extract all table rows with their cell contents."""
        rows = []
        # Find all tr elements
        tr_pattern = r'<tr[^>]*>(.*?)</tr>'
        for tr_match in re.finditer(tr_pattern, self.html, re.IGNORECASE | re.DOTALL):
            row_html = tr_match.group(1)
            # Find all td/th elements in this row
            cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
            cells = []
            for cell_match in re.finditer(cell_pattern, row_html, re.IGNORECASE | re.DOTALL):
                cell_html = cell_match.group(1)
                # Extract text, removing tags
                cell_text = re.sub(r'<[^>]+>', ' ', cell_html)
                cell_text = ' '.join(cell_text.split())  # Normalize whitespace
                cells.append(cell_text)
            if cells:
                rows.append(cells)
        return rows

    def extract_rider_link(self, cell_html: str) -> Optional[str]:
        """Extract rider name from a cell containing a rider link."""
        pattern = r'<a[^>]*href=["\'][^"\']*\/rider\/[^"\']*["\'][^>]*>([^<]*)</a>'
        match = re.search(pattern, cell_html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def extract_team_link(self, cell_html: str) -> Optional[str]:
        """Extract team name from a cell containing a team link."""
        pattern = r'<a[^>]*href=["\'][^"\']*\/team\/[^"\']*["\'][^>]*>([^<]*)</a>'
        match = re.search(pattern, cell_html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None


def fetch_page(url: str) -> Optional[str]:
    """Fetch a page and return HTML string."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        # Create SSL context that doesn't verify certificates (for compatibility)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def discover_category_urls(event_url: str) -> list[CategoryURLs]:
    """Discover startlist and results URLs for ME and WE categories from event page."""
    html = fetch_page(event_url)
    if not html:
        return []

    categories = []

    # Find all href patterns for race links (more robust regex)
    href_pattern = r'href=["\']([^"\']*\/race\/[^"\']*)["\']'
    all_hrefs = re.findall(href_pattern, html, re.IGNORECASE)

    # Look for race links - they follow pattern /race/{slug}/startlist or /result
    startlist_links = {}
    result_links = {}

    for href in all_hrefs:
        # Match startlist links
        if "/startlist" in href:
            if "-we-" in href.lower():
                startlist_links["Women-Elite"] = href
            elif "-mj-" not in href.lower() and "-mu-" not in href.lower():
                # Men Elite doesn't have a category suffix
                startlist_links["Men-Elite"] = href

        # Match result links
        if "/result" in href:
            if "-we-" in href.lower():
                result_links["Women-Elite"] = href
            elif "-mj-" not in href.lower() and "-mu-" not in href.lower():
                result_links["Men-Elite"] = href

    # Build full URLs
    base_url = "https://cyclingflash.com"

    for category in ["Men-Elite", "Women-Elite"]:
        if category in startlist_links and category in result_links:
            startlist_url = startlist_links[category]
            results_url = result_links[category]

            # Ensure full URLs
            if not startlist_url.startswith("http"):
                startlist_url = base_url + startlist_url
            if not results_url.startswith("http"):
                results_url = base_url + results_url

            categories.append(CategoryURLs(
                category=category,
                startlist_url=startlist_url,
                results_url=results_url
            ))

    return categories


def parse_startlist(html: str) -> list[dict]:
    """Parse startlist page and extract rider data."""
    riders = []
    seen_names = set()

    # CyclingFlash uses /profile/ for rider links
    # Rider name is in <span itemProp="name">Name</span>

    # Extract tbody first for better matching
    tbody_pattern = r'<tbody[^>]*>(.*?)</tbody>'
    tbody_match = re.search(tbody_pattern, html, re.IGNORECASE | re.DOTALL)
    search_html = tbody_match.group(1) if tbody_match else html

    # Find table rows
    tr_pattern = r'<tr[^>]*>(.*?)</tr>'
    for tr_match in re.finditer(tr_pattern, search_html, re.IGNORECASE | re.DOTALL):
        row_html = tr_match.group(1)

        # Look for rider name with itemProp="name"
        rider_pattern = r'<span[^>]*itemProp=["\']name["\'][^>]*>([^<]+)</span>'
        rider_match = re.search(rider_pattern, row_html, re.IGNORECASE)

        if rider_match:
            name = rider_match.group(1).strip()
            if name and len(name) >= 2 and name not in seen_names:
                # Look for team link in same row
                team_pattern = r'<a[^>]*href=["\'][^"\']*\/team\/[^"\']*["\'][^>]*>.*?<span[^>]*>([^<]+)</span>'
                team_match = re.search(team_pattern, row_html, re.IGNORECASE | re.DOTALL)
                team = team_match.group(1).strip() if team_match else ""

                riders.append({"name": name, "team": team})
                seen_names.add(name)

    # Fallback: find all spans with itemProp name
    if not riders:
        rider_pattern = r'<span[^>]*itemProp=["\']name["\'][^>]*>([^<]+)</span>'
        for match in re.finditer(rider_pattern, html, re.IGNORECASE):
            name = match.group(1).strip()
            if name and len(name) >= 2 and name not in seen_names:
                # Look for team link near this position
                start_pos = match.end()
                context = html[start_pos:start_pos + 1000]
                team_pattern = r'<a[^>]*href=["\'][^"\']*\/team\/[^"\']*["\'][^>]*>.*?<span[^>]*>([^<]+)</span>'
                team_match = re.search(team_pattern, context, re.IGNORECASE | re.DOTALL)
                team = team_match.group(1).strip() if team_match else ""

                riders.append({"name": name, "team": team})
                seen_names.add(name)

    return riders


def parse_results(html: str) -> list[dict]:
    """Parse results page and extract rider data."""
    results = []

    # Results are in table rows - skip header row
    tr_pattern = r'<tr[^>]*class=""[^>]*>(.*?)</tr>'
    all_rows = list(re.finditer(tr_pattern, html, re.IGNORECASE | re.DOTALL))

    # If no rows with class="", try all tr in tbody
    if not all_rows:
        tbody_pattern = r'<tbody[^>]*>(.*?)</tbody>'
        tbody_match = re.search(tbody_pattern, html, re.IGNORECASE | re.DOTALL)
        if tbody_match:
            tbody_html = tbody_match.group(1)
            tr_pattern = r'<tr[^>]*>(.*?)</tr>'
            all_rows = list(re.finditer(tr_pattern, tbody_html, re.IGNORECASE | re.DOTALL))

    for tr_match in all_rows:
        row_html = tr_match.group(1)

        result = {
            "position": "",
            "name": "",
            "age": "",
            "team": "",
            "time": ""
        }

        # Extract position - first td with just a number
        pos_pattern = r'<td[^>]*>(\d{1,3})</td>'
        pos_match = re.search(pos_pattern, row_html, re.IGNORECASE)
        if pos_match:
            result["position"] = pos_match.group(1)

        # Extract rider name from profile link - name is in second <span>
        rider_pattern = r'<a[^>]*href=["\'][^"\']*\/profile\/[^"\']*["\'][^>]*>.*?<span>([^<]+)</span>'
        rider_match = re.search(rider_pattern, row_html, re.IGNORECASE | re.DOTALL)
        if rider_match:
            result["name"] = rider_match.group(1).strip()

        # Extract team from team link
        team_pattern = r'<a[^>]*href=["\'][^"\']*\/team\/[^"\']*["\'][^>]*>.*?<span>([^<]+)</span>'
        team_match = re.search(team_pattern, row_html, re.IGNORECASE | re.DOTALL)
        if team_match:
            result["team"] = team_match.group(1).strip()

        # Extract age - look for <span>XX</span> where XX is 2 digits between 15-55
        age_pattern = r'<span>(\d{2})</span>'
        for age_match in re.finditer(age_pattern, row_html):
            age_val = int(age_match.group(1))
            if 15 <= age_val <= 55:
                result["age"] = str(age_val)
                break

        # Extract time - look for time format (XX:XX or +XX:XX or +XX or Lap)
        # Time is often in the last cell, formats: "59:04", "+ 37", "+ 01:16", "+1 Lap"
        time_patterns = [
            r'>(\d{1,2}:\d{2}:\d{2})<',           # HH:MM:SS
            r'>(\d{1,2}:\d{2})<',                 # MM:SS
            r'>(\+\s*\d{1,2}:\d{2})<',            # + MM:SS (with optional space)
            r'>(\+\s*\d+)<',                      # + seconds (with optional space)
            r'>(\+\s*\d+\s*Lap[s]?)<',            # +X Lap(s)
        ]
        for pattern in time_patterns:
            time_match = re.search(pattern, row_html, re.IGNORECASE)
            if time_match:
                # Normalize: remove extra spaces after +
                time_val = time_match.group(1).strip()
                time_val = re.sub(r'\+\s+', '+', time_val)
                result["time"] = time_val
                break

        # Only add if we have at least position and name
        if result["position"] and result["name"]:
            results.append(result)

    return results


def save_startlist(riders: list[dict], race_info: RaceInfo, category: str):
    """Save startlist to CSV file."""
    STARTLISTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"Startlist__{race_info.series}__{race_info.race_name}__{category}__{race_info.date}.csv"
    filepath = STARTLISTS_DIR / filename

    # Convert to expected format: Name, NAT, Club (capitalized headers)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "NAT", "Club"])
        writer.writeheader()
        for rider in riders:
            writer.writerow({
                "Name": rider["name"],
                "NAT": "",  # Not available from CyclingFlash
                "Club": rider.get("team", "")
            })

    print(f"  ✓ Saved {len(riders)} riders to {filepath.name}")
    return filepath


def save_results(results: list[dict], race_info: RaceInfo, category: str):
    """Save results to CSV file."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"Results__{race_info.series}__{race_info.race_name}__{category}__{race_info.date}__{race_info.location}.csv"
    filepath = RESULTS_DIR / filename

    # Convert to expected format: Position, Name, Team, Time (capitalized headers)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Position", "Name", "Team", "Time"])
        writer.writeheader()
        for result in results:
            writer.writerow({
                "Position": result["position"],
                "Name": result["name"],
                "Team": result.get("team", ""),
                "Time": result.get("time", "")
            })

    print(f"  ✓ Saved {len(results)} results to {filepath.name}")
    return filepath


def scrape_event(event_url: str, race_info: RaceInfo):
    """Main function to scrape an event."""
    print(f"\n{'='*60}")
    print(f"Scraping: {event_url}")
    print(f"Series: {race_info.series} | Race: {race_info.race_name}")
    print(f"Date: {race_info.date} | Location: {race_info.location}")
    print(f"{'='*60}\n")

    # Discover category URLs
    print("Discovering race categories...")
    categories = discover_category_urls(event_url)

    if not categories:
        print("ERROR: Could not find any race categories on the event page.")
        return

    print(f"Found {len(categories)} categories: {[c.category for c in categories]}\n")

    # Process each category
    for cat in categories:
        print(f"\n--- {cat.category} ---")

        # Fetch and parse startlist
        print(f"Fetching startlist: {cat.startlist_url}")
        startlist_html = fetch_page(cat.startlist_url)
        if startlist_html:
            riders = parse_startlist(startlist_html)
            if riders:
                save_startlist(riders, race_info, cat.category)
            else:
                print("  ⚠ No riders found in startlist")

        # Fetch and parse results
        print(f"Fetching results: {cat.results_url}")
        results_html = fetch_page(cat.results_url)
        if results_html:
            results = parse_results(results_html)
            if results:
                save_results(results, race_info, cat.category)
            else:
                print("  ⚠ No results found")

    print(f"\n{'='*60}")
    print("Done!")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape startlists and results from CyclingFlash.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python scrape_cyclingflash.py https://cyclingflash.com/event/x2o-badkamers-trofee-gp-sven-nys-2026 \\
        --series "X2O-Trofee" --race "GP-Sven-Nys" --location "BAAL-BELGIUM" --date "2026-01-01"
        """
    )

    parser.add_argument("event_url", help="CyclingFlash event URL")
    parser.add_argument("--series", required=True, help="Series name (e.g., X2O-Trofee, UCI-WC, Superprestige)")
    parser.add_argument("--race", required=True, help="Race name (e.g., GP-Sven-Nys)")
    parser.add_argument("--location", required=True, help="Location with country (e.g., BAAL-BELGIUM)")
    parser.add_argument("--date", required=True, help="Race date in YYYY-MM-DD format")

    args = parser.parse_args()

    # Validate date format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        print(f"ERROR: Date must be in YYYY-MM-DD format, got: {args.date}")
        sys.exit(1)

    race_info = RaceInfo(
        series=args.series,
        race_name=args.race,
        location=args.location,
        date=args.date
    )

    scrape_event(args.event_url, race_info)


if __name__ == "__main__":
    main()
