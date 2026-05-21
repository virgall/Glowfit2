# complete_fitness_meal_dashboard.py
# Full Streamlit Fitness + Meal Dashboard
# Flow: Grocery Hub -> Weekly Plan -> Daily Meals -> Workouts -> Progress
# Saves data locally in CSV files inside ./fitness_dashboard_data

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta
import uuid

st.set_page_config(
    page_title="Fitness + Meal Dashboard",
    page_icon="🥗",
    layout="wide"
)

DATA_DIR = Path("fitness_dashboard_data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "grocery": DATA_DIR / "grocery.csv",
    "saved_meals": DATA_DIR / "saved_meals.csv",
    "weekly_plan": DATA_DIR / "weekly_plan.csv",
    "meal_log": DATA_DIR / "meal_log.csv",
    "workout_log": DATA_DIR / "workout_log.csv",
    "body_log": DATA_DIR / "body_log.csv",
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

EQUIPMENT = [
    "Barbell + plates",
    "Dumbbells",
    "Cable functional trainer",
    "Treadmill",
    "Elliptical",
    "Upright bike",
    "Abs machine",
]

GROCERY_COLUMNS = [
    "id", "food", "category", "serving", "calories", "protein_g", "carbs_g",
    "fat_g", "fiber_g", "sugar_g", "prep_time", "blood_sugar_rating",
    "fat_loss_rating", "timing", "tags", "notes"
]

SAVED_MEAL_COLUMNS = [
    "id", "meal_name", "meal_type", "items", "calories", "protein_g", "carbs_g",
    "fat_g", "fiber_g", "sugar_g", "prep_time", "blood_sugar_rating",
    "fat_loss_rating", "timing", "tags", "instructions", "notes"
]

WEEKLY_PLAN_COLUMNS = [
    "id", "day", "date", "meal_type", "meal_id", "meal_name", "calories",
    "protein_g", "carbs_g", "fat_g", "status", "notes"
]

MEAL_LOG_COLUMNS = [
    "id", "date", "day", "meal_type", "source", "meal_id", "meal_name", "items",
    "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "notes"
]

WORKOUT_LOG_COLUMNS = [
    "id", "date", "day", "workout_name", "mode", "equipment", "duration_min",
    "cardio_machine", "cardio_min", "intensity", "exercises", "notes"
]

BODY_LOG_COLUMNS = [
    "id", "date", "weight_lb", "waist_in", "hips_in", "chest_in", "energy",
    "sleep_hours", "notes"
]

st.markdown("""
<style>
.main .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
div[data-testid="stMetric"] {
    border: 1px solid rgba(120,120,120,0.2);
    padding: 14px;
    border-radius: 14px;
}
.small-note {
    color: #777;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


def make_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def load_csv(path, columns):
    if path.exists():
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]
        except Exception:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)


def save_csv(df, key):
    df.to_csv(FILES[key], index=False)


def num(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def seed_grocery():
    rows = [
        ["Chicken breast", "Protein", "100 g cooked", 165, 31, 0, 4, 0, 0, "15-25 min", "Excellent", "Excellent", "Anytime", "High protein; Blood sugar friendly; Easy prep", "Good for bowls, wraps, salads"],
        ["Salmon", "Protein", "100 g cooked", 208, 22, 0, 12, 0, 0, "15-25 min", "Excellent", "Great", "Dinner; Post-workout", "High protein; Healthy fats", "Pair with vegetables or konjac rice"],
        ["Shrimp", "Protein", "100 g cooked", 99, 24, 0, 0, 0, 0, "10 min", "Excellent", "Excellent", "Anytime", "High protein; Fast meal", "Good for stir fry"],
        ["Lean ground beef", "Protein", "100 g cooked", 217, 26, 0, 12, 0, 0, "15 min", "Excellent", "Good", "Lunch; Dinner", "High protein; Filling", "Use lean or extra lean"],
        ["Eggs", "Protein", "1 large", 70, 6, 1, 5, 0, 0, "5-10 min", "Excellent", "Great", "Breakfast; Snack", "Easy prep; Blood sugar friendly", "Pair with vegetables"],
        ["Greek yogurt plain", "Protein", "170 g", 100, 17, 6, 0, 0, 5, "2 min", "Great", "Excellent", "Breakfast; Snack", "High protein; Sweet craving option", "Choose unsweetened"],
        ["Cottage cheese", "Protein", "1/2 cup", 110, 13, 5, 5, 0, 4, "1 min", "Great", "Great", "Snack; Late night", "High protein; Filling", "Good with berries"],
        ["Tuna", "Protein", "1 can", 120, 26, 0, 1, 0, 0, "2 min", "Excellent", "Excellent", "Lunch; Snack", "High protein; No cook", "Use with wraps or salad"],
        ["Turkey slices", "Protein", "100 g", 110, 20, 2, 2, 0, 1, "1 min", "Great", "Great", "Lunch; Snack", "Easy prep; High protein", "Watch sodium"],
        ["Protein shake", "Protein", "1 scoop", 120, 24, 3, 2, 0, 1, "1 min", "Great", "Great", "Post-workout; Snack", "Fast protein; Easy", "Use when protein is low"],

        ["Konjac noodles", "Carb swap", "1 pack", 10, 0, 3, 0, 2, 0, "5 min", "Excellent", "Excellent", "Lunch; Dinner", "Very low carb; Fat loss friendly", "Rinse well before cooking"],
        ["Konjac rice", "Carb swap", "1 pack", 10, 0, 3, 0, 2, 0, "5 min", "Excellent", "Excellent", "Lunch; Dinner", "Very low carb; Fat loss friendly", "Best with saucy proteins"],
        ["High protein wrap", "Carb", "1 wrap", 120, 10, 18, 3, 8, 1, "1 min", "Good", "Great", "Lunch; Post-workout", "High fiber; Convenient", "Use for chicken/tuna wraps"],
        ["Sweet potato", "Carb", "150 g", 130, 2, 30, 0, 4, 6, "20-35 min", "Good", "Good", "Post-workout; Dinner", "Workout carb; Filling", "Best after training"],
        ["Oats", "Carb", "1/2 cup dry", 150, 5, 27, 3, 4, 1, "5 min", "Good", "Good", "Breakfast; Pre-workout", "Filling; Fiber", "Pair with protein"],
        ["Protein cereal", "Limited", "1 serving", 180, 20, 25, 3, 5, 5, "1 min", "Moderate", "Good", "Post-workout; Breakfast", "Limited; Best after workout", "Pair with Greek yogurt or protein milk"],
        ["Low sugar cereal", "Limited", "1 serving", 150, 4, 28, 2, 3, 6, "1 min", "Moderate", "Moderate", "Post-workout only", "Limited; Use occasionally", "Add protein to reduce sugar spike"],

        ["Berries", "Fruit", "1 cup", 60, 1, 14, 0, 8, 7, "1 min", "Excellent", "Excellent", "Breakfast; Snack", "Blood sugar friendly; Fiber", "Great with yogurt"],
        ["Apple", "Fruit", "1 medium", 95, 0, 25, 0, 4, 19, "1 min", "Good", "Good", "Snack; Pre-workout", "Pair with protein", "Add peanut butter or yogurt"],
        ["Pear", "Fruit", "1 medium", 100, 1, 27, 0, 6, 17, "1 min", "Good", "Good", "Snack", "Fiber; Pair with protein", "Good portion-controlled fruit"],
        ["Kiwi", "Fruit", "1 fruit", 42, 1, 10, 0, 2, 6, "1 min", "Great", "Great", "Snack", "Vitamin C; Blood sugar friendly", "Good with yogurt"],
        ["Orange", "Fruit", "1 medium", 62, 1, 15, 0, 3, 12, "1 min", "Good", "Good", "Post-workout; Snack", "Limited timing; Hydrating", "Better earlier in day or post-workout"],

        ["Broccoli", "Vegetable", "1 cup", 55, 4, 11, 0, 5, 2, "5-10 min", "Excellent", "Excellent", "Lunch; Dinner", "High fiber; Filling", "Add to bowls"],
        ["Spinach", "Vegetable", "2 cups", 15, 2, 2, 0, 1, 0, "2 min", "Excellent", "Excellent", "Anytime", "Low calorie; Easy add-in", "Add to eggs/smoothies"],
        ["Cauliflower rice", "Vegetable", "1 cup", 25, 2, 5, 0, 2, 2, "5 min", "Excellent", "Excellent", "Lunch; Dinner", "Low carb; Filling", "Use as rice base"],
        ["Mixed vegetables", "Vegetable", "1 cup", 80, 3, 15, 1, 5, 5, "5-10 min", "Excellent", "Excellent", "Lunch; Dinner", "Easy prep; Fiber", "Frozen is fine"],

        ["Air popped popcorn", "Snack", "3 cups", 100, 3, 18, 2, 4, 0, "3 min", "Good", "Great", "Snack; Evening", "Low calorie snack", "Avoid buttery versions"],
        ["Nuts", "Snack", "1 oz", 170, 6, 6, 15, 3, 1, "1 min", "Excellent", "Moderate", "Snack", "Healthy fats; Portion control", "Measure portion"],
        ["Cheese stick", "Snack", "1 stick", 80, 7, 1, 6, 0, 0, "1 min", "Excellent", "Good", "Snack", "Protein snack", "Pair with fruit"],
        ["Protein bar", "Snack", "1 bar", 200, 20, 20, 7, 8, 3, "1 min", "Good", "Good", "Snack; Emergency", "Convenient; Limited", "Choose low sugar"],

        ["White bread", "Limited", "1 slice", 80, 3, 15, 1, 1, 2, "1 min", "Limited", "Limited", "Post-workout only; Occasional", "Limited; Pair with protein", "Not ideal alone"],
        ["Juice", "Limited", "1 cup", 110, 0, 26, 0, 0, 24, "1 min", "Limited", "Limited", "Avoid; Use only around workout if needed", "Limited; Sugar spike risk", "Whole fruit is better"],
        ["Dessert", "Limited", "1 small serving", 250, 3, 35, 12, 1, 25, "0 min", "Limited", "Limited", "Occasional; After balanced meal", "Limited; Treat", "Avoid eating alone on empty stomach"],
        ["Fries", "Limited", "Small", 300, 4, 40, 15, 4, 0, "0 min", "Limited", "Limited", "Occasional; After workout if desired", "Limited; High calorie", "Portion control"],
    ]

    df = pd.DataFrame(rows, columns=GROCERY_COLUMNS[1:])
    df.insert(0, "id", [make_id("food") for _ in range(len(df))])
    save_csv(df, "grocery")


def seed_saved_meals():
    g = load_csv(FILES["grocery"], GROCERY_COLUMNS)

    def combine(meal_name, meal_type, foods, instructions, timing="Anytime", tags="Easy prep"):
        selected = g[g["food"].isin(foods)]
        return {
            "id": make_id("meal"),
            "meal_name": meal_name,
            "meal_type": meal_type,
            "items": "; ".join(foods),
            "calories": int(selected["calories"].astype(float).sum()) if not selected.empty else 0,
            "protein_g": int(selected["protein_g"].astype(float).sum()) if not selected.empty else 0,
            "carbs_g": int(selected["carbs_g"].astype(float).sum()) if not selected.empty else 0,
            "fat_g": int(selected["fat_g"].astype(float).sum()) if not selected.empty else 0,
            "fiber_g": int(selected["fiber_g"].astype(float).sum()) if not selected.empty else 0,
            "sugar_g": int(selected["sugar_g"].astype(float).sum()) if not selected.empty else 0,
            "prep_time": "5-25 min",
            "blood_sugar_rating": "Great",
            "fat_loss_rating": "Great",
            "timing": timing,
            "tags": tags,
            "instructions": instructions,
            "notes": ""
        }

    rows = [
        combine("Chicken Konjac Noodle Stir Fry", "Dinner", ["Chicken breast", "Konjac noodles", "Mixed vegetables"], "Cook chicken, rinse konjac noodles, stir fry with mixed vegetables and low sugar sauce.", "Dinner", "High protein; Low carb; Fat loss friendly"),
        combine("Greek Yogurt Berry Bowl", "Breakfast", ["Greek yogurt plain", "Berries"], "Mix plain Greek yogurt with berries. Add cinnamon if desired.", "Breakfast; Snack", "High protein; Blood sugar friendly"),
        combine("Protein Cereal Bowl", "Breakfast", ["Protein cereal", "Greek yogurt plain", "Berries"], "Use Greek yogurt as the base and add protein cereal and berries.", "Post-workout; Breakfast", "Limited food timing; High protein"),
        combine("Salmon + Konjac Rice Bowl", "Dinner", ["Salmon", "Konjac rice", "Broccoli"], "Cook salmon, steam broccoli, serve over konjac rice.", "Dinner; Post-workout", "High protein; Healthy fats"),
        combine("Shrimp Cauliflower Rice Bowl", "Lunch", ["Shrimp", "Cauliflower rice", "Mixed vegetables"], "Cook shrimp and vegetables, serve with cauliflower rice.", "Lunch; Dinner", "Low carb; Fast meal"),
        combine("Tuna Protein Wrap", "Lunch", ["Tuna", "High protein wrap", "Spinach"], "Mix tuna with seasoning, add spinach, wrap and serve.", "Lunch", "No cook; High protein"),
        combine("Egg + Spinach Breakfast", "Breakfast", ["Eggs", "Spinach"], "Scramble eggs with spinach.", "Breakfast", "Easy prep; Blood sugar friendly"),
        combine("Lean Beef Vegetable Bowl", "Dinner", ["Lean ground beef", "Mixed vegetables", "Cauliflower rice"], "Cook lean beef, add vegetables and cauliflower rice.", "Dinner", "Filling; High protein"),
        combine("Cottage Cheese Fruit Snack", "Snack", ["Cottage cheese", "Berries"], "Add berries to cottage cheese.", "Snack; Late night", "High protein snack"),
        combine("Post Workout Sweet Potato Plate", "Dinner", ["Chicken breast", "Sweet potato", "Broccoli"], "Cook chicken, sweet potato and broccoli. Best after a harder workout.", "Post-workout", "Workout carb; Balanced"),
        combine("Quick Turkey Wrap", "Lunch", ["Turkey slices", "High protein wrap", "Spinach"], "Add turkey and spinach to a wrap. Add low sugar sauce if desired.", "Lunch", "Fast; Work lunch"),
        combine("Protein Shake + Apple", "Snack", ["Protein shake", "Apple"], "Drink protein shake and pair with an apple.", "Pre-workout; Snack", "Simple; Craving control"),
    ]
    save_csv(pd.DataFrame(rows, columns=SAVED_MEAL_COLUMNS), "saved_meals")


def initialize_files():
    if not FILES["grocery"].exists():
        seed_grocery()
    if not FILES["saved_meals"].exists():
        seed_saved_meals()
    for key, cols in [
        ("weekly_plan", WEEKLY_PLAN_COLUMNS),
        ("meal_log", MEAL_LOG_COLUMNS),
        ("workout_log", WORKOUT_LOG_COLUMNS),
        ("body_log", BODY_LOG_COLUMNS),
    ]:
        if not FILES[key].exists():
            save_csv(pd.DataFrame(columns=cols), key)


initialize_files()

grocery_df = load_csv(FILES["grocery"], GROCERY_COLUMNS)
saved_meals_df = load_csv(FILES["saved_meals"], SAVED_MEAL_COLUMNS)
weekly_plan_df = load_csv(FILES["weekly_plan"], WEEKLY_PLAN_COLUMNS)
meal_log_df = load_csv(FILES["meal_log"], MEAL_LOG_COLUMNS)
workout_log_df = load_csv(FILES["workout_log"], WORKOUT_LOG_COLUMNS)
body_log_df = load_csv(FILES["body_log"], BODY_LOG_COLUMNS)


def rerun():
    st.rerun()


def meal_by_id(meal_id):
    match = saved_meals_df[saved_meals_df["id"] == meal_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_week_dates(start_date):
    start = start_date - timedelta(days=start_date.weekday())
    return {DAYS[i]: start + timedelta(days=i) for i in range(7)}


def add_to_meal_log(log_date, meal_type, meal, source="Planned"):
    global meal_log_df
    log_date = pd.to_datetime(log_date).date()
    new = {
        "id": make_id("log"),
        "date": str(log_date),
        "day": log_date.strftime("%A"),
        "meal_type": meal_type,
        "source": source,
        "meal_id": meal.get("id", ""),
        "meal_name": meal.get("meal_name", ""),
        "items": meal.get("items", ""),
        "calories": meal.get("calories", 0),
        "protein_g": meal.get("protein_g", 0),
        "carbs_g": meal.get("carbs_g", 0),
        "fat_g": meal.get("fat_g", 0),
        "fiber_g": meal.get("fiber_g", 0),
        "sugar_g": meal.get("sugar_g", 0),
        "notes": meal.get("notes", ""),
    }
    meal_log_df = pd.concat([meal_log_df, pd.DataFrame([new])], ignore_index=True)
    save_csv(meal_log_df, "meal_log")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Fitness Dashboard")
page = st.sidebar.radio(
    "Choose dashboard",
    [
        "Home",
        "Grocery Hub",
        "Saved Meals",
        "Weekly Plan",
        "Daily Meals",
        "Workouts",
        "Progress",
        "Settings / Reset"
    ]
)

st.sidebar.markdown("### Goal")
st.sidebar.write("Fat loss, prediabetic-friendly meals, quality food, less prep time.")

st.sidebar.markdown("### Equipment")
st.sidebar.write(", ".join(EQUIPMENT))


# =========================================================
# HOME
# =========================================================

if page == "Home":
    st.title("Fitness + Meal Dashboard")
    st.write("Main flow: Grocery Hub → Saved Meals → Weekly Plan → Daily Meals → Progress")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Grocery Foods", len(grocery_df))
    c2.metric("Saved Meals", len(saved_meals_df))
    c3.metric("Planned Meals", len(weekly_plan_df))
    c4.metric("Logged Meals", len(meal_log_df))

    st.subheader("How to use it")
    st.markdown("""
    1. Start in **Grocery Hub**. This is your main food source.
    2. Create meals in **Saved Meals** using grocery foods.
    3. Build your week in **Weekly Plan**.
    4. Go to **Daily Meals** to log planned meals or manual meals.
    5. Log workouts and body progress under **Workouts** and **Progress**.
    """)

    st.subheader("Smart design choices")
    st.markdown("""
    - Cereal and other higher-carb foods are marked as **Limited** and timed around workouts.
    - Konjac rice and konjac noodles are included as low-carb swaps.
    - Fruits are chosen with blood sugar and fat loss in mind: berries, apple, pear, kiwi, orange with timing.
    - Workouts are tailored to your actual equipment.
    """)


# =========================================================
# GROCERY HUB
# =========================================================

elif page == "Grocery Hub":
    st.title("Grocery Hub")
    st.write("This is the main place for food. Weekly plans and meals should come from here.")

    search = st.text_input("Search grocery foods")
    category_filter = st.multiselect(
        "Filter category",
        sorted(grocery_df["category"].dropna().unique().tolist())
    )

    display = grocery_df.copy()
    if search:
        mask = display.apply(lambda row: search.lower() in " ".join(row.astype(str)).lower(), axis=1)
        display = display[mask]
    if category_filter:
        display = display[display["category"].isin(category_filter)]

    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Add a new grocery food")
    with st.form("add_grocery_food"):
        cols = st.columns(3)
        food = cols[0].text_input("Food name")
        category = cols[1].selectbox("Category", ["Protein", "Carb", "Carb swap", "Fruit", "Vegetable", "Snack", "Limited", "Other"])
        serving = cols[2].text_input("Serving", value="1 serving")

        cols2 = st.columns(6)
        calories = cols2[0].number_input("Calories", min_value=0.0, step=10.0)
        protein_g = cols2[1].number_input("Protein (g)", min_value=0.0, step=1.0)
        carbs_g = cols2[2].number_input("Carbs (g)", min_value=0.0, step=1.0)
        fat_g = cols2[3].number_input("Fat (g)", min_value=0.0, step=1.0)
        fiber_g = cols2[4].number_input("Fiber (g)", min_value=0.0, step=1.0)
        sugar_g = cols2[5].number_input("Sugar (g)", min_value=0.0, step=1.0)

        cols3 = st.columns(4)
        prep_time = cols3[0].text_input("Prep time", value="5-15 min")
        blood_sugar_rating = cols3[1].selectbox("Blood sugar rating", ["Excellent", "Great", "Good", "Moderate", "Limited"])
        fat_loss_rating = cols3[2].selectbox("Fat loss rating", ["Excellent", "Great", "Good", "Moderate", "Limited"])
        timing = cols3[3].text_input("Best timing", value="Anytime")

        tags = st.text_input("Tags", value="High protein; Easy prep")
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Add food")

        if submit and food.strip():
            new = {
                "id": make_id("food"),
                "food": food.strip(),
                "category": category,
                "serving": serving,
                "calories": calories,
                "protein_g": protein_g,
                "carbs_g": carbs_g,
                "fat_g": fat_g,
                "fiber_g": fiber_g,
                "sugar_g": sugar_g,
                "prep_time": prep_time,
                "blood_sugar_rating": blood_sugar_rating,
                "fat_loss_rating": fat_loss_rating,
                "timing": timing,
                "tags": tags,
                "notes": notes,
            }
            grocery_df = pd.concat([grocery_df, pd.DataFrame([new])], ignore_index=True)
            save_csv(grocery_df, "grocery")
            st.success(f"Added {food}.")
            rerun()

    st.subheader("Delete grocery food")
    if not grocery_df.empty:
        delete_food = st.selectbox("Choose food to delete", [""] + grocery_df["food"].tolist())
        if st.button("Delete selected food"):
            if delete_food:
                grocery_df = grocery_df[grocery_df["food"] != delete_food]
                save_csv(grocery_df, "grocery")
                st.success(f"Deleted {delete_food}.")
                rerun()

    st.subheader("Limited foods timing guide")
    limited = grocery_df[grocery_df["category"].astype(str).str.lower() == "limited"]
    if not limited.empty:
        st.dataframe(limited[["food", "serving", "timing", "tags", "notes"]], use_container_width=True, hide_index=True)


# =========================================================
# SAVED MEALS
# =========================================================

elif page == "Saved Meals":
    st.title("Saved Meals")
    st.write("Create reusable meals from the Grocery Hub. These become options for the Weekly Plan.")

    st.subheader("Current saved meals")
    st.dataframe(saved_meals_df, use_container_width=True, hide_index=True)

    st.subheader("Create a meal from grocery foods")
    food_options = grocery_df["food"].tolist()

    with st.form("create_saved_meal"):
        meal_name = st.text_input("Meal name", placeholder="Chicken konjac noodle bowl")
        meal_type = st.selectbox("Default meal type", MEAL_TYPES)
        selected_foods = st.multiselect("Choose foods from Grocery Hub", food_options)
        instructions = st.text_area("Instructions", placeholder="Cook protein, add vegetables, serve with konjac noodles...")
        notes = st.text_area("Notes")
        submit_meal = st.form_submit_button("Save meal")

        if submit_meal and meal_name and selected_foods:
            selected = grocery_df[grocery_df["food"].isin(selected_foods)]
            new_meal = {
                "id": make_id("meal"),
                "meal_name": meal_name,
                "meal_type": meal_type,
                "items": "; ".join(selected_foods),
                "calories": int(selected["calories"].astype(float).sum()),
                "protein_g": int(selected["protein_g"].astype(float).sum()),
                "carbs_g": int(selected["carbs_g"].astype(float).sum()),
                "fat_g": int(selected["fat_g"].astype(float).sum()),
                "fiber_g": int(selected["fiber_g"].astype(float).sum()),
                "sugar_g": int(selected["sugar_g"].astype(float).sum()),
                "prep_time": "Custom",
                "blood_sugar_rating": "Review",
                "fat_loss_rating": "Review",
                "timing": "Custom",
                "tags": "Custom meal",
                "instructions": instructions,
                "notes": notes,
            }
            saved_meals_df = pd.concat([saved_meals_df, pd.DataFrame([new_meal])], ignore_index=True)
            save_csv(saved_meals_df, "saved_meals")
            st.success(f"Saved {meal_name}.")
            rerun()

    st.subheader("Delete saved meal")
    if not saved_meals_df.empty:
        delete_meal = st.selectbox("Choose meal to delete", [""] + saved_meals_df["meal_name"].tolist())
        if st.button("Delete selected saved meal"):
            if delete_meal:
                saved_meals_df = saved_meals_df[saved_meals_df["meal_name"] != delete_meal]
                save_csv(saved_meals_df, "saved_meals")
                st.success(f"Deleted {delete_meal}.")
                rerun()


# =========================================================
# WEEKLY PLAN
# =========================================================

elif page == "Weekly Plan":
    st.title("Weekly Plan")
    st.write("Choose meals from Saved Meals. These will appear under Daily Meals based on day/date.")

    selected_week = st.date_input("Choose any date in the week", date.today())
    week_dates = get_week_dates(selected_week)

    st.subheader("Add meals to plan")

    meal_name_options = saved_meals_df["meal_name"].tolist()

    with st.form("add_weekly_plan"):
        c1, c2, c3 = st.columns(3)
        day = c1.selectbox("Day", DAYS)
        meal_type = c2.selectbox("Meal type", MEAL_TYPES)
        meal_name = c3.selectbox("Meal", meal_name_options if meal_name_options else ["No saved meals yet"])

        notes = st.text_input("Notes")
        submit = st.form_submit_button("Add to weekly plan")

        if submit and meal_name_options:
            meal = saved_meals_df[saved_meals_df["meal_name"] == meal_name].iloc[0].to_dict()
            planned_date = week_dates[day]
            new_plan = {
                "id": make_id("plan"),
                "day": day,
                "date": str(planned_date),
                "meal_type": meal_type,
                "meal_id": meal["id"],
                "meal_name": meal["meal_name"],
                "calories": meal["calories"],
                "protein_g": meal["protein_g"],
                "carbs_g": meal["carbs_g"],
                "fat_g": meal["fat_g"],
                "status": "Planned",
                "notes": notes,
            }
            weekly_plan_df = pd.concat([weekly_plan_df, pd.DataFrame([new_plan])], ignore_index=True)
            save_csv(weekly_plan_df, "weekly_plan")
            st.success("Meal added to weekly plan.")
            rerun()

    st.subheader("Auto-populate a simple week")
    st.write("This fills a balanced plan using your saved meals. You can still edit/delete after.")

    if st.button("Auto-fill week from saved meals"):
        if saved_meals_df.empty:
            st.warning("Create saved meals first.")
        else:
            new_rows = []
            for d in DAYS:
                for mt in MEAL_TYPES:
                    options = saved_meals_df[saved_meals_df["meal_type"] == mt]
                    if options.empty:
                        options = saved_meals_df
                    meal = options.sample(1).iloc[0].to_dict()
                    new_rows.append({
                        "id": make_id("plan"),
                        "day": d,
                        "date": str(week_dates[d]),
                        "meal_type": mt,
                        "meal_id": meal["id"],
                        "meal_name": meal["meal_name"],
                        "calories": meal["calories"],
                        "protein_g": meal["protein_g"],
                        "carbs_g": meal["carbs_g"],
                        "fat_g": meal["fat_g"],
                        "status": "Planned",
                        "notes": "Auto-filled",
                    })
            weekly_plan_df = pd.concat([weekly_plan_df, pd.DataFrame(new_rows)], ignore_index=True)
            save_csv(weekly_plan_df, "weekly_plan")
            st.success("Week auto-filled.")
            rerun()

    st.subheader("Current weekly plan")
    if not weekly_plan_df.empty:
        week_start = week_dates["Monday"]
        week_end = week_dates["Sunday"]
        temp = weekly_plan_df.copy()
        temp["date_dt"] = pd.to_datetime(temp["date"], errors="coerce").dt.date
        display = temp[(temp["date_dt"] >= week_start) & (temp["date_dt"] <= week_end)]
        if display.empty:
            st.info("No planned meals for this selected week yet.")
        else:
            st.dataframe(display.drop(columns=["date_dt"]), use_container_width=True, hide_index=True)

            delete_plan = st.selectbox("Delete planned item", [""] + display["id"].tolist(), format_func=lambda x: "" if x == "" else display[display["id"] == x].iloc[0]["meal_name"])
            if st.button("Delete selected planned item"):
                if delete_plan:
                    weekly_plan_df = weekly_plan_df[weekly_plan_df["id"] != delete_plan]
                    save_csv(weekly_plan_df, "weekly_plan")
                    st.success("Deleted planned item.")
                    rerun()
    else:
        st.info("No weekly plan entries yet.")

    st.subheader("Grocery list generated from weekly plan")
    if not weekly_plan_df.empty:
        planned_meal_ids = weekly_plan_df["meal_id"].dropna().tolist()
        planned_meals = saved_meals_df[saved_meals_df["id"].isin(planned_meal_ids)]
        needed_items = []
        for items in planned_meals["items"].dropna():
            needed_items.extend([x.strip() for x in str(items).split(";") if x.strip()])
        if needed_items:
            grocery_needed = pd.Series(needed_items).value_counts().reset_index()
            grocery_needed.columns = ["Food", "Times used this week"]
            st.dataframe(grocery_needed, use_container_width=True, hide_index=True)
        else:
            st.info("No grocery items detected yet.")


# =========================================================
# DAILY MEALS
# =========================================================

elif page == "Daily Meals":
    st.title("Daily Meals")
    st.write("Log planned meals or manually input food. Planned meals come from your weekly plan.")

    selected_date = st.date_input("Select date", date.today())
    selected_day = selected_date.strftime("%A")

    st.subheader(f"Planned meals for {selected_day}, {selected_date}")
    planned_today = weekly_plan_df[
        (weekly_plan_df["date"].astype(str) == str(selected_date)) |
        ((weekly_plan_df["day"].astype(str) == selected_day) & (weekly_plan_df["date"].astype(str).isin(["", "nan", "NaT"])))
    ]

    if planned_today.empty:
        st.info("No planned meals for this date.")
    else:
        for _, row in planned_today.iterrows():
            with st.expander(f"{row['meal_type']}: {row['meal_name']}", expanded=True):
                st.write(f"Calories: {row['calories']} | Protein: {row['protein_g']}g | Carbs: {row['carbs_g']}g | Fat: {row['fat_g']}g")
                st.write(f"Status: {row['status']}")
                c1, c2 = st.columns(2)
                if c1.button("Log this planned meal", key=f"log_plan_{row['id']}"):
                    meal = meal_by_id(row["meal_id"])
                    if meal:
                        add_to_meal_log(selected_date, row["meal_type"], meal, source="Planned")
                        weekly_plan_df.loc[weekly_plan_df["id"] == row["id"], "status"] = "Logged"
                        save_csv(weekly_plan_df, "weekly_plan")
                        st.success("Logged meal.")
                        rerun()
                if c2.button("Skip this meal", key=f"skip_plan_{row['id']}"):
                    weekly_plan_df.loc[weekly_plan_df["id"] == row["id"], "status"] = "Skipped"
                    save_csv(weekly_plan_df, "weekly_plan")
                    st.success("Marked skipped.")
                    rerun()

    st.subheader("Manual meal entry")
    with st.form("manual_meal_log"):
        c1, c2 = st.columns(2)
        meal_type = c1.selectbox("Meal type", MEAL_TYPES)
        meal_name = c2.text_input("Meal name")

        c3, c4, c5, c6 = st.columns(4)
        calories = c3.number_input("Calories", min_value=0.0, step=10.0)
        protein = c4.number_input("Protein (g)", min_value=0.0, step=1.0)
        carbs = c5.number_input("Carbs (g)", min_value=0.0, step=1.0)
        fat = c6.number_input("Fat (g)", min_value=0.0, step=1.0)

        c7, c8 = st.columns(2)
        fiber = c7.number_input("Fiber (g)", min_value=0.0, step=1.0)
        sugar = c8.number_input("Sugar (g)", min_value=0.0, step=1.0)

        items = st.text_area("Items / ingredients")
        notes = st.text_area("Notes")
        save_as_meal = st.checkbox("Also save this as a reusable Saved Meal")
        submit_manual = st.form_submit_button("Log manual meal")

        if submit_manual and meal_name:
            new_log = {
                "id": make_id("log"),
                "date": str(selected_date),
                "day": selected_day,
                "meal_type": meal_type,
                "source": "Manual",
                "meal_id": "",
                "meal_name": meal_name,
                "items": items,
                "calories": calories,
                "protein_g": protein,
                "carbs_g": carbs,
                "fat_g": fat,
                "fiber_g": fiber,
                "sugar_g": sugar,
                "notes": notes,
            }
            meal_log_df = pd.concat([meal_log_df, pd.DataFrame([new_log])], ignore_index=True)
            save_csv(meal_log_df, "meal_log")

            if save_as_meal:
                new_saved = {
                    "id": make_id("meal"),
                    "meal_name": meal_name,
                    "meal_type": meal_type,
                    "items": items,
                    "calories": calories,
                    "protein_g": protein,
                    "carbs_g": carbs,
                    "fat_g": fat,
                    "fiber_g": fiber,
                    "sugar_g": sugar,
                    "prep_time": "Manual",
                    "blood_sugar_rating": "Review",
                    "fat_loss_rating": "Review",
                    "timing": "Manual",
                    "tags": "Manual saved meal",
                    "instructions": "",
                    "notes": notes,
                }
                saved_meals_df = pd.concat([saved_meals_df, pd.DataFrame([new_saved])], ignore_index=True)
                save_csv(saved_meals_df, "saved_meals")

            st.success("Manual meal logged.")
            rerun()

    st.subheader("Daily log")
    todays_log = meal_log_df[meal_log_df["date"].astype(str) == str(selected_date)]
    if todays_log.empty:
        st.info("No meals logged for this date.")
    else:
        st.dataframe(todays_log, use_container_width=True, hide_index=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", int(todays_log["calories"].astype(float).sum()))
        c2.metric("Protein", f"{int(todays_log['protein_g'].astype(float).sum())} g")
        c3.metric("Carbs", f"{int(todays_log['carbs_g'].astype(float).sum())} g")
        c4.metric("Fat", f"{int(todays_log['fat_g'].astype(float).sum())} g")

        delete_log = st.selectbox("Delete logged meal", [""] + todays_log["id"].tolist(), format_func=lambda x: "" if x == "" else todays_log[todays_log["id"] == x].iloc[0]["meal_name"])
        if st.button("Delete selected logged meal"):
            if delete_log:
                meal_log_df = meal_log_df[meal_log_df["id"] != delete_log]
                save_csv(meal_log_df, "meal_log")
                st.success("Deleted logged meal.")
                rerun()


# =========================================================
# WORKOUTS
# =========================================================

elif page == "Workouts":
    st.title("Workout Dashboard")
    st.write("Tailored to your equipment: barbell, dumbbells, cables, treadmill, elliptical, upright bike, abs machine.")

    workout_templates = {
        "Lower Body + Incline Walk": {
            "equipment": "Barbell; Dumbbells; Cable; Treadmill",
            "exercises": [
                "Goblet squat or barbell squat - 3 sets x 8-12",
                "Romanian deadlift - 3 sets x 8-12",
                "Cable glute kickback - 3 sets x 12-15",
                "Walking lunges - 2 sets x 10 each leg",
                "Glute bridge - 3 sets x 10-15",
                "Incline treadmill walk - 20-30 min"
            ]
        },
        "Upper Push": {
            "equipment": "Dumbbells; Cable; Elliptical",
            "exercises": [
                "Dumbbell shoulder press - 3 sets x 8-12",
                "Dumbbell chest press - 3 sets x 8-12",
                "Cable fly - 3 sets x 12-15",
                "Lateral raise - 3 sets x 12-15",
                "Tricep pushdown - 3 sets x 10-15",
                "Elliptical cooldown - 10-15 min"
            ]
        },
        "Upper Pull": {
            "equipment": "Cable; Dumbbells; Barbell; Treadmill",
            "exercises": [
                "Cable row - 3 sets x 8-12",
                "Lat pulldown - 3 sets x 8-12",
                "Dumbbell row - 3 sets x 10 each side",
                "Barbell row - 3 sets x 8-10",
                "Face pulls - 3 sets x 12-15",
                "Bicep curls - 3 sets x 10-12"
            ]
        },
        "Conditioning + Core": {
            "equipment": "Upright bike; Abs machine; Cable; Elliptical",
            "exercises": [
                "Upright bike intervals - 15-20 min",
                "Abs machine crunch - 3 sets x 10-15",
                "Cable crunch - 3 sets x 12-15",
                "Plank - 3 rounds",
                "Elliptical steady state - 10-20 min"
            ]
        },
        "Full Body Metabolic": {
            "equipment": "Dumbbells; Cable; Bike; Abs machine",
            "exercises": [
                "Dumbbell squat press - 3 sets x 10",
                "Cable row - 3 sets x 12",
                "Romanian deadlift - 3 sets x 10",
                "Pushups or chest press - 3 sets x 8-12",
                "Bike intervals - 10-15 min",
                "Abs machine - 2-3 sets"
            ]
        },
        "Recovery Cardio": {
            "equipment": "Treadmill; Elliptical; Upright bike",
            "exercises": [
                "Treadmill incline walk OR elliptical OR upright bike - 20-45 min",
                "Light stretching - 5-10 min",
                "Optional easy core - 2 sets"
            ]
        }
    }

    mode = st.selectbox("Workout mode", ["Full Workout", "Quick Workout", "Low Energy", "Recovery"])
    chosen = st.selectbox("Choose workout", list(workout_templates.keys()))
    template = workout_templates[chosen]

    st.subheader(chosen)
    st.write(f"Equipment: {template['equipment']}")
    for ex in template["exercises"]:
        st.write(f"- {ex}")

    if mode == "Quick Workout":
        st.info("Quick mode: do first 3 exercises + 10 minutes cardio.")
    elif mode == "Low Energy":
        st.info("Low energy mode: reduce each exercise by 1 set and keep cardio easy.")
    elif mode == "Recovery":
        st.info("Recovery mode: cardio only, low intensity, no heavy lifting.")

    st.subheader("Log workout")
    with st.form("log_workout"):
        workout_date = st.date_input("Workout date", date.today())
        c1, c2, c3 = st.columns(3)
        duration = c1.number_input("Total duration (min)", min_value=0, step=5)
        cardio_machine = c2.selectbox("Cardio machine", ["None", "Treadmill", "Elliptical", "Upright bike"])
        cardio_min = c3.number_input("Cardio minutes", min_value=0, step=5)

        intensity = st.selectbox("Intensity", ["Low", "Moderate", "High"])
        exercises_done = st.text_area("Exercises completed", value="\n".join(template["exercises"]))
        notes = st.text_area("Notes")
        submit_workout = st.form_submit_button("Save workout")

        if submit_workout:
            log = {
                "id": make_id("workout"),
                "date": str(workout_date),
                "day": workout_date.strftime("%A"),
                "workout_name": chosen,
                "mode": mode,
                "equipment": template["equipment"],
                "duration_min": duration,
                "cardio_machine": cardio_machine,
                "cardio_min": cardio_min,
                "intensity": intensity,
                "exercises": exercises_done,
                "notes": notes,
            }
            workout_log_df = pd.concat([workout_log_df, pd.DataFrame([log])], ignore_index=True)
            save_csv(workout_log_df, "workout_log")
            st.success("Workout logged.")
            rerun()

    st.subheader("Workout log")
    if workout_log_df.empty:
        st.info("No workouts logged yet.")
    else:
        st.dataframe(workout_log_df, use_container_width=True, hide_index=True)

        delete_workout = st.selectbox("Delete workout", [""] + workout_log_df["id"].tolist(), format_func=lambda x: "" if x == "" else workout_log_df[workout_log_df["id"] == x].iloc[0]["workout_name"])
        if st.button("Delete selected workout"):
            if delete_workout:
                workout_log_df = workout_log_df[workout_log_df["id"] != delete_workout]
                save_csv(workout_log_df, "workout_log")
                st.success("Deleted workout.")
                rerun()


# =========================================================
# PROGRESS
# =========================================================

elif page == "Progress":
    st.title("Progress Dashboard")

    st.subheader("Body progress entry")
    with st.form("body_progress"):
        progress_date = st.date_input("Date", date.today())
        c1, c2, c3, c4 = st.columns(4)
        weight = c1.number_input("Weight (lb)", min_value=0.0, step=0.5)
        waist = c2.number_input("Waist (in)", min_value=0.0, step=0.5)
        hips = c3.number_input("Hips (in)", min_value=0.0, step=0.5)
        chest = c4.number_input("Chest (in)", min_value=0.0, step=0.5)

        c5, c6 = st.columns(2)
        energy = c5.selectbox("Energy", ["Low", "Moderate", "High"])
        sleep = c6.number_input("Sleep hours", min_value=0.0, step=0.5)
        notes = st.text_area("Notes")
        submit_body = st.form_submit_button("Save progress")

        if submit_body:
            row = {
                "id": make_id("body"),
                "date": str(progress_date),
                "weight_lb": weight,
                "waist_in": waist,
                "hips_in": hips,
                "chest_in": chest,
                "energy": energy,
                "sleep_hours": sleep,
                "notes": notes,
            }
            body_log_df = pd.concat([body_log_df, pd.DataFrame([row])], ignore_index=True)
            save_csv(body_log_df, "body_log")
            st.success("Progress saved.")
            rerun()

    st.subheader("Nutrition summary")
    if meal_log_df.empty:
        st.info("No meal logs yet.")
    else:
        df = meal_log_df.copy()
        for col in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        daily = df.groupby("date")[["calories", "protein_g", "carbs_g", "fat_g"]].sum().reset_index()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg calories/day", int(daily["calories"].mean()))
        c2.metric("Avg protein/day", f"{int(daily['protein_g'].mean())} g")
        c3.metric("Meals logged", len(df))
        c4.metric("Days tracked", len(daily))
        st.line_chart(daily.set_index("date")[["calories", "protein_g"]])
        st.dataframe(daily, use_container_width=True, hide_index=True)

    st.subheader("Workout summary")
    if workout_log_df.empty:
        st.info("No workout logs yet.")
    else:
        w = workout_log_df.copy()
        w["duration_min"] = pd.to_numeric(w["duration_min"], errors="coerce").fillna(0)
        w["cardio_min"] = pd.to_numeric(w["cardio_min"], errors="coerce").fillna(0)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total workouts", len(w))
        c2.metric("Total workout minutes", int(w["duration_min"].sum()))
        c3.metric("Total cardio minutes", int(w["cardio_min"].sum()))
        workout_daily = w.groupby("date")[["duration_min", "cardio_min"]].sum().reset_index()
        st.line_chart(workout_daily.set_index("date")[["duration_min", "cardio_min"]])
        st.dataframe(w, use_container_width=True, hide_index=True)

    st.subheader("Body log")
    if body_log_df.empty:
        st.info("No body progress logged yet.")
    else:
        b = body_log_df.copy()
        for col in ["weight_lb", "waist_in", "hips_in", "chest_in", "sleep_hours"]:
            b[col] = pd.to_numeric(b[col], errors="coerce").fillna(0)
        st.dataframe(b, use_container_width=True, hide_index=True)
        chart_cols = [c for c in ["weight_lb", "waist_in", "hips_in", "chest_in"] if c in b.columns]
        if chart_cols:
            st.line_chart(b.set_index("date")[chart_cols])


# =========================================================
# SETTINGS
# =========================================================

elif page == "Settings / Reset":
    st.title("Settings / Reset")
    st.warning("Be careful: reset actions will erase saved CSV data.")

    st.subheader("Export files")
    st.write(f"Data folder: `{DATA_DIR.resolve()}`")
    for key, path in FILES.items():
        if path.exists():
            st.download_button(
                label=f"Download {key}.csv",
                data=path.read_bytes(),
                file_name=path.name,
                mime="text/csv"
            )

    st.subheader("Reset options")

    if st.button("Reset grocery and saved meal templates"):
        if FILES["grocery"].exists():
            FILES["grocery"].unlink()
        if FILES["saved_meals"].exists():
            FILES["saved_meals"].unlink()
        seed_grocery()
        seed_saved_meals()
        st.success("Grocery and saved meal templates reset.")
        rerun()

    if st.button("Clear weekly plan"):
        save_csv(pd.DataFrame(columns=WEEKLY_PLAN_COLUMNS), "weekly_plan")
        st.success("Weekly plan cleared.")
        rerun()

    if st.button("Clear meal logs"):
        save_csv(pd.DataFrame(columns=MEAL_LOG_COLUMNS), "meal_log")
        st.success("Meal logs cleared.")
        rerun()

    if st.button("Clear workout logs"):
        save_csv(pd.DataFrame(columns=WORKOUT_LOG_COLUMNS), "workout_log")
        st.success("Workout logs cleared.")
        rerun()

    if st.button("Clear body progress logs"):
        save_csv(pd.DataFrame(columns=BODY_LOG_COLUMNS), "body_log")
        st.success("Body progress logs cleared.")
        rerun()

    st.subheader("Run command")
    st.code("streamlit run complete_fitness_meal_dashboard.py", language="bash")
