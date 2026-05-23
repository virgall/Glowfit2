# fitness_app.py

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
import uuid

st.set_page_config(
    page_title="Fitness + Meal Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_DIR = Path("fitness_dashboard_data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "grocery": DATA_DIR / "grocery.csv",
    "meals": DATA_DIR / "meals.csv",
    "weekly_plan": DATA_DIR / "weekly_plan.csv",
    "meal_log": DATA_DIR / "meal_log.csv",
    "workout_plan": DATA_DIR / "workout_plan.csv",
    "workout_sets": DATA_DIR / "workout_sets.csv",
    "workout_log": DATA_DIR / "workout_log.csv",
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

GROCERY_COLS = [
    "id", "food", "category", "serving", "calories", "protein_g", "carbs_g",
    "fat_g", "fiber_g", "sugar_g", "timing", "tags", "notes"
]

MEAL_COLS = [
    "id", "meal_name", "meal_type", "items", "calories", "protein_g", "carbs_g",
    "fat_g", "fiber_g", "sugar_g", "timing", "tags", "instructions"
]

WEEKLY_PLAN_COLS = [
    "id", "date", "day", "meal_type", "meal_id", "meal_name", "items",
    "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g",
    "status", "notes"
]

MEAL_LOG_COLS = [
    "id", "date", "day", "meal_type", "meal_name", "items", "calories",
    "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "notes"
]

WORKOUT_PLAN_COLS = [
    "id", "date", "day", "workout_name", "exercise", "sets", "reps",
    "equipment", "demo_link", "order"
]

WORKOUT_SET_COLS = [
    "id", "date", "exercise", "set_number", "completed", "weight", "reps_done"
]

WORKOUT_LOG_COLS = [
    "id", "date", "day", "workout_name", "duration_min", "cardio_machine",
    "cardio_min", "notes"
]


def make_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def load_csv(path, cols):
    if path.exists():
        df = pd.read_csv(path)
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)


def save_csv(df, key):
    df.to_csv(FILES[key], index=False)


def numeric(df, cols):
    df = df.copy()
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def week_dates(any_date):
    monday = any_date - timedelta(days=any_date.weekday())
    return {DAYS[i]: monday + timedelta(days=i) for i in range(7)}


def seed_grocery():
    rows = [
        ["Chicken breast", "Protein", "100 g cooked", 165, 31, 0, 4, 0, 0, "Anytime", "High protein; blood sugar friendly; easy prep", "Great for bowls and salads"],
        ["Salmon", "Protein", "100 g cooked", 208, 22, 0, 12, 0, 0, "Dinner; post-workout", "High protein; healthy fats", "Good with vegetables or konjac rice"],
        ["Shrimp", "Protein", "100 g cooked", 99, 24, 0, 0, 0, 0, "Lunch; dinner", "High protein; fast prep", "Good for stir-fry"],
        ["Lean beef", "Protein", "100 g cooked", 217, 26, 0, 12, 0, 0, "Lunch; dinner", "High protein; filling", "Use lean or extra lean"],
        ["Eggs", "Protein", "1 large", 70, 6, 1, 5, 0, 0, "Breakfast; snack", "Easy prep; blood sugar friendly", "Pair with vegetables"],
        ["Greek yogurt plain", "Protein", "170 g", 100, 17, 6, 0, 0, 5, "Breakfast; snack", "High protein; sweet craving option", "Choose unsweetened"],
        ["Cottage cheese", "Protein", "1/2 cup", 110, 13, 5, 5, 0, 4, "Snack; late night", "High protein; filling", "Good with berries"],
        ["Tuna", "Protein", "1 can", 120, 26, 0, 1, 0, 0, "Lunch; snack", "High protein; no cook", "Use with salad bowls"],
        ["Turkey slices", "Protein", "100 g", 110, 20, 2, 2, 0, 1, "Lunch; snack", "Easy prep; high protein", "Watch sodium"],
        ["Protein shake", "Protein", "1 scoop", 120, 24, 3, 2, 0, 1, "Post-workout; snack", "Fast protein", "Useful when protein is low"],

        ["Konjac noodles", "Carb swap", "1 pack", 10, 0, 3, 0, 2, 0, "Lunch; dinner", "Very low carb; fat loss friendly", "Rinse well before cooking"],
        ["Konjac rice", "Carb swap", "1 pack", 10, 0, 3, 0, 2, 0, "Lunch; dinner", "Very low carb; fat loss friendly", "Good with saucy protein"],
        ["Cauliflower rice", "Vegetable", "1 cup", 25, 2, 5, 0, 2, 2, "Lunch; dinner", "Low carb; filling", "Use as rice base"],
        ["Broccoli", "Vegetable", "1 cup", 55, 4, 11, 0, 5, 2, "Lunch; dinner", "High fiber; filling", "Great side"],
        ["Spinach", "Vegetable", "2 cups", 15, 2, 2, 0, 1, 0, "Anytime", "Low calorie; easy add-in", "Good with eggs"],
        ["Mixed vegetables", "Vegetable", "1 cup", 80, 3, 15, 1, 5, 5, "Lunch; dinner", "Easy prep; fiber", "Frozen is fine"],

        ["Sweet potato", "Carb", "150 g", 130, 2, 30, 0, 4, 6, "Post-workout; dinner", "Workout carb; filling", "Best after training"],
        ["Oats", "Carb", "1/2 cup dry", 150, 5, 27, 3, 4, 1, "Breakfast; pre-workout", "Filling; fiber", "Pair with protein"],
        ["Protein cereal", "Limited", "1 serving", 180, 20, 25, 3, 5, 5, "Post-workout; breakfast", "Limited; high protein", "Pair with Greek yogurt"],
        ["Low sugar cereal", "Limited", "1 serving", 150, 4, 28, 2, 3, 6, "Post-workout only", "Limited; occasional", "Add protein to reduce spike"],

        ["Berries", "Fruit", "1 cup", 60, 1, 14, 0, 8, 7, "Breakfast; snack", "Blood sugar friendly; fiber", "Great with yogurt"],
        ["Apple", "Fruit", "1 medium", 95, 0, 25, 0, 4, 19, "Snack; pre-workout", "Pair with protein", "Do not eat alone if cravings spike"],
        ["Pear", "Fruit", "1 medium", 100, 1, 27, 0, 6, 17, "Snack", "Fiber; pair with protein", "Portion controlled"],
        ["Kiwi", "Fruit", "1 fruit", 42, 1, 10, 0, 2, 6, "Snack", "Blood sugar friendly", "Good with yogurt"],
        ["Orange", "Fruit", "1 medium", 62, 1, 15, 0, 3, 12, "Post-workout; snack", "Timed fruit", "Better earlier in day"],

        ["Air popped popcorn", "Snack", "3 cups", 100, 3, 18, 2, 4, 0, "Evening snack", "Low calorie snack", "Avoid buttery version"],
        ["Nuts", "Snack", "1 oz", 170, 6, 6, 15, 3, 1, "Snack", "Healthy fats; portion control", "Measure portion"],
        ["Cheese stick", "Snack", "1 stick", 80, 7, 1, 6, 0, 0, "Snack", "Protein snack", "Pair with fruit"],
        ["Protein bar", "Snack", "1 bar", 200, 20, 20, 7, 8, 3, "Emergency snack", "Convenient; limited", "Choose low sugar"],

        ["White bread", "Limited", "1 slice", 80, 3, 15, 1, 1, 2, "Post-workout only; occasional", "Limited; pair with protein", "Not ideal alone"],
        ["Juice", "Limited", "1 cup", 110, 0, 26, 0, 0, 24, "Avoid; workout only if needed", "Sugar spike risk", "Whole fruit is better"],
        ["Dessert", "Limited", "Small serving", 250, 3, 35, 12, 1, 25, "Occasional; after balanced meal", "Treat; limited", "Avoid on empty stomach"],
    ]

    df = pd.DataFrame(rows, columns=GROCERY_COLS[1:])
    df.insert(0, "id", [make_id("food") for _ in range(len(df))])
    save_csv(df, "grocery")


def seed_meals():
    g = load_csv(FILES["grocery"], GROCERY_COLS)
    g = numeric(g, ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])

    def meal(name, meal_type, foods, timing, tags, instructions):
        selected = g[g["food"].isin(foods)]
        return {
            "id": make_id("meal"),
            "meal_name": name,
            "meal_type": meal_type,
            "items": "; ".join(foods),
            "calories": int(selected["calories"].sum()),
            "protein_g": int(selected["protein_g"].sum()),
            "carbs_g": int(selected["carbs_g"].sum()),
            "fat_g": int(selected["fat_g"].sum()),
            "fiber_g": int(selected["fiber_g"].sum()),
            "sugar_g": int(selected["sugar_g"].sum()),
            "timing": timing,
            "tags": tags,
            "instructions": instructions,
        }

    rows = [
        meal("Chicken Konjac Noodle Stir Fry", "Dinner", ["Chicken breast", "Konjac noodles", "Mixed vegetables"], "Dinner", "High protein; low carb", "Cook chicken, rinse konjac noodles, stir-fry with vegetables and low sugar sauce."),
        meal("Salmon Konjac Rice Bowl", "Dinner", ["Salmon", "Konjac rice", "Broccoli"], "Dinner; post-workout", "High protein; healthy fats", "Cook salmon and broccoli, serve over konjac rice."),
        meal("Shrimp Cauliflower Rice Bowl", "Lunch", ["Shrimp", "Cauliflower rice", "Mixed vegetables"], "Lunch; dinner", "Fast prep; low carb", "Cook shrimp, cauliflower rice, and mixed vegetables together."),
        meal("Lean Beef Veggie Bowl", "Dinner", ["Lean beef", "Cauliflower rice", "Mixed vegetables"], "Dinner", "Filling; high protein", "Cook lean beef, add vegetables and cauliflower rice."),
        meal("Tuna Salad Bowl", "Lunch", ["Tuna", "Spinach", "Broccoli"], "Lunch", "No cook; high protein", "Serve tuna over spinach with broccoli or other vegetables."),
        meal("Egg Spinach Breakfast", "Breakfast", ["Eggs", "Spinach"], "Breakfast", "Easy; blood sugar friendly", "Scramble eggs with spinach."),
        meal("Greek Yogurt Berry Bowl", "Breakfast", ["Greek yogurt plain", "Berries"], "Breakfast; snack", "High protein; sweet craving", "Mix Greek yogurt with berries and cinnamon."),
        meal("Protein Cereal Yogurt Bowl", "Breakfast", ["Protein cereal", "Greek yogurt plain", "Berries"], "Post-workout breakfast", "Limited; workout timing", "Use Greek yogurt as base, add protein cereal and berries."),
        meal("Cottage Cheese Berry Snack", "Snack", ["Cottage cheese", "Berries"], "Snack; late night", "High protein snack", "Add berries to cottage cheese."),
        meal("Protein Shake Apple Snack", "Snack", ["Protein shake", "Apple"], "Pre-workout; snack", "Simple; craving control", "Drink protein shake and eat apple."),
        meal("Chicken Sweet Potato Plate", "Dinner", ["Chicken breast", "Sweet potato", "Broccoli"], "Post-workout dinner", "Balanced; workout carb", "Cook chicken, sweet potato, and broccoli."),
        meal("Turkey Egg Breakfast Plate", "Breakfast", ["Turkey slices", "Eggs", "Spinach"], "Breakfast", "High protein; low carb", "Cook eggs with spinach and serve with turkey slices."),
        meal("Shrimp Konjac Noodle Soup", "Dinner", ["Shrimp", "Konjac noodles", "Spinach"], "Dinner", "Light; high protein", "Simmer shrimp, spinach, broth, and rinsed konjac noodles."),
        meal("Salmon Veggie Plate", "Dinner", ["Salmon", "Mixed vegetables", "Broccoli"], "Dinner", "Low carb; high protein", "Cook salmon and serve with vegetables."),
        meal("Chicken Cauliflower Rice Bowl", "Lunch", ["Chicken breast", "Cauliflower rice", "Mixed vegetables"], "Lunch", "Meal prep friendly", "Cook chicken and serve with cauliflower rice and vegetables."),
        meal("Lean Beef Konjac Rice Bowl", "Dinner", ["Lean beef", "Konjac rice", "Broccoli"], "Dinner", "Filling; lower carb", "Cook lean beef, broccoli, and konjac rice."),
        meal("Greek Yogurt Protein Shake Bowl", "Snack", ["Greek yogurt plain", "Protein shake", "Berries"], "Snack; post-workout", "Very high protein", "Mix protein powder into yogurt and top with berries."),
        meal("Egg Cottage Cheese Plate", "Breakfast", ["Eggs", "Cottage cheese", "Spinach"], "Breakfast", "High protein; filling", "Scramble eggs with spinach and serve with cottage cheese."),
    ]

    save_csv(pd.DataFrame(rows, columns=MEAL_COLS), "meals")


def seed_workout_plan():
    today = date.today()
    dates = week_dates(today)

    demos = {
        "Goblet squat": "https://www.youtube.com/results?search_query=goblet+squat+proper+form",
        "Romanian deadlift": "https://www.youtube.com/results?search_query=dumbbell+romanian+deadlift+proper+form",
        "Cable glute kickback": "https://www.youtube.com/results?search_query=cable+glute+kickback+proper+form",
        "Incline treadmill walk": "https://www.youtube.com/results?search_query=incline+treadmill+walking+fat+loss",
        "Dumbbell shoulder press": "https://www.youtube.com/results?search_query=dumbbell+shoulder+press+proper+form",
        "Dumbbell chest press": "https://www.youtube.com/results?search_query=dumbbell+chest+press+proper+form",
        "Cable fly": "https://www.youtube.com/results?search_query=cable+chest+fly+proper+form",
        "Tricep pushdown": "https://www.youtube.com/results?search_query=cable+tricep+pushdown+proper+form",
        "Cable row": "https://www.youtube.com/results?search_query=cable+row+proper+form",
        "Lat pulldown": "https://www.youtube.com/results?search_query=lat+pulldown+proper+form",
        "Face pull": "https://www.youtube.com/results?search_query=cable+face+pull+proper+form",
        "Bicep curls": "https://www.youtube.com/results?search_query=dumbbell+bicep+curl+proper+form",
        "Upright bike intervals": "https://www.youtube.com/results?search_query=stationary+bike+interval+workout+beginner",
        "Abs machine crunch": "https://www.youtube.com/results?search_query=ab+crunch+machine+proper+form",
        "Cable crunch": "https://www.youtube.com/results?search_query=cable+crunch+proper+form",
        "Plank": "https://www.youtube.com/results?search_query=plank+proper+form",
        "Dumbbell squat press": "https://www.youtube.com/results?search_query=dumbbell+squat+to+press+proper+form",
        "Elliptical steady state": "https://www.youtube.com/results?search_query=elliptical+steady+state+cardio",
    }

    template = {
        "Monday": ("Lower Body + Incline Walk", [
            ("Goblet squat", 3, "8-12", "Dumbbell"),
            ("Romanian deadlift", 3, "8-12", "Barbell or dumbbells"),
            ("Cable glute kickback", 3, "12-15 each leg", "Cable"),
            ("Incline treadmill walk", 1, "20-30 min", "Treadmill"),
        ]),
        "Tuesday": ("Upper Push", [
            ("Dumbbell shoulder press", 3, "8-12", "Dumbbells"),
            ("Dumbbell chest press", 3, "8-12", "Dumbbells"),
            ("Cable fly", 3, "12-15", "Cable"),
            ("Tricep pushdown", 3, "10-15", "Cable"),
        ]),
        "Wednesday": ("Conditioning + Core", [
            ("Upright bike intervals", 1, "15-20 min", "Upright bike"),
            ("Abs machine crunch", 3, "10-15", "Abs machine"),
            ("Cable crunch", 3, "12-15", "Cable"),
            ("Plank", 3, "30-45 sec", "Bodyweight"),
        ]),
        "Thursday": ("Upper Pull", [
            ("Cable row", 3, "8-12", "Cable"),
            ("Lat pulldown", 3, "8-12", "Cable"),
            ("Face pull", 3, "12-15", "Cable"),
            ("Bicep curls", 3, "10-12", "Dumbbells"),
        ]),
        "Friday": ("Full Body Metabolic", [
            ("Dumbbell squat press", 3, "10", "Dumbbells"),
            ("Romanian deadlift", 3, "10", "Barbell or dumbbells"),
            ("Cable row", 3, "12", "Cable"),
            ("Upright bike intervals", 1, "10-15 min", "Upright bike"),
            ("Abs machine crunch", 2, "12-15", "Abs machine"),
        ]),
        "Saturday": ("Recovery Cardio", [
            ("Elliptical steady state", 1, "25-45 min", "Elliptical"),
            ("Plank", 2, "30 sec", "Bodyweight"),
        ]),
        "Sunday": ("Rest / Optional Walk", [
            ("Incline treadmill walk", 1, "15-30 min easy", "Treadmill"),
        ]),
    }

    rows = []
    for day, (workout_name, exercises) in template.items():
        for i, (exercise, sets, reps, equipment) in enumerate(exercises, start=1):
            rows.append({
                "id": make_id("wp"),
                "date": str(dates[day]),
                "day": day,
                "workout_name": workout_name,
                "exercise": exercise,
                "sets": sets,
                "reps": reps,
                "equipment": equipment,
                "demo_link": demos.get(exercise, "https://www.youtube.com/results?search_query=" + exercise.replace(" ", "+") + "+proper+form"),
                "order": i,
            })

    save_csv(pd.DataFrame(rows, columns=WORKOUT_PLAN_COLS), "workout_plan")


def initialize():
    if not FILES["grocery"].exists():
        seed_grocery()
    if not FILES["meals"].exists():
        seed_meals()
    if not FILES["weekly_plan"].exists():
        save_csv(pd.DataFrame(columns=WEEKLY_PLAN_COLS), "weekly_plan")
    if not FILES["meal_log"].exists():
        save_csv(pd.DataFrame(columns=MEAL_LOG_COLS), "meal_log")
    if not FILES["workout_plan"].exists():
        seed_workout_plan()
    if not FILES["workout_sets"].exists():
        save_csv(pd.DataFrame(columns=WORKOUT_SET_COLS), "workout_sets")
    if not FILES["workout_log"].exists():
        save_csv(pd.DataFrame(columns=WORKOUT_LOG_COLS), "workout_log")


initialize()

grocery = numeric(load_csv(FILES["grocery"], GROCERY_COLS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
meals = numeric(load_csv(FILES["meals"], MEAL_COLS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
weekly = numeric(load_csv(FILES["weekly_plan"], WEEKLY_PLAN_COLS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
meal_log = numeric(load_csv(FILES["meal_log"], MEAL_LOG_COLS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
workout_plan = load_csv(FILES["workout_plan"], WORKOUT_PLAN_COLS)
workout_sets = load_csv(FILES["workout_sets"], WORKOUT_SET_COLS)
workout_log = load_csv(FILES["workout_log"], WORKOUT_LOG_COLS)

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; max-width: 1150px;}
.card {border: 1px solid rgba(128,128,128,.25); border-radius: 18px; padding: 14px; margin-bottom: 12px; background: rgba(128,128,128,.06);}
.title {font-weight: 800; font-size: 1.05rem;}
.muted {color: #888; font-size: .9rem;}
.pill {display: inline-block; border: 1px solid rgba(128,128,128,.25); border-radius: 999px; padding: 3px 9px; margin: 3px 3px 0 0; font-size: .78rem;}
@media(max-width:768px){div[data-testid="column"]{width:100%!important; flex:1 1 100%!important;} button{width:100%;}}
</style>
""", unsafe_allow_html=True)

st.title("Fitness + Meal Planner")

tabs = st.tabs(["Home", "Grocery", "Weekly Meals", "Daily Log", "Workouts", "Settings"])


with tabs[0]:
    st.subheader("Main flow")
    st.write("Grocery → choose meals/ingredients → weekly plan → daily log.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Grocery foods", len(grocery))
    c2.metric("Meals", len(meals))
    c3.metric("Planned meals", len(weekly))
    c4.metric("Logged meals", len(meal_log))


with tabs[1]:
    st.subheader("Grocery Hub")
    st.write("No wraps included. Meals are built around protein, vegetables, konjac rice/noodles, smart carbs, and blood-sugar-friendly snacks.")

    planning_week = st.date_input("Planning week", date.today(), key="planning_week")
    dates = week_dates(planning_week)

    mode = st.radio("Choose from:", ["Meals", "Individual ingredients", "Grocery list"], horizontal=True)

    if mode == "Meals":
        meal_type_filter = st.selectbox("Meal type", ["All"] + MEAL_TYPES)
        search = st.text_input("Search meals")

        display = meals.copy()
        if meal_type_filter != "All":
            display = display[display["meal_type"] == meal_type_filter]
        if search:
            display = display[display.apply(lambda r: search.lower() in " ".join(r.astype(str)).lower(), axis=1)]

        for _, meal in display.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="title">{meal['meal_name']}</div>
                <div class="muted">{meal['items']}</div>
                <span class="pill">{meal['meal_type']}</span>
                <span class="pill">{int(meal['calories'])} cal</span>
                <span class="pill">{int(meal['protein_g'])}g protein</span>
                <span class="pill">{meal['timing']}</span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Add {meal['meal_name']} to week"):
                c1, c2 = st.columns(2)
                day = c1.selectbox("Day", DAYS, key=f"day_{meal['id']}")
                meal_type = c2.selectbox("Meal type", MEAL_TYPES, index=MEAL_TYPES.index(meal["meal_type"]), key=f"type_{meal['id']}")
                notes = st.text_input("Notes", key=f"notes_{meal['id']}")

                if st.button("Add to weekly meal plan", key=f"add_{meal['id']}"):
                    row = {
                        "id": make_id("plan"),
                        "date": str(dates[day]),
                        "day": day,
                        "meal_type": meal_type,
                        "meal_id": meal["id"],
                        "meal_name": meal["meal_name"],
                        "items": meal["items"],
                        "calories": meal["calories"],
                        "protein_g": meal["protein_g"],
                        "carbs_g": meal["carbs_g"],
                        "fat_g": meal["fat_g"],
                        "fiber_g": meal["fiber_g"],
                        "sugar_g": meal["sugar_g"],
                        "status": "Planned",
                        "notes": notes,
                    }
                    weekly = pd.concat([weekly, pd.DataFrame([row])], ignore_index=True)
                    save_csv(weekly, "weekly_plan")
                    st.success("Added to weekly plan.")
                    st.rerun()

    elif mode == "Individual ingredients":
        selected = st.multiselect("Select ingredients", grocery["food"].tolist())
        meal_name = st.text_input("Meal name", placeholder="e.g., Chicken konjac rice bowl")
        meal_type = st.selectbox("Meal type", MEAL_TYPES, key="ingredient_meal_type")
        day = st.selectbox("Day", DAYS, key="ingredient_day")

        if selected:
            picked = grocery[grocery["food"].isin(selected)]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", int(picked["calories"].sum()))
            c2.metric("Protein", f"{int(picked['protein_g'].sum())}g")
            c3.metric("Carbs", f"{int(picked['carbs_g'].sum())}g")
            c4.metric("Fat", f"{int(picked['fat_g'].sum())}g")

            if st.button("Add ingredient-built meal to weekly plan"):
                name = meal_name if meal_name else "Custom grocery meal"
                row = {
                    "id": make_id("plan"),
                    "date": str(dates[day]),
                    "day": day,
                    "meal_type": meal_type,
                    "meal_id": "",
                    "meal_name": name,
                    "items": "; ".join(selected),
                    "calories": int(picked["calories"].sum()),
                    "protein_g": int(picked["protein_g"].sum()),
                    "carbs_g": int(picked["carbs_g"].sum()),
                    "fat_g": int(picked["fat_g"].sum()),
                    "fiber_g": int(picked["fiber_g"].sum()),
                    "sugar_g": int(picked["sugar_g"].sum()),
                    "status": "Planned",
                    "notes": "",
                }
                weekly = pd.concat([weekly, pd.DataFrame([row])], ignore_index=True)
                save_csv(weekly, "weekly_plan")
                st.success("Added to weekly plan.")
                st.rerun()

    else:
        category = st.selectbox("Category", ["All"] + sorted(grocery["category"].unique().tolist()))
        display = grocery if category == "All" else grocery[grocery["category"] == category]

        for _, food in display.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="title">{food['food']}</div>
                <div class="muted">{food['serving']} • {food['category']}</div>
                <span class="pill">{int(food['calories'])} cal</span>
                <span class="pill">{int(food['protein_g'])}g protein</span>
                <span class="pill">{int(food['carbs_g'])}g carbs</span>
                <span class="pill">{food['timing']}</span>
                <div class="muted">{food['tags']}</div>
            </div>
            """, unsafe_allow_html=True)


with tabs[2]:
    st.subheader("Weekly Meal Plan")
    selected_week = st.date_input("Week", date.today(), key="meal_week")
    dates = week_dates(selected_week)

    temp = weekly.copy()
    if not temp.empty:
        temp["date_dt"] = pd.to_datetime(temp["date"], errors="coerce").dt.date
        temp = temp[(temp["date_dt"] >= dates["Monday"]) & (temp["date_dt"] <= dates["Sunday"])]

    if temp.empty:
        st.info("No meals planned yet.")
    else:
        for day in DAYS:
            day_df = temp[temp["day"] == day]
            with st.expander(f"{day} — {dates[day]}", expanded=(day == date.today().strftime("%A"))):
                if day_df.empty:
                    st.write("No meals planned.")
                else:
                    for _, row in day_df.iterrows():
                        st.markdown(f"""
                        <div class="card">
                            <div class="title">{row['meal_type']}: {row['meal_name']}</div>
                            <div class="muted">{row['items']}</div>
                            <span class="pill">{int(row['calories'])} cal</span>
                            <span class="pill">{int(row['protein_g'])}g protein</span>
                            <span class="pill">{row['status']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        c1, c2 = st.columns(2)
                        if c1.button("Log meal", key=f"log_meal_{row['id']}"):
                            log = {
                                "id": make_id("log"),
                                "date": row["date"],
                                "day": row["day"],
                                "meal_type": row["meal_type"],
                                "meal_name": row["meal_name"],
                                "items": row["items"],
                                "calories": row["calories"],
                                "protein_g": row["protein_g"],
                                "carbs_g": row["carbs_g"],
                                "fat_g": row["fat_g"],
                                "fiber_g": row["fiber_g"],
                                "sugar_g": row["sugar_g"],
                                "notes": row["notes"],
                            }
                            meal_log = pd.concat([meal_log, pd.DataFrame([log])], ignore_index=True)
                            save_csv(meal_log, "meal_log")
                            weekly.loc[weekly["id"] == row["id"], "status"] = "Logged"
                            save_csv(weekly, "weekly_plan")
                            st.success("Meal logged.")
                            st.rerun()

                        if c2.button("Delete", key=f"delete_meal_{row['id']}"):
                            weekly = weekly[weekly["id"] != row["id"]]
                            save_csv(weekly, "weekly_plan")
                            st.success("Deleted.")
                            st.rerun()


with tabs[3]:
    st.subheader("Daily Food Log")
    selected_date = st.date_input("Date", date.today(), key="daily_date")
    today_log = meal_log[meal_log["date"].astype(str) == str(selected_date)]

    if today_log.empty:
        st.info("No meals logged for this date.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", int(today_log["calories"].sum()))
        c2.metric("Protein", f"{int(today_log['protein_g'].sum())}g")
        c3.metric("Carbs", f"{int(today_log['carbs_g'].sum())}g")
        c4.metric("Fat", f"{int(today_log['fat_g'].sum())}g")

        for _, row in today_log.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="title">{row['meal_type']}: {row['meal_name']}</div>
                <div class="muted">{row['items']}</div>
                <span class="pill">{int(row['calories'])} cal</span>
                <span class="pill">{int(row['protein_g'])}g protein</span>
            </div>
            """, unsafe_allow_html=True)


with tabs[4]:
    st.subheader("Workout Week")

    workout_plan["date_dt"] = pd.to_datetime(workout_plan["date"], errors="coerce").dt.date
    workout_plan["order"] = pd.to_numeric(workout_plan["order"], errors="coerce").fillna(0)

    today = date.today()
    future = workout_plan[workout_plan["date_dt"] >= today].sort_values(["date_dt", "order"])
    past = workout_plan[workout_plan["date_dt"] < today].sort_values(["date_dt", "order"], ascending=[False, True])

    def render_workout_day(day_df, title):
        st.markdown(f"### {title}")
        grouped = day_df.groupby(["date", "day", "workout_name"], sort=False)

        for (workout_date, day_name, workout_name), group in grouped:
            with st.expander(f"{day_name}, {workout_date} — {workout_name}", expanded=(str(workout_date) == str(today))):
                for _, ex in group.iterrows():
                    st.markdown(f"""
                    <div class="card">
                        <div class="title">{ex['exercise']}</div>
                        <div class="muted">{ex['equipment']} • {ex['sets']} sets • {ex['reps']} reps</div>
                        <a href="{ex['demo_link']}" target="_blank">Exercise demo</a>
                    </div>
                    """, unsafe_allow_html=True)

                    sets = int(float(ex["sets"]))
                    for set_no in range(1, sets + 1):
                        key = f"{ex['date']}_{ex['exercise']}_{set_no}"
                        existing = workout_sets[
                            (workout_sets["date"].astype(str) == str(ex["date"])) &
                            (workout_sets["exercise"].astype(str) == str(ex["exercise"])) &
                            (workout_sets["set_number"].astype(str) == str(set_no))
                        ]

                        already_done = False
                        if not existing.empty:
                            already_done = str(existing.iloc[-1]["completed"]) == "True"

                        checked = st.checkbox(
                            f"Set {set_no} complete",
                            value=already_done,
                            key=key
                        )

                        if checked != already_done:
                            workout_sets_new = workout_sets[
                                ~(
                                    (workout_sets["date"].astype(str) == str(ex["date"])) &
                                    (workout_sets["exercise"].astype(str) == str(ex["exercise"])) &
                                    (workout_sets["set_number"].astype(str) == str(set_no))
                                )
                            ]

                            new_set = {
                                "id": make_id("set"),
                                "date": ex["date"],
                                "exercise": ex["exercise"],
                                "set_number": set_no,
                                "completed": checked,
                                "weight": "",
                                "reps_done": "",
                            }

                            workout_sets_new = pd.concat([workout_sets_new, pd.DataFrame([new_set])], ignore_index=True)
                            save_csv(workout_sets_new, "workout_sets")
                            st.rerun()

                st.markdown("#### Finish workout log")
                c1, c2, c3 = st.columns(3)
                duration = c1.number_input("Duration min", min_value=0, step=5, key=f"dur_{workout_date}_{workout_name}")
                cardio_machine = c2.selectbox("Cardio", ["None", "Treadmill", "Elliptical", "Upright bike"], key=f"cardio_{workout_date}_{workout_name}")
                cardio_min = c3.number_input("Cardio min", min_value=0, step=5, key=f"cardio_min_{workout_date}_{workout_name}")
                notes = st.text_area("Notes", key=f"notes_{workout_date}_{workout_name}")

                if st.button("Save workout log", key=f"save_workout_{workout_date}_{workout_name}"):
                    log = {
                        "id": make_id("workout"),
                        "date": workout_date,
                        "day": day_name,
                        "workout_name": workout_name,
                        "duration_min": duration,
                        "cardio_machine": cardio_machine,
                        "cardio_min": cardio_min,
                        "notes": notes,
                    }
                    new_log = pd.concat([workout_log, pd.DataFrame([log])], ignore_index=True)
                    save_csv(new_log, "workout_log")
                    st.success("Workout saved.")
                    st.rerun()

    if not future.empty:
        render_workout_day(future, "Today + Upcoming Workouts")
    else:
        st.info("No upcoming workouts. Use Settings to reset this week’s workout plan.")

    if not past.empty:
        render_workout_day(past, "Past Workouts")

    st.subheader("Saved workout logs")
    if workout_log.empty:
        st.info("No saved workout logs yet.")
    else:
        st.dataframe(workout_log.drop(columns=["id"], errors="ignore"), use_container_width=True)


with tabs[5]:
    st.subheader("Settings")

    if st.button("Reset grocery + meals with no wraps"):
        seed_grocery()
        seed_meals()
        st.success("Reset grocery and meals. Wraps removed.")
        st.rerun()

    if st.button("Reset workout week"):
        seed_workout_plan()
        save_csv(pd.DataFrame(columns=WORKOUT_SET_COLS), "workout_sets")
        st.success("Workout week reset.")
        st.rerun()

    if st.button("Clear meal plan"):
        save_csv(pd.DataFrame(columns=WEEKLY_PLAN_COLS), "weekly_plan")
        st.success("Meal plan cleared.")
        st.rerun()

    if st.button("Clear meal logs"):
        save_csv(pd.DataFrame(columns=MEAL_LOG_COLS), "meal_log")
        st.success("Meal logs cleared.")
        st.rerun()

    if st.button("Clear workout logs"):
        save_csv(pd.DataFrame(columns=WORKOUT_LOG_COLS), "workout_log")
        st.success("Workout logs cleared.")
        st.rerun()

    st.code("streamlit run fitness_app.py", language="bash")
