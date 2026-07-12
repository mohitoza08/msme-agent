# Scheme Finder - Ye file government schemes dhundhti hai
# User ka profile leke match karti hai eligible schemes se
# JSON file me saare schemes ka data hai

import json
import os

# Schemes ka data load karo JSON file se
# Ye file data/ folder me hai
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_schemes():
    """JSON file se schemes ka data load karo"""
    schemes_path = os.path.join(DATA_DIR, "schemes.json")
    with open(schemes_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Global variable - baar baar file read na karni pade
ALL_SCHEMES = load_schemes()


def find_schemes(investment: float = 0, category: str = "general",
                 business_type: str = "manufacturing", age: int = 25) -> list:
    """
    User ki profile ke basis pe eligible schemes dhundhta hai.

    Parameters:
        investment (float): Kitna invest karna chahta hai (in rupees)
        category (str): general / sc / st / obc / minority / women
        business_type (str): manufacturing / service / trade
        age (int): User ki age

    Returns:
        list: Eligible schemes sorted by relevance
    """
    eligible = []

    for scheme in ALL_SCHEMES:
        score = 0  # Ye score hai - jitna zyada utni best scheme
        reasons = []  # Kyun eligible hai

        # Check 1: Category match
        # Scheme me eligible_categories me user ki category hai ya nahi
        if category.lower() in [c.lower() for c in scheme.get("eligible_categories", [])]:
            score += 30
            reasons.append(f"Category match ({category})")
        elif "general" in [c.lower() for c in scheme.get("eligible_categories", [])]:
            score += 15
            reasons.append("General category ke liye available hai")

        # Check 2: Business type match
        # Manufacturing, service, ya trade - kya match karta hai?
        btypes = [bt.lower() for bt in scheme.get("business_types", [])]
        if business_type.lower() in btypes:
            score += 25
            reasons.append(f"Business type match ({business_type})")
        elif "manufacturing" in btypes or "service" in btypes:
            score += 10  # Close enough

        # Check 3: Investment range
        # Investment scheme ke range me aata hai ya nahi
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
            # Agar investment range define nahi hai toh maan lo eligible hai
            score += 10

        # Check 4: Age check
        min_age = scheme.get("age_min", 18)
        if age >= min_age:
            score += 10
            reasons.append(f"Age qualify karti hai ({age} >= {min_age})")

        # Agar score 30 se zyada hai toh eligible hai
        if score >= 30:
            eligible.append({
                "scheme": scheme,
                "score": score,
                "reasons": reasons
            })

    # Score ke hisaab se sort karo - best scheme pehle
    eligible.sort(key=lambda x: x["score"], reverse=True)

    # Top 5 schemes return karo
    return eligible[:5]


def get_scheme_by_id(scheme_id: int) -> dict:
    """Ek specific scheme ka full detail return karo"""
    for scheme in ALL_SCHEMES:
        if scheme["id"] == scheme_id:
            return scheme
    return None


def get_all_schemes_summary() -> list:
    """Saare schemes ka short summary return karo"""
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
    Schemes ka formatted string banao jo AI ko context me de sako.
    AI ko ye data dega ki kaunsi scheme best hai user ke liye.
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
