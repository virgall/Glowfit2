import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date, datetime, timedelta

st.set_page_config(page_title='GlowFit', layout='wide', initial_sidebar_state='expanded')
DATA_DIR=Path('data'); DATA_DIR.mkdir(exist_ok=True); DATA_FILE=DATA_DIR/'glowfit_data.json'
DAYS=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MEAL_TYPES=['Breakfast','Lunch','Dinner','Snack']
PROFILE={'height_in':69,'start_weight':224.0,'current_weight':224.0,'goal_weight':199.0,'protein_target':140,'training_day':True,'calorie_training':1850,'calorie_rest':1650,'carb_training':150,'carb_rest':105,'water_target_l':2.8,'step_target':8000}
MEALS={
'Greek Yogurt Berry Parfait':{'type':'Breakfast','cal':360,'protein':34,'carbs':32,'fibre':8,'gi':'Low','when':'Good breakfast or post-workout snack.','prep_servings':4,'ingredients':{'Greek yogurt plain':[800,'g'],'Mixed berries':[480,'g'],'Chia seeds':[48,'g'],'Low sugar granola':[120,'g']},'steps':['Weigh yogurt and berries.','Portion 200g yogurt per serving.','Keep granola measured at 30g per serving.']},
'Protein Oats With Berries':{'type':'Breakfast','cal':420,'protein':35,'carbs':46,'fibre':9,'gi':'Moderate','when':'Best on training mornings or before lower body/cardio days.','prep_servings':3,'ingredients':{'Rolled oats':[120,'g'],'Protein powder':[90,'g'],'Mixed berries':[360,'g'],'Chia seeds':[30,'g']},'steps':['Measure dry oats: 40g per serving.','Add protein after cooking.','Use berries instead of syrup.']},
'High Protein Cereal Bowl':{'type':'Breakfast','cal':390,'protein':32,'carbs':42,'fibre':8,'gi':'Moderate','when':'Best at breakfast or after training. Avoid late-night oversized bowls.','prep_servings':1,'ingredients':{'High protein low sugar cereal':[45,'g'],'Greek yogurt plain':[170,'g'],'Strawberries':[100,'g'],'Chia seeds':[10,'g']},'steps':['Weigh cereal at 45g.','Use Greek yogurt to increase protein.','Add berries for fibre.']},
'Eggs Avocado Toast Plate':{'type':'Breakfast','cal':430,'protein':28,'carbs':30,'fibre':8,'gi':'Low-Moderate','when':'Good filling breakfast, especially on active days.','prep_servings':1,'ingredients':{'Eggs':[2,'large'],'Egg whites':[120,'g'],'Avocado':[50,'g'],'Whole grain toast':[1,'slice'],'Spinach':[60,'g']},'steps':['Measure avocado to 50g.','Use 1 slice toast.','Cook with spray or measured oil.']},
'Chicken Konjac Rice Bowl':{'type':'Lunch','cal':480,'protein':48,'carbs':24,'fibre':10,'gi':'Low','when':'Great lunch or dinner for fat loss and blood sugar stability.','prep_servings':4,'ingredients':{'Chicken breast':[680,'g'],'Konjac rice':[800,'g'],'Broccoli':[500,'g'],'Bell peppers':[300,'g'],'Olive oil':[20,'g']},'steps':['Rinse konjac rice very well.','Dry-pan before mixing.','Measure oil with a teaspoon or scale.','Split into 4 containers.']},
'Shrimp Konjac Rice Bowl':{'type':'Lunch','cal':430,'protein':44,'carbs':20,'fibre':8,'gi':'Low','when':'Good lighter lunch or dinner, especially on rest days.','prep_servings':3,'ingredients':{'Shrimp':[540,'g'],'Konjac rice':[600,'g'],'Zucchini':[300,'g'],'Spinach':[180,'g'],'Avocado':[120,'g']},'steps':['Drain shrimp well.','Use konjac rice for volume.','Measure avocado to control calories.']},
'Chicken Shawarma Bowl':{'type':'Lunch','cal':520,'protein':50,'carbs':32,'fibre':9,'gi':'Low-Moderate','when':'Use more vegetables and less wrap/rice on rest days.','prep_servings':4,'ingredients':{'Chicken breast':[720,'g'],'Cucumber':[300,'g'],'Tomatoes':[300,'g'],'Lettuce':[300,'g'],'Greek yogurt sauce':[240,'g'],'Low carb wrap':[4,'wraps']},'steps':['Use yogurt sauce.','Keep wrap to one serving.','Add extra lettuce and cucumber.']},
'Tuna Egg Salad Plate':{'type':'Lunch','cal':420,'protein':42,'carbs':18,'fibre':7,'gi':'Low','when':'Good low-carb lunch or rest-day meal.','prep_servings':2,'ingredients':{'Tuna':[2,'cans'],'Eggs':[4,'large'],'Greek yogurt plain':[80,'g'],'Celery':[120,'g'],'Cucumber':[200,'g'],'Lettuce':[200,'g']},'steps':['Use Greek yogurt instead of lots of mayo.','Serve over lettuce/cucumber.','Measure dressing.']},
'Salmon Veg Sweet Potato':{'type':'Dinner','cal':560,'protein':42,'carbs':38,'fibre':8,'gi':'Moderate','when':'Best after training or on higher activity days.','prep_servings':3,'ingredients':{'Salmon':[450,'g'],'Sweet potato':[450,'g'],'Green beans':[450,'g'],'Olive oil':[18,'g']},'steps':['Keep sweet potato around 150g per serving.','Pair carb with salmon and vegetables.','Avoid sugary glazes.']},
'Turkey Konjac Noodle Stir Fry':{'type':'Dinner','cal':470,'protein':45,'carbs':22,'fibre':9,'gi':'Low','when':'Good dinner when you want noodles without a heavy carb load.','prep_servings':4,'ingredients':{'Lean ground turkey':[680,'g'],'Konjac noodles':[800,'g'],'Mixed stir fry vegetables':[700,'g'],'Low sodium soy sauce':[60,'ml'],'Sesame oil':[16,'g']},'steps':['Rinse and dry-pan konjac noodles.','Cook turkey fully.','Measure sesame oil carefully.']},
'Fish Tacos Low Carb Wrap':{'type':'Dinner','cal':500,'protein':42,'carbs':34,'fibre':9,'gi':'Low-Moderate','when':'Better on training days or active days.','prep_servings':3,'ingredients':{'White fish':[540,'g'],'Low carb wrap':[6,'wraps'],'Cabbage slaw':[360,'g'],'Greek yogurt sauce':[180,'g'],'Avocado':[120,'g']},'steps':['Use 2 small wraps or 1 large wrap.','Measure avocado.','Use yogurt sauce instead of creamy dressing.']},
'Apple Peanut Butter Protein Snack':{'type':'Snack','cal':260,'protein':12,'carbs':28,'fibre':6,'gi':'Low-Moderate','when':'Good pre-workout snack or afternoon snack. Measure peanut butter.','prep_servings':1,'ingredients':{'Green apple':[1,'medium'],'Peanut butter':[16,'g'],'Greek yogurt plain':[100,'g']},'steps':['Use one medium green apple.','Measure peanut butter at 16g.','Pair with Greek yogurt.']},
'Kiwi Cottage Cheese Bowl':{'type':'Snack','cal':240,'protein':25,'carbs':22,'fibre':4,'gi':'Low','when':'Good snack or light breakfast.','prep_servings':1,'ingredients':{'Cottage cheese':[200,'g'],'Kiwi':[1,'whole'],'Chia seeds':[8,'g']},'steps':['Measure cottage cheese.','Use one kiwi.','Add chia for fibre.']}
}
LIMITED={'Banana':'Best pre/post-workout with protein. Use half or small banana. Avoid alone late at night.','Mango':'Best after intense lower-body/cardio in a small serving with protein.','Pineapple':'Best post-workout in controlled portion with Greek yogurt/cottage cheese.','Grapes':'Small measured handful after activity or paired with nuts/protein.','Watermelon':'Small portions on hot/active days with protein.','Dried fruit':'Rare and measured, preferably around training.','Fruit juice':'Avoid as default unless clinician guidance says otherwise.'}
GROCERY={'Proteins':['Chicken breast','Salmon','White fish','Shrimp','Lean ground turkey','Eggs','Egg whites','Tuna','Greek yogurt plain','Cottage cheese','Protein powder'],'Low sugar fruits':['Strawberries','Blueberries','Raspberries','Blackberries','Green apple','Kiwi','Grapefruit','Pear','Cherries'],'Limited fruits':list(LIMITED.keys()),'Vegetables':['Broccoli','Spinach','Lettuce','Cucumber','Tomatoes','Zucchini','Green beans','Bell peppers','Celery','Cabbage slaw','Mixed stir fry vegetables'],'Smart carbs and swaps':['Konjac rice','Konjac noodles','Rolled oats','Sweet potato','Low carb wrap','Whole grain toast','High protein low sugar cereal'],'Fats and extras':['Avocado','Peanut butter','Olive oil','Chia seeds','Low sodium soy sauce','Greek yogurt sauce','Sesame oil','Low sugar granola']}
WORKOUT={'Monday':('Glutes + Lower Body',[['Hip Thrust',4,10,55],['Goblet Squat',3,10,25],['Romanian Deadlift',3,10,35],['Glute Kickback',3,12,10],['Incline Walk',1,25,0]]),'Tuesday':('Upper Body + Core',[['Lat Pulldown',3,10,40],['Seated Row',3,10,35],['Shoulder Press',3,10,15],['Triceps Pressdown',3,12,20],['Dead Bug',3,12,0]]),'Wednesday':('Cardio + Core',[['Incline Walk',1,35,0],['Plank',3,30,0],['Cable Woodchop',3,12,15],['Bird Dog',3,10,0]]),'Thursday':('Glutes + Hamstrings',[['Leg Press',4,10,90],['Romanian Deadlift',3,10,35],['Bulgarian Split Squat',3,8,15],['Hip Abduction',3,15,35],['Stairmaster',1,15,0]]),'Friday':('Upper Body Tone + Cardio',[['Incline Push Up',3,8,0],['Dumbbell Row',3,10,20],['Bicep Curl',3,12,10],['Lateral Raise',3,12,8],['Bike or Elliptical',1,25,0]]),'Saturday':('Active Recovery',[['Outdoor Walk',1,45,0],['Glute Bridge',3,15,0],['Stretching',1,15,0]]),'Sunday':('Rest + Prep',[['Gentle Walk',1,25,0],['Mobility',1,10,0]])}
SYMPTOMS={'Excessive thirst':'Hydrate and review recent meals. If persistent, discuss with your clinician.','Frequent urination':'Track timing and hydration. If persistent or severe, seek medical advice.','Shakiness':'Pause and follow clinician guidance. Pair carbs with protein/fibre.','Dizziness':'Pause activity, hydrate, and eat balanced food if needed. Seek help if severe.','Blurred vision':'Take seriously if new or recurrent. Consider medical advice.','Extreme fatigue':'Review sleep, meals, hydration, and training load.','Headache':'Hydrate and check meal timing.','Nausea':'Avoid intense workouts while feeling unwell.'}

def default_data(): return {'profile':PROFILE.copy(),'weekly_plan':{d:{m:'' for m in MEAL_TYPES} for d in DAYS},'manual_foods':[],'grocery_selected':{},'grocery_checked':{},'manual_grocery':[],'workout_logs':{},'daily_logs':{},'symptom_logs':[],'weight_logs':[]}
def merge(a,b):
    for k,v in b.items():
        if isinstance(v,dict) and isinstance(a.get(k),dict): merge(a[k],v)
        else: a[k]=v
def load():
    if DATA_FILE.exists():
        try:
            d=default_data(); merge(d,json.loads(DATA_FILE.read_text(encoding='utf-8'))); return d
        except Exception: return default_data()
    return default_data()
def save(): DATA_FILE.write_text(json.dumps(st.session_state.data,indent=2),encoding='utf-8')
def init():
    if 'data' not in st.session_state: st.session_state.data=load()
    if 'page' not in st.session_state: st.session_state.page='Home'
def today(): return date.today().isoformat()
def dname(ds): return datetime.strptime(ds,'%Y-%m-%d').strftime('%A')
def wkstart(): return (date.today()-timedelta(days=date.today().weekday())).isoformat()
def bmi(w,h=69): return round((w/(h*h))*703,1)
def totals(ds):
    data=st.session_state.data; out={'cal':0,'protein':0,'carbs':0,'fibre':0}; dn=dname(ds)
    for mt,mn in data['weekly_plan'].get(dn,{}).items():
        if mn in MEALS:
            for k in out: out[k]+=MEALS[mn][k]
    for x in data['manual_foods']:
        if x.get('date')==ds:
            for k in out: out[k]+=float(x.get(k,0) or 0)
    return out
def grocery_totals():
    data=st.session_state.data; out={}
    for d in DAYS:
        for mt,mn in data['weekly_plan'].get(d,{}).items():
            if mn in MEALS:
                for ing,(qty,unit) in MEALS[mn]['ingredients'].items(): out[(ing,unit)]=out.get((ing,unit),0)+qty
    for x in data['manual_grocery']: out[(x['name'],x.get('unit','item'))]=out.get((x['name'],x.get('unit','item')),0)+float(x.get('qty',1))
    return out
def suggestions():
    selected=[k for k,v in st.session_state.data['grocery_selected'].items() if v]; out=[]
    for mn,m in MEALS.items():
        score=sum(1 for ing in m['ingredients'] for s in selected if s.lower() in ing.lower() or ing.lower() in s.lower())
        if score: out.append((score,mn))
    return [m for s,m in sorted(out,reverse=True)]
def css(): st.markdown("""<style>.stApp{background:#0b0d14;color:#f5eef6}section[data-testid='stSidebar']{background:#10131d}.title{font-size:34px;font-weight:800}.sub{color:#c9bdc9}.card{background:#171a25;border:1px solid #2b3040;border-radius:18px;padding:16px;margin:10px 0}.muted{color:#b8adba}</style>""",unsafe_allow_html=True)
def card(x): st.markdown(f"<div class='card'>{x}</div>",unsafe_allow_html=True)

init(); css(); data=st.session_state.data
st.sidebar.markdown('## GlowFit'); st.sidebar.caption('Prediabetes-aware | fat loss | glute growth')
pages=['Home','Meals','Weekly Plan','Grocery','Workouts','Progress','Blood Sugar','Settings / Backup']
page=st.sidebar.radio('Dashboard',pages,index=pages.index(st.session_state.page)); st.session_state.page=page

if page=='Home':
    st.markdown("<p class='title'>Today Dashboard</p><p class='sub'>Linked meals, workouts, progress, and blood sugar awareness.</p>",unsafe_allow_html=True)
    p=data['profile']; c1,c2,c3=st.columns(3); c1.metric('Weight',f"{p['current_weight']} lb"); c2.metric('BMI',bmi(p['current_weight'],p['height_in'])); c3.metric('Protein target',f"{p['protein_target']}g")
    tr=st.toggle('Training day today',value=p.get('training_day',True))
    if tr!=p.get('training_day'): p['training_day']=tr; save()
    target=p['calorie_training'] if p['training_day'] else p['calorie_rest']; carbs=p['carb_training'] if p['training_day'] else p['carb_rest']
    st.info(f'Target today: {target} calories, {p["protein_target"]}g protein, about {carbs}g carbs.')
    t=totals(today()); c1,c2,c3,c4=st.columns(4); c1.metric('Calories',int(t['cal'])); c2.metric('Protein',f"{int(t['protein'])}g"); c3.metric('Carbs',f"{int(t['carbs'])}g"); c4.metric('Fibre',f"{int(t['fibre'])}g")
    dl=data['daily_logs'].setdefault(today(),{'water_l':0.0,'steps':0,'notes':''})
    with st.form('daily'):
        water=st.number_input('Water litres',0.0,step=.25,value=float(dl['water_l'])); steps=st.number_input('Steps',0,step=500,value=int(dl['steps'])); notes=st.text_area('Notes',value=dl.get('notes','')); sub=st.form_submit_button('Save daily habits')
    if sub: dl.update({'water_l':water,'steps':steps,'notes':notes}); save(); st.success('Saved.')

elif page=='Meals':
    st.markdown("<p class='title'>Meal Dashboard</p><p class='sub'>Planned meals plus manual foods for the selected date.</p>",unsafe_allow_html=True)
    ds=st.date_input('Date',value=date.today()).isoformat(); dn=dname(ds); t=totals(ds); st.success(f"{dn}: {int(t['cal'])} calories | {int(t['protein'])}g protein | {int(t['carbs'])}g carbs | {int(t['fibre'])}g fibre")
    for mt in MEAL_TYPES:
        st.markdown(f'### {mt}'); mn=data['weekly_plan'].get(dn,{}).get(mt,'')
        if mn in MEALS:
            m=MEALS[mn]; card(f"<b>{mn}</b><br>{m['cal']} cal | {m['protein']}g protein | GI: {m['gi']}<br><span class='muted'>{m['when']}</span>")
        else: st.caption('No planned meal for this slot yet.')
        for x in [i for i in data['manual_foods'] if i.get('date')==ds and i.get('meal_type')==mt]: st.write(f"- {x['name']}: {x.get('cal',0)} cal, {x.get('protein',0)}g protein")
    st.subheader('Add manual food')
    with st.form('manual',clear_on_submit=True):
        n=st.text_input('Food name'); mt=st.selectbox('Meal type',MEAL_TYPES); c1,c2,c3,c4=st.columns(4); cal=c1.number_input('Calories',0,step=10); pro=c2.number_input('Protein g',0.0,step=1.0); ca=c3.number_input('Carbs g',0.0,step=1.0); fib=c4.number_input('Fibre g',0.0,step=1.0); add=st.checkbox('Add to grocery too'); sub=st.form_submit_button('Save manual food')
    if sub and n.strip():
        data['manual_foods'].append({'date':ds,'meal_type':mt,'name':n.strip(),'cal':cal,'protein':pro,'carbs':ca,'fibre':fib})
        if add: data['manual_grocery'].append({'name':n.strip(),'qty':1,'unit':'item'})
        save(); st.success('Saved.')
    st.subheader('Recipes and portion steps'); filt=st.selectbox('Filter recipes',['All']+MEAL_TYPES)
    for mn,m in MEALS.items():
        if filt!='All' and m['type']!=filt: continue
        with st.expander(mn):
            st.write(f"{m['cal']} cal | {m['protein']}g protein | {m['carbs']}g carbs | GI: {m['gi']}"); st.write(m['when']); st.markdown('**Whole meal prep quantities**')
            for ing,(qty,u) in m['ingredients'].items(): st.write(f'- {ing}: {qty} {u} for {m["prep_servings"]} serving(s)')
            st.markdown('**Measuring/dishing steps**')
            for s in m['steps']: st.write(f'- {s}')

elif page=='Weekly Plan':
    st.markdown("<p class='title'>Weekly Plan</p><p class='sub'>Choose meals for each day. This updates Meals and Grocery.</p>",unsafe_allow_html=True)
    names={mt:['']+[n for n,m in MEALS.items() if m['type']==mt] for mt in MEAL_TYPES}; sug=suggestions()
    if sug: st.info('Suggested from selected grocery: '+', '.join(sug[:5]))
    for d in DAYS:
        with st.expander(d,expanded=(d==datetime.today().strftime('%A'))):
            cols=st.columns(2)
            for i,mt in enumerate(MEAL_TYPES):
                opts=names[mt]; cur=data['weekly_plan'][d].get(mt,''); cur=cur if cur in opts else ''; choice=cols[i%2].selectbox(mt,opts,index=opts.index(cur),key=f'w_{d}_{mt}')
                if choice!=cur: data['weekly_plan'][d][mt]=choice; save(); st.toast('Saved')

elif page=='Grocery':
    st.markdown("<p class='title'>Smart Grocery</p><p class='sub'>Choose groceries, get meal ideas, add meals to your week, then view generated list.</p>",unsafe_allow_html=True)
    tab1,tab2,tab3=st.tabs(['Choose groceries','Suggested meals','Generated list'])
    with tab1:
        for cat,items in GROCERY.items():
            st.markdown(f'### {cat}'); cols=st.columns(2)
            for i,item in enumerate(items):
                cur=bool(data['grocery_selected'].get(item,False)); new=cols[i%2].checkbox(item,value=cur,key=f'g_{item}')
                if new!=cur: data['grocery_selected'][item]=new; save()
        st.subheader('Limited fruit timing')
        for k,v in LIMITED.items(): st.caption(f'{k}: {v}')
    with tab2:
        sug=suggestions()
        if not sug: st.info('Select grocery foods first to get meal suggestions.')
        for mn in sug:
            m=MEALS[mn]
            with st.expander(f"{mn} - {m['type']}"):
                st.write(m['when']); st.write(f"{m['cal']} cal | {m['protein']}g protein | {m['carbs']}g carbs | GI: {m['gi']}")
                c1,c2,c3=st.columns(3); d=c1.selectbox('Day',DAYS,key=f'd_{mn}'); slot=c2.selectbox('Meal slot',MEAL_TYPES,index=MEAL_TYPES.index(m['type']),key=f's_{mn}')
                if c3.button('Add to weekly plan',key=f'a_{mn}'): data['weekly_plan'][d][slot]=mn; save(); st.success(f'Added to {d} {slot}.')
    with tab3:
        gt=grocery_totals()
        if not gt: st.info('No generated groceries yet. Add meals to Weekly Plan.')
        for (name,u),qty in sorted(gt.items()):
            key=f'chk_{name}_{u}'; cur=bool(data['grocery_checked'].get(key,False)); new=st.checkbox(f'{name}: {round(qty,1)} {u}',value=cur,key=key)
            if new!=cur: data['grocery_checked'][key]=new; save()
        with st.form('custom_g',clear_on_submit=True):
            n=st.text_input('Custom item'); q=st.number_input('Qty',0.0,value=1.0); u=st.text_input('Unit',value='item'); sub=st.form_submit_button('Add custom grocery item')
        if sub and n.strip(): data['manual_grocery'].append({'name':n.strip(),'qty':q,'unit':u}); save(); st.success('Added.')

elif page=='Workouts':
    st.markdown("<p class='title'>Workout Dashboard</p><p class='sub'>Set-by-set tracking that saves.</p>",unsafe_allow_html=True); wk=wkstart(); logs=data['workout_logs'].setdefault(wk,{}); today_idx=date.today().weekday()
    def show(d,collapsed=False):
        title,exs=WORKOUT[d]; dl=logs.setdefault(d,{'completed':False,'rating':0,'notes':'','sets':{}})
        with st.expander(f'{d}: {title}',expanded=not collapsed):
            for ex,sets,reps,wt in exs:
                st.markdown(f'**{ex}**'); dl['sets'].setdefault(ex,[])
                while len(dl['sets'][ex])<sets: dl['sets'][ex].append({'done':False,'weight':wt,'reps':reps})
                for si in range(sets):
                    row=dl['sets'][ex][si]; c1,c2,c3=st.columns(3); done=c1.checkbox(f'Set {si+1}',value=row['done'],key=f'{wk}{d}{ex}{si}d'); weight=c2.number_input('Weight',0.0,step=2.5,value=float(row['weight']),key=f'{wk}{d}{ex}{si}w'); r=c3.number_input('Reps/min',0,step=1,value=int(row['reps']),key=f'{wk}{d}{ex}{si}r')
                    if done!=row['done'] or weight!=row['weight'] or r!=row['reps']: row.update({'done':done,'weight':weight,'reps':r}); save()
            rating=st.slider('Workout rating',0,10,int(dl.get('rating',0)),key=f'{wk}{d}rat'); comp=st.checkbox('Mark day complete',value=dl.get('completed',False),key=f'{wk}{d}comp'); notes=st.text_area('Notes',value=dl.get('notes',''),key=f'{wk}{d}notes')
            if rating!=dl.get('rating') or comp!=dl.get('completed') or notes!=dl.get('notes'): dl.update({'rating':rating,'completed':comp,'notes':notes}); save()
    st.subheader('Remaining this week')
    for i,d in enumerate(DAYS):
        if i>=today_idx and not logs.get(d,{}).get('completed',False): show(d,False)
    st.subheader('Previous or completed')
    for i,d in enumerate(DAYS):
        if i<today_idx or logs.get(d,{}).get('completed',False): show(d,True)

elif page=='Progress':
    st.markdown("<p class='title'>Progress</p>",unsafe_allow_html=True); p=data['profile']
    with st.form('weight'):
        wt=st.number_input('Current weight lb',50.0,500.0,float(p['current_weight']),step=.5); sub=st.form_submit_button('Save weight')
    if sub: p['current_weight']=wt; data['weight_logs'].append({'date':today(),'weight':wt,'bmi':bmi(wt,p['height_in'])}); save(); st.success('Saved.')
    c1,c2=st.columns(2); c1.metric('BMI',bmi(p['current_weight'],p['height_in'])); c2.metric('To under 200 lb',f"{max(0,p['current_weight']-p['goal_weight']):.1f} lb")
    if data['weight_logs']:
        df=pd.DataFrame(data['weight_logs']); df['date']=pd.to_datetime(df['date']); st.line_chart(df.set_index('date')[['weight','bmi']])
    rows=[]
    for ds,dl in data['daily_logs'].items():
        t=totals(ds); rows.append({'date':ds,'calories':t['cal'],'protein':t['protein'],'carbs':t['carbs'],'water_l':dl.get('water_l',0),'steps':dl.get('steps',0)})
    if rows: df=pd.DataFrame(rows); df['date']=pd.to_datetime(df['date']); st.line_chart(df.set_index('date'))

elif page=='Blood Sugar':
    st.markdown("<p class='title'>Blood Sugar Awareness</p>",unsafe_allow_html=True); st.warning('Awareness only. Use clinician glucose targets and seek medical advice for concerning symptoms.')
    with st.form('sym'):
        ds=st.date_input('Date',value=date.today()).isoformat(); sy=st.multiselect('Symptoms',list(SYMPTOMS.keys())); notes=st.text_area('Notes'); sub=st.form_submit_button('Save symptoms')
    if sub: data['symptom_logs'].append({'date':ds,'symptoms':sy,'notes':notes}); save(); st.success('Saved.')
    if sy:
        for s in sy: st.write(f'- {s}: {SYMPTOMS[s]}')
    for log in reversed(data['symptom_logs'][-10:]): card(f"<b>{log['date']}</b><br>{', '.join(log.get('symptoms',[]))}<br><span class='muted'>{log.get('notes','')}</span>")

elif page=='Settings / Backup':
    st.markdown("<p class='title'>Settings / Backup</p>",unsafe_allow_html=True); p=data['profile']
    with st.form('settings'):
        c1,c2,c3=st.columns(3); h=c1.number_input('Height inches',48,84,int(p['height_in'])); sw=c2.number_input('Start weight',50.0,500.0,float(p['start_weight'])); cw=c3.number_input('Current weight',50.0,500.0,float(p['current_weight']))
        c1,c2,c3=st.columns(3); pro=c1.number_input('Protein target',40,250,int(p['protein_target'])); ct=c2.number_input('Training calories',1000,3500,int(p['calorie_training'])); cr=c3.number_input('Rest calories',1000,3500,int(p['calorie_rest']))
        c1,c2=st.columns(2); cbt=c1.number_input('Training carbs',40,300,int(p['carb_training'])); cbr=c2.number_input('Rest carbs',40,300,int(p['carb_rest'])); sub=st.form_submit_button('Save settings')
    if sub: p.update({'height_in':h,'start_weight':sw,'current_weight':cw,'protein_target':pro,'calorie_training':ct,'calorie_rest':cr,'carb_training':cbt,'carb_rest':cbr}); save(); st.success('Settings saved.')
    st.download_button('Download backup JSON',json.dumps(data,indent=2),'glowfit_backup.json','application/json')
    up=st.file_uploader('Restore backup',type='json')
    if up:
        try: st.session_state.data=json.load(up); save(); st.success('Backup restored.')
        except Exception as e: st.error(str(e))
    if st.button('Reset all data'): st.session_state.data=default_data(); save(); st.warning('Reset complete.')
