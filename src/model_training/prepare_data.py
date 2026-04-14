import pandas as pd
import json

def create_data_frame(file_path):
    data = []
    with open(file_path) as f:
        for line in f:
            data.append(json.loads(line))

    # --- Prepare ---
    card_ids = set()
    battle_types = set()
    tower_troops = set()
    rarity_mapping = {'common': 1, 'rare': 2, 'epic': 3, 'legendary': 4, 'champion': 5}

    for battle in data:
        if battle is None:
            continue
        battle_types.add(battle.get("battle_type", "unknown"))
        for deck in [battle.get("cards_a", []), battle.get("cards_b", [])]:
            for card in deck:
                card_ids.add(card)
        for t_troop in [battle.get("tower_troop_a", 999999999), battle.get("tower_troop_b", 999999999)]:
            tower_troops.add(t_troop)

    card_ids = sorted(card_ids)
    battle_types = sorted(battle_types)
    tower_troops = sorted(tower_troops)

    # --- Feature Extraction ---
    rows = []

    for battle in data:
        if battle is None:
            continue

        row = {}
        # Initialize all card-related features to 0
        for id in card_ids:
            row[f"level_{id}_a"] = 0
            row[f"evo_{id}_a"] = 0
            row[f"level_{id}_b"] = 0
            row[f"evo_{id}_b"] = 0
        
        for type in battle_types:
            row[f"mode_{type}"] = 0
        
        for t_troop in tower_troops:
            row[f"tower_{t_troop}_a"] = 0
            row[f"tower_{t_troop}_b"] = 0

        # Fill card data
        cards_a = battle.get("cards_a", [])
        cards_b = battle.get("cards_b", [])
        levels_a = battle.get("levels_a", [])
        levels_b = battle.get("levels_b", [])
        evos_a = battle.get("evos_a", [])
        evos_b = battle.get("evos_b", [])
        for i in range(len(cards_a)):
            row[f"level_{cards_a[i]}_a"] = levels_a[i]
            row[f"evo_{cards_a[i]}_a"] = evos_a[i]

        for i in range(len(cards_b)):
            row[f"level_{cards_b[i]}_b"] = levels_b[i]
            row[f"evo_{cards_b[i]}_b"] = evos_b[i]
        
        row[f"mode_{battle.get("battle_type", "unknown")}"] = 1

        row[f"tower_{battle.get("tower_troop_a", 999999999)}_a"] = 1
        row[f"tower_{battle.get("tower_troop_b", 999999999)}_b"] = 1

        row["avg_elixir_a"] = battle.get("avg_elixir_a", 8)
        row["avg_elixir_b"] = battle.get("avg_elixir_b", 8)
        row["cycle_cost_a"] = battle.get("cycle_cost_a", 25)
        row["cycle_cost_b"] = battle.get("cycle_cost_b", 25)

        row["label"] = battle.get("label", 0)

        rows.append(row)

    # --- Create DataFrame ---
    return pd.DataFrame(rows)
