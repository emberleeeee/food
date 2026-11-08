import json, re, sys
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from match import keys_for_line
D=json.load(open(os.path.join(os.path.dirname(HERE),'data.json')))
N=json.load(open('notion.json'))
def mins(t):
    t=t.lower(); m=0
    h=re.search(r'(\d+(?:\.\d+)?)\s*hr',t); mm=re.search(r'(\d+)\s*min',t)
    if h: m+=float(h.group(1))*60
    if mm and (not h or t.index('min')<t.index('hr')+8): m+=int(mm.group(1))
    return int(m) if m else 0
def meals(types):
    s=set(types); out=[]
    if 'Breakfast' in s: out.append('Breakfast')
    if 'Lunch' in s: out.append('Lunch')
    if s & {'Dinner','Meal','Slow cooker','Freezer'}: out += [x for x in ('Dinner','Lunch') if x not in out]
    if not out:
        if 'Snack' in s: out.append('Snack')
        if 'Side' in s: out.append('Side')
        if 'Dessert' in s: out.append('Dessert')
        if 'Cocktail' in s: out.append('Drink')
    if not out: out=['Side']
    return out
def lean(p,c):
    if p is None or c is None: return 'Any'
    if c>=40: return 'Bike'
    if p>=30 and c<=20: return 'Strength'
    return 'Any'
SITE=json.load(open('sitemap.json'))
rec=[]
SKIP=re.compile(r'^\W*([\d/½¼¾⅓⅔.\s–-]*(cups?|tbsp|tsp|tablespoons?|teaspoons?|g|ml|oz)?\s*)?(ice |cold |hot |warm |boiling )?water\b|^ice$|^salt|^kosher salt|^sea salt|^salt and|^black pepper|^freshly ground|^pinch|^cooking spray|^neutral oil|^low calorie',re.I)
UNITS=r'(cups?|c|tbsp|tbs|tablespoons?|tsp|teaspoons?|g|kg|ml|l|oz|ounces?|lbs?|pounds?|cans?|jars?|packets?|packages?|bunch(es)?|heads?|cloves?|sprigs?|slices?|handfuls?|large|medium|small|whole|big|heaping|scoops?|sheets?|sticks?|pieces?|pints?|quarts?|dash(es)?|drops?)'
GEN={}
def generic(l):
    l=re.sub(r"^\s*[A-Za-z][A-Za-z '&/-]{0,24}:\s+","",l,count=1)
    t=re.sub(r'\(.*?\)','',l.lower())
    t=re.split(r',| for | to | plus |;|:',t)[0]
    t=re.sub(r'[\d/½¼¾⅓⅔⅛.\-–×x]+',' ',t)
    t=re.sub(r'\b'+UNITS+r'\b',' ',t)
    t=re.sub(r'\b(fresh|frozen|dried|chopped|minced|diced|sliced|grated|thinly|finely|coarsely|cut|into|peeled|of|a|an|the|about|optional|ripe|good|cooked|uncooked|raw|unsweetened|plain|organic|extra|virgin|lightly|beaten|softened|melted|cold|room|temperature|halved|quartered|trimmed|drained|rinsed|seeded|crushed|loosely|packed|very)\b',' ',t)
    t=re.sub(r'\s+',' ',t).strip()
    if len(t)<3: return None
    return ('x_'+re.sub(r'[^a-z0-9]+','_',t).strip('_'), t[:1].upper()+t[1:])
for i,o in enumerate(N):
    req=[]
    for l in o['ing']:
        ks,spice=keys_for_line(l)
        opt=bool(re.search(r'optional|to serve|to garnish|for garnish|to top',l,re.I))
        if not ks:
            if spice or SKIP.search(re.sub(r'\(.*?\)','',re.sub(r"^\s*[A-Za-z][A-Za-z '&/-]{0,24}:\s+",'',l,count=1))): req.append({'l':l,'k':[],'spice':bool(spice)}); continue
            g=generic(l)
            if not g: req.append({'l':l,'k':[],'spice':False}); continue
            GEN[g[0]]=g[1]
            req.append({'l':l,'k':[[g[0]]],'opt':opt,'free':True}); continue
        if 'vanilla' in ks and len(ks)>1 and 'protein_powder' in ks: ks=[k for k in ks if k!='vanilla']
        alt=bool(re.search(r'\bor\b',l)) and len(set(ks))>1
        req.append({'l':l,'k':[sorted(set(ks))] if alt else [[k] for k in dict.fromkeys(ks)],'opt':opt,'spice':spice})
    method='Slow cooker' if 'Slow cooker' in o['types'] else ('Freezer-friendly' if 'Freezer' in o['types'] else '')
    rec.append(dict(id='n%d'%i,src='Your library',name=o['name'],cuisine='',category=', '.join(o['types']),meal=meals(o['types']),
        method_type=method,servings=o['servings'],time=mins(o['time']),timeText=o['time'],cook='',freezer='',
        kcal=o['kcal'],p=o['p'],c=o['c'],f=o['f'],fi=None,lean=lean(o['p'],o['c']),req=req,steps=o['steps'],serve={},base='',
        note=o['note'],fave=o['fave'],url=o['source'],link=not o['ing'],
        site=('https://food.emilyblackwell.com/recipes/'+(SITE.get(o['name']) or ('freezer-recipes' if 'Freezer' in o['types'] else ''))+'.html') if (SITE.get(o['name']) or 'Freezer' in o['types']) else ''))
# drop placeholders that now have full versions
drop={'lib4','lib5','lib7','lib8'}
old=[r for r in D['recipes'] if r['id'] not in drop]
for r in old:
    if r['src']=='Slow cooker': r['meal']=r['meal']
D['recipes']=old+rec
for k,v in GEN.items(): D['labels'].setdefault(k,{'l':v,'g':'Other'})
json.dump(D,open(os.path.join(os.path.dirname(HERE),'data.json'),'w'),separators=(',',':'))
from collections import Counter
print(len(D['recipes']), Counter(r['src'] for r in D['recipes']))
print(Counter(m for r in rec for m in r['meal']))
print(sum(1 for r in rec if r['p'] is not None),'with macros')
# sanity: free lines (no key, not spice) sample
fr=[it['l'] for r in rec for it in r['req'] if it.get('free')]
print(len(fr)); print('\n'.join(fr[:60]))
