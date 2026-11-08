import re, json, glob, sys
sys.path.insert(0,'/home/claude/mp')
from match import keys_for_line
from rules import RULES
out=[]
for f in sorted(glob.glob('recipes_*.txt')):
    for blk in open(f).read().split('@@ ')[1:]:
        lines=blk.strip().split('\n')
        head=[x.strip() for x in lines[0].split('|')]
        while len(head)<7: head.append('')
        name,types,fave,src,serv,time,nut=head[:7]
        sec=None; d={'ING':[],'STEP':[],'NOTE':[]}
        for l in lines[1:]:
            if l.startswith('#'): sec=l[1:].strip(); continue
            if l.strip() and sec: d[sec].append(l.strip())
        n=(nut.split(',')+['','','',''])[:4]
        num=lambda v: int(round(float(v))) if v.strip() else None
        out.append(dict(name=name,types=[t.strip() for t in types.split(',') if t.strip()],fave=fave=='fave',source=src,
            servings=int(serv) if serv.strip().isdigit() else None,time=time,kcal=num(n[0]),p=num(n[1]),c=num(n[2]),f=num(n[3]),
            ing=d['ING'],steps=d['STEP'],note=' '.join(d['NOTE'])))
print(len(out))
json.dump(out,open('notion.json','w'),indent=0)
names=[o['name'].lower() for o in out]
from collections import Counter
print(Counter(t for o in out for t in o['types']))
print(sum(1 for o in out if not o['ing']),'link-only')
