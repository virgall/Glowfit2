import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

APP_TITLE = "GlowFit Metabolic Dashboard"
DATA_FILE = Path("glowfit_data.json")

st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")

st.markdown('''
<style>
.stApp { background: linear-gradient(135deg, #111018 0%, #1a1525 45%, #211722 100%); color: #f7eef7; }
[data-testid="stSidebar"] { background: #15121d; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
.metric-card { background: rgba(255,255,255,0.065); border: 1px solid rgba(255,255,255,0.12); border-radius: 22px; padding: 18px; box-shadow: 0 12px 35px rgba(0,0,0,0.22); }
.soft-card { background: rgba(255,255,255,0.055); border: 1px solid rgba(255,255,255,0.10); border-radius: 20px; padding: 18px; margin: 8px 0 18px 0; }
.small-muted { color: #cdbfd0; font-size: 0.92rem; }
.pill { display: inline-block; padding: 5px 10px; border-radius: 999px; background: rgba(244,170,199,0.18); border: 1px solid rgba(244,170,199,0.28); margin: 2px; font-size: 0.85rem; }
.warn { color: #ffd6a8; }
.good { color: #b7f3d0; }
.h1 { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.04em; }
hr { border-color: rgba(255,255,255,0.12); }
button[kind="primary"] { border-radius: 12px; }
</style>
''', unsafe_allow_html=True)

DEFAULT_PROFILE = {
    "height_ft": 5,
    "height_in": 9,
    "start_weight": 224.0,
    "current_weight": 224.0,
    "goal_weight": 199.0,
    "age": 25,
    "activity_level": "Lightly active",
    "protein_target": 140,
    "water_target_l": 2.7,
    "step_target": 8000,
    "calorie_target_rest": 1750,
    "calorie_target_training": 1950,
    "carb_rest": 120,
    "carb_training": 155,
}

MEALS = [
    {"name":"Greek Yogurt Power Bowl", "meal":"Breakfast", "cal":420, "protein":38, "carbs":38, "fiber":8, "gi":"Low", "items":"Plain Greek yogurt, berries, chia, cinnamon, small oats", "portion":"250 g yogurt + 1/2 cup berries + 1 tbsp chia + 1/3 cup oats", "warning":"Keep yogurt unsweetened. Add cinnamon/berries instead of honey.", "prep":"5 min"},
    {"name":"Chicken Quinoa Veg Bowl", "meal":"Lunch", "cal":560, "protein":48, "carbs":50, "fiber":10, "gi":"Low–Moderate", "items":"Chicken breast, quinoa, spinach, cucumber, peppers, avocado", "portion":"150 g cooked chicken + 3/4 cup cooked quinoa + 2 cups veggies + 1/4 avocado", "warning":"Quinoa is better paired with protein/fibre. Keep sauce measured.", "prep":"20 min"},
    {"name":"Salmon Potato Plate", "meal":"Dinner", "cal":610, "protein":42, "carbs":45, "fiber":8, "gi":"Moderate", "items":"Salmon, cooled/roasted potato, broccoli, salad", "portion":"150 g salmon + 180 g potato + 2 cups vegetables", "warning":"Potato can spike glucose for some people. Keep portion moderate and pair with protein/veg.", "prep":"25 min"},
    {"name":"Egg Veggie Scramble", "meal":"Breakfast", "cal":390, "protein":30, "carbs":25, "fiber":7, "gi":"Low", "items":"Eggs, egg whites, vegetables, one slice whole grain toast", "portion":"2 eggs + 120 g egg whites + 2 cups veg + 1 slice toast", "warning":"Choose high-fibre bread and avoid juice on the side.", "prep":"12 min"},
    {"name":"Tuna Cucumber Chickpea Bowl", "meal":"Lunch", "cal":480, "protein":42, "carbs":38, "fiber":11, "gi":"Low", "items":"Tuna, chickpeas, cucumber, tomatoes, greens, Greek yogurt dressing", "portion":"1 can tuna + 1/2 cup chickpeas + 2 cups vegetables", "warning":"Measure chickpeas; they’re healthy but still carb-containing.", "prep":"8 min"},
    {"name":"Turkey Lettuce Taco Bowl", "meal":"Dinner", "cal":520, "protein":45, "carbs":35, "fiber":9, "gi":"Low", "items":"Lean turkey, lettuce, beans, salsa, Greek yogurt, avocado", "portion":"150 g turkey + 1/3 cup beans + 3 cups salad + 2 tbsp Greek yogurt", "warning":"Use beans as the carb and skip chips/tortillas if glucose is high.", "prep":"18 min"},
]

RECIPES = [
    {"title":"Low-GI Chicken Meal Prep Bowl", "cal":560, "protein":48, "servings":1, "ingredients":["150 g cooked chicken breast", "3/4 cup cooked quinoa", "2 cups chopped vegetables", "1 tbsp measured dressing", "1/4 avocado"], "steps":["Weigh cooked chicken on a food scale.", "Scoop quinoa with a measuring cup, level it off.", "Fill half the plate/container with vegetables first.", "Add chicken, then quinoa, then measured dressing.", "Log the portion before eating so calories stay accurate."], "swap":"Swap quinoa for cauliflower rice on lower-carb rest days."},
    {"title":"Greek Yogurt Berry Protein Bowl", "cal":420, "protein":38, "servings":1, "ingredients":["250 g plain Greek yogurt", "1/2 cup berries", "1 tbsp chia", "1/3 cup oats", "cinnamon"], "steps":["Weigh yogurt in grams.", "Use measuring cups/spoons for berries, oats, and chia.", "Mix cinnamon in for sweetness without added sugar.", "Add extra yogurt, not extra oats, if you need more fullness."], "swap":"Swap oats for nuts/seeds if carbs are already high."},
    {"title":"Salmon + Smart Potato Plate", "cal":610, "protein":42, "servings":1, "ingredients":["150 g salmon", "180 g potato", "2 cups broccoli/salad", "1 tsp olive oil", "lemon/herbs"], "steps":["Weigh potato cooked or raw consistently each time.", "Measure oil with a teaspoon, don’t free-pour.", "Plate vegetables first, then salmon, then potato.", "Keep sauces on the side and measure them."], "swap":"Use sweet potato or lentils if regular potato spikes you."},
]

EXERCISES = {
    "Glutes + Lower Body": [
        {"name":"Hip Thrust", "sets":4, "reps":"8–12", "weight":40, "link":"https://www.youtube.com/results?search_query=hip+thrust+proper+form", "cue":"Drive through heels, pause at top, ribs down."},
        {"name":"Romanian Deadlift", "sets":3, "reps":"8–10", "weight":30, "link":"https://www.youtube.com/results?search_query=romanian+deadlift+proper+form", "cue":"Hinge hips back, soft knees, feel hamstrings."},
        {"name":"Bulgarian Split Squat", "sets":3, "reps":"8 each leg", "weight":10, "link":"https://www.youtube.com/results?search_query=bulgarian+split+squat+form", "cue":"Slight forward lean for glutes."},
        {"name":"Cable/Dumbbell Kickback", "sets":3, "reps":"12–15", "weight":8, "link":"https://www.youtube.com/results?search_query=glute+kickback+proper+form", "cue":"Control the movement, don’t swing."},
    ],
    "Upper Body + Arms": [
        {"name":"Lat Pulldown", "sets":3, "reps":"10–12", "weight":35, "link":"https://www.youtube.com/results?search_query=lat+pulldown+proper+form", "cue":"Pull elbows down, chest tall."},
        {"name":"Dumbbell Shoulder Press", "sets":3, "reps":"8–10", "weight":10, "link":"https://www.youtube.com/results?search_query=dumbbell+shoulder+press+form", "cue":"Brace core, don’t arch back."},
        {"name":"Seated Row", "sets":3, "reps":"10–12", "weight":35, "link":"https://www.youtube.com/results?search_query=seated+row+proper+form", "cue":"Squeeze shoulder blades."},
        {"name":"Triceps Rope Pushdown", "sets":3, "reps":"12–15", "weight":15, "link":"https://www.youtube.com/results?search_query=triceps+rope+pushdown+form", "cue":"Elbows stay tucked."},
    ],
    "Core + Cardio": [
        {"name":"Incline Treadmill Walk", "sets":1, "reps":"25–35 min", "weight":0, "link":"https://www.youtube.com/results?search_query=incline+treadmill+walking+fat+loss", "cue":"Brisk pace, nasal breathing if possible."},
        {"name":"Dead Bug", "sets":3, "reps":"10 each side", "weight":0, "link":"https://www.youtube.com/results?search_query=dead+bug+exercise+proper+form", "cue":"Low back stays gently pressed down."},
        {"name":"Plank", "sets":3, "reps":"20–45 sec", "weight":0, "link":"https://www.youtube.com/results?search_query=plank+proper+form", "cue":"Ribs down, squeeze glutes."},
        {"name":"Stairmaster", "sets":1, "reps":"10–20 min", "weight":0, "link":"https://www.youtube.com/results?search_query=stairmaster+beginner+workout", "cue":"Light hands, steady pace."},
    ],
    "Full Body Strength": [
        {"name":"Goblet Squat", "sets":3, "reps":"10–12", "weight":20, "link":"https://www.youtube.com/results?search_query=goblet+squat+proper+form", "cue":"Knees track over toes, chest proud."},
        {"name":"Dumbbell Bench Press", "sets":3, "reps":"8–12", "weight":15, "link":"https://www.youtube.com/results?search_query=dumbbell+bench+press+proper+form", "cue":"Control down, press strong."},
        {"name":"Walking Lunges", "sets":3, "reps":"10 each leg", "weight":10, "link":"https://www.youtube.com/results?search_query=walking+lunges+proper+form", "cue":"Step long enough to feel glutes."},
        {"name":"Farmer Carry", "sets":3, "reps":"30–45 sec", "weight":20, "link":"https://www.youtube.com/results?search_query=farmer+carry+proper+form", "cue":"Tall posture, core tight."},
    ],
}

SYMPTOMS = ["Extreme thirst", "Frequent urination", "Blurred vision", "Shakiness/sweating", "Unusual fatigue", "Nausea", "Confusion", "Rapid heartbeat", "Fruity breath", "Feeling faint"]
SWAPS = [
    ("White rice", "quinoa, lentils, cauliflower rice, or smaller rice portion with extra protein"),
    ("Juice/pop", "water, sparkling water, or zero-sugar drink"),
    ("Sweet cereal", "Greek yogurt bowl or oats with protein"),
    ("Creamy sauce", "Greek yogurt sauce or measured light dressing"),
    ("Large potato portion", "smaller potato + extra veggies + protein"),
    ("Candy snack", "Greek yogurt, boiled eggs, berries, cheese, or nuts"),
]

GROCERY_CATEGORIES = {
    "Proteins": ["Chicken breast/thigh", "Salmon", "Tuna", "Eggs", "Egg whites", "Lean turkey", "Greek yogurt", "Cottage cheese"],
    "Low-GI Carbs": ["Oats", "Quinoa", "Lentils", "Chickpeas", "Sweet potato", "High-fibre wraps", "Berries"],
    "Vegetables": ["Spinach", "Broccoli", "Peppers", "Cucumber", "Tomatoes", "Mixed greens", "Zucchini", "Cauliflower rice"],
    "Fats & Extras": ["Avocado", "Chia seeds", "Olive oil", "Nuts", "Cinnamon", "Salsa", "Lemon", "Herbs"],
}


def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"profile": DEFAULT_PROFILE.copy(), "daily_logs": [], "weight_logs": [], "workout_logs": [], "meal_logs": [], "symptom_logs": []}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2, default=str))


def today_str():
    return date.today().isoformat()


def mifflin_st_jeor(weight_lb, height_in, age):
    kg = weight_lb * 0.453592
    cm = height_in * 2.54
    return (10 * kg) + (6.25 * cm) - (5 * age) - 161


def tdee(profile):
    factors = {"Sedentary":1.2, "Lightly active":1.375, "Moderately active":1.55, "Very active":1.725}
    height_in = profile["height_ft"]*12 + profile["height_in"]
    return round(mifflin_st_jeor(profile["current_weight"], height_in, profile["age"]) * factors.get(profile["activity_level"], 1.375))


def add_log(key, item):
    st.session_state.data[key].append(item)
    save_data(st.session_state.data)


def metric_card(label, value, note=""):
    st.markdown(f"<div class='metric-card'><div class='small-muted'>{label}</div><div style='font-size:1.7rem;font-weight:800'>{value}</div><div class='small-muted'>{note}</div></div>", unsafe_allow_html=True)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
profile = data["profile"]

st.sidebar.title("🌙 GlowFit")
page = st.sidebar.radio("Go to", ["Home", "Meal Dashboard", "Workout Dashboard", "Progress", "Blood Sugar", "Settings / Backup"])
st.sidebar.caption("Warm, practical, never punitive. Not medical advice; use with your clinician's guidance.")

if page == "Home":
    st.markdown("<div class='h1'>GlowFit Metabolic Dashboard</div>", unsafe_allow_html=True)
    st.write("A prediabetic-friendly wellness dashboard for fat loss, glute growth, strength, food quality, and consistency.")

    training_day = st.toggle("Today is a training day", value=True)
    calories = profile["calorie_target_training"] if training_day else profile["calorie_target_rest"]
    carbs = profile["carb_training"] if training_day else profile["carb_rest"]
    est_tdee = tdee(profile)
    deficit = max(est_tdee - calories, 0)
    weeks_to_goal = round(((profile["current_weight"] - profile["goal_weight"]) * 3500) / max(deficit*7, 1), 1) if profile["current_weight"] > profile["goal_weight"] else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Current weight", f"{profile['current_weight']} lb", f"Goal: under {profile['goal_weight']} lb")
    with c2: metric_card("Calorie target", f"{calories} kcal", "Adjusted for training/rest day")
    with c3: metric_card("Protein target", f"{profile['protein_target']} g", "Preset for muscle retention + fullness")
    with c4: metric_card("Estimated TDEE", f"{est_tdee} kcal", f"Goal timeline estimate: {weeks_to_goal} weeks")

    st.progress(min(max((profile["start_weight"]-profile["current_weight"])/(profile["start_weight"]-profile["goal_weight"]), 0), 1), text="Progress toward under 200 lb")

    st.subheader("Today’s Log")
    with st.form("daily_form"):
        col1, col2, col3, col4 = st.columns(4)
        kcal = col1.number_input("Calories eaten", 0, 5000, 0)
        protein = col2.number_input("Protein (g)", 0, 300, 0)
        water = col3.number_input("Water (L)", 0.0, 8.0, 0.0, step=0.25)
        steps = col4.number_input("Steps", 0, 50000, 0)
        mood = st.select_slider("Energy / mood", options=["Low", "Okay", "Good", "Strong"])
        hunger = st.select_slider("Hunger level", options=["Not hungry", "Manageable", "Hungry", "Very hungry"])
        submitted = st.form_submit_button("Save today’s log")
        if submitted:
            add_log("daily_logs", {"date": today_str(), "training_day": training_day, "calories": kcal, "protein": protein, "water": water, "steps": steps, "mood": mood, "hunger": hunger})
            st.success("Saved. Small consistent entries matter more than perfect days.")

    st.subheader("Quick swap suggestions")
    for old, new in SWAPS:
        st.markdown(f"<span class='pill'>{old} → {new}</span>", unsafe_allow_html=True)

elif page == "Meal Dashboard":
    st.title("🍽️ Meal Dashboard")
    st.caption("Low-glycemic, high-protein, portion-aware meals. Measure calmly, not obsessively.")
    tab1, tab2, tab3, tab4 = st.tabs(["Meal Planner", "Recipes", "Weekly Plan", "Grocery List"])

    with tab1:
        st.subheader("Preset low-GI meal planner")
        meal_type = st.selectbox("Filter meal type", ["All"] + sorted(set(m["meal"] for m in MEALS)))
        for m in MEALS:
            if meal_type != "All" and m["meal"] != meal_type: continue
            with st.expander(f"{m['name']} — {m['cal']} kcal, {m['protein']}g protein, GI: {m['gi']}", expanded=False):
                st.write(m["items"])
                st.info(f"Portion guidance: {m['portion']}")
                st.warning(f"GI note: {m['warning']}")
                st.caption(f"Prep time: {m['prep']} | Carbs: {m['carbs']}g | Fibre: {m['fiber']}g")
                if st.button(f"Log meal: {m['name']}", key=f"meal_{m['name']}"):
                    add_log("meal_logs", {"date": today_str(), **m})
                    st.success("Meal logged.")

        st.subheader("Custom meal log")
        with st.form("custom_meal"):
            name = st.text_input("Meal name")
            col1, col2, col3, col4 = st.columns(4)
            cal = col1.number_input("Calories", 0, 3000, 0, key="custom_cal")
            pro = col2.number_input("Protein (g)", 0, 200, 0, key="custom_pro")
            carb = col3.number_input("Carbs (g)", 0, 300, 0, key="custom_carb")
            fibre = col4.number_input("Fibre (g)", 0, 80, 0, key="custom_fibre")
            gi = st.selectbox("GI warning", ["Low", "Low–Moderate", "Moderate", "Caution"])
            notes = st.text_area("Portion/measuring notes")
            if st.form_submit_button("Save custom meal"):
                add_log("meal_logs", {"date": today_str(), "name": name or "Custom meal", "cal": cal, "protein": pro, "carbs": carb, "fiber": fibre, "gi": gi, "portion": notes})
                st.success("Custom meal saved.")

    with tab2:
        st.subheader("Recipes + portion accuracy steps")
        for r in RECIPES:
            with st.expander(f"{r['title']} — {r['cal']} kcal, {r['protein']}g protein"):
                st.write("Ingredients")
                st.write("\n".join([f"- {x}" for x in r["ingredients"]]))
                st.write("Dishing / measuring steps")
                st.write("\n".join([f"{i+1}. {x}" for i,x in enumerate(r["steps"])]))
                st.info(f"Smart swap: {r['swap']}")

        st.markdown("""
        **Portion accuracy rules**
        - Use a food scale for protein, rice/quinoa/potatoes, yogurt, and oils when possible.
        - Use measuring cups/spoons for oats, sauces, nut butters, chia, and dressings.
        - Track cooked vs raw weight consistently.
        - Measure oils and sauces because they add up quickly.
        - Plate order: vegetables first → protein → smart carb → fats/sauce.
        """)

    with tab3:
        st.subheader("Simple weekly meal plan")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        selected = {}
        for d in days:
            st.markdown(f"**{d}**")
            c1,c2,c3 = st.columns(3)
            selected[f"{d}_breakfast"] = c1.selectbox("Breakfast", [m["name"] for m in MEALS if m["meal"]=="Breakfast"], key=f"b{d}")
            selected[f"{d}_lunch"] = c2.selectbox("Lunch", [m["name"] for m in MEALS if m["meal"]=="Lunch"], key=f"l{d}")
            selected[f"{d}_dinner"] = c3.selectbox("Dinner", [m["name"] for m in MEALS if m["meal"]=="Dinner"], key=f"di{d}")
        if st.button("Save weekly plan"):
            data["weekly_plan"] = selected
            save_data(data)
            st.success("Weekly meal plan saved.")

    with tab4:
        st.subheader("Auto grocery list")
        st.caption("Built from the preset foods used across meals and recipes.")
        for cat, items in GROCERY_CATEGORIES.items():
            st.markdown(f"### {cat}")
            for item in items:
                st.checkbox(item, key=f"grocery_{cat}_{item}")

elif page == "Workout Dashboard":
    st.title("🏋🏾‍♀️ Workout Dashboard")
    st.caption("Built for weight loss, glute growth, core strength, upper-body tone, cardio, and a slim/fit look. You cannot spot-reduce fat, but you can reduce overall body fat while shaping muscle.")

    focus = st.selectbox("Choose workout focus", list(EXERCISES.keys()))
    st.info("Friendly progression: when a weight feels controlled for all sets/reps for 2 sessions, increase by 2.5–5 lb next time. If form breaks, stay or reduce.")

    with st.form("workout_log"):
        workout_date = st.date_input("Workout date", value=date.today())
        rating = st.slider("How did the workout feel?", 1, 10, 7)
        notes = st.text_area("Workout notes")
        rows = []
        for ex in EXERCISES[focus]:
            st.markdown(f"### {ex['name']}")
            st.caption(ex["cue"])
            st.markdown(f"[Form video search]({ex['link']})")
            c1,c2,c3 = st.columns(3)
            sets = c1.number_input(f"Sets - {ex['name']}", 0, 10, ex["sets"], key=f"sets_{ex['name']}")
            reps = c2.text_input(f"Reps - {ex['name']}", ex["reps"], key=f"reps_{ex['name']}")
            weight = c3.number_input(f"Weight lb - {ex['name']}", 0.0, 500.0, float(ex["weight"]), step=2.5, key=f"wt_{ex['name']}")
            rows.append({"exercise": ex["name"], "sets": sets, "reps": reps, "weight": weight})
        cardio = st.number_input("Cardio minutes completed", 0, 180, 20)
        submitted = st.form_submit_button("Save workout")
        if submitted:
            add_log("workout_logs", {"date": workout_date.isoformat(), "focus": focus, "rating": rating, "notes": notes, "cardio_min": cardio, "exercises": rows})
            st.success("Workout saved. Progress is built one logged session at a time.")

    st.subheader("Weekly structure suggestion")
    st.write("""
    - Day 1: Glutes + Lower Body
    - Day 2: Upper Body + Arms + incline walk
    - Day 3: Core + Cardio
    - Day 4: Rest / steps
    - Day 5: Glutes + Lower Body
    - Day 6: Full Body Strength + light cardio
    - Day 7: Rest / mobility / walk
    """)

elif page == "Progress":
    st.title("📈 Progress Tracker")
    with st.form("weight_form"):
        wdate = st.date_input("Date", value=date.today(), key="wdate")
        weight = st.number_input("Weight (lb)", 50.0, 500.0, float(profile["current_weight"]), step=0.2)
        waist = st.number_input("Waist measurement (optional, inches)", 0.0, 80.0, 0.0, step=0.25)
        hips = st.number_input("Hips measurement (optional, inches)", 0.0, 90.0, 0.0, step=0.25)
        if st.form_submit_button("Save progress"):
            profile["current_weight"] = weight
            add_log("weight_logs", {"date": wdate.isoformat(), "weight": weight, "waist": waist, "hips": hips})
            save_data(data)
            st.success("Progress saved.")

    if data["weight_logs"]:
        df = pd.DataFrame(data["weight_logs"])
        df["date"] = pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date")[["weight"]])
    else:
        st.info("No weight entries yet.")

    if data["daily_logs"]:
        ddf = pd.DataFrame(data["daily_logs"])
        ddf["date"] = pd.to_datetime(ddf["date"])
        st.subheader("Calories, protein, water, steps")
        st.line_chart(ddf.set_index("date")[["calories", "protein", "water", "steps"]])

    if data["workout_logs"]:
        wdf = pd.DataFrame([{ "date": x["date"], "rating": x["rating"], "cardio_min": x["cardio_min"]} for x in data["workout_logs"]])
        wdf["date"] = pd.to_datetime(wdf["date"])
        st.subheader("Workout rating + cardio minutes")
        st.line_chart(wdf.set_index("date")[["rating", "cardio_min"]])

elif page == "Blood Sugar":
    st.title("🩸 Blood Sugar Awareness")
    st.warning("This is not a diagnostic tool. If symptoms are severe, unusual, or you feel unsafe, seek medical care promptly.")
    st.subheader("Symptom checklist")
    selected = []
    cols = st.columns(2)
    for i, s in enumerate(SYMPTOMS):
        if cols[i%2].checkbox(s, key=f"symptom_{s}"):
            selected.append(s)
    notes = st.text_area("Notes: what did you eat, when did symptoms start, any glucose reading?")
    if st.button("Save symptom check"):
        add_log("symptom_logs", {"date": datetime.now().isoformat(timespec="minutes"), "symptoms": selected, "notes": notes})
        if any(s in selected for s in ["Confusion", "Feeling faint", "Fruity breath", "Nausea"]):
            st.error("Some selected symptoms can be concerning. Consider contacting a healthcare provider, especially if symptoms are severe or persistent.")
        else:
            st.success("Symptom check saved.")

    st.subheader("Blood-sugar-friendly reminders")
    st.write("""
    - Pair carbs with protein, fibre, and healthy fats.
    - Be careful with liquid sugar: juice, regular pop, sweet drinks.
    - Walk 10–15 minutes after meals when possible.
    - Prioritize sleep and hydration; they can affect cravings and glucose stability.
    - Ask your clinician what glucose ranges you should personally watch for.
    """)

elif page == "Settings / Backup":
    st.title("⚙️ Settings / Backup")
    st.subheader("Profile settings")
    with st.form("profile_form"):
        c1,c2,c3,c4 = st.columns(4)
        profile["age"] = c1.number_input("Age", 18, 80, int(profile["age"]))
        profile["height_ft"] = c2.number_input("Height ft", 4, 7, int(profile["height_ft"]))
        profile["height_in"] = c3.number_input("Height inches", 0, 11, int(profile["height_in"]))
        profile["activity_level"] = c4.selectbox("Activity", ["Sedentary", "Lightly active", "Moderately active", "Very active"], index=["Sedentary", "Lightly active", "Moderately active", "Very active"].index(profile["activity_level"]))
        c5,c6,c7,c8 = st.columns(4)
        profile["start_weight"] = c5.number_input("Start weight", 50.0, 500.0, float(profile["start_weight"]))
        profile["current_weight"] = c6.number_input("Current weight", 50.0, 500.0, float(profile["current_weight"]))
        profile["goal_weight"] = c7.number_input("Goal weight", 50.0, 500.0, float(profile["goal_weight"]))
        profile["protein_target"] = c8.number_input("Protein target (g)", 60, 250, int(profile["protein_target"]))
        c9,c10,c11,c12 = st.columns(4)
        profile["calorie_target_rest"] = c9.number_input("Rest day calories", 1000, 3500, int(profile["calorie_target_rest"]))
        profile["calorie_target_training"] = c10.number_input("Training day calories", 1000, 4000, int(profile["calorie_target_training"]))
        profile["carb_rest"] = c11.number_input("Rest day carbs (g)", 50, 300, int(profile["carb_rest"]))
        profile["carb_training"] = c12.number_input("Training day carbs (g)", 50, 350, int(profile["carb_training"]))
        if st.form_submit_button("Save settings"):
            data["profile"] = profile
            save_data(data)
            st.success("Settings saved.")

    st.subheader("Export / import data")
    st.download_button("Download backup JSON", data=json.dumps(data, indent=2), file_name="glowfit_backup.json", mime="application/json")
    uploaded = st.file_uploader("Restore from backup JSON", type="json")
    if uploaded is not None:
        try:
            restored = json.loads(uploaded.read())
            st.session_state.data = restored
            save_data(restored)
            st.success("Backup restored. Refresh the app if needed.")
        except Exception as e:
            st.error(f"Could not restore backup: {e}")

    if st.button("Reset all data", type="secondary"):
        st.session_state.data = {"profile": DEFAULT_PROFILE.copy(), "daily_logs": [], "weight_logs": [], "workout_logs": [], "meal_logs": [], "symptom_logs": []}
        save_data(st.session_state.data)
        st.warning("Data reset.")
