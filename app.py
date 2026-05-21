import streamlit as st
import pandas as pd
import json, os
from datetime import date, datetime, timedelta
from collections import defaultdict

APP_TITLE = "GlowFit Metabolic Dashboard"
DATA_FILE = "glowfit_data.json"
HEIGHT_IN = 69
START_WEIGHT = 224.0
GOAL_WEIGHT = 199.0
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MEAL_TYPES = ["Breakfast","Lunch","Dinner","Snack"]

RECIPES = {
    "Greek Yogurt Oat Protein Bowl": {"meal_type":"Breakfast","servings":4,"gi":"Low–Moderate","warning":"Use unsweetened Greek yogurt; measure oats and toppings.","cal":380,"protein":32,"carbs":38,"fiber":8,"ingredients":{"Greek yogurt 0-2% (g)":800,"rolled oats (g)":160,"berries (g)":400,"chia seeds (tbsp)":8,"cinnamon (tsp)":2},"steps":["Weigh 200g yogurt per container.","Add 40g oats, 100g berries, 2 tbsp chia.","Measure toppings instead of free-pouring."],"swap":"Swap honey/granola for cinnamon, chia, or berries."},
    "Chicken Quinoa Veggie Bowls": {"meal_type":"Lunch","servings":5,"gi":"Low","warning":"Keep quinoa measured; add extra vegetables for volume.","cal":520,"protein":45,"carbs":45,"fiber":9,"ingredients":{"chicken breast (g)":900,"cooked quinoa (cups)":5,"broccoli (g)":600,"bell peppers (g)":400,"olive oil (tbsp)":5,"avocado (g)":250},"steps":["Weigh 180g cooked chicken per serving.","Use 1 cup cooked quinoa per bowl.","Add 200g+ vegetables. Measure oil."],"swap":"Use half quinoa and half cauliflower rice on rest days."},
    "Salmon Potato Green Plate": {"meal_type":"Dinner","servings":4,"gi":"Moderate","warning":"Potato is portion-sensitive; pair with protein and vegetables.","cal":560,"protein":42,"carbs":42,"fiber":7,"ingredients":{"salmon fillets (g)":680,"baby potatoes (g)":800,"green beans (g)":600,"Greek yogurt sauce (g)":240,"olive oil (tbsp)":4},"steps":["Weigh 170g salmon per serving.","Measure 200g potato per serving.","Add 150g green beans and 60g yogurt sauce."],"swap":"Swap half the potato for more green beans if needed."},
    "Egg Veggie Breakfast Wrap": {"meal_type":"Breakfast","servings":3,"gi":"Moderate","warning":"Choose high-fibre wraps; avoid sugary drinks alongside.","cal":410,"protein":30,"carbs":34,"fiber":8,"ingredients":{"eggs":6,"egg whites (cups)":1.5,"high fibre wraps":3,"spinach (g)":180,"mushrooms (g)":240,"cheese (g)":60},"steps":["Use 2 eggs + 1/2 cup whites per wrap.","Measure cheese at 20g.","Load vegetables first."],"swap":"Use a lettuce bowl instead of wrap for lower-carb days."},
    "Turkey Chili Meal Prep": {"meal_type":"Dinner","servings":6,"gi":"Low","warning":"Beans are fibre-rich but portion still matters.","cal":450,"protein":38,"carbs":40,"fiber":12,"ingredients":{"lean ground turkey (g)":900,"black beans cans":2,"kidney beans cans":2,"crushed tomatoes cans":2,"onion":2,"bell peppers":3,"chili seasoning (tbsp)":4},"steps":["Cook turkey fully.","Simmer with beans, tomatoes, and vegetables.","Divide into 6 equal containers."],"swap":"Serve over cauliflower rice instead of white rice."},
    "Tuna Egg Cottage Snack Box": {"meal_type":"Snack","servings":4,"gi":"Low","warning":"Measure crackers; use veggie dippers when carbs are high.","cal":310,"protein":35,"carbs":18,"fiber":4,"ingredients":{"tuna cans":4,"boiled eggs":4,"cottage cheese (g)":600,"cucumber (g)":400,"whole grain crackers servings":4},"steps":["Pack 1 tuna can, 1 egg, 150g cottage cheese.","Add cucumber/veg first.","Measure crackers as one serving."],"swap":"Swap crackers for cucumber or peppers."},
}

WORKOUTS = {
 "Monday": {"focus":"Glutes + Lower Body Strength","type":"Training","exercises":[("Barbell or Smith Hip Thrust",4,"8-12",95,"https://www.youtube.com/results?search_query=hip+thrust+proper+form"),("Romanian Deadlift",3,"8-10",40,"https://www.youtube.com/results?search_query=romanian+deadlift+form"),("Leg Press - Glute Bias",3,"10-12",120,"https://www.youtube.com/results?search_query=glute+bias+leg+press"),("Cable Kickback",3,"12-15 each",15,"https://www.youtube.com/results?search_query=cable+kickback+form"),("Incline Walk",1,"20 min",0,"https://www.youtube.com/results?search_query=treadmill+incline+walking+fat+loss")]},
 "Tuesday": {"focus":"Upper Body + Core","type":"Training","exercises":[("Lat Pulldown",3,"10-12",50,"https://www.youtube.com/results?search_query=lat+pulldown+form"),("Dumbbell Shoulder Press",3,"8-10",15,"https://www.youtube.com/results?search_query=dumbbell+shoulder+press+form"),("Seated Cable Row",3,"10-12",50,"https://www.youtube.com/results?search_query=seated+cable+row+form"),("Tricep Rope Pushdown",3,"12-15",25,"https://www.youtube.com/results?search_query=tricep+rope+pushdown+form"),("Dead Bug",3,"10 each",0,"https://www.youtube.com/results?search_query=dead+bug+exercise+form")]},
 "Wednesday": {"focus":"Cardio + Mobility Recovery","type":"Training","exercises":[("Incline Treadmill Walk",1,"30-40 min",0,"https://www.youtube.com/results?search_query=incline+treadmill+walking+workout"),("Step Ups",3,"10 each",10,"https://www.youtube.com/results?search_query=dumbbell+step+ups+form"),("Glute Bridge Burnout",3,"20",0,"https://www.youtube.com/results?search_query=glute+bridge+form"),("Side Plank",3,"20-30 sec each",0,"https://www.youtube.com/results?search_query=side+plank+form")]},
 "Thursday": {"focus":"Glutes + Hamstrings","type":"Training","exercises":[("Bulgarian Split Squat",3,"8-10 each",15,"https://www.youtube.com/results?search_query=bulgarian+split+squat+form"),("Hamstring Curl",3,"10-12",45,"https://www.youtube.com/results?search_query=hamstring+curl+machine+form"),("Goblet Squat",3,"10-12",25,"https://www.youtube.com/results?search_query=goblet+squat+form"),("Hip Abduction Machine",4,"12-20",60,"https://www.youtube.com/results?search_query=hip+abduction+machine+form"),("Stairmaster",1,"10-15 min",0,"https://www.youtube.com/results?search_query=stairmaster+beginner+workout")]},
 "Friday": {"focus":"Upper Body Tone + Core","type":"Training","exercises":[("Chest Press Machine",3,"10-12",40,"https://www.youtube.com/results?search_query=chest+press+machine+form"),("Assisted Row",3,"10-12",45,"https://www.youtube.com/results?search_query=machine+row+form"),("Lateral Raises",3,"12-15",8,"https://www.youtube.com/results?search_query=dumbbell+lateral+raise+form"),("Bicep Curl",3,"10-12",10,"https://www.youtube.com/results?search_query=dumbbell+bicep+curl+form"),("Pallof Press",3,"10 each",15,"https://www.youtube.com/results?search_query=pallof+press+form")]},
 "Saturday": {"focus":"Full Body + Cardio","type":"Training","exercises":[("Kettlebell Deadlift",3,"10-12",35,"https://www.youtube.com/results?search_query=kettlebell+deadlift+form"),("Walking Lunges",3,"10 each",10,"https://www.youtube.com/results?search_query=walking+lunge+form"),("Push Ups Incline",3,"8-12",0,"https://www.youtube.com/results?search_query=incline+pushup+form"),("Bike or Elliptical",1,"25-35 min",0,"https://www.youtube.com/results?search_query=elliptical+beginner+workout")]},
 "Sunday": {"focus":"Rest + Steps + Stretch","type":"Rest","exercises":[("Easy Walk",1,"20-45 min",0,"https://www.youtube.com/results?search_query=easy+walk+recovery+day"),("Hip Flexor Stretch",2,"30 sec each",0,"https://www.youtube.com/results?search_query=hip+flexor+stretch"),("Glute Stretch",2,"30 sec each",0,"https://www.youtube.com/results?search_query=glute+stretch")]},
}

SYMPTOMS = {"Shaky or trembling":"Eat a balanced snack if needed; track timing and speak with a clinician if frequent.","Dizzy or lightheaded":"Sit down, hydrate, and avoid intense training until stable.","Very thirsty":"Hydrate; persistent excessive thirst should be discussed with a provider.","Frequent urination":"Track pattern; persistent symptoms should be discussed with a clinician.","Blurred vision":"Pause driving/training and seek medical advice if sudden or persistent.","Extreme fatigue":"Prioritize rest, protein/fibre meals, hydration, and review sleep/stress.","Headache":"Hydrate and check meal timing; watch if linked to high-sugar meals.","Sweating unexpectedly":"Rest and consider whether food timing or exertion could be involved."}
SWAPS = [("White rice","Quinoa, lentils, cauliflower rice, or half rice + half veg"),("Juice/soda","Water, sparkling water, unsweetened tea, zero-sugar drink"),("Granola","Chia, flax, berries, measured nuts"),("Creamy dressing","Greek-yogurt sauce, salsa, lemon, measured olive oil"),("Large potato serving","Smaller cooled/reheated potato + extra protein/greens"),("Sugary snack","Greek yogurt, egg snack box, cottage cheese, apple + peanut butter")]

def today_str(): return date.today().isoformat()
def week_start(d=None):
    d = d or date.today(); return (d - timedelta(days=d.weekday())).isoformat()
def day_name(s): return datetime.strptime(s, "%Y-%m-%d").strftime("%A")
def default_week(): return {day:{mt:[] for mt in MEAL_TYPES} for day in DAYS}
def default_data():
    return {"profile":{"height_in":HEIGHT_IN,"start_weight":START_WEIGHT,"goal_weight":GOAL_WEIGHT,"age":28},"settings":{"training_day":True,"calorie_target_training":1900,"calorie_target_rest":1700,"protein_target":140,"water_target":3.0,"step_target":8000},"daily":{},"weight_logs":[],"manual_foods":[],"weekly_plan":{week_start():default_week()},"grocery_checked":{},"workout_logs":{},"symptom_logs":[]}
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f: data=json.load(f)
        except Exception: data=default_data()
    else: data=default_data()
    d=default_data()
    for k,v in d.items(): data.setdefault(k,v)
    data.setdefault("weekly_plan",{}).setdefault(week_start(), default_week())
    return data
def save_data():
    with open(DATA_FILE,"w") as f: json.dump(st.session_state.data,f,indent=2)
def get_day(ds):
    st.session_state.data["daily"].setdefault(ds,{"water":0.0,"steps":0,"training_day":st.session_state.data["settings"].get("training_day",True),"notes":""})
    return st.session_state.data["daily"][ds]
def get_plan(ws=None):
    ws=ws or week_start(); st.session_state.data["weekly_plan"].setdefault(ws, default_week()); return st.session_state.data["weekly_plan"][ws]
def nutrition_recipe(name, servings=1):
    r=RECIPES[name]; return {"calories":r["cal"]*servings,"protein":r["protein"]*servings,"carbs":r["carbs"]*servings,"fiber":r["fiber"]*servings}
def planned_meals(ds):
    return st.session_state.data.get("weekly_plan",{}).get(week_start(datetime.strptime(ds,"%Y-%m-%d").date()),{}).get(day_name(ds),{mt:[] for mt in MEAL_TYPES})
def manual_foods(ds): return [f for f in st.session_state.data["manual_foods"] if f.get("date")==ds]
def daily_totals(ds):
    t={"calories":0,"protein":0,"carbs":0,"fiber":0}
    for meals in planned_meals(ds).values():
        for m in meals:
            n=nutrition_recipe(m["recipe"],float(m.get("servings",1)))
            for k in t: t[k]+=n[k]
    for f in manual_foods(ds):
        for k in t: t[k]+=float(f.get(k,0))
    return t
def grocery_totals(ws=None):
    ws=ws or week_start(); totals=defaultdict(float)
    for day,slots in get_plan(ws).items():
        for meals in slots.values():
            for m in meals:
                r=RECIPES[m["recipe"]]; factor=float(m.get("servings",1))/r["servings"]
                for ing,qty in r["ingredients"].items(): totals[ing]+=qty*factor
    for f in st.session_state.data["manual_foods"]:
        if f.get("add_to_grocery") and f.get("grocery_item"): totals[f["grocery_item"]]+=float(f.get("grocery_qty",1))
    return dict(totals)
def bmi(w): return round(w/(HEIGHT_IN**2)*703,1)
def current_weight():
    logs=st.session_state.data["weight_logs"]
    return float(sorted(logs,key=lambda x:x["date"])[-1]["weight"]) if logs else START_WEIGHT
def tdee(w,training=True):
    kg=w*0.453592; cm=HEIGHT_IN*2.54; age=st.session_state.data["profile"].get("age",28)
    return int((10*kg+6.25*cm-5*age-161)*(1.45 if training else 1.32))
def progress_df():
    rows=[]
    for ds,vals in st.session_state.data["daily"].items(): rows.append({"date":ds,"water":vals.get("water",0),"steps":vals.get("steps",0),**daily_totals(ds)})
    return pd.DataFrame(rows).sort_values("date") if rows else pd.DataFrame()
def wkey(day,ei,si,ws=None): return f"{ws or week_start()}|{day}|{ei}|{si}"
def day_completion(day,ws=None):
    ws=ws or week_start(); total=done=0
    for ei,ex in enumerate(WORKOUTS[day]["exercises"]):
        sets=ex[1]
        for si in range(sets):
            total+=1
            if st.session_state.data["workout_logs"].get(wkey(day,ei,si,ws),{}).get("done"): done+=1
    return total>0 and done==total, done, total

def theme():
    st.markdown("""<style>.stApp{background:linear-gradient(135deg,#120f19,#1b1424 50%,#21101d);color:#f6eef8}[data-testid='stSidebar']{background:#100d16}.card{padding:16px;border-radius:18px;background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.10);margin-bottom:12px}.soft{color:#d7c4dc}.warn{padding:12px;border-radius:14px;background:rgba(255,190,120,.12);border:1px solid rgba(255,190,120,.3)}h1,h2,h3{color:#fff3fb}</style>""",unsafe_allow_html=True)

st.set_page_config(APP_TITLE,page_icon="💗",layout="wide")
if "data" not in st.session_state: st.session_state.data=load_data()
theme()
with st.sidebar:
    st.title("💗 GlowFit")
    page=st.radio("Go to",["Home","Meals","Weekly Plan","Recipes","Grocery","Workouts","Progress","Blood Sugar","Settings / Backup"],label_visibility="collapsed")
    st.caption("Prediabetes-aware • fat loss • glute growth")
    if st.button("💾 Save now",use_container_width=True): save_data(); st.success("Saved")

if page=="Home":
    st.title("Home Dashboard")
    ds=st.date_input("Dashboard date",date.today()).isoformat(); day=get_day(ds); totals=daily_totals(ds); wt=current_weight()
    training=st.toggle("Training day mode",value=bool(day.get("training_day",True)))
    day["training_day"]=training; st.session_state.data["settings"]["training_day"]=training; save_data()
    cal_target=st.session_state.data["settings"]["calorie_target_training"] if training else st.session_state.data["settings"]["calorie_target_rest"]
    c=st.columns(4); c[0].metric("Weight",f"{wt:.1f} lb"); c[1].metric("Calories",f"{int(totals['calories'])}/{cal_target}"); c[2].metric("Protein",f"{int(totals['protein'])}/{st.session_state.data['settings']['protein_target']}g"); c[3].metric("BMI",bmi(wt))
    st.progress(max(0,min(1,(START_WEIGHT-wt)/(START_WEIGHT-GOAL_WEIGHT))), text="Progress toward under 200 lb")
    st.info(("Training day: more smart carbs around workouts. " if training else "Rest day: emphasize protein, fibre, and measured carbs. ")+f"Estimated TDEE: ~{tdee(wt,training)} kcal")
    c1,c2,c3=st.columns(3); day["water"]=c1.number_input("Water today (L)",0.0,8.0,float(day.get("water",0)),0.25); day["steps"]=c2.number_input("Steps today",0,50000,int(day.get("steps",0)),500); day["notes"]=c3.text_input("Daily note",day.get("notes",""))
    if st.button("Save today’s home metrics"): save_data(); st.success("Saved")
    st.subheader("Today’s planned + manual food")
    for mt in MEAL_TYPES:
        with st.expander(mt,expanded=True):
            items=planned_meals(ds).get(mt,[]); mf=[f for f in manual_foods(ds) if f.get("meal_type")==mt]
            if not items and not mf: st.caption("Nothing added yet.")
            for p in items: st.write(f"• Planned: {p['recipe']} × {p.get('servings',1)}")
            for f in mf: st.write(f"• Manual: {f['name']} — {f.get('calories',0)} kcal")

elif page=="Meals":
    st.title("Food Dashboard")
    ds=st.date_input("Food date",date.today()).isoformat(); totals=daily_totals(ds)
    cols=st.columns(4); cols[0].metric("Calories",int(totals["calories"])); cols[1].metric("Protein",f"{int(totals['protein'])}g"); cols[2].metric("Carbs",f"{int(totals['carbs'])}g"); cols[3].metric("Fibre",f"{int(totals['fiber'])}g")
    st.subheader("Meals from weekly plan")
    for mt,items in planned_meals(ds).items():
        st.markdown(f"### {mt}")
        if not items: st.caption("No planned meal selected.")
        for item in items:
            r=RECIPES[item["recipe"]]; n=nutrition_recipe(item["recipe"],item.get("servings",1))
            st.markdown(f"<div class='card'><b>{item['recipe']}</b><br><span class='soft'>{int(n['calories'])} kcal • {int(n['protein'])}g protein • GI: {r['gi']}<br>{r['warning']}</span></div>",unsafe_allow_html=True)
    st.divider(); st.subheader("Add manual food")
    with st.form("manual_food",clear_on_submit=True):
        a,b=st.columns(2); name=a.text_input("Food/meal name"); mt=b.selectbox("Meal slot",MEAL_TYPES)
        cal=st.number_input("Calories",0,3000,0,10); pro=st.number_input("Protein (g)",0.0,250.0,0.0); carb=st.number_input("Carbs (g)",0.0,300.0,0.0); fib=st.number_input("Fibre (g)",0.0,100.0,0.0); gi=st.selectbox("GI awareness",["Low","Moderate","Caution/High","Unknown"])
        addg=st.checkbox("Also add item to grocery list"); gitem=st.text_input("Grocery item name",value=name if name else "") if addg else ""; gqty=st.number_input("Grocery quantity",0.0,10000.0,1.0) if addg else 0
        if st.form_submit_button("Save manual food") and name:
            st.session_state.data["manual_foods"].append({"date":ds,"meal_type":mt,"name":name,"calories":cal,"protein":pro,"carbs":carb,"fiber":fib,"gi":gi,"add_to_grocery":addg,"grocery_item":gitem,"grocery_qty":gqty,"created_at":datetime.now().isoformat()}); save_data(); st.success("Saved and linked."); st.rerun()
    st.subheader("Manual foods for this date")
    for f in manual_foods(ds): st.write(f"{f['meal_type']}: **{f['name']}** — {f['calories']} kcal, {f['protein']}g protein")

elif page=="Weekly Plan":
    st.title("Weekly Meal Plan")
    ws=week_start(st.date_input("Choose any date in week",date.today())); plan=get_plan(ws)
    st.caption("This feeds the Food Dashboard and Grocery List automatically.")
    for day in DAYS:
        with st.expander(day,expanded=(day==date.today().strftime('%A'))):
            for mt in MEAL_TYPES:
                existing=[x["recipe"] for x in plan[day][mt]]
                selected=st.multiselect(f"{day} {mt}",list(RECIPES.keys()),default=existing,key=f"plan_{ws}_{day}_{mt}")
                new=[]
                for r in selected:
                    old=next((x for x in plan[day][mt] if x["recipe"]==r),None)
                    serv=st.number_input(f"Servings of {r}",0.5,20.0,float(old.get("servings",1) if old else 1),0.5,key=f"serv_{ws}_{day}_{mt}_{r}")
                    new.append({"recipe":r,"servings":serv})
                plan[day][mt]=new
    if st.button("Save weekly plan and update groceries",use_container_width=True): save_data(); st.success("Saved")

elif page=="Recipes":
    st.title("Recipes + Portion Accuracy")
    st.markdown("<div class='warn'>Use a food scale when possible. Divide finished meal prep into equal containers for accurate calories.</div>",unsafe_allow_html=True)
    for name,r in RECIPES.items():
        with st.expander(name):
            st.write(f"Meal type: {r['meal_type']} • Batch servings: {r['servings']} • GI: {r['gi']}"); st.write(f"Per serving: {r['cal']} kcal • {r['protein']}g protein • {r['carbs']}g carbs • {r['fiber']}g fibre"); st.warning(r["warning"])
            st.write("Full meal prep ingredients:"); st.table(pd.DataFrame([{"Ingredient":k,"Batch quantity":v} for k,v in r["ingredients"].items()]))
            st.write("Dishing/accuracy steps:"); [st.write(f"- {s}") for s in r["steps"]]; st.write(f"Swap: {r['swap']}")
    st.subheader("Swap suggestions"); [st.write(f"**{a} →** {b}") for a,b in SWAPS]

elif page=="Grocery":
    st.title("Smart Grocery List")
    ws=week_start(st.date_input("Grocery week",date.today())); g=grocery_totals(ws); checked=st.session_state.data.setdefault("grocery_checked",{})
    if not g: st.info("Add meals or manual foods with grocery enabled.")
    cats={"Protein":[],"Carbs/Fibre":[],"Vegetables/Fruit":[],"Dairy/Fats/Pantry":[]}
    for item,qty in g.items():
        low=item.lower(); cat="Dairy/Fats/Pantry"
        if any(x in low for x in ["chicken","salmon","turkey","tuna","egg"]): cat="Protein"
        elif any(x in low for x in ["oat","quinoa","potato","beans","wrap","cracker"]): cat="Carbs/Fibre"
        elif any(x in low for x in ["broccoli","pepper","green","berries","spinach","mushroom","cucumber","onion"]): cat="Vegetables/Fruit"
        cats[cat].append((item,qty))
    for cat,items in cats.items():
        st.subheader(cat)
        for item,qty in items:
            key=f"{ws}|{item}"; checked[key]=st.checkbox(f"{item}: {round(qty,2)}",value=checked.get(key,False),key=f"chk_{key}")
    if st.button("Save grocery checks"): save_data(); st.success("Saved")

elif page=="Workouts":
    st.title("Workout Dashboard")
    ws=week_start(st.date_input("Workout week",date.today())); today_idx=date.today().weekday()
    remaining=[]; previous=[]
    for i,day in enumerate(DAYS):
        complete,done,total=day_completion(day,ws); (remaining if i>=today_idx and not complete else previous).append((day,done,total))
    def render_day(day,done,total,expanded=False):
        w=WORKOUTS[day]
        with st.expander(f"{day}: {w['focus']} — {done}/{total} sets complete",expanded=expanded):
            st.write(f"Type: {w['type']}"); logs=st.session_state.data["workout_logs"]
            for ei,ex in enumerate(w["exercises"]):
                name,sets,reps,weight,video=ex; st.markdown(f"#### {name}"); st.link_button("Form video",video)
                for si in range(sets):
                    k=wkey(day,ei,si,ws); row=logs.setdefault(k,{"done":False,"weight":weight,"reps":reps,"rating":3})
                    c=st.columns([1,1,1,1]); row["done"]=c[0].checkbox(f"Set {si+1}",value=row.get("done",False),key=f"done_{k}"); row["weight"]=c[1].number_input("Weight",0.0,1000.0,float(row.get("weight",0)),5.0,key=f"wt_{k}"); row["reps"]=c[2].text_input("Reps/time",str(row.get("reps",reps)),key=f"reps_{k}"); row["rating"]=c[3].slider("Effort",1,5,int(row.get("rating",3)),key=f"rate_{k}")
            if st.button(f"Save {day}",key=f"save_{ws}_{day}"): save_data(); st.success("Workout saved"); st.rerun()
    st.subheader("Current / Remaining this week")
    for day,done,total in remaining: render_day(day,done,total,expanded=(day==date.today().strftime('%A')))
    st.subheader("Completed / Previous")
    for day,done,total in previous: render_day(day,done,total)

elif page=="Progress":
    st.title("Progress + BMI")
    wt=current_weight(); c=st.columns(3); c[0].metric("Current weight",f"{wt:.1f} lb"); c[1].metric("BMI",bmi(wt)); c[2].metric("Goal","Under 200 lb")
    with st.form("weight_form",clear_on_submit=True):
        d=st.date_input("Log date",date.today()); w=st.number_input("Weight (lb)",50.0,500.0,wt,0.1); waist=st.number_input("Waist optional (in)",0.0,100.0,0.0,0.1)
        if st.form_submit_button("Save weight/progress"):
            st.session_state.data["weight_logs"].append({"date":d.isoformat(),"weight":w,"waist":waist if waist>0 else None,"bmi":bmi(w),"created_at":datetime.now().isoformat()}); save_data(); st.success("Saved"); st.rerun()
    if st.session_state.data["weight_logs"]:
        df=pd.DataFrame(st.session_state.data["weight_logs"]).sort_values("date"); st.line_chart(df.set_index("date")[["weight","bmi"]])
    df=progress_df()
    if not df.empty: st.subheader("Daily trends"); st.line_chart(df.set_index("date")[[x for x in ["calories","protein","carbs","fiber","water","steps"] if x in df.columns]])
    rows=[]
    for day in DAYS:
        comp,done,total=day_completion(day,week_start()); rows.append({"day":day,"sets_done":done,"total_sets":total,"percent":round(done/total*100 if total else 0,1)})
    st.subheader("Workout completion"); st.dataframe(pd.DataFrame(rows),use_container_width=True)

elif page=="Blood Sugar":
    st.title("Blood Sugar Awareness")
    st.caption("Not a diagnosis tool. Use it to notice patterns and decide when to seek medical support.")
    ds=st.date_input("Symptom date",date.today()).isoformat(); selected=[]
    for sym,tip in SYMPTOMS.items():
        if st.checkbox(sym,key=f"sym_{ds}_{sym}"): selected.append(sym); st.info(tip)
    notes=st.text_area("Notes: food timing, workout, stress, sleep")
    if st.button("Save symptom log"):
        st.session_state.data["symptom_logs"].append({"date":ds,"symptoms":selected,"notes":notes,"tips":[SYMPTOMS[s] for s in selected],"created_at":datetime.now().isoformat()}); save_data(); st.success("Saved")
    st.subheader("Symptom history")
    for log in sorted(st.session_state.data["symptom_logs"],key=lambda x:x["date"],reverse=True):
        st.write(f"**{log['date']}**: {', '.join(log['symptoms']) if log['symptoms'] else 'No symptoms selected'}");
        if log.get("notes"): st.caption(log["notes"])

elif page=="Settings / Backup":
    st.title("Settings / Backup")
    s=st.session_state.data["settings"]
    with st.form("settings_form"):
        s["calorie_target_training"]=st.number_input("Training day calorie target",1200,3500,int(s.get("calorie_target_training",1900)),50); s["calorie_target_rest"]=st.number_input("Rest day calorie target",1200,3500,int(s.get("calorie_target_rest",1700)),50); s["protein_target"]=st.number_input("Protein target (g/day)",80,220,int(s.get("protein_target",140)),5); s["water_target"]=st.number_input("Water target (L/day)",1.0,6.0,float(s.get("water_target",3.0)),0.25); s["step_target"]=st.number_input("Step target",1000,30000,int(s.get("step_target",8000)),500); st.session_state.data["profile"]["age"]=st.number_input("Age for TDEE estimate",18,80,int(st.session_state.data["profile"].get("age",28)),1)
        if st.form_submit_button("Save settings"): save_data(); st.success("Settings saved and will persist after refresh.")
    st.download_button("Download backup JSON",json.dumps(st.session_state.data,indent=2),"glowfit_backup.json","application/json")
    up=st.file_uploader("Restore from backup JSON",type="json")
    if up is not None:
        try: st.session_state.data=json.load(up); save_data(); st.success("Backup restored.")
        except Exception as e: st.error(f"Could not restore: {e}")
    if st.button("Reset all data",type="secondary"): st.session_state.data=default_data(); save_data(); st.warning("All data reset."); st.rerun()

