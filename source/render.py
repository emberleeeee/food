"""Render template.html + data.json into ../site (self-hosted) and ../dist/pantry-planner.html (claude.ai artifact)."""
import json, os
from rules import SPICES
SHARE = "https://claude.ai/artifact/J7hHeDtG6GJiGBdBBTCjrm#create"
d = json.load(open("data.json")); d["spices"] = SPICES
data = json.dumps(d, separators=(",", ":"), ensure_ascii=False)
t = open("template.html").read()
os.makedirs("../site/data", exist_ok=True); os.makedirs("../dist", exist_ok=True)
for out, hosted in (("../dist/pantry-planner.html", "false"), ("../site/index.html", "true")):
    open(out, "w").write(t.replace("__DATA__", data).replace("__HOSTED__", hosted).replace("__SHARE__", SHARE))
json.dump(d, open("../site/data/recipes.json", "w"), indent=1, ensure_ascii=False)
os.remove("data.json")
