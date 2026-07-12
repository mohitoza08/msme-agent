# GST Helper - Ye file GST calculations karti hai
# GST = Goods and Services Tax - India me har cheez pe lagta hai
# 5 slabs hain: 0%, 5%, 12%, 18%, 28%

# Ye dictionary hai - common cheezon ke GST rates
# Format: {cheez ka naam: GST rate}
# Rates government ne fix kiye hain
GST_RATES = {
    # Zero tax - gareeb logo ki cheezein
    "essentials": {
        "rate": 0,
        "items": ["fresh vegetables", "fresh fruits", "milk", "curd", "bread", "eggs",
                  "salt", "rice", "wheat", "dal", "unbranded flour"],
        "note": "Ye sab zero GST hai - government ne gareeb logo ke liye chhoda hai"
    },
    # 5% - basic packaged items
    "low": {
        "rate": 5,
        "items": ["packaged food", "tea", "coffee", "spices", "sugar",
                  "paneer", "frozen vegetables", "apparel below 1000"],
        "note": "Packaged ya processed food mostly 5% pe aata hai"
    },
    # 12% - middle category
    "medium": {
        "rate": 12,
        "items": ["clothing above 1000", "processed food", "business class air ticket",
                  "fertilizers", "umbrella", "mobile phone"],
        "note": "Clothing 1000 se upar ya processed food items pe 12% lagta hai"
    },
    # 18% - sabse common rate (services, electronics)
    "standard": {
        "rate": 18,
        "items": ["restaurant service", "beauty salon", "gym", "consulting",
                  "software service", "internet", "mobile recharge", "car repair",
                  "most electronics", "stationery", "printing"],
        "note": "Maximum services pe 18% lagta hai - ye sabse common rate hai"
    },
    # 28% - luxury items
    "high": {
        "rate": 28,
        "items": ["car", "bike", "AC", "washing machine", "airline tickets",
                  "cinema", "tobacco", "aerated drinks", "luxury hotels"],
        "note": "Luxury items pe 28% - government isse sabse zyada tax leti hai"
    }
}

# Filing dates - ye yaad rakhna zaroori hai
# Agar late ho jaye toh penalty lagegi
FILING_DATES = {
    "GSTR-1": {
        "deadline": "11th of every month",
        "penalty": "Rs 50/day (late filing)",
        "what_is_it": "Tumne kya becha - sabka detail file karna hai"
    },
    "GSTR-3B": {
        "deadline": "20th of every month",
        "penalty": "Rs 50/day (late filing), max Rs 10,000",
        "what_is_it": "Monthly summary return - kitna tax bana aur kitna bhara"
    },
    "GSTR-9": {
        "deadline": "31st December every year",
        "penalty": "Rs 200/day, max 0.5% of turnover",
        "what_is_it": "Annual return - saal bhar ka ek saath file karo"
    },
    "GSTR-9C": {
        "deadline": "31st December (only if turnover > 5 crore)",
        "penalty": "Same as GSTR-9",
        "what_is_it": "Self-certified reconciliation statement - audit jaisa hai"
    }
}


def calculate_gst(amount: float, rate: float) -> dict:
    """
    GST calculate karta hai given amount pe.

    Example:
        calculate_gst(1000, 18) -> {
            "base_price": 847.46,
            "gst_amount": 152.54,
            "total": 1000,
            "cgst": 76.27,
            "sgst": 76.27
        }

    Parameters:
        amount (float): Total amount (GST inclusive)
        rate (float): GST rate (0, 5, 12, 18, ya 28)

    Returns:
        dict: Breakdown of the GST calculation
    """
    # Formula: Agar amount GST inclusive hai toh:
    # Base price = amount / (1 + rate/100)
    # GST = amount - base_price
    # CGST = GST / 2 (Central GST)
    # SGST = GST / 2 (State GST)

    base_price = round(amount / (1 + rate / 100), 2)
    gst_amount = round(amount - base_price, 2)
    cgst = round(gst_amount / 2, 2)    # CGST = Central Government ka share
    sgst = round(gst_amount / 2, 2)    # SGST = State Government ka share

    return {
        "base_price": base_price,
        "gst_rate": f"{rate}%",
        "gst_amount": gst_amount,
        "cgst": cgst,
        "sgst": sgst,
        "total": amount,
        "note": "CGST aur SGST equal hota hai - central aur state dono ko barabar milta hai"
    }


def calculate_gst_exclusive(amount: float, rate: float) -> dict:
    """
    GST exclusive calculation - pehle base price hai, uspe GST lagao.

    Example:
        calculate_gst_exclusive(1000, 18) -> {
            "base_price": 1000,
            "gst_amount": 180,
            "total": 1180
        }
    """
    gst_amount = round(amount * rate / 100, 2)
    total = round(amount + gst_amount, 2)
    cgst = round(gst_amount / 2, 2)
    sgst = round(gst_amount / 2, 2)

    return {
        "base_price": amount,
        "gst_rate": f"{rate}%",
        "gst_amount": gst_amount,
        "cgst": cgst,
        "sgst": sgst,
        "total": total
    }


def get_filing_dates() -> dict:
    """
    GST filing dates return karta hai - ye monthly/yearly deadlines hain.
    """
    return FILING_DATES


def get_rate_for_item(item_name: str) -> dict:
    """
    Item ka GST rate dhundhta hai.
    Simple keyword matching use karta hai.
    """
    item_lower = item_name.lower()

    # Har slab ke items me check karo
    for slab_name, slab_data in GST_RATES.items():
        for item in slab_data["items"]:
            if item in item_lower or item_lower in item:
                return {
                    "item": item_name,
                    "rate": slab_data["rate"],
                    "slab": slab_name,
                    "note": slab_data["note"]
                }

    # Agar match nahi mila
    return {
        "item": item_name,
        "rate": None,
        "note": "Is item ka exact rate government website pe check karo: https://cbic-gst.gov.in"
    }


def get_all_slabs() -> list:
    """
    Saare GST slabs ka summary return karta hai.
    """
    result = []
    for name, data in GST_RATES.items():
        result.append({
            "slab": name,
            "rate": f"{data['rate']}%",
            "examples": ", ".join(data["items"][:5]),  # Sirf 5 examples dikhao
            "note": data["note"]
        })
    return result
