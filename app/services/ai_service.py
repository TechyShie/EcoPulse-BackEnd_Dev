import os
import requests
import random
from ..core.config import settings

def get_ai_response(prompt: str):
    """
    Get AI response from OpenRouter
    Falls back to mock response if no API key is configured
    """
    # Try OpenRouter first
    if settings.OPENROUTER_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "anthropic/claude-3-sonnet",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an eco-friendly assistant that helps users track and understand their environmental impact. Provide helpful, accurate, and encouraging responses about sustainability, carbon footprint reduction, and eco-friendly practices."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 500
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"OpenRouter API exception: {str(e)}")

    # Fallback mock responses for eco-questions
    eco_responses = {
        "transport": [
            "Cycling instead of driving a car for 10km saves approximately 2.5kg of CO2! 🚴‍♂️",
            "Taking public transport reduces emissions by about 70% compared to driving alone.",
            "Carpooling with 2 others can cut your transportation emissions by 60%."
        ],
        "energy": [
            "Switching to LED bulbs saves about 0.1kg CO2 per bulb per day! 💡",
            "Unplugging electronics when not in use can save up to 100kg CO2 annually.",
            "Using a programmable thermostat can reduce heating emissions by 10-15%."
        ],
        "waste": [
            "Recycling 1kg of plastic saves about 3kg of CO2 emissions! ♻️",
            "Composting food waste prevents methane emissions - about 0.5kg CO2 per kg of waste.",
            "Reducing paper usage by 1kg saves approximately 3.5kg of CO2."
        ],
        "food": [
            "Choosing plant-based meals saves about 2.5kg CO2 per meal compared to beef! 🌱",
            "Reducing food waste by 1kg prevents about 2.5kg of CO2 emissions.",
            "Eating local seasonal produce can reduce food transportation emissions by 10%."
        ],
        "water": [
            "Taking 5-minute showers instead of 10-minute ones saves about 0.5kg CO2 per shower! 🚿",
            "Fixing a leaky faucet can save 350kg CO2 annually from water heating.",
            "Using cold water for laundry saves about 0.3kg CO2 per load."
        ]
    }

    # Try to match prompt with categories
    prompt_lower = prompt.lower()
    for category, responses in eco_responses.items():
        if category in prompt_lower:
            return random.choice(responses)

    # General eco tips
    general_tips = [
        "Every small eco-friendly action adds up! Keep tracking your progress. 🌍",
        "Did you know the average person can save 2-3 tons of CO2 annually through simple changes?",
        "Consistency is key - regular eco-habits have the biggest environmental impact!",
        "Consider conducting a home energy audit to find more savings opportunities.",
        "Share your eco-journey with friends - collective action creates bigger impact!"
    ]
    return random.choice(general_tips)

def calculate_co2_saved(activity_type: str, description: str, quantity: float = 1.0) -> dict:
    """
    Calculate CO2 savings and points for eco activities
    Returns: {"emissions_saved": float, "points_earned": int}
    """
    # Base calculations per unit (these are approximate values)
    calculations = {
        "transport": {
            "bike": {"co2": 0.25, "points": 2},
            "cycled": {"co2": 0.25, "points": 2},
            "walk": {"co2": 0.28, "points": 3},
            "walked": {"co2": 0.28, "points": 3},
            "public_transport": {"co2": 0.1, "points": 1},
            "carpool": {"co2": 0.15, "points": 2},
            "carpooled": {"co2": 0.15, "points": 2},
            "electric": {"co2": 0.05, "points": 2},
            "scooter": {"co2": 0.08, "points": 1}
        },
        "energy": {
            "led": {"co2": 0.1, "points": 1},
            "bulb": {"co2": 0.1, "points": 1},
            "unplug": {"co2": 0.3, "points": 2},
            "unplugged": {"co2": 0.3, "points": 2},
            "thermostat": {"co2": 0.5, "points": 3},
            "solar": {"co2": 0.8, "points": 5},
            "air-dried": {"co2": 0.4, "points": 3}
        },
        "waste": {
            "recycled": {"co2": 3.0, "points": 2},
            "recycle": {"co2": 3.0, "points": 2},
            "compost": {"co2": 0.5, "points": 3},
            "composted": {"co2": 0.5, "points": 3},
            "reused": {"co2": 1.0, "points": 2},
            "reusable": {"co2": 1.0, "points": 2},
            "repaired": {"co2": 2.0, "points": 3},
            "donated": {"co2": 1.5, "points": 2}
        },
        "food": {
            "plant-based": {"co2": 2.5, "points": 4},
            "plant_based": {"co2": 2.5, "points": 4},
            "local": {"co2": 0.3, "points": 2},
            "organic": {"co2": 0.2, "points": 2},
            "leftover": {"co2": 2.5, "points": 3},
            "waste": {"co2": 2.5, "points": 3}
        },
        "water": {
            "shower": {"co2": 0.1, "points": 1},
            "leak": {"co2": 1.0, "points": 3},
            "leaky": {"co2": 1.0, "points": 3},
            "cold": {"co2": 0.3, "points": 2},
            "efficient": {"co2": 0.01, "points": 1},
            "rainwater": {"co2": 0.5, "points": 2}
        }
    }

    # Default values if no specific match
    default_values = {"emissions_saved": 1.0, "points_earned": 5}

    # Try to find matching calculation
    description_lower = description.lower()
    
    if activity_type in calculations:
        for key, values in calculations[activity_type].items():
            if key in description_lower:
                emissions_saved = values["co2"] * quantity
                points_earned = values["points"] * int(quantity)
                return {
                    "emissions_saved": round(emissions_saved, 2),
                    "points_earned": max(1, points_earned)
                }

    # If no specific match, use activity type defaults
    type_defaults = {
        "transport": {"emissions_saved": 2.5, "points_earned": 8},
        "energy": {"emissions_saved": 1.2, "points_earned": 6},
        "waste": {"emissions_saved": 1.8, "points_earned": 7},
        "food": {"emissions_saved": 2.0, "points_earned": 8},
        "water": {"emissions_saved": 0.8, "points_earned": 5}
    }

    return type_defaults.get(activity_type, default_values)