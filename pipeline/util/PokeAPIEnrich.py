import time
import pandas as pd
import requests

API_BASE = "https://pokeapi.co/api/v2"
SESSION = requests.Session()

# Faz uma requisição GET para a URL e retorna o conteúdo JSON.
def fetch_json(url):
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

# Busca dados de uma espécie de Pokémon pelo ID na PokeAPI.
def get_species(species_id):
    return fetch_json(f"{API_BASE}/pokemon-species/{species_id}/")

# Busca dados de um Pokémon. Pode receber o nome do Pokémon ou uma URL completa.
def get_pokemon(name_or_url):
    if name_or_url.startswith("http"):
        url = name_or_url
    else:
        url = f"{API_BASE}/pokemon/{name_or_url}/"
    return fetch_json(url)

# Converte a taxa de crescimento do Pokémon para a experiência necessária para atingir nível 100.
def xp_to_level_100(growth_rate_name):
    mapping = {
        "slow": 1250000,
        "medium": 1000000,
        "fast": 800000,
        "medium-slow": 1059860,
        "slow-then-very-fast": 600000,
        "fast-then-very-slow": 1640000,
    }
    return mapping.get(growth_rate_name, 1000000)

# Converte o nome da geração da PokeAPI em um número inteiro.
def generation_number(gen_name):
    mapping = {
        "generation-i": 1,
        "generation-ii": 2,
        "generation-iii": 3,
        "generation-iv": 4,
        "generation-v": 5,
        "generation-vi": 6,
        "generation-vii": 7,
        "generation-viii": 8,
        "generation-ix": 9,
    }
    return mapping.get(gen_name)

# Extrai os stats base de um Pokémon do JSON retornado pela API. Retorna um dicionário com hp, attack, defense, sp_attack, sp_defense, speed e base_total.
def extract_stats(poke_json):
    wanted = {
        "hp": "hp",
        "attack": "attack",
        "defense": "defense",
        "special-attack": "sp_attack",
        "special-defense": "sp_defense",
        "speed": "speed",
    }
    stats = {v: 0 for v in wanted.values()}
    for s in poke_json["stats"]:
        name = s["stat"]["name"]
        if name in wanted:
            stats[wanted[name]] = int(s["base_stat"])
    stats["base_total"] = sum(stats.values())
    return stats

# Extrai os tipos de um Pokémon do JSON retornado pela API. Retorna um dicionário com type1 e type2 (ou None se não houver segundo tipo).
def extract_types(poke_json):
    slots = sorted(poke_json["types"], key=lambda t: t["slot"])
    t1 = slots[0]["type"]["name"] if len(slots) > 0 else None
    t2 = slots[1]["type"]["name"] if len(slots) > 1 else None
    return {"type1": t1, "type2": t2}

# Verifica se dois dicionários de stats e tipos são iguais. Útil para identificar variações cosméticas de um Pokémon.
def same_stats_and_types(a, b):
    stat_keys = ["hp","attack","defense","sp_attack","sp_defense","speed"]
    type_keys = ["type1","type2"]
    return all(a.get(k) == b.get(k) for k in stat_keys + type_keys)

# Gera o nome da forma do Pokémon, se houver. Se for a forma padrão, retorna None.
def form_name(species_slug, variant_slug, default=False):
    if default:
        return None
    if variant_slug.startswith(species_slug):
        suffix = variant_slug[len(species_slug):].lstrip("-")
    else:
        suffix = variant_slug
    if not suffix:
        return None
    return suffix.capitalize()

"""
Recebe um DataFrame com Pokémon e enriquece os dados usando a PokeAPI.
Inclui stats, tipos, geração, captura, experiência e formas alternativas.
sleep_between: tempo de espera entre chamadas à API para não sobrecarregar o servidor.
"""
def enrich_with_pokeapi(df, sleep_between=0.0):
    df = df.copy()
    all_new_rows = []

    # Itera por cada Pokémon único no DataFrame
    for species_id in df["pokedex_number"].unique():
        try:
            species = get_species(int(species_id))
        except Exception as e:
            print(f"Erro ao buscar species {species_id}: {e}")
            continue

        # Informações gerais
        capture_rate = species.get("capture_rate")
        growth_rate = species.get("growth_rate", {}).get("name", "medium")
        exp_growth = xp_to_level_100(growth_rate)
        generation = generation_number(species.get("generation", {}).get("name", ""))
        is_legendary = 1 if species.get("is_legendary", False) else 0

        # Base row do Pokémon
        base_idx = df.index[df["pokedex_number"] == species_id][0]
        base_row = df.loc[base_idx].to_dict()
        base_name = base_row["name"]
        species_slug = species["name"]

        varieties = species.get("varieties", [])
        default_var = next((v for v in varieties if v["is_default"]), None)
        if not default_var:
            continue

        # Corrige stats e tipos da forma padrão
        default_poke = get_pokemon(default_var["pokemon"]["name"])
        stats = extract_stats(default_poke)
        types = extract_types(default_poke)
        for k,v in {**stats, **types}.items():
            base_row[k] = v
        base_row["capture_rate"] = capture_rate
        base_row["experience_growth"] = exp_growth
        base_row["generation"] = generation
        base_row["is_legendary"] = is_legendary
        base_row["form"] = None
        df.loc[base_idx] = base_row
        base_compare = {**stats, **types}

        # Processa variações não-padrão
        for var in varieties:
            poke_name = var["pokemon"]["name"]
            if var["is_default"]:
                continue
            poke_data = get_pokemon(poke_name)
            var_stats = extract_stats(poke_data)
            var_types = extract_types(poke_data)

            # Ignora variações cosméticas
            if same_stats_and_types(var_stats, base_compare):
                continue

            # Popula a new_row com as novas informações
            new_row = base_row.copy()
            new_row.update(var_stats)
            new_row.update(var_types)
            new_row["capture_rate"] = capture_rate
            new_row["experience_growth"] = exp_growth
            new_row["generation"] = generation
            new_row["is_legendary"] = is_legendary

            # Decide nome e forma
            if poke_data["species"]["name"] != species_slug:
                new_row["name"] = poke_data["name"].capitalize()
                new_row["form"] = None
            else:
                new_row["name"] = base_name
                new_row["form"] = form_name(species_slug, poke_data["name"])

            all_new_rows.append(new_row)

            if sleep_between > 0:
                time.sleep(sleep_between)

    # Combina DataFrame original com novas linhas
    return pd.concat([df, pd.DataFrame(all_new_rows)], ignore_index=True)