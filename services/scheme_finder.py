# Scheme Finder - matches government schemes to an MSME owner's profile.
# Reads the scheme catalogue from the bundled JSON file and ranks the
# schemes most relevant to the given profile.

import json
import os

# Load the scheme catalogue from data/schemes.json
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_schemes():
    """Load the scheme data from the JSON catalogue file."""
    schemes_path = os.path.join(DATA_DIR, "schemes.json")
    with open(schemes_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Loaded once at startup to avoid re-reading the file for every request
ALL_SCHEMES = load_schemes()


def find_schemes(investment: float = 0, category: str = "general",
                 business_type: str = "manufacturing", age: int = 25) -> list:
    """
    Finds eligible schemes based on the user's profile.

    Parameters:
        investment (float): Amount the user plans to invest (in rupees)
        category (str): general / sc / st / obc / minority / women
        business_type (str): manufacturing / service / trade
        age (int): User's age

    Returns:
        list: Eligible schemes sorted by relevance
    """
    eligible = []

    for scheme in ALL_SCHEMES:
        score = 0  # Higher score = better match
        reasons = []  # Why the scheme is eligible

        # Check 1: Category match
        # True when the user's category appears in the scheme's eligible categories
        if category.lower() in [c.lower() for c in scheme.get("eligible_categories", [])]:
            score += 30
            reasons.append(f"Category match ({category})")
        elif "general" in [c.lower() for c in scheme.get("eligible_categories", [])]:
            score += 15
            reasons.append("General category ke liye available hai")

        # Check 2: Business type match
        # Awards points when the user's business type matches the scheme
        btypes = [bt.lower() for bt in scheme.get("business_types", [])]
        if business_type.lower() in btypes:
            score += 25
            reasons.append(f"Business type match ({business_type})")
        elif "manufacturing" in btypes or "service" in btypes:
            score += 10  # Partial credit for a closely related business type

        # Check 3: Investment range
        # Rewards schemes whose investment range includes the user's amount
        inv_range = scheme.get("investment_range", {})
        if inv_range and investment > 0:
            min_inv = inv_range.get("min", 0)
            max_inv = inv_range.get("max", float("inf"))
            if min_inv <= investment <= max_inv:
                score += 25
                reasons.append(f"Investment Rs {investment:,.0f} scheme ke range me hai")
            elif investment < min_inv:
                score += 5
                reasons.append(f"Investment thoda kam hai (min: Rs {min_inv:,.0f})")
        elif not inv_range:
            # Grant small credit when the scheme defines no investment range
            score += 10

        # Check 4: Age eligibility
        min_age = scheme.get("age_min", 18)
        if age >= min_age:
            score += 10
            reasons.append(f"Age qualify karti hai ({age} >= {min_age})")

        # Only schemes above the minimum score threshold are eligible
        if score >= 30:
            eligible.append({
                "scheme": scheme,
                "score": score,
                "reasons": reasons
            })

    # Sort by score in descending order so the best match comes first
    eligible.sort(key=lambda x: x["score"], reverse=True)

    # Return only the top five matches
    return eligible[:5]


def get_scheme_by_id(scheme_id: int) -> dict:
    """Return the full details of a specific scheme by its id."""
    for scheme in ALL_SCHEMES:
        if scheme["id"] == scheme_id:
            return scheme
    return None


def get_all_schemes_summary() -> list:
    """Return a short summary of all available schemes."""
    summary = []
    for scheme in ALL_SCHEMES:
        summary.append({
            "id": scheme["id"],
            "name": scheme["name"],
            "full_name": scheme["full_name"],
            "description": scheme["description"],
            "benefit": scheme["benefit"],
            "apply_url": scheme["apply_url"]
        })
    return summary


def format_schemes_for_ai(schemes: list) -> str:
    """
    Builds a formatted string describing the matched schemes, ready to be
    injected into the AI prompt as grounding context.
    """
    if not schemes:
        return "Koi eligible scheme nahi mili user ki profile ke liye."

    result = "Eligible schemes for this user:\n\n"
    for i, item in enumerate(schemes, 1):
        s = item["scheme"]
        result += f"--- Scheme {i}: {s['name']} ({s['full_name']}) ---\n"
        result += f"Description: {s['description']}\n"
        result += f"Benefit: {s['benefit']}\n"
        result += f"Apply: {s['apply_url']}\n"
        result += f"Documents: {', '.join(s.get('documents', []))}\n"
        result += f"Steps: {s.get('how_to_apply', 'Website pe jao')}\n"
        result += f"Match score: {item['score']}/100\n"
        result += f"Reasons: {', '.join(item['reasons'])}\n\n"

    return result
