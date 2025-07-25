import pandas as pd
import random
import json
import os
from itertools import product
from datetime import datetime

# === Configuration ===
CSV_PATH = "AI Menu Recommender Items.csv"
STATE_FILE = "combo_day_tracker.txt"

# === Helper Functions ===

def get_current_day():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            f.write("1")
        return 1
    with open(STATE_FILE, "r") as f:
        return int(f.read().strip())

def increment_day():
    day = get_current_day() + 1
    with open(STATE_FILE, "w") as f:
        f.write(str(day))
    return day

def generate_remark(taste_profile_list):
    taste_counts = {tp: taste_profile_list.count(tp) for tp in ['spicy', 'savory', 'sweet']}
    dominant = max(taste_counts, key=taste_counts.get)
    return f"This combo emphasizes a {dominant} flavor profile with balanced calories and popularity."

def is_similar(c1, c2, c3, tol_cal=20, tol_pop=0.2):
    cal_vals = [c['total_calories'] for c in [c1, c2, c3]]
    pop_vals = [c['total_popularity'] for c in [c1, c2, c3]]
    return (max(cal_vals) - min(cal_vals) <= tol_cal) and (max(pop_vals) - min(pop_vals) <= tol_pop)

# === Main Combo Generator ===

def generate_combo_for_day(day_number):
    df = pd.read_csv(CSV_PATH)

    # Randomly select 4 mains, 3 sides, 3 drinks
    random_main = df[df['category'] == 'main'].sample(n=4, random_state=day_number).reset_index(drop=True)
    random_side = df[df['category'] == 'side'].sample(n=3, random_state=day_number).reset_index(drop=True)
    random_drink = df[df['category'] == 'drink'].sample(n=3, random_state=day_number).reset_index(drop=True)

    # Generate all valid combinations (1 main, 1 side, 1 drink)
    all_combos = []
    for main_item, side_item, drink_item in product(random_main.itertuples(index=False),
                                                    random_side.itertuples(index=False),
                                                    random_drink.itertuples(index=False)):
        combo = {
            'main': main_item.item_name,
            'side': side_item.item_name,
            'drink': drink_item.item_name,
            'total_calories': main_item.calories + side_item.calories + drink_item.calories,
            'total_popularity': round(main_item.popularity_score + side_item.popularity_score + drink_item.popularity_score, 2),
            'taste_profile': [main_item.taste_profile, side_item.taste_profile, drink_item.taste_profile]
        }
        all_combos.append(combo)

    # Find 3 non-overlapping combos with similar calories and popularity
    valid_triplets = []
    for i in range(len(all_combos)):
        for j in range(i+1, len(all_combos)):
            for k in range(j+1, len(all_combos)):
                c1, c2, c3 = all_combos[i], all_combos[j], all_combos[k]
                items = [c1['main'], c1['side'], c1['drink'],
                         c2['main'], c2['side'], c2['drink'],
                         c3['main'], c3['side'], c3['drink']]
                if len(set(items)) == 9 and is_similar(c1, c2, c3):
                    valid_triplets.append([c1, c2, c3])
                    break
            if valid_triplets:
                break
        if valid_triplets:
            break

    selected_combos = valid_triplets[0] if valid_triplets else []

    # Prepare JSON
    weekday = (["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][(day_number - 1) % 7])
    output = {
        "day_number": day_number,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weekday": weekday,
        "meal_combos": []
    }

    if not selected_combos:
        output["remarks"] = "No valid meal combinations found for today. Try again tomorrow."
        return output

    for idx, combo in enumerate(selected_combos, 1):
        output["meal_combos"].append({
            "combo_id": f"combo_{idx}",
            "main_course": combo['main'],
            "side_dish": combo['side'],
            "drink": combo['drink'],
            "total_calories": combo['total_calories'],
            "total_popularity_score": combo['total_popularity'],
            "remarks": generate_remark(combo['taste_profile'])
        })

    return output
