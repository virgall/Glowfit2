# mobile_friendly_fitness_dashboard.py
# Streamlit Fitness + Meal Dashboard
# Mobile-friendly version: Grocery is the main food/planning hub.

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
import uuid

st.set_page_config(page_title="Fitness + Meal Planner", page_icon="🥗", layout="wide", initial_sidebar_state="collapsed")

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

GROCERY_COLUMNS = ["id", "food", "category", "serving", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "prep_time", "blood_sugar_rating", "fat_loss_rating", "timing", "tags", "notes"]
SAVED_MEAL_COLUMNS = ["id", "meal_name", "meal_type", "items", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "prep_time", "blood_sugar_rating", "fat_loss_rating", "timing", "tags", "instructions", "notes"]
WEEKLY_PLAN_COLUMNS = ["id", "day", "date", "meal_type", "meal_id", "meal_name", "items", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "source", "status", "notes"]
MEAL_LOG_COLUMNS = ["id", "date", "day", "meal_type", "source", "meal_id", "meal_name", "items", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "notes"]
WORKOUT_LOG_COLUMNS = ["id", "date", "day", "workout_name", "mode", "equipment", "duration_min", "cardio_machine", "cardio_min", "intensity", "exercises", "notes"]
BODY_LOG_COLUMNS = ["id", "date", "weight_lb", "waist_in", "hips_in", "chest_in", "energy", "sleep_hours", "notes"]

st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; max-width: 1150px; }
h1, h2, h3 { letter-spacing: -0.03em; }
.food-card { border: 1px solid rgba(128,128,128,0.22); border-radius: 18px; padding: 15px; margin-bottom: 12px; background: rgba(128,128,128,0.06); }
.food-title { font-size: 1.08rem; font-weight: 800; margin-bottom: 4px; }
.muted { color: #8a8a8a; font-size: 0.9rem; }
.pill { display: inline-block; border: 1px solid rgba(128,128,128,0.25); border-radius: 999px; padding: 3px 9px; margin: 2px 3px 2px 0; font-size: 0.78rem; background: rgba(128,128,128,0.08); }
div[data-testid="stMetric"] { border: 1px solid rgba(128,128,128,0.20); border-radius: 16px; padding: 12px; background: rgba(128,128,128,0.045); }
.stDataFrame { border-radius: 16px; overflow: hidden; }
@media (max-width: 768px) {
  .block-container { padding-left: 0.75rem; padding-right: 0.75rem; }
  .food-card { padding: 13px; border-radius: 16px; }
  .food-title { font-size: 1rem; }
  div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
  button { width: 100%; }
}
</style>
""", unsafe_allow_html=True)


def make_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


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


def numeric_cols(df, cols):
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def week_dates(any_date):
    monday = any_date - timedelta(days=any_date.weekday())
    return {DAYS[i]: monday + timedelta(days=i) for i in range(7)}


def visible_grocery(df):
    cols = ["food", "category", "serving", "calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "timing", "tags"]
    return df[[c for c in cols if c in df.columns]]


def add_plan_row(day, planned_date, meal_type, meal_name, items, calories, protein, carbs, fat, fiber, sugar, source, meal_id="", notes=""):
    weekly_df = load_csv(FILES["weekly_plan"], WEEKLY_PLAN_COLUMNS)
    row = {
        "id": make_id("plan"), "day": day, "date": str(planned_date), "meal_type": meal_type,
        "meal_id": meal_id, "meal_name": meal_name, "items": items, "calories": calories,
        "protein_g": protein, "carbs_g": carbs, "fat_g": fat, "fiber_g": fiber, "sugar_g": sugar,
        "source": source, "status": "Planned", "notes": notes
    }
    weekly_df = pd.concat([weekly_df, pd.DataFrame([row])], ignore_index=True)
    save_csv(weekly_df, "weekly_plan")


def add_meal_log_from_plan(plan_row):
    logs_df = load_csv(FILES["meal_log"], MEAL_LOG_COLUMNS)
    selected_date = pd.to_datetime(plan_row["date"]).date()
    row = {
        "id": make_id("log"), "date": str(selected_date), "day": selected_date.strftime("%A"),
        "meal_type": plan_row["meal_type"], "source": "Planned", "meal_id": plan_row.get("meal_id", ""),
        "meal_name": plan_row["meal_name"], "items": plan_row.get("items", ""), "calories": plan_row["calories"],
        "protein_g": plan_row["protein_g"], "carbs_g": plan_row["carbs_g"], "fat_g": plan_row["fat_g"],
        "fiber_g": plan_row.get("fiber_g", 0), "sugar_g": plan_row.get("sugar_g", 0), "notes": plan_row.get("notes", "")
    }
    logs_df = pd.concat([logs_df, pd.DataFrame([row])], ignore_index=True)
    save_csv(logs_df, "meal_log")


def seed_grocery():
    rows = [
        ["Chicken breast", "Protein", "100 g cooked", 165, 31, 0, 4, 0, 0, "15-25 min", "Excellent", "Excellent", "Anytime", "High protein; Blood sugar friendly; Easy prep", "Great for bowls, wraps, salads"],
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
    g = numeric_cols(g, ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
    def combo(name, meal_type, foods, instructions, timing, tags):
        selected = g[g["food"].isin(foods)]
        return {
            "id": make_id("meal"), "meal_name": name, "meal_type": meal_type, "items": "; ".join(foods),
            "calories": int(selected["calories"].sum()), "protein_g": int(selected["protein_g"].sum()),
            "carbs_g": int(selected["carbs_g"].sum()), "fat_g": int(selected["fat_g"].sum()),
            "fiber_g": int(selected["fiber_g"].sum()), "sugar_g": int(selected["sugar_g"].sum()),
            "prep_time": "5-25 min", "blood_sugar_rating": "Great", "fat_loss_rating": "Great",
            "timing": timing, "tags": tags, "instructions": instructions, "notes": ""
        }
    meals = [
        combo("Chicken Konjac Noodle Stir Fry", "Dinner", ["Chicken breast", "Konjac noodles", "Mixed vegetables"], "Cook chicken, rinse konjac noodles, stir fry with mixed vegetables and low sugar sauce.", "Dinner", "High protein; Low carb; Fat loss friendly"),
        combo("Greek Yogurt Berry Bowl", "Breakfast", ["Greek yogurt plain", "Berries"], "Mix plain Greek yogurt with berries. Add cinnamon if desired.", "Breakfast; Snack", "High protein; Blood sugar friendly"),
        combo("Protein Cereal Bowl", "Breakfast", ["Protein cereal", "Greek yogurt plain", "Berries"], "Use Greek yogurt as base, add protein cereal and berries.", "Post-workout; Breakfast", "Limited food timing; High protein"),
        combo("Salmon + Konjac Rice Bowl", "Dinner", ["Salmon", "Konjac rice", "Broccoli"], "Cook salmon, steam broccoli, serve over konjac rice.", "Dinner; Post-workout", "High protein; Healthy fats"),
        combo("Shrimp Cauliflower Rice Bowl", "Lunch", ["Shrimp", "Cauliflower rice", "Mixed vegetables"], "Cook shrimp and vegetables, serve with cauliflower rice.", "Lunch; Dinner", "Low carb; Fast meal"),
        combo("Tuna Protein Wrap", "Lunch", ["Tuna", "High protein wrap", "Spinach"], "Mix tuna with seasoning, add spinach, wrap and serve.", "Lunch", "No cook; High protein"),
        combo("Egg + Spinach Breakfast", "Breakfast", ["Eggs", "Spinach"], "Scramble eggs with spinach.", "Breakfast", "Easy prep; Blood sugar friendly"),
        combo("Lean Beef Vegetable Bowl", "Dinner", ["Lean ground beef", "Mixed vegetables", "Cauliflower rice"], "Cook lean beef, add vegetables and cauliflower rice.", "Dinner", "Filling; High protein"),
        combo("Cottage Cheese Berry Snack", "Snack", ["Cottage cheese", "Berries"], "Add berries to cottage cheese.", "Snack; Late night", "High protein snack"),
        combo("Post Workout Chicken Plate", "Dinner", ["Chicken breast", "Sweet potato", "Broccoli"], "Cook chicken, sweet potato and broccoli. Best after harder workout.", "Post-workout", "Workout carb; Balanced"),
        combo("Quick Turkey Wrap", "Lunch", ["Turkey slices", "High protein wrap", "Spinach"], "Add turkey and spinach to a wrap.", "Lunch", "Fast; Work lunch"),
        combo("Protein Shake + Apple", "Snack", ["Protein shake", "Apple"], "Drink protein shake and pair with an apple.", "Pre-workout; Snack", "Simple; Craving control"),
    ]
    save_csv(pd.DataFrame(meals, columns=SAVED_MEAL_COLUMNS), "saved_meals")


def initialize():
    if not FILES["grocery"].exists(): seed_grocery()
    if not FILES["saved_meals"].exists(): seed_saved_meals()
    for key, cols in {"weekly_plan": WEEKLY_PLAN_COLUMNS, "meal_log": MEAL_LOG_COLUMNS, "workout_log": WORKOUT_LOG_COLUMNS, "body_log": BODY_LOG_COLUMNS}.items():
        if not FILES[key].exists(): save_csv(pd.DataFrame(columns=cols), key)

initialize()

grocery = numeric_cols(load_csv(FILES["grocery"], GROCERY_COLUMNS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
saved_meals = numeric_cols(load_csv(FILES["saved_meals"], SAVED_MEAL_COLUMNS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
weekly = numeric_cols(load_csv(FILES["weekly_plan"], WEEKLY_PLAN_COLUMNS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
logs = numeric_cols(load_csv(FILES["meal_log"], MEAL_LOG_COLUMNS), ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g"])
workouts = load_csv(FILES["workout_log"], WORKOUT_LOG_COLUMNS)
body = load_csv(FILES["body_log"], BODY_LOG_COLUMNS)

st.title("🥗 Fitness + Meal Planner")
tabs = st.tabs(["🏠 Home", "🛒 Grocery", "📅 Weekly Plan", "🍽️ Daily Meals", "🏋️ Workouts", "📈 Progress", "⚙️ Settings"])

with tabs[0]:
    st.subheader("Dashboard flow")
    st.markdown("**Grocery is the main hub.** Choose foods or saved meals in Grocery, add them to the week, then log them in Daily Meals.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Grocery Foods", len(grocery)); c2.metric("Saved Meals", len(saved_meals)); c3.metric("Planned Meals", len(weekly)); c4.metric("Logged Meals", len(logs))
    st.markdown('<div class="food-card"><b>Built for:</b><br>• Fat loss<br>• Prediabetic-friendly meals<br>• Less prep time<br>• Equipment: barbell, dumbbells, cables, treadmill, elliptical, upright bike, abs machine</div>', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("🛒 Grocery Hub")
    st.write("Select foods or saved meals here and send them straight to your weekly plan.")
    planning_week = st.date_input("Planning week", date.today(), key="grocery_week")
    dates = week_dates(planning_week)
    mode = st.radio("What do you want to plan from?", ["Saved meals", "Individual grocery foods", "View grocery list"], horizontal=True)

    if mode == "Saved meals":
        meal_filter = st.selectbox("Filter meal type", ["All"] + MEAL_TYPES)
        meal_search = st.text_input("Search meals")
        meal_display = saved_meals.copy()
        if meal_filter != "All": meal_display = meal_display[meal_display["meal_type"] == meal_filter]
        if meal_search: meal_display = meal_display[meal_display.apply(lambda r: meal_search.lower() in " ".join(r.astype(str)).lower(), axis=1)]
        for _, meal in meal_display.iterrows():
            st.markdown(f'<div class="food-card"><div class="food-title">{meal["meal_name"]}</div><div class="muted">{meal["items"]}</div><span class="pill">{meal["meal_type"]}</span><span class="pill">{int(meal["calories"])} cal</span><span class="pill">{int(meal["protein_g"])}g protein</span><span class="pill">{meal["timing"]}</span></div>', unsafe_allow_html=True)
            with st.expander(f"Plan {meal['meal_name']}"):
                c1, c2 = st.columns(2)
                day = c1.selectbox("Day", DAYS, key=f"day_meal_{meal['id']}")
                default_idx = MEAL_TYPES.index(meal["meal_type"]) if meal["meal_type"] in MEAL_TYPES else 0
                meal_type = c2.selectbox("Meal type", MEAL_TYPES, index=default_idx, key=f"type_meal_{meal['id']}")
                notes = st.text_input("Notes", key=f"notes_meal_{meal['id']}")
                if st.button("Add to weekly plan", key=f"add_meal_{meal['id']}"):
                    add_plan_row(day, dates[day], meal_type, meal["meal_name"], meal["items"], meal["calories"], meal["protein_g"], meal["carbs_g"], meal["fat_g"], meal["fiber_g"], meal["sugar_g"], "Saved meal", meal["id"], notes)
                    st.success(f"Added {meal['meal_name']} to {day}."); st.rerun()

    elif mode == "Individual grocery foods":
        custom_meal_name = st.text_input("Meal name", placeholder="e.g., Chicken + konjac rice bowl")
        custom_meal_type = st.selectbox("Meal type", MEAL_TYPES, key="custom_food_meal_type")
        selected_foods = st.multiselect("Select grocery foods", grocery["food"].tolist())
        if selected_foods:
            selected = grocery[grocery["food"].isin(selected_foods)]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", int(selected["calories"].sum())); c2.metric("Protein", f"{int(selected['protein_g'].sum())}g"); c3.metric("Carbs", f"{int(selected['carbs_g'].sum())}g"); c4.metric("Fat", f"{int(selected['fat_g'].sum())}g")
            chosen_day = st.selectbox("Add to day", DAYS, key="custom_food_day")
            save_reusable = st.checkbox("Also save as reusable meal", value=True)
            notes = st.text_input("Notes", key="custom_food_notes")
            if st.button("Add grocery-built meal to weekly plan"):
                name = custom_meal_name if custom_meal_name else "Custom grocery meal"
                items = "; ".join(selected_foods)
                add_plan_row(chosen_day, dates[chosen_day], custom_meal_type, name, items, int(selected["calories"].sum()), int(selected["protein_g"].sum()), int(selected["carbs_g"].sum()), int(selected["fat_g"].sum()), int(selected["fiber_g"].sum()), int(selected["sugar_g"].sum()), "Grocery foods", "", notes)
                if save_reusable:
                    new_meal = {"id": make_id("meal"), "meal_name": name, "meal_type": custom_meal_type, "items": items, "calories": int(selected["calories"].sum()), "protein_g": int(selected["protein_g"].sum()), "carbs_g": int(selected["carbs_g"].sum()), "fat_g": int(selected["fat_g"].sum()), "fiber_g": int(selected["fiber_g"].sum()), "sugar_g": int(selected["sugar_g"].sum()), "prep_time": "Custom", "blood_sugar_rating": "Review", "fat_loss_rating": "Review", "timing": "Custom", "tags": "Custom meal", "instructions": "", "notes": notes}
                    saved_meals = pd.concat([saved_meals, pd.DataFrame([new_meal])], ignore_index=True); save_csv(saved_meals, "saved_meals")
                st.success(f"Added {name} to {chosen_day}."); st.rerun()

    else:
        search = st.text_input("Search grocery")
        categories = ["All"] + sorted(grocery["category"].dropna().unique().tolist())
        cat = st.selectbox("Category", categories)
        display = grocery.copy()
        if cat != "All": display = display[display["category"] == cat]
        if search: display = display[display.apply(lambda r: search.lower() in " ".join(r.astype(str)).lower(), axis=1)]
        view_type = st.radio("View style", ["Cards", "Compact table"], horizontal=True)
        if view_type == "Cards":
            for _, food in display.iterrows():
                st.markdown(f'<div class="food-card"><div class="food-title">{food["food"]}</div><div class="muted">{food["serving"]} • {food["category"]}</div><span class="pill">{int(food["calories"])} cal</span><span class="pill">{int(food["protein_g"])}g protein</span><span class="pill">{int(food["carbs_g"])}g carbs</span><span class="pill">{int(food["fat_g"])}g fat</span><span class="pill">{food["timing"]}</span><div class="muted">{food["tags"]}</div></div>', unsafe_allow_html=True)
        else:
            st.dataframe(visible_grocery(display), use_container_width=True, hide_index=True)

    st.divider(); st.markdown("### Add new grocery food")
    with st.expander("Add food manually"):
        with st.form("add_food_form"):
            c1, c2 = st.columns(2); food_name = c1.text_input("Food name"); category = c2.selectbox("Category", ["Protein", "Carb", "Carb swap", "Fruit", "Vegetable", "Snack", "Limited", "Other"])
            c3, c4 = st.columns(2); serving = c3.text_input("Serving", value="1 serving"); prep_time = c4.text_input("Prep time", value="5-10 min")
            a,b,c,d = st.columns(4); calories = a.number_input("Calories", min_value=0.0, step=10.0); protein = b.number_input("Protein", min_value=0.0, step=1.0); carb_amt = c.number_input("Carbs", min_value=0.0, step=1.0); fat_amt = d.number_input("Fat", min_value=0.0, step=1.0)
            e,f = st.columns(2); fiber = e.number_input("Fiber", min_value=0.0, step=1.0); sugar = f.number_input("Sugar", min_value=0.0, step=1.0)
            timing = st.text_input("Best timing", value="Anytime"); tags = st.text_input("Tags", value="Easy prep"); notes = st.text_area("Notes")
            if st.form_submit_button("Save food") and food_name:
                row = {"id": make_id("food"), "food": food_name, "category": category, "serving": serving, "calories": calories, "protein_g": protein, "carbs_g": carb_amt, "fat_g": fat_amt, "fiber_g": fiber, "sugar_g": sugar, "prep_time": prep_time, "blood_sugar_rating": "Review", "fat_loss_rating": "Review", "timing": timing, "tags": tags, "notes": notes}
                grocery = pd.concat([grocery, pd.DataFrame([row])], ignore_index=True); save_csv(grocery, "grocery"); st.success("Food saved."); st.rerun()

with tabs[2]:
    st.subheader("📅 Weekly Plan")
    chosen_week = st.date_input("Week", date.today(), key="weekly_week"); dates = week_dates(chosen_week)
    if not weekly.empty:
        temp = weekly.copy(); temp["date_dt"] = pd.to_datetime(temp["date"], errors="coerce").dt.date
        week_display = temp[(temp["date_dt"] >= dates["Monday"]) & (temp["date_dt"] <= dates["Sunday"])]
    else: week_display = weekly
    if week_display.empty: st.info("No meals planned for this week yet. Go to Grocery and add foods/meals to the plan.")
    else:
        for day in DAYS:
            day_df = week_display[week_display["day"] == day]
            with st.expander(f"{day} — {dates[day]}", expanded=(day == date.today().strftime("%A"))):
                if day_df.empty: st.write("No meals planned.")
                else:
                    for _, row in day_df.iterrows():
                        st.markdown(f'<div class="food-card"><div class="food-title">{row["meal_type"]}: {row["meal_name"]}</div><div class="muted">{row["items"]}</div><span class="pill">{int(row["calories"])} cal</span><span class="pill">{int(row["protein_g"])}g protein</span><span class="pill">{row["status"]}</span></div>', unsafe_allow_html=True)
                        c1,c2 = st.columns(2)
                        if c1.button("Log meal", key=f"log_from_week_{row['id']}"):
                            add_meal_log_from_plan(row); weekly.loc[weekly["id"] == row["id"], "status"] = "Logged"; save_csv(weekly, "weekly_plan"); st.success("Meal logged."); st.rerun()
                        if c2.button("Delete", key=f"delete_plan_{row['id']}"):
                            weekly = weekly[weekly["id"] != row["id"]]; save_csv(weekly, "weekly_plan"); st.success("Deleted."); st.rerun()
        c1,c2,c3,c4 = st.columns(4); c1.metric("Calories", int(week_display["calories"].sum())); c2.metric("Protein", f"{int(week_display['protein_g'].sum())}g"); c3.metric("Carbs", f"{int(week_display['carbs_g'].sum())}g"); c4.metric("Fat", f"{int(week_display['fat_g'].sum())}g")
        st.subheader("Auto grocery list from planned meals")
        all_items=[]
        for items in week_display["items"].dropna(): all_items += [x.strip() for x in str(items).split(";") if x.strip()]
        if all_items:
            need = pd.Series(all_items).value_counts().reset_index(); need.columns=["Food", "Times used"]
            st.dataframe(need, use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("🍽️ Daily Meals")
    selected_date = st.date_input("Date", date.today(), key="daily_date"); selected_day = selected_date.strftime("%A")
    planned_today = weekly[weekly["date"].astype(str) == str(selected_date)]
    st.markdown(f"### Planned for {selected_day}")
    if planned_today.empty: st.info("No planned meals for this date.")
    else:
        for _, row in planned_today.iterrows():
            st.markdown(f'<div class="food-card"><div class="food-title">{row["meal_type"]}: {row["meal_name"]}</div><div class="muted">{row["items"]}</div><span class="pill">{int(row["calories"])} cal</span><span class="pill">{int(row["protein_g"])}g protein</span><span class="pill">{row["status"]}</span></div>', unsafe_allow_html=True)
            if st.button("Log this meal", key=f"daily_log_{row['id']}"):
                add_meal_log_from_plan(row); weekly.loc[weekly["id"] == row["id"], "status"] = "Logged"; save_csv(weekly, "weekly_plan"); st.success("Logged."); st.rerun()
    st.markdown("### Manual meal log")
    with st.expander("Add manual meal"):
        with st.form("manual_meal"):
            c1,c2 = st.columns(2); meal_type = c1.selectbox("Meal type", MEAL_TYPES, key="manual_meal_type"); meal_name = c2.text_input("Meal name")
            a,b,c,d = st.columns(4); calories=a.number_input("Calories", min_value=0.0, step=10.0, key="manual_cal"); protein=b.number_input("Protein", min_value=0.0, step=1.0, key="manual_pro"); carb_amt=c.number_input("Carbs", min_value=0.0, step=1.0, key="manual_carb"); fat_amt=d.number_input("Fat", min_value=0.0, step=1.0, key="manual_fat")
            fiber = st.number_input("Fiber", min_value=0.0, step=1.0, key="manual_fiber"); sugar = st.number_input("Sugar", min_value=0.0, step=1.0, key="manual_sugar")
            items = st.text_area("Items"); notes = st.text_area("Notes")
            if st.form_submit_button("Log manual meal") and meal_name:
                row = {"id": make_id("log"), "date": str(selected_date), "day": selected_day, "meal_type": meal_type, "source": "Manual", "meal_id": "", "meal_name": meal_name, "items": items, "calories": calories, "protein_g": protein, "carbs_g": carb_amt, "fat_g": fat_amt, "fiber_g": fiber, "sugar_g": sugar, "notes": notes}
                logs = pd.concat([logs, pd.DataFrame([row])], ignore_index=True); save_csv(logs, "meal_log"); st.success("Meal logged."); st.rerun()
    todays_logs = logs[logs["date"].astype(str) == str(selected_date)]
    st.markdown("### Logged today")
    if todays_logs.empty: st.info("No meals logged today.")
    else:
        for _, row in todays_logs.iterrows(): st.markdown(f'<div class="food-card"><div class="food-title">{row["meal_type"]}: {row["meal_name"]}</div><div class="muted">{row["items"]}</div><span class="pill">{int(row["calories"])} cal</span><span class="pill">{int(row["protein_g"])}g protein</span><span class="pill">{row["source"]}</span></div>', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4); c1.metric("Calories", int(todays_logs["calories"].sum())); c2.metric("Protein", f"{int(todays_logs['protein_g'].sum())}g"); c3.metric("Carbs", f"{int(todays_logs['carbs_g'].sum())}g"); c4.metric("Fat", f"{int(todays_logs['fat_g'].sum())}g")

with tabs[4]:
    st.subheader("🏋️ Workouts")
    templates = {
        "Lower Body + Incline Walk": ["Goblet squat or barbell squat — 3 x 8-12", "Romanian deadlift — 3 x 8-12", "Cable glute kickback — 3 x 12-15", "Walking lunges — 2 x 10 each leg", "Glute bridge — 3 x 10-15", "Incline treadmill walk — 20-30 min"],
        "Upper Push": ["Dumbbell shoulder press — 3 x 8-12", "Dumbbell chest press — 3 x 8-12", "Cable fly — 3 x 12-15", "Lateral raise — 3 x 12-15", "Tricep pushdown — 3 x 10-15", "Elliptical cooldown — 10-15 min"],
        "Upper Pull": ["Cable row — 3 x 8-12", "Lat pulldown — 3 x 8-12", "Dumbbell row — 3 x 10 each side", "Barbell row — 3 x 8-10", "Face pull — 3 x 12-15", "Bicep curls — 3 x 10-12"],
        "Conditioning + Core": ["Upright bike intervals — 15-20 min", "Abs machine crunch — 3 x 10-15", "Cable crunch — 3 x 12-15", "Plank — 3 rounds", "Elliptical steady state — 10-20 min"],
        "Full Body Metabolic": ["Dumbbell squat press — 3 x 10", "Cable row — 3 x 12", "Romanian deadlift — 3 x 10", "Pushups or chest press — 3 x 8-12", "Bike intervals — 10-15 min", "Abs machine — 2-3 sets"],
        "Recovery Cardio": ["Treadmill, elliptical, or upright bike — 20-45 min", "Light stretch — 5-10 min"]
    }
    selected_template = st.selectbox("Workout", list(templates.keys())); mode = st.selectbox("Mode", ["Full Workout", "Quick Workout", "Low Energy", "Recovery"])
    for ex in templates[selected_template]: st.write(f"• {ex}")
    if mode == "Quick Workout": st.info("Quick mode: first 3 exercises + 10 minutes cardio.")
    elif mode == "Low Energy": st.info("Low energy mode: reduce each exercise by 1 set and keep cardio easy.")
    elif mode == "Recovery": st.info("Recovery mode: low-intensity cardio and stretching only.")
    with st.expander("Log workout"):
        with st.form("workout_log_form"):
            workout_date = st.date_input("Workout date", date.today()); a,b,c = st.columns(3); duration=a.number_input("Duration", min_value=0, step=5); cardio_machine=b.selectbox("Cardio machine", ["None", "Treadmill", "Elliptical", "Upright bike"]); cardio_min=c.number_input("Cardio min", min_value=0, step=5)
            intensity=st.selectbox("Intensity", ["Low", "Moderate", "High"]); exercises=st.text_area("Exercises done", value="\n".join(templates[selected_template])); notes=st.text_area("Notes")
            if st.form_submit_button("Save workout"):
                row={"id": make_id("workout"), "date": str(workout_date), "day": workout_date.strftime("%A"), "workout_name": selected_template, "mode": mode, "equipment": "Barbell; Dumbbells; Cable; Treadmill; Elliptical; Upright bike; Abs machine", "duration_min": duration, "cardio_machine": cardio_machine, "cardio_min": cardio_min, "intensity": intensity, "exercises": exercises, "notes": notes}
                workouts = pd.concat([workouts, pd.DataFrame([row])], ignore_index=True); save_csv(workouts, "workout_log"); st.success("Workout saved."); st.rerun()
    if not workouts.empty: st.dataframe(workouts.drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True)

with tabs[5]:
    st.subheader("📈 Progress")
    st.markdown("### Nutrition")
    if logs.empty: st.info("No meal logs yet.")
    else:
        daily = logs.groupby("date")[["calories", "protein_g", "carbs_g", "fat_g"]].sum().reset_index()
        c1,c2,c3,c4=st.columns(4); c1.metric("Avg Calories", int(daily["calories"].mean())); c2.metric("Avg Protein", f"{int(daily['protein_g'].mean())}g"); c3.metric("Days Logged", len(daily)); c4.metric("Meals Logged", len(logs))
        st.line_chart(daily.set_index("date")[["calories", "protein_g"]])
    st.markdown("### Workouts")
    if workouts.empty: st.info("No workouts logged yet.")
    else:
        w=numeric_cols(workouts, ["duration_min", "cardio_min"]); c1,c2,c3=st.columns(3); c1.metric("Total Workouts", len(w)); c2.metric("Workout Minutes", int(w["duration_min"].sum())); c3.metric("Cardio Minutes", int(w["cardio_min"].sum()))
    st.markdown("### Body progress")
    with st.expander("Add body progress"):
        with st.form("body_form"):
            body_date=st.date_input("Date", date.today(), key="body_date"); a,b,c,d=st.columns(4); weight=a.number_input("Weight lb", min_value=0.0, step=0.5); waist=b.number_input("Waist in", min_value=0.0, step=0.5); hips=c.number_input("Hips in", min_value=0.0, step=0.5); chest=d.number_input("Chest in", min_value=0.0, step=0.5)
            energy=st.selectbox("Energy", ["Low", "Moderate", "High"]); sleep=st.number_input("Sleep hours", min_value=0.0, step=0.5); notes=st.text_area("Notes", key="body_notes")
            if st.form_submit_button("Save progress"):
                row={"id": make_id("body"), "date": str(body_date), "weight_lb": weight, "waist_in": waist, "hips_in": hips, "chest_in": chest, "energy": energy, "sleep_hours": sleep, "notes": notes}
                body=pd.concat([body, pd.DataFrame([row])], ignore_index=True); save_csv(body, "body_log"); st.success("Progress saved."); st.rerun()
    if not body.empty:
        b=numeric_cols(body, ["weight_lb", "waist_in", "hips_in", "chest_in"]); st.dataframe(b.drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True); st.line_chart(b.set_index("date")[["weight_lb", "waist_in"]])

with tabs[6]:
    st.subheader("⚙️ Settings")
    for key,path in FILES.items():
        if path.exists(): st.download_button(f"Download {key}.csv", data=path.read_bytes(), file_name=path.name, mime="text/csv")
    st.warning("Reset buttons erase saved data.")
    a,b=st.columns(2)
    if a.button("Reset grocery + saved meals"):
        if FILES["grocery"].exists(): FILES["grocery"].unlink()
        if FILES["saved_meals"].exists(): FILES["saved_meals"].unlink()
        seed_grocery(); seed_saved_meals(); st.success("Reset grocery and saved meals."); st.rerun()
    if b.button("Clear weekly plan"):
        save_csv(pd.DataFrame(columns=WEEKLY_PLAN_COLUMNS), "weekly_plan"); st.success("Weekly plan cleared."); st.rerun()
    c,d=st.columns(2)
    if c.button("Clear meal logs"):
        save_csv(pd.DataFrame(columns=MEAL_LOG_COLUMNS), "meal_log"); st.success("Meal logs cleared."); st.rerun()
    if d.button("Clear workout logs"):
        save_csv(pd.DataFrame(columns=WORKOUT_LOG_COLUMNS), "workout_log"); st.success("Workout logs cleared."); st.rerun()
    st.code("streamlit run mobile_friendly_fitness_dashboard.py", language="bash")
