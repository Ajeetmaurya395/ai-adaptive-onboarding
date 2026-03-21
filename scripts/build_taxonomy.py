#!/usr/bin/env python3
"""
Process raw O*NET text files into the app's data directory.

Generates:
  - data/skill_taxonomy.json   (expanded skill categories)
  - data/onet_occupations.json (occupation → skills mapping)
  - data/onet_tech_skills.json (occupation → technology skills)

Run download_onet.py first to fetch the raw data.
"""

import csv
import json
import os
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "onet_raw")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def _read_tsv(filename):
    """Read a tab-separated O*NET text file, return list of dicts."""
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        print(f"  ⚠️  {filename} not found — skipping")
        return []
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    print(f"  📄 {filename}: {len(rows)} rows")
    return rows


# ---------------------------------------------------------------------------
# 1. Build expanded skill taxonomy
# ---------------------------------------------------------------------------
def build_skill_taxonomy():
    """
    Merge O*NET Skills.txt + Knowledge.txt into a rich taxonomy.

    Skills.txt columns:  O*NET-SOC Code, Element ID, Element Name, Scale ID, Data Value, ...
    Knowledge.txt columns: same structure
    """
    print("\n📂 Building skill taxonomy...")

    skills_rows = _read_tsv("Skills.txt")
    knowledge_rows = _read_tsv("Knowledge.txt")

    # Collect unique skill/knowledge element names
    skill_names = set()
    knowledge_names = set()

    for row in skills_rows:
        name = row.get("Element Name", "").strip()
        if name:
            skill_names.add(name)

    for row in knowledge_rows:
        name = row.get("Element Name", "").strip()
        if name:
            knowledge_names.add(name)

    # Build tech skills from Technology Skills.txt
    tech_rows = _read_tsv("Technology Skills.txt")
    tech_skill_names = set()
    for row in tech_rows:
        example = row.get("Example", "").strip()
        commodity_title = row.get("Commodity Title", "").strip()
        if example:
            tech_skill_names.add(example)
        if commodity_title:
            tech_skill_names.add(commodity_title)

    # Build taxonomy structure
    taxonomy = {
        "source": "O*NET 29.2 (February 2025)",
        "citation": "O*NET® is a trademark of the U.S. Department of Labor/Employment and Training Administration (USDOL/ETA). Used under the CC-BY 4.0 license.",
        "categories": {
            "Core Skills (O*NET)": sorted(skill_names),
            "Knowledge Areas (O*NET)": sorted(knowledge_names),
            "Technology Skills (O*NET)": sorted(list(tech_skill_names)[:500]),  # Cap for sanity
        },
        "stats": {
            "total_skills": len(skill_names),
            "total_knowledge": len(knowledge_names),
            "total_tech_skills": len(tech_skill_names),
        },
    }

    out_path = os.path.join(DATA_DIR, "skill_taxonomy.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    print(f"  ✅ skill_taxonomy.json: {len(skill_names)} skills, {len(knowledge_names)} knowledge, {len(tech_skill_names)} tech skills")
    return taxonomy


# ---------------------------------------------------------------------------
# 2. Build occupation → skills mapping
# ---------------------------------------------------------------------------
def build_occupations():
    """
    Build a mapping from occupation (SOC code + title) to its required
    skills, knowledge, and importance ratings.
    """
    print("\n📂 Building occupation mappings...")

    # Load occupation titles
    occ_rows = _read_tsv("Occupation Data.txt")
    occupations = {}
    for row in occ_rows:
        code = row.get("O*NET-SOC Code", "").strip()
        title = row.get("Title", "").strip()
        if code and title:
            occupations[code] = {
                "title": title,
                "code": code,
                "skills": [],
                "knowledge": [],
            }

    # Add skills with importance ratings
    # Scale IDs: IM = Importance (1-5), LV = Level (0-7)
    skills_rows = _read_tsv("Skills.txt")
    for row in skills_rows:
        code = row.get("O*NET-SOC Code", "").strip()
        scale_id = row.get("Scale ID", "").strip()
        if code in occupations and scale_id == "IM":
            name = row.get("Element Name", "").strip()
            try:
                value = float(row.get("Data Value", 0))
            except (ValueError, TypeError):
                value = 0.0
            if name and value >= 2.5:  # Only include skills with decent importance
                occupations[code]["skills"].append({
                    "name": name,
                    "importance": round(value, 2),
                })

    # Add knowledge
    knowledge_rows = _read_tsv("Knowledge.txt")
    for row in knowledge_rows:
        code = row.get("O*NET-SOC Code", "").strip()
        scale_id = row.get("Scale ID", "").strip()
        if code in occupations and scale_id == "IM":
            name = row.get("Element Name", "").strip()
            try:
                value = float(row.get("Data Value", 0))
            except (ValueError, TypeError):
                value = 0.0
            if name and value >= 2.5:
                occupations[code]["knowledge"].append({
                    "name": name,
                    "importance": round(value, 2),
                })

    # Sort skills by importance (descending) within each occupation
    for occ in occupations.values():
        occ["skills"].sort(key=lambda x: x["importance"], reverse=True)
        occ["knowledge"].sort(key=lambda x: x["importance"], reverse=True)

    out_path = os.path.join(DATA_DIR, "onet_occupations.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(occupations, f, indent=2, ensure_ascii=False)

    print(f"  ✅ onet_occupations.json: {len(occupations)} occupations")
    return occupations


# ---------------------------------------------------------------------------
# 3. Build technology skills per occupation
# ---------------------------------------------------------------------------
def build_tech_skills():
    """
    Build a mapping from occupation → list of specific technology tools/software.
    """
    print("\n📂 Building technology skills mapping...")

    tech_rows = _read_tsv("Technology Skills.txt")
    tech_by_occ = defaultdict(list)

    seen = set()
    for row in tech_rows:
        code = row.get("O*NET-SOC Code", "").strip()
        example = row.get("Example", "").strip()
        commodity = row.get("Commodity Title", "").strip()
        if code and example:
            key = (code, example)
            if key not in seen:
                seen.add(key)
                tech_by_occ[code].append({
                    "tool": example,
                    "category": commodity,
                })

    # Sort and limit per occupation
    result = {}
    for code, tools in tech_by_occ.items():
        result[code] = tools[:50]  # Cap at 50 per occupation

    out_path = os.path.join(DATA_DIR, "onet_tech_skills.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  ✅ onet_tech_skills.json: {len(result)} occupations with tech skills")
    return result


# ---------------------------------------------------------------------------
# 4. Build a flat lookup for skill normalization
# ---------------------------------------------------------------------------
def build_skill_lookup():
    """
    Build a flat JSON map for fast skill normalization:
    lowercase_skill_name → { canonical, category, source }
    """
    print("\n📂 Building skill normalization lookup...")

    lookup = {}

    # From Skills.txt
    for row in _read_tsv("Skills.txt"):
        name = row.get("Element Name", "").strip()
        if name:
            lookup[name.lower()] = {
                "canonical": name,
                "category": "skill",
                "source": "onet_skills",
            }

    # From Knowledge.txt
    for row in _read_tsv("Knowledge.txt"):
        name = row.get("Element Name", "").strip()
        if name:
            lookup[name.lower()] = {
                "canonical": name,
                "category": "knowledge",
                "source": "onet_knowledge",
            }

    # From Technology Skills.txt (examples)
    for row in _read_tsv("Technology Skills.txt"):
        example = row.get("Example", "").strip()
        commodity = row.get("Commodity Title", "").strip()
        if example:
            lookup[example.lower()] = {
                "canonical": example,
                "category": "technology",
                "source": "onet_tech",
                "commodity": commodity,
            }

    out_path = os.path.join(DATA_DIR, "skill_lookup.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(lookup, f, indent=2, ensure_ascii=False)

    print(f"  ✅ skill_lookup.json: {len(lookup)} entries")
    return lookup


if __name__ == "__main__":
    print("=" * 60)
    print("O*NET Taxonomy Builder for AI-Adaptive Onboarding")
    print("=" * 60)

    # Check that raw data exists
    if not os.path.isdir(RAW_DIR):
        print(f"❌ Raw data directory not found: {RAW_DIR}")
        print("💡 Run download_onet.py first")
        sys.exit(1)

    taxonomy = build_skill_taxonomy()
    occupations = build_occupations()
    tech_skills = build_tech_skills()
    lookup = build_skill_lookup()

    print("\n" + "=" * 60)
    print("🎉 All data files generated in data/")
    print(f"   Skills:       {taxonomy['stats']['total_skills']}")
    print(f"   Knowledge:    {taxonomy['stats']['total_knowledge']}")
    print(f"   Tech skills:  {taxonomy['stats']['total_tech_skills']}")
    print(f"   Occupations:  {len(occupations)}")
    print(f"   Lookup:       {len(lookup)} entries")
    print("=" * 60)
