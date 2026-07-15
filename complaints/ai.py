from openai import OpenAI
from django.conf import settings
import json
from .smart_classifier import smart_classify
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def analyze_complaint(text):

    prompt = f"""
    You are an expert AI Complaint Classification System for a company.

    Your task is to classify each complaint into ONE department and ONE priority.

    Return ONLY valid JSON.

    =========================
    AVAILABLE DEPARTMENTS
    =========================

    IT
    HR
    Finance
    Facilities
    Security

    Use "General" ONLY if none of the above departments match.

    =========================
    DEPARTMENT GUIDELINES
    =========================

    IT
    - Computer
    - Laptop
    - Printer
    - Internet
    - WiFi
    - Network
    - Email
    - Software
    - Hardware
    - Website
    - System
    - Login
    - Password
    - Account
    - Server
    - Database
    - Keyboard
    - Mouse
    - Monitor
    - Scanner
    - Projector

    HR
    - Salary
    - Leave
    - Attendance
    - Promotion
    - Recruitment
    - Employee
    - Payroll
    - Resignation
    - Hiring
    - Training
    - Appraisal
    - Performance

    Finance
    - Invoice
    - Payment
    - Refund
    - Budget
    - Purchase
    - Expense
    - Tax
    - Bills
    - Reimbursement

    Facilities
    - AC
    - Air Conditioner
    - Electricity
    - Water
    - Furniture
    - Chair
    - Table
    - Door
    - Window
    - Cleaning
    - Washroom
    - Building
    - Office
    - Generator
    - Fan

    Security
    - Theft
    - Stolen
    - CCTV
    - Camera
    - Guard
    - Intruder
    - Violence
    - Fight
    - Fire
    - Emergency
    - Unauthorized Access

    =========================
    PRIORITY RULES
    =========================

    Critical
    - Fire
    - Security Breach
    - Theft
    - Violence
    - Server Completely Down
    - Gas Leak

    High
    - Internet Down
    - Printer Not Working
    - Power Failure
    - Water Leakage
    - Major Equipment Failure

    Medium
    - Slow Computer
    - Payment Delay
    - Leave Request
    - Broken Furniture

    Low
    - Suggestions
    - Information Requests
    - Minor Issues

    =========================
    IMPORTANT
    =========================

    Never invent a department.

    Always choose ONE department.

    Return ONLY JSON.

    Example:

    {{
        "department":"IT",
        "priority":"high"
    }}

    Complaint:

    {text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # 🧠 ensure valid JSON
        json_data = json.loads(content)
        return json.dumps(json_data)

    except Exception as e:

        print("AI ERROR:", e)
        print("Using Smart Classifier...")

        return smart_classify(text)


def fallback_analysis(text):

    text = text.lower()

    # =========================
    # HR
    # =========================
    if any(word in text for word in [

        "salary",
        "pay",
        "leave",
        "vacation",
        "attendance",
        "promotion",
        "employee",
        "recruitment",
        "hr",
        "harass",
        "harassment",
        "bully",
        "bullying",
        "manager",
        "supervisor",
        "coworker",
        "co-worker",
        "colleague",
        "misconduct",
        "behavior",
        "behaviour",
        "abuse",
        "abusive",
        "discrimination",
        "workplace",
        "threat",
        "threatening"

    ]):
        return {
            "department": "HR",
            "priority": "high"
        }

    # =========================
    # IT
    # =========================
    elif any(word in text for word in [
        "computer",
        "laptop",
        "printer",
        "wifi",
        "internet",
        "network",
        "server",
        "software",
        "system",
        "email",
        "keyboard",
        "mouse",
        "monitor"
    ]):
        return {
            "department": "IT",
            "priority": "high"
        }

    # =========================
    # Finance
    # =========================
    elif any(word in text for word in [
        "payment",
        "invoice",
        "refund",
        "bill",
        "budget",
        "expense",
        "finance",
        "tax",
        "purchase"
    ]):
        return {
            "department": "Finance",
            "priority": "medium"
        }

    # =========================
    # Facilities
    # =========================
    elif any(word in text for word in [
        "water",
        "leak",
        "electricity",
        "light",
        "chair",
        "table",
        "door",
        "window",
        "washroom",
        "building",
        "cleaning",
        "fan",
        "ac",
        "air conditioner"
    ]):
        return {
            "department": "Facilities",
            "priority": "high"
        }

    # =========================
    # Security
    # =========================
    elif any(word in text for word in [
        "stolen",
        "theft",
        "security",
        "guard",
        "camera",
        "cctv",
        "intruder"
    ]):
        return {
            "department": "Security",
            "priority": "critical"
        }

    # =========================
    # Default
    # =========================
    return {
        "department": "General",
        "priority": "low"
    }