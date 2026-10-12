#!/usr/bin/env python3
import json, os, sys, datetime, urllib.parse, urllib.request

KEY = os.environ.get("YT_API_KEY", "").strip()
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "trending", "trending.json"))

COUNTRIES = [
    ("GLOBAL", "Worldwide", "🌍", "US"),
    ("PK", "Pakistan", "🇵🇰", "PK"),
    ("IN", "India", "🇮🇳", "IN"),
    ("BD", "Bangladesh", "🇧🇩", "BD"),
    ("SA", "Saudi Arabia", "🇸🇦", "SA"),
    ("AE", "UAE", "🇦🇪", "AE"),
    ("QA", "Qatar", "🇶🇦", "QA"),
    ("OM", "Oman", "🇴🇲", "OM"),
    ("KW", "Kuwait", "🇰🇼", "KW"),
    ("EG", "Egypt", "🇪🇬", "EG"),
    ("TR", "Turkey", "🇹🇷", "TR"),
    ("ID", "Indonesia", "🇮🇩", "ID"),
    ("MY", "Malaysia", "🇲🇾", "MY"),
    ("NG", "Nigeria", "🇳🇬", "NG"),
    ("GB", "United Kingdom", "🇬🇧", "GB"),
    ("US", "United States", "🇺🇸", "US"),
    ("CA", "Canada", "🇨🇦", "CA"),
    ("AU", "Australia", "🇦🇺", "AU"),
    ("DE", "Germany", "🇩🇪", "DE"),
    ("FR", "France", "🇫🇷", "FR"),
    ("BR", "Brazil", "🇧🇷", "BR"),
]
GROUPS = [("Trending now", None), ("Music", "10"), ("Entertainment", "24"), ("Sports", "17")]
PER_GROUP = 15


def fetch(region, cat):
    p = {"part": "snippet", "chart": "mostPopular", "regionCode": region,
         "maxResults": str(PER_GROUP), "key": KEY}
    if cat:
        p["videoCategoryId"] = cat
    url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)
    except Exception as e:
        print("skip", region, cat, e)
        return []
    items = []
    for it in data.get("items", []):
        sn = it.get("snippet", {})
        title = (sn.get("title") or "").strip()
        if not title or not it.get("id"):
            continue
        items.append({
            "t": title[:90],
            "u": "https://www.youtube.com/watch?v=" + it["id"],
            "c": (sn.get("channelTitle") or "")[:40],
        })
    return items


def main():
    if not KEY:
        print("YT_API_KEY nahi mili - trending.json ko nahi chheda.")
        return 0
    try:
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f).get("countries", {})
    except Exception:
        old = {}
    result = {}
    for code, name, flag, region in COUNTRIES:
        groups = []
        for gname, cat in GROUPS:
            items = fetch(region, cat)
            if items:
                groups.append({"name": gname, "items": items})
        if groups:
            result[code] = {"name": name, "flag": flag, "groups": groups}
        elif code in old:
            result[code] = old[code]
    if not result:
        print("Kuch nahi mila - file nahi badli.")
        return 0
    doc = {
        "version": 1,
        "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "countries": result,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print("OK:", len(result), "mulk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
