import json
import time
from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")
START_PLAYER = "#88JL2QYG"
PLAYER_LIMITx2 = 100
DATA_FILE = 'data/extracted_battles.json'
ALLOWED_TYPES = {"PvP", "pathOfLegend"}#, "casual1v1"}

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

players = [START_PLAYER]
seen_players = set()

def is_valid_battle(battle):
    return (
        battle.get("type") in ALLOWED_TYPES
        and "team" in battle and "opponent" in battle
        and len(battle["team"]) > 0 and len(battle["opponent"]) > 0
    )

def parse_deck(cards, support_card=None):
    rarity_bonus = {
        "common": 0,
        "rare": 2,
        "epic": 5,
        "legendary": 8,
        "champion": 10
    }

    parsed_cards = []
    parsed_levels = []
    parsed_evos = []
    elixir_costs = []

    for card in cards:
        base_level = card.get("level", 0)
        rarity = card.get("rarity", "common")
        effective_level = base_level + rarity_bonus.get(rarity, 0)
        elixir = card.get("elixirCost", 0)

        parsed_cards.append(card.get("id"))
        parsed_levels.append(effective_level)
        parsed_evos.append(card.get("evolutionLevel", 0))

        if elixir > 0:
            elixir_costs.append(elixir)

    avg_elixir = round(sum(elixir_costs) / len(elixir_costs), 2) if elixir_costs else None
    cycle_cost = round(sum(sorted(elixir_costs)[:4]), 2) if len(elixir_costs) >= 4 else None

    return parsed_cards, parsed_levels, parsed_evos, avg_elixir, cycle_cost

def extract_battle_data(battle):
    try:
        team = battle['team'][0]
        opponent = battle['opponent'][0]

        tag_a = team.get('tag')
        tag_b = opponent.get('tag')

        if not tag_a or not tag_b or tag_b in seen_players:
            return None
        
        if len(seen_players) < PLAYER_LIMITx2 and tag_b not in players:
            players.append(tag_b)

        crowns_a = team.get('crowns', 0)
        crowns_b = opponent.get('crowns', 0)

        if crowns_a == crowns_b:
            return None
        
        cards_a, levels_a, evos_a, avg_a, cycle_a = parse_deck(team['cards'])
        cards_b, levels_b, evos_b, avg_b, cycle_b = parse_deck(opponent['cards'])

        tower_troop_a = team.get('supportCards', [None])[1]
        tower_troop_b = opponent.get('supportCards', [None])[1]

        return {
            'cards_a': cards_a,
            'cards_b': cards_b,
            'levels_a': levels_a,
            'levels_b': levels_b,
            'evos_a': evos_a,
            'evos_b': evos_b,

            'tower_troop_a': tower_troop_a,
            'tower_troop_b': tower_troop_b,

            'avg_elixir_a': avg_a,
            'avg_elixir_b': avg_b,
            'cycle_cost_a': cycle_a,
            'cycle_cost_b': cycle_b,

            'battle_type': battle.get("type"),

            'label': 1 if crowns_a > crowns_b else 0
        }

    except Exception as e:
        print("Error parsing match:", e)
        return None

def scrape_battle_log(player_tag):
    tag_encoded = player_tag.replace('#', '%23')
    url = f"https://api.clashroyale.com/v1/players/{tag_encoded}/battlelog"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        seen_players.add(player_tag)
        data = response.json()

        for battle in data:
            if not is_valid_battle(battle):
                continue
            extracted_battle = extract_battle_data(battle)
            if not extracted_battle:
                continue
            
            with open(DATA_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(extracted_battle) + "\n")

        print("Data saved successfully")

    else:
        print("Error:", response.status_code, response.text)

def scrape():
    while players:
        player = players.pop(0)
        scrape_battle_log(player)
        time.sleep(0.2)

if __name__ == "__main__":
    scrape()