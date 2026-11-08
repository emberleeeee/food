# Pantry Planner

The recipe planner at **food.emilyblackwell.com**: what you can cook from your pantry, a week plan, a shopping list, your own recipes and recipe import.

## How it fits together

```
source/            ← edit these
  template.html      the page: layout, styles, all the JavaScript
  pantry.txt         starting pantry (one item per line)
  spices.txt         the spice list (starts as "out")
  recommended.txt    suggested staples (start as "out")
  rules.py           how ingredient lines are matched to pantry items
  spicefam.py        how spice lines are matched to individual spices
  sc.json            slow cooker recipes
  originals.py       the 10 pantry-ready recipes
  library/recipes_*.txt   your recipe library, one block per recipe
build.sh           ← turns source/ into site/
site/              ← what goes on the server (built; don't hand-edit index.html or recipes.json)
  index.html, data/recipes.json, import.php
  .htaccess          tells search engines not to index the planner
  robots.txt         asks search engines not to crawl the site
.github/workflows/deploy.yml   builds and uploads site/ on every push to main
```

Every push to `main` rebuilds the site and uploads `site/` to your IONOS webspace. Uploads add and replace files; they never delete anything on the server.

## One-time setup: deploy secrets

1. **Create an SFTP account in IONOS.** In your IONOS account go to *Hosting → SFTP & SSH* and create an account (SFTP is enough). Note the server name, username and password it shows.
2. **Find the planner's folder path.** In *Domains & SSL*, check which webspace folder food.emilyblackwell.com points to. It is `sites/food.emilyblackwell.com`, and the planner is served from that folder's root.
3. **Add four secrets to this repo.** On GitHub open *Settings → Secrets and variables → Actions → New repository secret* and add:
   - `SFTP_HOST`: the server name, e.g. `access-5012345678.webspace-host.com`
   - `SFTP_USER`: the SFTP username
   - `SFTP_PASSWORD`: the SFTP password
   - `SFTP_PATH`: the folder path from step 2: `sites/food.emilyblackwell.com`
4. **Run it.** Go to *Actions → Build and deploy to IONOS → Run workflow*. When it turns green, open food.emilyblackwell.com.

## Making changes with Claude Code

Open this repo in Claude Code (on your Mac or at claude.ai/code) and describe the change. `CLAUDE.md` tells it how the project works. Changes go live when they're pushed to `main`; to check something first, ask for it on a branch and merge when you're happy.

To build and preview locally: `./build.sh`, then open `site/index.html` in a browser.

## Adding a recipe to the library

Add a block to `source/library/recipes_i.txt`:

```
@@ Recipe name | Dinner, Meal | fave | https://source-link | 4 | 30 min | 450,35,40,15
#ING
1 lb ground turkey
...
#STEP
First step.
...
#NOTE
Optional note.
```

Fields: name | types (Breakfast, Lunch, Dinner, Meal, Side, Snack, Dessert, Cocktail, Slow cooker, Freezer) | `fave` or blank | source link | servings | time | kcal,protein,carbs,fat per serving (optional).

Recipes you write or import inside the planner are saved in your browser, not here.
