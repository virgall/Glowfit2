import json
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

APP_TITLE = "GlowFit"
DATA_FILE = Path(__file__).with_name("glowfit_data.json")
HEIGHT_IN = 69
START_WEIGHT = 224.0
GOAL_WEIGHT = 199.0
PROTEIN_TARGET = 140

MEALS = {
    "Greek Yogurt Berry Crunch Bowl": {
        "type": ["Breakfast", "Snack"], "servings": 1, "cal": 360, "protein": 38, "carbs": 34, "fiber": 9,
        "gi": "Low", "timing": "Any day; great breakfast or evening sweet craving swap.",
        "ingredients": {"Greek yogurt 0-2% (g)": 250, "berries (g)": 120, "chia seeds (tbsp)": 1, "high-protein low-sugar cereal (g)": 25},
        "steps": ["Weigh yogurt in grams.", "Measure berries and cereal separately.", "Add chia last; let sit 5 minutes for fullness."],
    },
    "Protein Oats + Berries": {
        "type": ["Breakfast", "Pre-workout"], "servings": 1, "cal": 410, "protein": 35, "carbs": 45, "fiber": 8,
        "gi": "Moderate", "timing": "Best on training mornings or 1-2 hours before lifting/cardio.",
        "ingredients": {"rolled oats dry (g)": 40, "protein powder (scoop)": 1, "berries (g)": 100, "cinnamon (tsp)": 1, "unsweetened almond milk (ml)": 200},
        "steps": ["Weigh oats dry before cooking.", "Cook with almond milk and cinnamon.", "Stir protein in after cooking to avoid clumps."],
    },
    "Egg + Avocado Toast Plate": {
        "type": ["Breakfast", "Lunch"], "servings": 1, "cal": 430, "protein": 28, "carbs": 28, "fiber": 9,
        "gi": "Moderate", "timing": "Good on training or rest days; keep bread measured.",
        "ingredients": {"eggs": 2, "egg whites (ml)": 120, "whole grain toast slice": 1, "avocado (g)": 50, "spinach (g)": 50},
        "steps": ["Measure avocado by grams, not eyeballing.", "Use one toast slice unless it is a heavy training day.", "Add spinach/veg for volume."],
    },
    "High-Protein Cereal Bowl": {
        "type": ["Breakfast", "Post-workout"], "servings": 1, "cal": 380, "protein": 35, "carbs": 38, "fiber": 8,
        "gi": "Moderate", "timing": "Best at breakfast or after training; avoid as late-night oversized snack.",
        "ingredients": {"high-protein low-sugar cereal (g)": 45, "Greek yogurt 0-2% (g)": 200, "berries (g)": 80, "chia seeds (tbsp)": 1},
        "steps": ["Weigh cereal in grams; cereal portions are easy to overpour.", "Use Greek yogurt for protein instead of only milk.", "Add berries for sweetness and fibre."],
    },
    "Chicken Konjac Rice Bowl": {
        "type": ["Lunch", "Dinner"], "servings": 4, "cal": 430, "protein": 46, "carbs": 22, "fiber": 9,
        "gi": "Low", "timing": "Excellent rest-day or training-day fat-loss meal; add sweet potato if needed post-workout.",
        "ingredients": {"chicken breast raw (g)": 700, "konjac rice packs": 4, "mixed vegetables (g)": 800, "olive oil (tbsp)": 2, "low-sugar sauce (tbsp)": 4},
        "steps": ["Cook chicken, then divide total cooked weight by 4 containers.", "Rinse konjac rice well and dry-fry 2-3 minutes.", "Measure oil/sauce because they add calories quickly."],
    },
    "Salmon Veg + Sweet Potato": {
        "type": ["Lunch", "Dinner", "Post-workout"], "servings": 4, "cal": 520, "protein": 38, "carbs": 35, "fiber": 8,
        "gi": "Moderate", "timing": "Best post-workout or active days; keep sweet potato controlled on rest days.",
        "ingredients": {"salmon fillet raw (g)": 680, "sweet potato raw (g)": 600, "broccoli/asparagus (g)": 800, "olive oil (tbsp)": 2},
        "steps": ["Weigh sweet potato raw before roasting.", "Divide into 4 equal containers.", "Pair carb with salmon and veggies for steadier glucose."],
    },
    "Chicken Konjac Noodle Stir Fry": {
        "type": ["Lunch", "Dinner"], "servings": 4, "cal": 390, "protein": 44, "carbs": 18, "fiber": 8,
        "gi": "Low", "timing": "Great for fat loss and blood sugar stability.",
        "ingredients": {"chicken breast raw (g)": 700, "konjac noodles packs": 4, "stir fry vegetables (g)": 900, "sesame/olive oil (tbsp)": 2, "soy/teriyaki low sugar (tbsp)": 4},
        "steps": ["Rinse noodles very well, then dry-fry before sauce.", "Cook chicken separately for accurate portions.", "Use measured sauce/oil."],
    },
    "Lean Taco Bowl with Konjac Rice": {
        "type": ["Lunch", "Dinner"], "servings": 4, "cal": 460, "protein": 42, "carbs": 28, "fiber": 10,
        "gi": "Low-Moderate", "timing": "Good training-day meal; control beans/corn if glucose sensitive.",
        "ingredients": {"lean ground turkey/chicken (g)": 700, "konjac rice packs": 4, "lettuce (g)": 300, "black beans drained (g)": 240, "salsa (g)": 200, "Greek yogurt 0-2% (g)": 200},
        "steps": ["Measure beans by grams; keep portion moderate.", "Use Greek yogurt instead of sour cream.", "Build plate with lettuce first for volume."],
    },
    "Shrimp Veggie Konjac Noodles": {
        "type": ["Lunch", "Dinner"], "servings": 3, "cal": 350, "protein": 40, "carbs": 17, "fiber": 7,
        "gi": "Low", "timing": "Light dinner or rest-day meal.",
        "ingredients": {"shrimp raw (g)": 600, "konjac noodles packs": 3, "zucchini/bell pepper mix (g)": 700, "olive oil (tbsp)": 1.5, "garlic/ginger sauce (tbsp)": 3},
        "steps": ["Pat shrimp dry before cooking.", "Rinse and dry-fry konjac noodles.", "Divide into 3 equal containers."],
    },
    "Baked Potato Chicken Plate": {
        "type": ["Lunch", "Dinner", "Post-workout"], "servings": 1, "cal": 480, "protein": 45, "carbs": 42, "fiber": 7,
        "gi": "Moderate", "timing": "Best after workouts; choose smaller potato on rest days.",
        "ingredients": {"cooked chicken (g)": 150, "baked potato (g)": 180, "Greek yogurt 0-2% (g)": 80, "steamed vegetables (g)": 250},
        "steps": ["Weigh cooked potato portion.", "Top with Greek yogurt instead of heavy sour cream.", "Eat protein/veg first, then potato."],
    },
    "Tuna Egg Salad Bowl": {
        "type": ["Lunch", "Snack"], "servings": 1, "cal": 360, "protein": 42, "carbs": 16, "fiber": 6,
        "gi": "Low", "timing": "Good quick lunch; low prep.",
        "ingredients": {"tuna can drained": 1, "boiled eggs": 2, "cucumber/lettuce (g)": 250, "light mayo or Greek yogurt (tbsp)": 1.5},
        "steps": ["Drain tuna well.", "Measure dressing.", "Add crunchy vegetables for volume."],
    },
    "Fruit + Protein Snack Plate": {
        "type": ["Snack", "Pre-workout"], "servings": 1, "cal": 240, "protein": 20, "carbs": 25, "fiber": 6,
        "gi": "Low-Moderate", "timing": "Best pre-workout or mid-day; use preferred fruits first.",
        "ingredients": {"Greek yogurt 0-2% (g)": 170, "preferred fruit berries/kiwi/apple (g)": 120, "peanut butter or nuts (tbsp)": 1},
        "steps": ["Choose berries/kiwi/green apple most often.", "Pair fruit with protein/fat.", "Avoid fruit juice."],
    },
}

FRUIT_GUIDE = {
    "Preferred": {
        "Berries": "Low sugar for the volume; great with Greek yogurt or oats.",
        "Green apple": "Good with peanut butter or cheese; avoid juice form.",
        "Kiwi": "Good around workouts; vitamin C and fibre.",
        "Grapefruit": "Often good for low-cal sweetness; check medication interactions if applicable.",
        "Pear": "Fibre-rich; portion one small/medium.",
        "Cherries": "Use controlled portions; better with protein."},
    "Limited but useful timing": {
        "Banana": "Best pre/post-workout. Choose smaller or less ripe; pair with protein/peanut butter.",
        "Mango": "Best after lower-body/cardio days in small portions with Greek yogurt/protein.",
        "Pineapple": "Best post-workout in measured portions; avoid juice.",
        "Grapes": "Best small portion after activity; avoid grazing from a large bowl.",
        "Watermelon": "Best after walks/cardio in small portions with protein/fat nearby."}
}

WORKOUT_PLAN = {
    "Monday": {"focus": "Glutes + Lower Body Strength", "exercises": [
        ("Hip Thrust", 4, 10, 45, "https://www.youtube.com/results?search_query=hip+thrust+proper+form"),
        ("Romanian Deadlift", 3, 10, 25, "https://www.youtube.com/results?search_query=romanian+deadlift+form"),
        ("Leg Press", 3, 12, 90, "https://www.youtube.com/results?search_query=leg+press+form"),
        ("Cable Glute Kickback", 3, 12, 10, "https://www.youtube.com/results?search_query=cable+glute+kickback+form"),
        ("Incline Walk", 1, 25, 0, "https://www.youtube.com/results?search_query=treadmill+incline+walking+fat+loss") ]},
    "Tuesday": {"focus": "Upper Body + Core", "exercises": [
        ("Lat Pulldown", 3, 10, 35, "https://www.youtube.com/results?search_query=lat+pulldown+form"),
        ("Seated Row", 3, 10, 30, "https://www.youtube.com/results?search_query=seated+row+form"),
        ("Dumbbell Shoulder Press", 3, 10, 12, "https://www.youtube.com/results?search_query=dumbbell+shoulder+press+form"),
        ("Triceps Rope Pushdown", 3, 12, 15, "https://www.youtube.com/results?search_query=triceps+rope+pushdown+form"),
        ("Dead Bug", 3, 12, 0, "https://www.youtube.com/results?search_query=dead+bug+core+exercise") ]},
    "Wednesday": {"focus": "Cardio + Core", "exercises": [
        ("Incline Walk", 1, 35, 0, "https://www.youtube.com/results?search_query=incline+walking+workout"),
        ("Stairmaster", 1, 15, 0, "https://www.youtube.com/results?search_query=stairmaster+beginner+workout"),
        ("Plank", 3, 30, 0, "https://www.youtube.com/results?search_query=plank+proper+form"),
        ("Pallof Press", 3, 12, 10, "https://www.youtube.com/results?search_query=pallof+press+form") ]},
    "Thursday": {"focus": "Glutes + Hamstrings", "exercises": [
        ("Bulgarian Split Squat", 3, 10, 10, "https://www.youtube.com/results?search_query=bulgarian+split+squat+form"),
        ("Glute Bridge", 4, 12, 35, "https://www.youtube.com/results?search_query=weighted+glute+bridge+form"),
        ("Hamstring Curl", 3, 12, 30, "https://www.youtube.com/results?search_query=hamstring+curl+machine+form"),
        ("Hip Abduction", 3, 15, 35, "https://www.youtube.com/results?search_query=hip+abduction+machine+form"),
        ("Easy Walk", 1, 20, 0, "https://www.youtube.com/results?search_query=walking+for+fat+loss") ]},
    "Friday": {"focus": "Upper Body + Arms + Core", "exercises": [
        ("Chest Press", 3, 10, 25, "https://www.youtube.com/results?search_query=chest+press+machine+form"),
        ("One Arm Dumbbell Row", 3, 10, 15, "https://www.youtube.com/results?search_query=one+arm+dumbbell+row+form"),
        ("Lateral Raise", 3, 12, 7, "https://www.youtube.com/results?search_query=lateral+raise+form"),
        ("Biceps Curl", 3, 12, 10, "https://www.youtube.com/results?search_query=dumbbell+biceps+curl+form"),
        ("Cable Crunch", 3, 12, 15, "https://www.youtube.com/results?search_query=cable+crunch+form") ]},
    "Saturday": {"focus": "Full Body + Cardio", "exercises": [
        ("Goblet Squat", 3, 12, 20, "https://www.youtube.com/results?search_query=goblet+squat+form"),
        ("Kettlebell Deadlift", 3, 12, 25, "https://www.youtube.com/results?search_query=kettlebell+deadlift+form"),
        ("Step Ups", 3, 10, 10, "https://www.youtube.com/results?search_query=dumbbell+step+up+form"),
        ("Bike or Elliptical", 1, 25, 0, "https://www.youtube.com/results?search_query=elliptical+beginner+workout") ]},
    "Sunday": {"focus": "Rest + Mobility", "exercises": [
        ("Gentle Walk", 1, 30, 0, "https://www.youtube.com/results?search_query=walking+recovery+day"),
        ("Hip Flexor Stretch", 2, 45, 0, "https://www.youtube.com/results?search_query=hip+flexor+stretch"),
        ("Glute Stretch", 2, 45, 0, "https://www.youtube.com/results?search_query=glute+stretch") ]},
}

SYMPTOMS = {
    "Excessive thirst": "Hydrate and consider whether recent meals were high in sugar/refined carbs. If persistent, discuss with clinician.",
    "Frequent urination": "Track timing and hydration. Persistent symptoms deserve medical guidance.",
    "Shakiness/sweating": "Consider whether you under-ate or delayed meals. Pair carbs with protein; seek urgent help if severe.",
    "Dizziness/lightheaded": "Pause exercise, hydrate, and eat balanced food if needed. Seek help if recurring or severe.",
    "Blurred vision": "Do not ignore repeated blurred vision. Consider glucose check and clinician advice.",
    "Unusual fatigue": "Review sleep, calories, hydration, and meal balance. Monitor if it repeats.",
    "Headache": "Hydration, meal timing, and stress may matter. Track pattern.",
    "Nausea/confusion": "If severe, unusual, or paired with very high/low glucose symptoms, seek medical help promptly.",
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

def today_str():
    return date.today().isoformat()

def week_start(d=None):
    d = d or date.today()
    return (d - timedelta(days=d.weekday())).isoformat()

def default_data():
    ws = week_start()
    return {
        "profile": {"height_in": HEIGHT_IN, "start_weight": START_WEIGHT, "goal_weight": GOAL_WEIGHT, "protein_target": PROTEIN_TARGET, "calorie_target_rest": 1650, "calorie_target_training": 1850},
        "settings": {"training_day": True, "current_week": ws},
        "daily": {},
        "weekly_plan": {ws: {day: {mt: "" for mt in MEAL_TYPES} for day in DAYS}},
        "manual_foods": [],
        "workout_logs": {},
        "symptom_logs": [],
        "grocery_checked": {},
        "custom_grocery": [],
    }

def load_data():
    base = default_data()
    if DATA_FILE.exists():
        try:
            loaded = json.loads(DATA_FILE.read_text())
            return merge_defaults(base, loaded)
        except Exception:
            return base
    return base

def merge_defaults(base, loaded):
    if isinstance(base, dict):
        out = deepcopy(base)
        if isinstance(loaded, dict):
            for k, v in loaded.items():
                out[k] = merge_defaults(out.get(k), v) if k in out else v
        return out
    return loaded if loaded is not None else base

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2, default=str))

def get_data():
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    return st.session_state.data

def autosave():
    save_data(st.session_state.data)

def ensure_day(data, ds):
    data["daily"].setdefault(ds, {"weight": None, "calories": 0, "protein": 0, "carbs": 0, "fiber": 0, "water": 0, "steps": 0, "notes": ""})
    return data["daily"][ds]

def ensure_week(data):
    ws = week_start()
    data["settings"]["current_week"] = ws
    data["weekly_plan"].setdefault(ws, {day: {mt: "" for mt in MEAL_TYPES} for day in DAYS})
    return ws

def bmi(weight_lb):
    return round((weight_lb / (HEIGHT_IN ** 2)) * 703, 1) if weight_lb else None

def current_weight(data):
    weights = [(d, v.get("weight")) for d, v in data["daily"].items() if v.get("weight")]
    if weights:
        return sorted(weights)[-1][1]
    return data["profile"]["start_weight"]

def meal_options_for_type(mt):
    opts = [name for name, m in MEALS.items() if mt in m["type"]]
    return [""] + sorted(opts)

def day_name_from_date(ds):
    return datetime.strptime(ds, "%Y-%m-%d").strftime("%A")

def get_planned_meal(data, ds, mt):
    ws = week_start(datetime.strptime(ds, "%Y-%m-%d").date())
    day = day_name_from_date(ds)
    return data.get("weekly_plan", {}).get(ws, {}).get(day, {}).get(mt, "")

def manual_foods_for(data, ds, mt=None):
    rows = [f for f in data.get("manual_foods", []) if f.get("date") == ds]
    if mt:
        rows = [f for f in rows if f.get("meal_type") == mt]
    return rows

def planned_nutrition(data, ds):
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
    for mt in MEAL_TYPES:
        meal = get_planned_meal(data, ds, mt)
        if meal in MEALS:
            totals["calories"] += MEALS[meal]["cal"]
            totals["protein"] += MEALS[meal]["protein"]
            totals["carbs"] += MEALS[meal]["carbs"]
            totals["fiber"] += MEALS[meal]["fiber"]
    return totals

def manual_nutrition(data, ds):
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
    for f in manual_foods_for(data, ds):
        totals["calories"] += float(f.get("calories", 0))
        totals["protein"] += float(f.get("protein", 0))
        totals["carbs"] += float(f.get("carbs", 0))
        totals["fiber"] += float(f.get("fiber", 0))
    return totals

def total_nutrition(data, ds):
    p, m = planned_nutrition(data, ds), manual_nutrition(data, ds)
    return {k: p[k] + m[k] for k in p}

def grocery_from_week(data, ws):
    totals = {}
    plan = data.get("weekly_plan", {}).get(ws, {})
    for day in DAYS:
        for mt in MEAL_TYPES:
            meal = plan.get(day, {}).get(mt, "")
            if meal in MEALS:
                for item, qty in MEALS[meal]["ingredients"].items():
                    totals[item] = totals.get(item, 0) + qty
    for f in data.get("manual_foods", []):
        if f.get("add_to_grocery") and week_start(datetime.strptime(f["date"], "%Y-%m-%d").date()) == ws:
            item = f.get("grocery_item") or f.get("name")
            qty = f.get("grocery_qty", 1)
            totals[item] = totals.get(item, 0) + qty
    for item in data.get("custom_grocery", []):
        totals[item] = totals.get(item, 0) + 1
    return totals

def grocery_suggested_meals(selected_items):
    selected = [s.lower() for s in selected_items]
    suggestions = []
    for meal, info in MEALS.items():
        text = " ".join(info["ingredients"].keys()).lower()
        score = sum(1 for s in selected if s and s in text)
        if score:
            suggestions.append((score, meal))
    return [m for _, m in sorted(suggestions, reverse=True)[:8]]

def page_header(title, caption=""):
    st.title(title)
    if caption:
        st.caption(caption)

st.set_page_config(page_title="GlowFit", page_icon="ð", layout="wide")
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#0c0c12,#17111d,#0f1416); color: #f7eef7;}
[data-testid="stSidebar"] {background: #111118;}
.card {border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:18px; background:rgba(255,255,255,.055); margin-bottom:12px;}
.small {color:#cfc3cf; font-size:0.9rem;}
.good {color:#9ff0c5; font-weight:700;} .warn {color:#ffd28a; font-weight:700;}
</style>
""", unsafe_allow_html=True)

data = get_data()
ws = ensure_week(data)
ensure_day(data, today_str())
autosave()

st.sidebar.title("ð GlowFit")
page = st.sidebar.radio("Dashboard", ["Home", "Meals", "Weekly Plan", "Grocery", "Workouts", "Progress", "Blood Sugar", "Settings / Backup"])
st.sidebar.caption("Prediabetes-aware Â· fat loss Â· glute growth")

if page == "Home":
    page_header("Home Dashboard", "Todayâs plan pulls from your weekly meals, manual foods, training mode, and progress logs.")
    today = today_str()
    day = ensure_day(data, today)
    c1, c2, c3, c4 = st.columns(4)
    cw = current_weight(data)
    target = data["profile"]["calorie_target_training"] if data["settings"].get("training_day") else data["profile"]["calorie_target_rest"]
    tn = total_nutrition(data, today)
    c1.metric("Current weight", f"{cw:.1f} lb", f"BMI {bmi(cw)}")
    c2.metric("Calories", f"{tn['calories']:.0f}", f"target {target}")
    c3.metric("Protein", f"{tn['protein']:.0f}g", f"target {data['profile']['protein_target']}g")
    c4.metric("Steps", f"{day.get('steps',0):,.0f}")
    training = st.toggle("Training day mode", value=bool(data["settings"].get("training_day", True)), help="Changes calorie/carb guidance across the app.")
    if training != data["settings"].get("training_day"):
        data["settings"]["training_day"] = training; autosave(); st.rerun()
    st.info("Training day: slightly higher smart carbs around workouts. Rest day: prioritize protein, vegetables, fibre, and lower-GI carbs.")
    st.subheader("Todayâs Meals")
    cols = st.columns(4)
    for i, mt in enumerate(MEAL_TYPES):
        meal = get_planned_meal(data, today, mt)
        with cols[i]:
            st.markdown(f"**{mt}**")
            st.write(meal or "No planned meal yet")
            for f in manual_foods_for(data, today, mt):
                st.caption(f"+ {f['name']} ({f.get('calories',0)} cal)")
    st.subheader("Quick daily log")
    with st.form("home_daily_log"):
        col1, col2, col3, col4 = st.columns(4)
        weight = col1.number_input("Weight today (lb)", min_value=0.0, value=float(day.get("weight") or 0), step=0.1)
        water = col2.number_input("Water cups", min_value=0, value=int(day.get("water", 0)), step=1)
        steps = col3.number_input("Steps", min_value=0, value=int(day.get("steps", 0)), step=500)
        notes = col4.text_input("Note", value=day.get("notes", ""))
        if st.form_submit_button("Save daily log"):
            day.update({"weight": weight if weight > 0 else None, "water": water, "steps": steps, "notes": notes})
            autosave(); st.success("Saved.")

elif page == "Meals":
    page_header("Meal Dashboard", "Todayâs planned meals come from Weekly Plan. Manual food entries save by date and meal type.")
    selected_date = st.date_input("Food date", value=date.today()).isoformat()
    tn = total_nutrition(data, selected_date)
    st.metric("Total food calories", f"{tn['calories']:.0f}", f"Protein {tn['protein']:.0f}g Â· Carbs {tn['carbs']:.0f}g Â· Fibre {tn['fiber']:.0f}g")
    st.subheader("Planned + manual foods by meal")
    for mt in MEAL_TYPES:
        st.markdown(f"### {mt}")
        meal = get_planned_meal(data, selected_date, mt)
        if meal:
            info = MEALS[meal]
            st.markdown(f"**Planned:** {meal} â {info['cal']} cal, {info['protein']}g protein, GI: {info['gi']}")
            st.caption(info["timing"])
        else:
            st.caption("No planned meal for this slot yet.")
        mf = manual_foods_for(data, selected_date, mt)
        for idx, f in enumerate(mf):
            st.write(f"â¢ {f['name']} â {f.get('calories',0)} cal, {f.get('protein',0)}g protein")
    st.subheader("Add manual food")
    with st.form("manual_food"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Food name")
        meal_type = col2.selectbox("Meal type", MEAL_TYPES)
        c1, c2, c3, c4 = st.columns(4)
        calories = c1.number_input("Calories", 0, 3000, 0)
        protein = c2.number_input("Protein (g)", 0.0, 250.0, 0.0)
        carbs = c3.number_input("Carbs (g)", 0.0, 300.0, 0.0)
        fiber = c4.number_input("Fibre (g)", 0.0, 100.0, 0.0)
        add_groc = st.checkbox("Also add to grocery list")
        grocery_item = st.text_input("Grocery item name (optional)", placeholder="e.g., cereal, Greek yogurt, eggs")
        grocery_qty = st.number_input("Grocery quantity", 0.0, 1000.0, 1.0)
        if st.form_submit_button("Save manual food"):
            if name.strip():
                data["manual_foods"].append({"date": selected_date, "meal_type": meal_type, "name": name.strip(), "calories": calories, "protein": protein, "carbs": carbs, "fiber": fiber, "add_to_grocery": add_groc, "grocery_item": grocery_item.strip(), "grocery_qty": grocery_qty})
                autosave(); st.success("Food saved and linked."); st.rerun()
            else:
                st.error("Enter a food name.")
    st.subheader("Recipe library")
    meal_name = st.selectbox("Choose recipe", sorted(MEALS.keys()))
    info = MEALS[meal_name]
    servings = st.number_input("Meal prep servings", 1, 14, int(info["servings"]))
    scale = servings / info["servings"]
    st.markdown(f"**{meal_name}** Â· {info['gi']} GI Â· {info['cal']} cal/serving Â· {info['protein']}g protein/serving")
    st.caption(info["timing"])
    st.write("Ingredient quantities for the full prep:")
    st.table(pd.DataFrame([{"Ingredient": k, "Amount": round(v * scale, 2)} for k, v in info["ingredients"].items()]))
    st.write("Portion accuracy / dishing steps:")
    for s in info["steps"]:
        st.write(f"- {s}")
    st.subheader("Fruit guide")
    for group, items in FRUIT_GUIDE.items():
        st.markdown(f"**{group}**")
        for fruit, tip in items.items():
            st.caption(f"{fruit}: {tip}")

elif page == "Weekly Plan":
    page_header("Weekly Meal Plan", "Select meals for each day. This automatically feeds Meals and Grocery.")
    plan = data["weekly_plan"].setdefault(ws, {day: {mt: "" for mt in MEAL_TYPES} for day in DAYS})
    with st.form("weekly_plan_form"):
        for d in DAYS:
            st.markdown(f"### {d}")
            cols = st.columns(4)
            for i, mt in enumerate(MEAL_TYPES):
                opts = meal_options_for_type(mt)
                current = plan.get(d, {}).get(mt, "")
                idx = opts.index(current) if current in opts else 0
                plan[d][mt] = cols[i].selectbox(mt, opts, index=idx, key=f"plan_{d}_{mt}")
        if st.form_submit_button("Save weekly plan"):
            data["weekly_plan"][ws] = plan; autosave(); st.success("Weekly plan saved. Meals and grocery will update.")
    st.subheader("Weekly nutrition preview")
    rows = []
    for i, d in enumerate(DAYS):
        ds = (datetime.strptime(ws, "%Y-%m-%d").date() + timedelta(days=i)).isoformat()
        t = total_nutrition(data, ds)
        rows.append({"Day": d, "Calories": t["calories"], "Protein": t["protein"], "Carbs": t["carbs"], "Fibre": t["fiber"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

elif page == "Grocery":
    page_header("Grocery", "Smart list can come from weekly plan, manual foods, or selected groceries.")
    auto = grocery_from_week(data, ws)
    st.subheader("Auto-populated from weekly plan + manual foods")
    if auto:
        for item, qty in sorted(auto.items()):
            key = f"grocery_{ws}_{item}"
            checked = st.checkbox(f"{item}: {round(qty,2)}", value=data["grocery_checked"].get(key, False), key=key)
            data["grocery_checked"][key] = checked
        autosave()
    else:
        st.caption("No grocery items yet. Add meals to Weekly Plan or manual foods.")
    st.subheader("Smart grocery builder")
    common = ["chicken breast", "salmon", "shrimp", "eggs", "Greek yogurt", "high-protein low-sugar cereal", "berries", "green apples", "kiwi", "konjac rice", "konjac noodles", "sweet potato", "broccoli", "spinach", "lettuce", "avocado", "tuna", "cottage cheese", "chia seeds", "peanut butter"]
    selected = st.multiselect("Select groceries you have/want", common)
    suggestions = grocery_suggested_meals(selected)
    if suggestions:
        st.write("Meals that match your grocery selection:")
        for m in suggestions:
            st.write(f"- {m}")
    with st.form("custom_grocery"):
        item = st.text_input("Add custom grocery item")
        if st.form_submit_button("Add item") and item.strip():
            data["custom_grocery"].append(item.strip()); autosave(); st.rerun()

elif page == "Workouts":
    page_header("Workout Dashboard", "Weekly plan shows remaining days first; completed/past days move lower. Sets save individually.")
    today_idx = date.today().weekday()
    ordered_days = DAYS[today_idx:] + DAYS[:today_idx]
    logs = data["workout_logs"].setdefault(ws, {})
    def render_day(d, previous=False):
        workout = WORKOUT_PLAN[d]
        logs.setdefault(d, {})
        with st.expander(("Previous / completed: " if previous else "") + f"{d} â {workout['focus']}", expanded=not previous):
            for ex_name, sets, reps, weight, url in workout["exercises"]:
                st.markdown(f"**{ex_name}**  [video/form]({url})")
                exlog = logs[d].setdefault(ex_name, {"sets": [], "rating": 0, "notes": ""})
                while len(exlog["sets"]) < sets:
                    exlog["sets"].append({"done": False, "reps": reps, "weight": weight})
                for si in range(sets):
                    s = exlog["sets"][si]
                    c1, c2, c3 = st.columns([1, 1, 1])
                    s["done"] = c1.checkbox(f"Set {si+1}", value=bool(s.get("done", False)), key=f"{ws}_{d}_{ex_name}_{si}_done")
                    s["reps"] = c2.number_input("Reps", 0, 100, int(s.get("reps", reps)), key=f"{ws}_{d}_{ex_name}_{si}_reps")
                    s["weight"] = c3.number_input("Weight", 0.0, 1000.0, float(s.get("weight", weight)), step=2.5, key=f"{ws}_{d}_{ex_name}_{si}_wt")
                exlog["rating"] = st.slider(f"Difficulty rating for {ex_name}", 0, 10, int(exlog.get("rating", 0)), key=f"{ws}_{d}_{ex_name}_rating")
            logs[d]["day_notes"] = st.text_input(f"{d} notes", value=logs[d].get("day_notes", ""), key=f"{ws}_{d}_notes")
            if st.button(f"Save {d} workout", key=f"save_{d}"):
                autosave(); st.success(f"{d} workout saved.")
    st.subheader("Remaining / current week")
    for d in ordered_days:
        idx = DAYS.index(d)
        previous = idx < today_idx
        if not previous:
            render_day(d, previous=False)
    st.subheader("Previous / completed earlier this week")
    for d in ordered_days:
        idx = DAYS.index(d)
        if idx < today_idx:
            render_day(d, previous=True)
    autosave()

elif page == "Progress":
    page_header("Progress", "Charts read from saved daily logs and food/workout history.")
    day = ensure_day(data, today_str())
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        weight = col1.number_input("Save weight/progress", min_value=0.0, value=float(day.get("weight") or current_weight(data)), step=0.1)
        steps = col2.number_input("Save steps", min_value=0, value=int(day.get("steps", 0)), step=500)
        if st.form_submit_button("Save weight/progress"):
            day["weight"] = weight; day["steps"] = steps; autosave(); st.success("Saved.")
    cw = current_weight(data)
    st.metric("BMI", bmi(cw), "based on 5'9\" and latest saved weight")
    rows = []
    for ds, vals in sorted(data["daily"].items()):
        t = total_nutrition(data, ds)
        rows.append({"date": ds, "weight": vals.get("weight"), "steps": vals.get("steps", 0), "water": vals.get("water", 0), "calories": t["calories"], "protein": t["protein"], "bmi": bmi(vals.get("weight")) if vals.get("weight") else None})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        st.subheader("Weight trend")
        st.line_chart(df.dropna(subset=["weight"]).set_index("date")[["weight"]])
        st.subheader("Nutrition trend")
        st.line_chart(df.set_index("date")[["calories", "protein"]])
        st.subheader("Steps/water trend")
        st.line_chart(df.set_index("date")[["steps", "water"]])
        st.dataframe(df, use_container_width=True)
    else:
        st.caption("No progress data yet.")

elif page == "Blood Sugar":
    page_header("Blood Sugar Awareness", "Symptom tracking and supportive tips. Not a diagnosis tool.")
    selected_date = st.date_input("Symptom date", value=date.today()).isoformat()
    chosen = st.multiselect("Symptoms I felt", list(SYMPTOMS.keys()))
    note = st.text_area("Context note", placeholder="What did you eat, workout, water, stress, sleep?")
    if st.button("Save symptom log"):
        if chosen:
            data["symptom_logs"].append({"date": selected_date, "symptoms": chosen, "note": note, "timestamp": datetime.now().isoformat()})
            autosave(); st.success("Symptoms saved.")
        else:
            st.warning("Select at least one symptom.")
    if chosen:
        st.subheader("Tips based on selected symptoms")
        for s in chosen:
            st.write(f"**{s}:** {SYMPTOMS[s]}")
    st.subheader("History")
    if data["symptom_logs"]:
        st.dataframe(pd.DataFrame(data["symptom_logs"]), use_container_width=True)
    else:
        st.caption("No symptom logs yet.")

elif page == "Settings / Backup":
    page_header("Settings / Backup", "Save profile settings and export/import your app data.")
    prof = data["profile"]
    with st.form("settings_form"):
        prof["protein_target"] = st.number_input("Daily protein target (g)", 80, 220, int(prof.get("protein_target", PROTEIN_TARGET)))
        prof["calorie_target_rest"] = st.number_input("Rest-day calorie target", 1200, 2600, int(prof.get("calorie_target_rest", 1650)))
        prof["calorie_target_training"] = st.number_input("Training-day calorie target", 1200, 3000, int(prof.get("calorie_target_training", 1850)))
        prof["goal_weight"] = st.number_input("Goal weight", 100.0, 300.0, float(prof.get("goal_weight", GOAL_WEIGHT)))
        if st.form_submit_button("Save settings"):
            data["profile"] = prof; autosave(); st.success("Settings saved.")
    st.download_button("Download backup JSON", data=json.dumps(data, indent=2), file_name="glowfit_backup.json", mime="application/json")
    uploaded = st.file_uploader("Restore backup JSON", type="json")
    if uploaded and st.button("Restore backup"):
        st.session_state.data = merge_defaults(default_data(), json.loads(uploaded.read().decode("utf-8")))
        autosave(); st.success("Backup restored."); st.rerun()
    if st.button("Force save now"):
        autosave(); st.success("Saved.")
