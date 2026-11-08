#!/usr/bin/env bash
# Rebuild site/index.html and site/data/recipes.json from source/.
set -euo pipefail
cd "$(dirname "$0")/source"
( cd library && python3 parse.py >/dev/null )        # recipes_*.txt -> library/notion.json
python3 build.py >/dev/null                            # slow cooker + originals + pantry -> data.json
( cd library && python3 merge.py >/dev/null )          # merge your library into data.json
python3 render.py                                      # data.json + template.html -> site/
echo "Built site/index.html and site/data/recipes.json"
