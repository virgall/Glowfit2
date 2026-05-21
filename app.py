
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date, datetime, timedelta

st.set_page_config(page_title="GlowFit", layout="wide", initial_sidebar_state="expanded")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "glowfit_data.json"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

PROFILE_DEFAULT = {
    "height_in": 69,
    "start_weight": 224.0,
    "current_weight": 224.0,
    "goal_weight": 199.0,
    "protein_target": 140,
    "training_day": True,
    "calorie_training": 1850,
    "calorie_rest": 1650,
    "carb_training": 150,
    "carb_rest": 105,
    "water_target_l": 2.8,
    "step_target": 8000
}

MEALS = {
    "Greek Yogurt Berry Parfait": {
        "type": "Breakfast",
        "cal": 360, "protein": 34, "carbs": 32, "fibre": 8,
        "gi": "Low",
        "when": "Good breakfast or post-workout snack.",
        "prep_servings": 4,
        "ingredients": {
            "Greek yogurt 0-2%": {"qty": 800, "unit": "g"},
            "Mixed berries": {"qty": 480, "unit": "g"},
            "Chia seeds": {"qty": 48, "unit": "g"},
            "Low sugar granola": {"qty": 120, "unit": "g"}
        },
        "steps": [
            "Use a food scale for yogurt and berries.",
            "Portion 200g yogurt per serving.",
            "Add 120g berries and 12g chia per serving.",
            "Keep granola measured at 30g per serving."
        ]
    },
    "Protein Oats With Berries": {
        "type": "Breakfast",
        "cal": 420, "protein": 35, "carbs": 46, "fibre": 9,
        "gi": "Moderate",
        "when": "Best on training mornings or before lower body/cardio days.",
        "prep_servings": 3,
        "ingredients": {
            "Rolled oats": {"qty": 120, "unit": "g"},
            "Protein powder": {"qty": 90, "unit": "g"},
            "Mixed berries": {"qty": 360, "unit": "g"},
            "Chia seeds": {"qty": 30, "unit": "g"}
        },
        "steps": [
            "Measure dry oats before cooking: 40g per serving.",
            "Add protein after cooking so it mixes smoothly.",
            "Use berries instead of sugar or syrup.",
            "Pair with water or unsweetened milk."
        ]
    },
    "High Protein Cereal Bowl": {
        "type": "Breakfast",
        "cal": 390, "protein": 32, "carbs": 42, "fibre": 8,
        "gi": "Moderate",
        "when": "Best at breakfast or after training. Avoid late-night oversized bowls.",
        "prep_servings": 1,
        "ingredients": {
            "High protein low sugar cereal": {"qty": 45, "unit": "g"},
            "Greek yogurt": {"qty": 170, "unit": "g"},
            "Strawberries": {"qty": 100, "unit": "g"},
            "Chia seeds": {"qty": 10, "unit": "g"}
        },
        "steps": [
            "Weigh cereal at 45g instead of free-pouring.",
            "Use Greek yogurt to increase protein.",
            "Add berries for fibre and sweetness.",
            "Choose cereal with higher protein and lower added sugar."
        ]
    },
    "Eggs Avocado Toast Plate": {
        "type": "Breakfast",
        "cal": 430, "protein": 28, "carbs": 30, "fibre": 8,
        "gi": "Low-Moderate",
        "when": "Good filling breakfast, especially on active days.",
        "prep_servings": 1,
        "ingredients": {
            "Eggs": {"qty": 2, "unit": "whole"},
            "Egg whites": {"qty": 120, "unit": "g"},
            "Avocado": {"qty": 50, "unit": "g"},
            "Whole grain toast": {"qty": 1, "unit": "slice"},
            "Spinach": {"qty": 60, "unit": "g"}
        },
        "steps": [
            "Measure avocado to 50g.",
            "Use 1 slice toast, not 2, unless training day needs more carbs.",
            "Add spinach or vegetables for volume.",
            "Cook with spray or measured oil."
        ]
    },
    "Chicken Konjac Rice Bowl": {
        "type": "Lunch",
        "cal": 480, "protein": 48, "carbs": 24, "fibre": 10,
        "gi": "Low",
        "when": "Great lunch or dinner for fat loss and blood sugar stability.",
        "prep_servings": 4,
        "ingredients": {
            "Chicken breast": {"qty": 680, "unit": "g"},
            "Konjac rice": {"qty": 800, "unit": "g"},
            "Broccoli": {"qty": 500, "unit": "g"},
            "Bell peppers": {"qty": 300, "unit": "g"},
            "Olive oil": {"qty": 20, "unit": "g"}
        },
        "steps": [
            "Weigh chicken cooked or raw consistently.",
            "Rinse konjac rice very well, then dry-pan before mixing.",
            "Measure oil with a teaspoon or scale.",
            "Split into 4 containers."
        ]
    },
    "Salmon Veg Sweet Potato": {
        "type": "Dinner",
        "cal": 560, "protein": 42, "carbs": 38, "fibre": 8,
        "gi": "Moderate",
        "when": "Best after training or on days with higher activity.",
        "prep_servings": 3,
        "ingredients": {
            "Salmon fillets": {"qty": 450, "unit": "g"},
            "Sweet potato": {"qty": 450, "unit": "g"},
            "Green beans": {"qty": 450, "unit": "g"},
            "Olive oil": {"qty": 18, "unit": "g"}
        },
        "steps": [
            "Keep sweet potato at about 150g per serving.",
            "Pair carb with salmon and vegetables.",
            "Measure oil before roasting.",
            "Avoid sugary glazes."
        ]
    },
    "Turkey Konjac Noodle Stir Fry": {
        "type": "Dinner",
        "cal": 470, "protein": 45, "carbs": 22, "fibre": 9,
        "gi": "Low",
        "when": "Good dinner when you want noodles without a heavy carb load.",
        "prep_servings": 4,
        "ingredients": {
            "Lean ground turkey": {"qty": 680, "unit": "g"},
            "Konjac noodles": {"qty": 800, "unit": "g"},
            "Mixed stir fry vegetables": {"qty": 700, "unit": "g"},
            "Low sodium soy sauce": {"qty": 60, "unit": "ml"},
            "Sesame oil": {"qty": 16, "unit": "g"}
        },
        "steps": [
            "Rinse and dry-pan konjac noodles.",
            "Cook turkey fully and drain if needed.",
            "Measure sesame oil carefully.",
            "Add vegetables for volume and fibre."
        ]
    },
    "Shrimp Konjac Rice Bowl": {
        "type": "Lunch",
        "cal": 430, "protein": 44, "carbs": 20, "fibre": 8,
        "gi": "Low",
        "when": "Good lighter lunch or dinner, especially on rest days.",
        "prep_servings": 3,
        "ingredients": {
            "Shrimp": {"qty": 540, "unit": "g"},
            "Konjac rice": {"qty": 600, "unit": "g"},
            "Zucchini": {"qty": 300, "unit": "g"},
            "Spinach": {"qty": 180, "unit": "g"},
            "Avocado": {"qty": 120, "unit": "g"}
        },
        "steps": [
            "Weigh shrimp after thawing and draining.",
            "Add konjac rice for volume.",
            "Measure avocado to control calories.",
            "Season without sugary sauces."
        ]
    },
    "Chicken Shawarma Bowl": {
        "type": "Lunch",
        "cal": 520, "protein": 50, "carbs": 32, "fibre": 9,
        "gi": "Low-Moderate",
        "when": "Good high-protein meal. Use more vegetables and less wrap/rice on rest days.",
        "prep_servings": 4,
        "ingredients": {
            "Chicken breast": {"qty": 720, "unit": "g"},
            "Cucumber": {"qty": 300, "unit": "g"},
            "Tomatoes": {"qty": 300, "unit": "g"},
            "Lettuce": {"qty": 300, "unit": "g"},
            "Greek yogurt sauce": {"qty": 240, "unit": "g"},
            "Low carb wrap": {"qty": 4, "unit": "wraps"}
        },
        "steps": [
            "Use yogurt sauce instead of heavy creamy sauces.",
            "Keep wrap to one serving.",
            "Add extra lettuce/cucumber for volume.",
            "Use chicken as the anchor protein."
        ]
    },
    "Tuna Egg Salad Plate": {
        "type": "Lunch",
        "cal": 420, "protein": 42, "carbs": 18, "fibre": 7,
        "gi": "Low",
        "when": "Good low-carb lunch or rest-day meal.",
        "prep_servings": 2,
        "ingredients": {
            "Tuna in water": {"qty": 240, "unit": "g"},
            "Eggs": {"qty": 4, "unit": "whole"},
            "Greek yogurt": {"qty": 80, "unit": "g"},
            "Celery": {"qty": 120, "unit": "g"},
            "Cucumber": {"qty": 200, "unit": "g"},
            "Lettuce": {"qty": 200, "unit": "g"}
        },
        "steps": [
            "Use Greek yogurt instead of lots of mayo.",
            "Serve over lettuce and cucumber.",
            "Measure any added dressing.",
            "Add one fruit only if needed around workout."
        ]
    },
    "Apple Peanut Butter Protein Snack": {
        "type": "Snack",
        "cal": 260, "protein": 12, "carbs": 28, "fibre": 6,
        "gi": "Low-Moderate",
        "when": "Good pre-workout snack or afternoon snack. Measure peanut butter.",
        "prep_servings": 1,
        "ingredients": {
            "Green apple": {"qty": 1, "unit": "medium"},
            "Peanut butter": {"qty": 16, "unit": "g"},
            "Greek yogurt": {"qty": 100, "unit": "g"}
        },
        "steps": [
            "Use one medium green apple.",
            "Measure peanut butter at 16g.",
            "Pair with Greek yogurt for more protein.",
            "Avoid adding honey or caramel."
        ]
    },
    "Kiwi Cottage Cheese Bowl": {
        "type": "Snack",
        "cal": 240, "protein": 25, "carbs": 22, "fibre": 4,
        "gi": "Low",
        "when": "Good snack or light breakfast.",
        "prep_servings": 1,
        "ingredients": {
            "Cottage cheese": {"qty": 200, "unit": "g"},
            "Kiwi": {"qty": 1, "unit": "whole"},
            "Chia seeds": {"qty": 8, "unit": "g"}
        },
        "steps": [
            "Measure cottage cheese.",
            "Use one kiwi.",
            "Add chia for fibre.",
            "Keep it simple; no syrup needed."
        ]
    }
}

LIMITED_FOODS = {
    "Banana": "Best pre-workout or post-workout with Greek yogurt or protein. Choose half or small banana. Avoid alone late at night.",
    "Mango": "Best after intense lower-body/cardio training in a small serving, paired with protein. Avoid juice or large bowls.",
    "Pineapple": "Best post-workout in a controlled portion with Greek yogurt or cottage cheese. Avoid fasted or as juice.",
    "Grapes": "Use a small measured handful after activity or paired with nuts/protein. Avoid mindless snacking.",
    "Watermelon": "Use small portions on hot/active days with protein. Avoid large bowls alone.",
    "Dried fruit": "Use rarely and only measured, preferably around training. Easy to overeat and spike sugars.",
    "Fruit juice": "Avoid as default. If used for low blood sugar concerns, follow clinician guidance."
}

WORKOUT_WEEK = {
    "Monday": {
        "title": "Glutes + Lower Body Strength",
        "focus": "Glute growth, legs, strength",
        "exercises": [
            ["Hip Thrust", 4, 10, 55, "https://www.youtube.com/results?search_query=hip+thrust+proper+form"],
            ["Goblet Squat", 3, 10, 25, "https://www.youtube.com/results?search_query=goblet+squat+proper+form"],
            ["Romanian Deadlift", 3, 10, 35, "https://www.youtube.com/results?search_query=dumbbell+romanian+deadlift+proper+form"],
            ["Cable or Band Kickback", 3, 12, 10, "https://www.youtube.com/results?search_query=glute+kickback+proper+form"],
            ["Incline Walk", 1, 25, 0, "https://www.youtube.com/results?search_query=treadmill+incline+walking+fat+loss"]
        ]
    },
    "Tuesday": {
        "title": "Upper Body + Core",
        "focus": "Arms, back, shoulders, core",
        "exercises": [
            ["Lat Pulldown", 3, 10, 40, "https://www.youtube.com/results?search_query=lat+pulldown+proper+form"],
            ["Seated Row", 3, 10, 35, "https://www.youtube.com/results?search_query=seated+row+proper+form"],
            ["Dumbbell Shoulder Press", 3, 10, 15, "https://www.youtube.com/results?search_query=dumbbell+shoulder+press+proper+form"],
            ["Triceps Pressdown", 3, 12, 20, "https://www.youtube.com/results?search_query=tricep+pressdown+proper+form"],
            ["Dead Bug", 3, 12, 0, "https://www.youtube.com/results?search_query=dead+bug+exercise+proper+form"]
        ]
    },
    "Wednesday": {
        "title": "Cardio + Core",
        "focus": "Fat loss, stamina, waist/core strength",
        "exercises": [
            ["Incline Walk", 1, 35, 0, "https://www.youtube.com/results?search_query=treadmill+incline+walking+fat+loss"],
            ["Plank", 3, 30, 0, "https://www.youtube.com/results?search_query=plank+proper+form"],
            ["Cable Woodchop", 3, 12, 15, "https://www.youtube.com/results?search_query=cable+woodchop+proper+form"],
            ["Bird Dog", 3, 10, 0, "https://www.youtube.com/results?search_query=bird+dog+exercise+proper+form"]
        ]
    },
    "Thursday": {
        "title": "Glutes + Hamstrings",
        "focus": "Glute growth, posterior chain",
        "exercises": [
            ["Leg Press", 4, 10, 90, "https://www.youtube.com/results?search_query=leg+press+proper+form"],
            ["Dumbbell Romanian Deadlift", 3, 10, 35, "https://www.youtube.com/results?search_query=dumbbell+romanian+deadlift+proper+form"],
            ["Bulgarian Split Squat", 3, 8, 15, "https://www.youtube.com/results?search_query=bulgarian+split+squat+proper+form"],
            ["Hip Abduction Machine", 3, 15, 35, "https://www.youtube.com/results?search_query=hip+abduction+machine+proper+form"],
            ["Stairmaster", 1, 15, 0, "https://www.youtube.com/results?search_query=stairmaster+workout+beginner"]
        ]
    },
    "Friday": {
        "title": "Upper Body Tone + Cardio",
        "focus": "Arms, back, shoulders, fat loss",
        "exercises": [
            ["Assisted Push Up", 3, 8, 0, "https://www.youtube.com/results?search_query=incline+push+up+proper+form"],
            ["Dumbbell Row", 3, 10, 20, "https://www.youtube.com/results?search_query=dumbbell+row+proper+form"],
            ["Bicep Curl", 3, 12, 10, "https://www.youtube.com/results?search_query=dumbbell+bicep+curl+proper+form"],
            ["Lateral Raise", 3, 12, 8, "https://www.youtube.com/results?search_query=dumbbell+lateral+raise+proper+form"],
            ["Bike or Elliptical", 1, 25, 0, "https://www.youtube.com/results?search_query=elliptical+cardio+workout+beginner"]
        ]
    },
    "Saturday": {
        "title": "Active Recovery",
        "focus": "Steps, mobility, light cardio",
        "exercises": [
            ["Outdoor Walk", 1, 45, 0, "https://www.youtube.com/results?search_query=walking+for+fat+loss"],
            ["Glute Bridge", 3, 15, 0, "https://www.youtube.com/results?search_query=glute+bridge+proper+form"],
            ["Stretching", 1, 15, 0, "https://www.youtube.com/results?search_query=full+body+stretching+routine"]
        ]
    },
    "Sunday": {
        "title": "Rest + Prep",
        "focus": "Recovery, meal prep, gentle steps",
        "exercises": [
            ["Gentle Walk", 1, 25, 0, "https://www.youtube.com/results?search_query=gentle+walk+recovery"],
            ["Mobility", 1, 10, 0, "https://www.youtube.com/results?search_query=beginner+mobility+routine"]
        ]
    }
}

SYMPTOMS = {
    "Excessive thirst": "Hydrate and review recent high-carb/salty meals. If persistent, discuss with your clinician.",
    "Frequent urination": "Track timing and hydration. If persistent or severe, seek medical advice.",
    "Shakiness": "Do not ignore. If you use glucose monitoring, check your level. Pair carbs with protein and follow clinician guidance.",
    "Dizziness": "Pause activity, hydrate, and eat balanced food if needed. Seek help if severe or recurring.",
    "Blurred vision": "Take seriously if new, severe, or recurrent. Consider medical advice.",
    "Extreme fatigue": "Review sleep, meals, hydration, and training load. Persistent fatigue should be discussed with a provider.",
    "Headache": "Hydrate, check meal timing, and avoid skipping meals around workouts.",
    "Nausea": "Avoid intense workouts while feeling unwell. Seek advice if severe or repeated."
}

SMART_GROCERY = {
    "Proteins": ["Chicken breast", "Salmon", "White fish", "Shrimp", "Lean ground turkey", "Eggs", "Egg whites", "Tuna in water", "Greek yogurt", "Cottage cheese", "Protein powder"],
    "Low sugar fruits": ["Strawberries", "Blueberries", "Raspberries", "Blackberries", "Green apples", "Kiwi", "Grapefruit", "Pear", "Cherries"],
    "Caution fruits": list(LIMITED_FOODS.keys()),
    "Vegetables": ["Broccoli", "Spinach", "Lettuce", "Cucumber", "Tomatoes", "Zucchini", "Green beans", "Bell peppers", "Celery", "Cauliflower"],
    "Smart carbs": ["Konjac rice", "Konjac noodles", "Rolled oats", "Sweet potato", "Low carb wrap", "Whole grain toast", "High protein low sugar cereal"],
    "Fats and extras": ["Avocado", "Peanut butter", "Olive oil", "Chia seeds", "Low sodium soy sauce", "Greek yogurt sauce"]
}

def default_data():
    week = {}
    for d in DAYS:
        week[d] = {m: "" for m in MEAL_TYPES}
    return {
        "profile": PROFILE_DEFAULT.copy(),
        "weekly_plan": week,
        "manual_foods": [],
        "manual_grocery": [],
        "grocery_checked": {},
        "workout_logs": {},
        "daily_logs": {},
        "symptom_logs": [],
        "weight_logs": [],
        "settings": {}
    }

def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            base = default_data()
            deep_merge(base, loaded)
            return base
        except Exception:
            return default_data()
    return default_data()

def deep_merge(base, incoming):
    for k, v in incoming.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, indent=2)

def init():
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    if "page" not in st.session_state:
        st.session_state.page = "Home"

def today_str():
    return date.today().isoformat()

def day_name_from_date(ds):
    return datetime.strptime(ds, "%Y-%m-%d").strftime("%A")

def get_week_start(dt=None):
    dt = dt or date.today()
    return dt - timedelta(days=dt.weekday())

def meal_totals_for_date(ds):
    data = st.session_state.data
    day = day_name_from_date(ds)
    totals = {"cal": 0, "protein": 0, "carbs": 0, "fibre": 0}
    plan = data["weekly_plan"].get(day, {})
    for mt, meal_name in plan.items():
        if meal_name in MEALS:
            for k in totals:
                totals[k] += MEALS[meal_name].get(k, 0)
    for item in data["manual_foods"]:
        if item.get("date") == ds:
            for k in totals:
                totals[k] += float(item.get(k, 0) or 0)
    return totals

def weekly_grocery_totals():
    data = st.session_state.data
    totals = {}
    for d in DAYS:
        for mt, meal_name in data["weekly_plan"].get(d, {}).items():
            if meal_name in MEALS:
                meal = MEALS[meal_name]
                servings = meal.get("prep_servings", 1)
                for ing, q in meal["ingredients"].items():
                    key = (ing, q["unit"])
                    totals[key] = totals.get(key, 0) + q["qty"]
    for item in data["manual_grocery"]:
        key = (item["name"], item.get("unit", "item"))
        totals[key] = totals.get(key, 0) + float(item.get("qty", 1) or 1)
    return totals

def bmi(weight_lb, height_in=69):
    return round((weight_lb / (height_in * height_in)) * 703, 1)

def bmi_label(v):
    if v < 18.5: return "Underweight"
    if v < 25: return "Normal"
    if v < 30: return "Overweight"
    return "Obesity range"

def safe_df(rows):
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)

def card(text):
    st.markdown(f"<div class='gf-card'>{text}</div>", unsafe_allow_html=True)

def css():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
      html, body, [class*="css"] {font-family: Inter, sans-serif;}
      .stApp {background: radial-gradient(circle at 20% 10%, #35213f 0, #0e1018 40%, #090a0f 100%); color: #f7eef7;}
      section[data-testid="stSidebar"] {background: #11131c;}
      .gf-title {font-size: 42px; font-weight: 800; line-height: 1.1; margin-bottom: 6px;}
      .gf-sub {color: #c9bbc9; font-size: 16px;}
      .gf-card {background: rgba(255,255,255,0.075); border: 1px solid rgba(255,255,255,0.12); border-radius: 22px; padding: 18px; margin: 10px 0;}
      .gf-pill {display:inline-block; background: rgba(255, 158, 209, .18); border:1px solid rgba(255,158,209,.28); border-radius:99px; padding:6px 11px; margin:3px; color:#ffe3f3; font-weight:600;}
      .small {color:#c9bbc9; font-size:13px;}
      .good {color:#9ef0b2; font-weight:700;}
      .warn {color:#ffd17d; font-weight:700;}
      .bad {color:#ff9ba3; font-weight:700;}
      button[kind="secondary"] {border-radius: 12px;}
    </style>
    """, unsafe_allow_html=True)

init()
css()
data = st.session_state.data

st.sidebar.markdown("<h1>GlowFit</h1>", unsafe_allow_html=True)
st.sidebar.caption("Prediabetes-aware | fat loss | glute growth")

page = st.sidebar.radio(
    "Dashboard",
    ["Home", "Meals", "Weekly Plan", "Grocery", "Workouts", "Progress", "Blood Sugar", "Settings / Backup"],
    index=["Home", "Meals", "Weekly Plan", "Grocery", "Workouts", "Progress", "Blood Sugar", "Settings / Backup"].index(st.session_state.page)
)
st.session_state.page = page

if page == "Home":
    st.markdown("<div class='gf-title'>Today Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='gf-sub'>A linked daily view for food, workouts, steps, water, and blood sugar awareness.</div>", unsafe_allow_html=True)
    prof = data["profile"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current weight", f"{prof['current_weight']} lb")
    c2.metric("Goal", f"Under {prof['goal_weight'] + 1:.0f} lb")
    c3.metric("BMI", bmi(prof["current_weight"], prof["height_in"]))
    c4.metric("Protein target", f"{prof['protein_target']} g")
    training = st.toggle("Training day today", value=prof.get("training_day", True))
    if training != prof.get("training_day"):
        prof["training_day"] = training
        save_data()
    cal_target = prof["calorie_training"] if training else prof["calorie_rest"]
    carb_target = prof["carb_training"] if training else prof["carb_rest"]
    st.info(f"Today target: {cal_target} calories, {prof['protein_target']}g protein, about {carb_target}g carbs. Training/rest toggle changes these targets across the app.")
    ds = today_str()
    totals = meal_totals_for_date(ds)
    cols = st.columns(4)
    cols[0].metric("Calories logged", int(totals["cal"]), f"target {cal_target}")
    cols[1].metric("Protein", f"{int(totals['protein'])} g", f"target {prof['protein_target']}g")
    cols[2].metric("Carbs", f"{int(totals['carbs'])} g", f"target {carb_target}g")
    cols[3].metric("Fibre", f"{int(totals['fibre'])} g")
    st.divider()
    st.subheader("Quick daily log")
    dl = data["daily_logs"].setdefault(ds, {"water_l": 0.0, "steps": 0, "notes": ""})
    with st.form("daily_log_form"):
        water = st.number_input("Water today (L)", min_value=0.0, step=0.25, value=float(dl.get("water_l", 0.0)))
        steps = st.number_input("Steps today", min_value=0, step=500, value=int(dl.get("steps", 0)))
        notes = st.text_area("Notes", value=dl.get("notes", ""))
        if st.form_submit_button("Save daily log"):
            dl["water_l"] = water
            dl["steps"] = steps
            dl["notes"] = notes
            save_data()
            st.success("Daily log saved.")

elif page == "Meals":
    st.markdown("<div class='gf-title'>Meal Dashboard</div>", unsafe_allow_html=True)
    selected_date = st.date_input("Select date", value=date.today())
    ds = selected_date.isoformat()
    day = day_name_from_date(ds)
    st.caption(f"Showing planned and manual foods for {day}, {ds}")
    totals = meal_totals_for_date(ds)
    st.success(f"Calories {int(totals['cal'])} | Protein {int(totals['protein'])}g | Carbs {int(totals['carbs'])}g | Fibre {int(totals['fibre'])}g")
    st.subheader("Planned + manual foods by meal")
    plan = data["weekly_plan"].get(day, {})
    for mt in MEAL_TYPES:
        st.markdown(f"### {mt}")
        meal_name = plan.get(mt, "")
        if meal_name and meal_name in MEALS:
            m = MEALS[meal_name]
            card(f"<b>{meal_name}</b><br>{m['cal']} cal | {m['protein']}g protein | {m['carbs']}g carbs | GI: {m['gi']}<br><span class='small'>{m['when']}</span>")
        else:
            st.caption("No planned meal for this slot yet.")
        manual = [x for x in data["manual_foods"] if x.get("date") == ds and x.get("meal_type") == mt]
        for i, item in enumerate(manual):
            st.write(f"- {item['name']}: {item.get('cal',0)} cal, {item.get('protein',0)}g protein, {item.get('carbs',0)}g carbs")
    st.divider()
    st.subheader("Add manual food")
    with st.form("manual_food_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Food name")
        meal_type = c2.selectbox("Meal type", MEAL_TYPES)
        c3, c4, c5, c6 = st.columns(4)
        cal = c3.number_input("Calories", min_value=0, step=10)
        protein = c4.number_input("Protein g", min_value=0.0, step=1.0)
        carbs = c5.number_input("Carbs g", min_value=0.0, step=1.0)
        fibre = c6.number_input("Fibre g", min_value=0.0, step=1.0)
        add_grocery = st.checkbox("Also add this food/item to grocery list")
        qty = st.number_input("Grocery quantity", min_value=0.0, step=1.0, value=1.0)
        unit = st.text_input("Grocery unit", value="item")
        if st.form_submit_button("Save manual food"):
            if name.strip():
                data["manual_foods"].append({
                    "date": ds, "meal_type": meal_type, "name": name.strip(),
                    "cal": cal, "protein": protein, "carbs": carbs, "fibre": fibre,
                    "created_at": datetime.now().isoformat()
                })
                if add_grocery:
                    data["manual_grocery"].append({"name": name.strip(), "qty": qty, "unit": unit})
                save_data()
                st.success("Manual food saved and linked.")
            else:
                st.warning("Enter a food name first.")
    st.divider()
    st.subheader("Meal database and recipe quantities")
    filt = st.selectbox("Filter by meal type", ["All"] + MEAL_TYPES)
    for meal_name, m in MEALS.items():
        if filt != "All" and m["type"] != filt:
            continue
        with st.expander(meal_name):
            st.write(f"{m['cal']} cal | {m['protein']}g protein | {m['carbs']}g carbs | {m['fibre']}g fibre | GI: {m['gi']}")
            st.write(m["when"])
            st.markdown("**Meal prep ingredients**")
            for ing, q in m["ingredients"].items():
                st.write(f"- {ing}: {q['qty']} {q['unit']} for {m['prep_servings']} serving(s)")
            st.markdown("**Measuring and dishing steps**")
            for s in m["steps"]:
                st.write(f"- {s}")

elif page == "Weekly Plan":
    st.markdown("<div class='gf-title'>Weekly Meal Plan</div>", unsafe_allow_html=True)
    st.caption("Selections here automatically populate the daily Meal Dashboard and the Grocery list.")
    names_by_type = {mt: [""] + [n for n, m in MEALS.items() if m["type"] == mt] for mt in MEAL_TYPES}
    for d in DAYS:
        st.markdown(f"### {d}")
        cols = st.columns(4)
        for idx, mt in enumerate(MEAL_TYPES):
            current = data["weekly_plan"].setdefault(d, {}).get(mt, "")
            options = names_by_type[mt]
            if current not in options:
                current = ""
            choice = cols[idx].selectbox(mt, options, index=options.index(current), key=f"wp_{d}_{mt}")
            if choice != data["weekly_plan"][d].get(mt, ""):
                data["weekly_plan"][d][mt] = choice
                save_data()
    st.success("Weekly plan autosaves. Grocery list updates from this plan.")

elif page == "Grocery":
    st.markdown("<div class='gf-title'>Smart Grocery</div>", unsafe_allow_html=True)
    st.caption("This combines weekly plan ingredients, manual food items, and smart selectable groceries.")
    st.subheader("Auto-populated from weekly plan + manual foods")
    totals = weekly_grocery_totals()
    if not totals:
        st.info("No grocery items yet. Add meals in Weekly Plan or manual foods in Meals.")
    for (name, unit), qty in sorted(totals.items()):
        key = f"grocery_auto_{name}_{unit}"
        checked = data["grocery_checked"].get(key, False)
        new = st.checkbox(f"{name}: {round(qty, 1)} {unit}", value=checked, key=key)
        if new != checked:
            data["grocery_checked"][key] = new
            save_data()
    st.divider()
    st.subheader("Smart grocery options")
    st.caption("Select items you want available; these can guide meals and recipes.")
    for cat, items in SMART_GROCERY.items():
        with st.expander(cat):
            for item in items:
                key = f"smart_{cat}_{item}"
                current = data["grocery_checked"].get(key, False)
                new = st.checkbox(item, value=current, key=key)
                if new != current:
                    data["grocery_checked"][key] = new
                    if new:
                        data["manual_grocery"].append({"name": item, "qty": 1, "unit": "item"})
                    save_data()
    st.divider()
    st.subheader("Meal ideas based on selected grocery")
    selected_items = [k.split("_", 2)[-1] for k, v in data["grocery_checked"].items() if k.startswith("smart_") and v]
    if not selected_items:
        st.caption("Select grocery options to see matching meal ideas.")
    else:
        for meal_name, m in MEALS.items():
            match = [ing for ing in m["ingredients"] if any(sel.lower() in ing.lower() or ing.lower() in sel.lower() for sel in selected_items)]
            if match:
                st.write(f"- {meal_name} matches: {', '.join(match)}")

elif page == "Workouts":
    st.markdown("<div class='gf-title'>Workout Dashboard</div>", unsafe_allow_html=True)
    st.caption("Remaining days are shown first. Past/completed days move lower. Set-by-set progress saves.")
    week_start = get_week_start()
    today_idx = date.today().weekday()
    week_key = week_start.isoformat()
    logs = data["workout_logs"].setdefault(week_key, {})
    st.write(f"Workout week starting {week_key}")
    def render_day(d, previous=False):
        wk = WORKOUT_WEEK[d]
        day_log = logs.setdefault(d, {"completed": False, "rating": 0, "notes": "", "sets": {}})
        st.markdown(f"### {d}: {wk['title']}")
        st.caption(wk["focus"])
        for ex_name, sets, reps, weight, link in wk["exercises"]:
            with st.expander(ex_name, expanded=not previous):
                st.link_button("Form video/search", link)
                day_log["sets"].setdefault(ex_name, [])
                while len(day_log["sets"][ex_name]) < sets:
                    day_log["sets"][ex_name].append({"done": False, "weight": weight, "reps": reps})
                for sidx in range(sets):
                    row = day_log["sets"][ex_name][sidx]
                    c1, c2, c3, c4 = st.columns([1,2,2,2])
                    done = c1.checkbox(f"Set {sidx+1}", value=bool(row.get("done", False)), key=f"{week_key}_{d}_{ex_name}_{sidx}_done")
                    wt = c2.number_input("Weight", min_value=0.0, step=2.5, value=float(row.get("weight", weight)), key=f"{week_key}_{d}_{ex_name}_{sidx}_wt")
                    rp = c3.number_input("Reps/min", min_value=0, step=1, value=int(row.get("reps", reps)), key=f"{week_key}_{d}_{ex_name}_{sidx}_rp")
                    c4.write("Saved")
                    if done != row.get("done") or wt != row.get("weight") or rp != row.get("reps"):
                        row["done"] = done
                        row["weight"] = wt
                        row["reps"] = rp
                        save_data()
        rating = st.slider(f"{d} workout rating", 0, 10, int(day_log.get("rating", 0)), key=f"rating_{week_key}_{d}")
        notes = st.text_area(f"{d} notes", value=day_log.get("notes",""), key=f"notes_{week_key}_{d}")
        complete = st.checkbox(f"Mark {d} complete", value=bool(day_log.get("completed", False)), key=f"complete_{week_key}_{d}")
        if rating != day_log.get("rating") or notes != day_log.get("notes") or complete != day_log.get("completed"):
            day_log["rating"] = rating
            day_log["notes"] = notes
            day_log["completed"] = complete
            save_data()
    st.subheader("Remaining this week")
    for i, d in enumerate(DAYS):
        if i >= today_idx and not logs.get(d, {}).get("completed", False):
            render_day(d, previous=False)
    st.divider()
    st.subheader("Previous or completed")
    for i, d in enumerate(DAYS):
        if i < today_idx or logs.get(d, {}).get("completed", False):
            render_day(d, previous=True)

elif page == "Progress":
    st.markdown("<div class='gf-title'>Progress</div>", unsafe_allow_html=True)
    prof = data["profile"]
    st.subheader("BMI and weight")
    with st.form("weight_form"):
        wt = st.number_input("Current weight lb", min_value=50.0, max_value=500.0, value=float(prof["current_weight"]), step=0.5)
        if st.form_submit_button("Save weight/progress"):
            prof["current_weight"] = wt
            data["weight_logs"].append({"date": today_str(), "weight": wt, "bmi": bmi(wt, prof["height_in"])})
            save_data()
            st.success("Weight saved.")
    current_bmi = bmi(prof["current_weight"], prof["height_in"])
    c1, c2, c3 = st.columns(3)
    c1.metric("BMI", current_bmi)
    c2.metric("BMI category", bmi_label(current_bmi))
    c3.metric("To under 200", f"{max(0, prof['current_weight'] - prof['goal_weight']):.1f} lb")
    rows = data["weight_logs"]
    if rows:
        df = safe_df(rows)
        df["date"] = pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date")[["weight", "bmi"]])
    else:
        st.info("No weight history yet.")
    st.subheader("Food and habit trends")
    day_rows = []
    for ds, dl in data["daily_logs"].items():
        totals = meal_totals_for_date(ds)
        day_rows.append({"date": ds, "calories": totals["cal"], "protein": totals["protein"], "carbs": totals["carbs"], "water_l": dl.get("water_l", 0), "steps": dl.get("steps", 0)})
    if day_rows:
        df = safe_df(day_rows)
        df["date"] = pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date")[["calories", "protein", "carbs", "water_l", "steps"]])
    else:
        st.info("No daily trend data yet.")

elif page == "Blood Sugar":
    st.markdown("<div class='gf-title'>Blood Sugar Awareness</div>", unsafe_allow_html=True)
    st.warning("This is an awareness tool, not a diagnosis or emergency tool. Use targets from your clinician.")
    with st.form("symptoms_form"):
        ds = st.date_input("Date", value=date.today()).isoformat()
        selected = st.multiselect("Select symptoms felt", list(SYMPTOMS.keys()))
        notes = st.text_area("Notes/context")
        if st.form_submit_button("Save symptom log"):
            data["symptom_logs"].append({"date": ds, "symptoms": selected, "notes": notes, "created_at": datetime.now().isoformat()})
            save_data()
            st.success("Symptoms saved.")
    if selected:
        st.subheader("Tips based on selected symptoms")
        for s in selected:
            st.write(f"- {s}: {SYMPTOMS[s]}")
    st.subheader("Symptom history")
    if data["symptom_logs"]:
        st.dataframe(safe_df(data["symptom_logs"]), use_container_width=True)
    else:
        st.caption("No symptom logs yet.")

elif page == "Settings / Backup":
    st.markdown("<div class='gf-title'>Settings / Backup</div>", unsafe_allow_html=True)
    prof = data["profile"]
    with st.form("profile_form"):
        c1, c2, c3 = st.columns(3)
        height = c1.number_input("Height inches", min_value=48, max_value=84, value=int(prof["height_in"]))
        start = c2.number_input("Start weight", min_value=50.0, max_value=500.0, value=float(prof["start_weight"]))
        current = c3.number_input("Current weight", min_value=50.0, max_value=500.0, value=float(prof["current_weight"]))
        c4, c5, c6 = st.columns(3)
        protein = c4.number_input("Protein target g", min_value=40, max_value=250, value=int(prof["protein_target"]))
        cal_train = c5.number_input("Training day calories", min_value=1000, max_value=3500, value=int(prof["calorie_training"]))
        cal_rest = c6.number_input("Rest day calories", min_value=1000, max_value=3500, value=int(prof["calorie_rest"]))
        c7, c8 = st.columns(2)
        carb_train = c7.number_input("Training day carbs g", min_value=40, max_value=300, value=int(prof["carb_training"]))
        carb_rest = c8.number_input("Rest day carbs g", min_value=40, max_value=300, value=int(prof["carb_rest"]))
        if st.form_submit_button("Save settings"):
            prof.update({"height_in": height, "start_weight": start, "current_weight": current, "protein_target": protein, "calorie_training": cal_train, "calorie_rest": cal_rest, "carb_training": carb_train, "carb_rest": carb_rest})
            save_data()
            st.success("Settings saved.")
    st.subheader("Backup")
    st.download_button("Download backup JSON", data=json.dumps(data, indent=2), file_name="glowfit_backup.json", mime="application/json")
    up = st.file_uploader("Restore backup JSON", type=["json"])
    if up is not None:
        try:
            restored = json.load(up)
            st.session_state.data = restored
            save_data()
            st.success("Backup restored. Refresh if needed.")
        except Exception as e:
            st.error(f"Could not restore backup: {e}")
    if st.button("Reset all data"):
        st.session_state.data = default_data()
        save_data()
        st.warning("All app data reset.")
