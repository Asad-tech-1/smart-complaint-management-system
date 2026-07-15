import json
import math

# =====================================
# Department Knowledge Base
# =====================================

DEPARTMENTS = {

    "IT": {

        # Critical Infrastructure
        "server": 10,
        "database": 10,
        "network": 9,
        "internet": 9,
        "wifi": 9,
        "router": 8,
        "switch": 8,
        "firewall": 8,

        # Systems
        "software": 8,
        "system": 8,
        "application": 8,
        "website": 8,
        "portal": 8,
        "login": 8,
        "password": 8,
        "email": 8,
        "account": 8,

        # Hardware
        "printer": 7,
        "scanner": 7,
        "monitor": 6,
        "computer": 6,
        "desktop": 6,
        "pc": 6,
        "laptop": 6,
        "cpu": 6,
        "keyboard": 4,
        "mouse": 4,
        "usb": 4,
        "projector": 5,
        "camera": 4,

        # Problems
        "crash": 8,
        "error": 7,
        "bug": 7,
        "slow": 5,
        "freeze": 7,
        "restart": 5,
        "install": 5,
        "update": 5

    },

    "HR": {

        "salary": 10,
        "pay": 10,
        "payroll": 10,
        "leave": 8,
        "attendance": 8,
        "promotion": 8,
        "increment": 8,
        "employee": 6,
        "staff": 5,
        "manager": 6,
        "supervisor": 6,
        "recruitment": 8,
        "interview": 8,
        "training": 6,
        "appraisal": 7,
        "performance": 7,

        "harassment": 10,
        "harass": 10,
        "bully": 10,
        "bullying": 10,
        "abuse": 9,
        "abusive": 9,
        "misconduct": 9,
        "behavior": 6,
        "behaviour": 6,
        "threat": 9,
        "discrimination": 10,
        "coworker": 5,
        "co-worker": 5,
        "colleague": 5

    },

    "Finance": {

        "payment": 10,
        "invoice": 10,
        "refund": 9,
        "budget": 8,
        "expense": 8,
        "purchase": 8,
        "bill": 8,
        "finance": 8,
        "tax": 8,
        "reimbursement": 9,
        "allowance": 8,
        "deduction": 8,
        "bank": 7,
        "transfer": 7,
        "receipt": 6

    },

    "Facilities": {

        "electricity": 10,
        "power": 10,
        "generator": 9,
        "water": 9,
        "leak": 10,
        "pipe": 8,

        "ac": 8,
        "air conditioner": 10,
        "fan": 7,
        "light": 7,

        "chair": 5,
        "table": 5,
        "desk": 5,
        "door": 6,
        "window": 6,
        "washroom": 8,
        "toilet": 8,
        "cleaning": 8,
        "building": 6,
        "office": 5

    },

    "Security": {

        "security": 10,
        "guard": 8,
        "cctv": 9,
        "camera": 8,

        "theft": 10,
        "stolen": 10,
        "steal": 10,
        "robbery": 10,

        "fire": 10,
        "intruder": 10,
        "violence": 10,
        "fight": 9,
        "weapon": 10,
        "emergency": 10,
        "unauthorized": 10,
        "trespassing": 9

    }

}

# =====================================
# Phrase Knowledge Base
# =====================================

PHRASES = {

    "IT": {

        "cannot login": 20,
        "unable to login": 20,
        "login failed": 18,
        "forgot password": 15,
        "password reset": 15,

        "internet down": 20,
        "network down": 20,
        "server down": 25,
        "email not working": 18,
        "printer not working": 18,
        "system crashed": 20,
        "website not working": 18,
        "cannot access": 15,
        "connection lost": 18

    },

    "HR": {

        "salary not paid": 25,
        "salary delay": 20,
        "leave rejected": 18,
        "promotion issue": 18,

        "being harassed": 25,
        "workplace harassment": 30,
        "manager harassment": 30,
        "mental harassment": 30,
        "physical harassment": 35,
        "verbal abuse": 25,
        "employee misconduct": 25,
        "staff behavior": 18

    },

    "Finance": {

        "payment failed": 25,
        "refund not received": 25,
        "invoice issue": 20,
        "budget approval": 18,
        "purchase request": 18,
        "tax deduction": 18,
        "salary credited": 15

    },

    "Facilities": {

        "water leakage": 25,
        "water leak": 25,
        "air conditioner": 20,
        "ac not working": 25,
        "air conditioner not cooling": 30,
        "electricity failure": 30,
        "power outage": 30,
        "broken chair": 18,
        "broken table": 18,
        "dirty washroom": 25

    },

    "Security": {

        "stolen laptop": 35,
        "stolen computer": 35,
        "office theft": 35,
        "security breach": 40,
        "unauthorized access": 40,
        "fire alarm": 40,
        "physical fight": 35,
        "armed person": 50,
        "emergency evacuation": 45

    }

}


def smart_classify(text):

    text = text.lower()

    department = detect_department(text)

    priority = detect_priority(text)

    return json.dumps({
        "department": department,
        "priority": priority
    })


def detect_department(text):

    scores = {}
    matched_keywords = {}

    for department in DEPARTMENTS:

        score = 0
        matched = []

        # -------------------------
        # Phrase Matching
        # -------------------------

        for phrase, weight in PHRASES[department].items():

            if phrase in text:

                score += weight

                matched.append(f"{phrase} (+{weight})")

        # -------------------------
        # Keyword Matching
        # -------------------------

        for keyword, weight in DEPARTMENTS[department].items():

            if keyword in text:

                score += weight

                matched.append(f"{keyword} (+{weight})")

        scores[department] = score
        matched_keywords[department] = matched

    print("\n=========== SMART AI REPORT ===========")

    for department in scores:

        print(
            f"{department:<12}"
            f"Score={scores[department]:<3}"
            f"  {matched_keywords[department]}"
        )

    best_department = max(scores, key=scores.get)

    if scores[best_department] == 0:

        print("No department matched.")
        print("Confidence : 0%")
        print("=======================================\n")

        return "General"

    confidence = calculate_confidence(scores)

    print(f"\nSelected Department : {best_department}")

    print(f"Confidence          : {confidence}%")

    print("=======================================\n")

    return best_department


# =====================================
# Priority Detection
# =====================================

def detect_priority(text):

    text = text.lower()

    critical = [

        "fire",
        "theft",
        "stolen",
        "violence",
        "fight",
        "emergency"

    ]

    high = [

        "printer",
        "internet",
        "wifi",
        "server",
        "network",
        "harassment",
        "harass",
        "water leak",
        "electricity"

    ]

    medium = [

        "salary",
        "leave",
        "payment",
        "refund",
        "chair",
        "table"

    ]

    for word in critical:

        if word in text:
            return "critical"

    for word in high:

        if word in text:
            return "high"

    for word in medium:

        if word in text:
            return "medium"

    return "low"



def calculate_confidence(scores):

    highest = max(scores.values())

    if highest == 0:
        return 0

    total = sum(scores.values())

    confidence = (highest / total) * 100

    return round(confidence, 1)