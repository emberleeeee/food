import json, re
from rules import RULES, SUBS
from match import keys_for_line, pantry_key, CR
from originals import N, O
LAB={k:(lab,g) for k,lab,g,ps in RULES}
def lean(p,c):
    if c>=40: return "Bike"
    if p>=30 and c<=20: return "Strength"
    return "Any"
out=[]
# slow cooker
for r in json.load(open("sc.json")):
    req=[]
    for l in r["ingredients"]:
        ks,spice=keys_for_line(l)
        opt=bool(re.search(r"to finish|to serve|optional",l,re.I))
        if not ks: 
            if spice: req.append({"l":l,"k":[],"spice":True})
            continue
        if 'vanilla' in ks and len(ks)>1 and 'protein_powder' in ks: ks=[k for k in ks if k!='vanilla']
        alt=bool(re.search(r"\bor\b",l)) and len(set(ks))>1
        if alt: req.append({"l":l,"k":[sorted(set(ks))],"opt":opt,"spice":spice})
        else: req.append({"l":l,"k":[[k] for k in dict.fromkeys(ks)],"opt":opt,"spice":spice})
    serve={}
    for part in re.split(r"(?<=\.)\s+(?=(?:Hearty|Lighter|Balanced):)",r["serve"]):
        m=re.match(r"(Hearty|Lighter|Balanced):\s*(.*)",part)
        if m: serve[{"Hearty":"bike","Lighter":"strength","Balanced":"rest"}[m.group(1)]]=m.group(2)
    meal=["Breakfast"] if r["category"]=="Breakfast" else ["Dinner","Lunch"]
    out.append(dict(id="sc%d"%r["id"],src="Slow cooker",name=r["name"],cuisine=r["cuisine"],category=r["category"],meal=meal,
        method_type="Slow cooker",servings=r["servings"],time=r["prep"],cook="LOW %s h · HIGH %s h"%(r["low"],r["high"]),
        freezer=r["freezer"],kcal=r["kcal"],p=r["protein"],c=r["carbs"],f=r["fat"],fi=r["fiber"],lean=lean(r["protein"],r["carbs"]),
        req=req,steps=r["method"]+(["Finish: "+r["finish"]] if r["finish"] else []),serve=serve,base="",note=r["tip"],sear=r["sear"]))
def serve_of(b):
    out={}
    for t,lab in (("bike","Hearty|Heartier"),("strength","Lighter"),("rest","Balanced")):
        m=re.search("(?:"+lab+r"): ([^.]*\.)",b)
        if m: out[t]=m.group(1)[0].upper()+m.group(1)[1:]
    for t in ("bike","strength","rest"):
        if out and t not in out: out[t]="As written."
    return out
def general_of(b):
    return " ".join(x for x in re.split(r"(?<=\.)\s+",b) if not re.match(r"(Hearty|Lighter|Balanced|Heartier):",x))
# originals
for o in O:
    tot=[0]*5
    for line,k,nk,g in o["ing"]:
        for i,v in enumerate(N[nk]): tot[i]+=v*g/100
    s=o["servings"]; kc,p,c,f,fi=[round(x/s) for x in tot]
    req=[]
    for line,k,nk,g in o["ing"]:
        if line.startswith("("): continue
        if k=="spice": req.append({"l":line,"k":[],"spice":True}); continue
        ks=[[k]]
        if k=="onion" and "carrot" in line: ks=[["onion"],["carrots"]]
        req.append({"l":line,"k":ks})
    out.append(dict(id=o["id"],src="Pantry-ready",name=o["name"],cuisine=o["cuisine"],category="Pantry-ready",meal=o["meal"],
        method_type=o["method_type"],servings=s,time=o["time"],cook="",freezer=o["freezer"],kcal=kc,p=p,c=c,f=f,fi=fi,lean=lean(p,c),
        req=req,steps=o["steps"],serve=serve_of(o["base"]),base=general_of(o["base"]),note=""))
# library (key ingredients only)
LIB=[("Shakshuka",["eggs","crushed_tomatoes","onion","garlic","bell_pepper","feta"],["Breakfast","Dinner"]),
 ("Fried Rice",["jasmine_rice","eggs","edamame","carrots","onion","garlic","soy","sesame_oil"],["Dinner","Lunch"]),
 ("Tuna Niçoise",["tuna","eggs","potato","green_beans","olives","lemon","mustard","olive_oil","red_wine_vinegar"],["Lunch"]),
 ("Gochujang Turkey Bowl",["ground_turkey","gochujang","soy","garlic","ginger","farro","broccoli","sesame_oil","rice_vinegar"],["Dinner","Lunch"]),
 ("Stuffed Peppers (turkey, farro, black beans)",["bell_pepper","ground_turkey","farro","black_beans","crushed_tomatoes","onion","garlic","cheddar"],["Dinner"]),
 ("Lentil-Chickpea Stew",["green_lentils","chickpeas","crushed_tomatoes","onion","carrots","garlic","broth_chicken"],["Dinner","Lunch"]),
 ("Crispy Chickpea & Garlic Yogurt Bowl",["chickpeas","greek_yogurt","garlic","lemon","olive_oil","farro"],["Lunch"]),
 ("Sesame Salmon with Edamame & Farro",["salmon","edamame","farro","sesame_oil","soy","honey","garlic","rice_vinegar"],["Dinner"]),
 ("Maple-Glazed Chickpea Bowl with Garlic Tahini Yogurt",["chickpeas","maple","tahini","greek_yogurt","garlic","lemon","farro"],["Lunch","Dinner"])]
for i,(n,ks,meal) in enumerate(LIB):
    out.append(dict(id="lib%d"%i,src="Your library",name=n,cuisine="",category="Library",meal=meal,method_type="",servings=4,time=0,cook="",
        freezer="",kcal=None,p=None,c=None,f=None,fi=None,lean="Any",req=[{"l":LAB[k][0],"k":[[k]]} for k in ks],steps=[],serve={},
        base="",note=""))
# pantry
pantry=[]
for n in open("pantry.txt").read().strip().split("\n"):
    k=pantry_key(n) or re.sub(r"[^a-z0-9]+","_",n.lower()).strip("_")
    g=LAB.get(k,("", "Other"))[1]
    if k in ("spice",): g="Spices"
    if k.startswith("dressing") or k in ("hot_sauce","mustard","mayo","relish","a1_steak_sauce","oyster_sauce","fish_sauce","sriracha","sambal","gochujang","harissa","red_curry","worcestershire","soy","tahini","peanut_butter"): g="Sauces & condiments"
    if k in ("olive_oil","ghee","sesame_oil") or "vinegar" in k or k=="balsamic": g="Oils & vinegars"
    if k in ("flour","sugar","brown_sugar","cornstarch","vanilla","extract","baking_soda","baking_powder","molasses","active_dry_yeast","corn_syrup","honey"): g="Baking & sweeteners"
    if k in ("coffee_beans","tea","triscuits","grape_nuts","granola","nuts","popcorn","peanuts","dried_fruit"): g="Snacks, nuts & breakfast"
    if k in ("chicken","ground_beef","salmon","sausage","edamame","blueberries","hashbrowns","broccoli") and n.lower().startswith(("frozen","hash")): g="Freezer"
    if k in ("eggs","greek_yogurt","milk","feta","cheddar","sauerkraut","ravioli"): g="Fridge"
    if k in ("onion","garlic","carrots","cabbage","lemon","lime","apple","banana"): g="Produce"
    if k in ("tuna","sardines","black_beans","chickpeas","crushed_tomatoes","tomato_paste","pumpkin","pineapple","artichokes","capers","marinara","coconut_cream"): g="Cans & jars"
    if k in ("jasmine_rice","arborio","farro","oats","penne","orzo","red_lentils","green_lentils","tortillas","pita","bread","breadcrumbs"): g="Grains, pasta & bread"
    if k in ("broth_chicken","broth_beef","apple_cider","nooch"): g="Pantry"
    if k in ("hot_sauce",) : g="Sauces & condiments"
    if g in ("Other","Protein","Produce") and k not in ("onion","garlic","carrots","cabbage","lemon","lime","apple","banana"): pass
    pantry.append({"n":n,"k":k,"g":g})
# recommended staples: listed as "out" until bought
for l in open("recommended.txt").read().strip().split("\n"):
    g,n=l.split("|")
    if n.lower() in {p["n"].lower() for p in pantry}: continue
    pantry.append({"n":n,"k":pantry_key(n) or re.sub(r"[^a-z0-9]+","_",n.lower()).strip("_"),"g":g,"st":"out"})
# full spice rack: listed as "out" until marked as on hand
have_names={p["n"].lower() for p in pantry}
for n in open("spices.txt").read().strip().split("\n"):
    if n.lower() in have_names: continue
    pantry.append({"n":n,"k":"sesame_seeds" if "sesame" in n.lower() else "sp_"+re.sub(r"[^a-z0-9]+","_",n.lower()).strip("_"),"g":"Spices","st":"out"})
for p in pantry:
    if p["k"]=="spice": p["k"]="sp_"+re.sub(r"[^a-z0-9]+","_",p["n"].lower()).strip("_")
from spicefam import FAM
nk={p["n"]:p["k"] for p in pantry}
spfam=[[rx,[nk[n] for n in names]] for rx,names in FAM]
spl={p["k"]:{"l":p["n"],"g":"Spices"} for p in pantry if p["k"].startswith("sp_")}
labels={k:{"l":lab,"g":g} for k,lab,g,ps in RULES}
rules=[[k,ps] for k,lab,g,ps in RULES]
labels.update(spl)
json.dump({"recipes":out,"pantry":pantry,"labels":labels,"subs":SUBS,"rules":rules,"spfam":spfam},open("data.json","w"))
from collections import Counter
print(len(out), Counter(r["src"] for r in out), Counter(r["lean"] for r in out))
print(Counter(p["g"] for p in pantry))
for o in out:
    if o["src"]=="Pantry-ready": print(o["name"],o["kcal"],o["p"],o["c"],o["f"],o["fi"],o["lean"])
