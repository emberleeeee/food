import re, json
from rules import RULES, SPICES, SUBS
CR=[(k,lab,g,[re.compile(p,re.I) for p in ps]) for k,lab,g,ps in RULES]
SP=[re.compile(p,re.I) for p in SPICES]
OVR={"Sausage and broccoli rabe ravioli":"ravioli","Cilantro lime dressing":"dressing_cilantro","Caesar dressing":"dressing_caesar","Almond extract":"extract","Mint extract":"extract","Apple cider":"apple_cider","Hot honey":"honey","Coconut whipping cream":"coconut_cream","Light corn syrup":"corn_syrup","Popcorn kernels":"popcorn","Adobo seasoning":"spice","Tajin":"spice","Tiger sauce":"hot_sauce","Frank's RedHot":"hot_sauce"}
SECTION=re.compile(r"^\s*[A-Za-z][A-Za-z '&/-]{0,24}:\s+")  # "Topping: ", "Peach jam: " labels name a sub-recipe, not an ingredient
def keys_for_line(line):
    line=SECTION.sub("",line,count=1)
    found=[]; rest=line
    for k,lab,g,ps in CR:
        for p in ps:
            if p.search(rest):
                found.append(k); rest=p.sub(" ",rest); break
    spice=any(p.search(line) for p in SP)
    return found, spice
def pantry_key(name):
    if name in OVR: return OVR[name]
    for k,lab,g,ps in CR:
        if any(p.search(name) for p in ps): return k
    return None
if __name__=="__main__":
    D=json.load(open("sc.json"))
    unk=[]
    for r in D:
        for l in r["ingredients"]:
            f,s=keys_for_line(l)
            if not f and not s: unk.append(l)
    print("UNMATCHED:",*unk,sep="\n  ")
    for n in open("pantry.txt").read().strip().split("\n"):
        print(n,"->",pantry_key(n))
