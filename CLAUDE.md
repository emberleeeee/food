# Pantry Planner: notes for Claude Code

Personal recipe and meal planner for Emberlee, hosted at food.emilyblackwell.com/planner/ (IONOS shared hosting, PHP available, no Node on the server). A matching copy runs as a claude.ai artifact.

## Build and check
- Edit files in `source/` only. Run `./build.sh` to regenerate `site/index.html`, `site/data/recipes.json` and `dist/pantry-planner.html` (the claude.ai artifact build). Commit the rebuilt `site/` with the source change.
- `template.html` contains placeholders `__DATA__`, `__HOSTED__` (true for the self-hosted site) and `__SHARE__` (claude.ai generator link). Never hand-edit the built files.
- After changes, open the built page in a headless browser (Playwright is the easy way) and confirm there are no page errors, the Cook tab renders, and `#recipe-<slug>` opens a recipe.
- When changing `rules.py` or `spicefam.py`, compare old and new `site/data/recipes.json` and list every recipe line whose matched keys changed. Unintended changes are bugs.
- Pushing to `main` deploys to the live site. For anything risky, work on a branch.

## Product rules
- No workout or training references anywhere (no bike/strength/rest days, rides, training days). Carb labels are "Higher carb" / "Lower carb"; serving notes are "Hearty / Lighter / Balanced". The data still uses lean values `Bike`/`Strength` internally; keep those keys, never show them.
- Guidance tone is dietician-like: protein-forward, practical. Don't invent macros; leave them blank if unknown.
- Writing style for any UI copy or notes: plain narrative prose, minimal em dashes.
- Design tokens (match food.emilyblackwell.com): cream #F5F0E8, ink #1C1A17, accent #C8553D, green #3D6B4F, gold #C4973A, blue #3F5E78, plum #7A4A63, border #E2DDD4; Playfair Display + DM Sans; pill buttons; 16px card radius.
- New pantry items that the user doesn't confirm owning start with status "out" (`"st":"out"`).
- Recipe steps copied from other sites should be rewritten in our own words.

## How matching works
- `rules.py` RULES: ordered `(key, label, group, [regex])`; each match removes its text before later rules run. SUBS maps a key to swaps. Protein keys weigh 3×, swaps count 0.75, spices 0.5, optional lines are skipped.
- `spicefam.py` FAM: ordered spice patterns → pantry spice names (any one in stock satisfies the line).
- Unmatched ingredient lines become generic `x_<slug>` keys so they still reach the shopping list.
- Library recipe IDs (`n0`…) come from block order in `library/recipes_*.txt`; append new recipes at the end so IDs stay stable. Recipe links use name slugs, with old ID links still working.

## Storage
- claude.ai artifact: per-user state in the artifact's `db` (`data/users/<id>/planner`), localStorage fallback.
- Self-hosted: localStorage only (key `pantry-planner`). Recipes the user writes or imports live there, not in this repo.
- `site/import.php` fetches public recipe pages for "Import from link" (SSRF-guarded, same-site referer only).
