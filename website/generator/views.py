from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
import io
import threading
from contextlib import redirect_stdout

# Add ML logic to path
ml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ml_path not in sys.path:
    sys.path.append(ml_path)

from functools import lru_cache
from main.simulator.generate_build import DeadlockBuildGenerator
import random

generation_lock = threading.Lock()

def index(request):
    return render(request, 'generator/room.html', {'room_code': ''})

def room(request, room_code):
    return render(request, 'generator/room.html', {'room_code': room_code.upper()})

# Cache up to 3 heroes to avoid RAM overload on 1GB VPS
@lru_cache(maxsize=3)
def get_cached_generator(hero_id):
    return DeadlockBuildGenerator(hero_id=hero_id, archetype=0)

@csrf_exempt
def api_generate_build(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hero_id_str = data.get('hero_id', '')
            temperature = float(data.get('temperature', 2.0))
            
            try:
                if not hero_id_str or hero_id_str == 'random':
                    active_heroes = [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 27, 31, 35, 50, 52, 58, 60, 63, 64, 65, 66, 67, 69, 72, 76, 77, 79, 80, 81]
                    hero_id = random.choice(active_heroes)
                else:
                    hero_id = int(hero_id_str)
                    
                try:
                    with open(os.path.join(ml_path, 'django_ml_module', 'dictionary', 'archetypes_count.json'), 'r') as f:
                        archetypes_count = json.load(f)
                    max_arch = archetypes_count.get(str(hero_id), 2)
                    archetype = random.randint(0, max_arch - 1)
                except Exception:
                    archetype = random.randint(0, 1)
                
                f = io.StringIO()
                with generation_lock:
                    with redirect_stdout(f):
                        generator = get_cached_generator(hero_id)
                        # Reset state for fresh generation
                        generator.archetype = archetype
                        generator.inventory = []
                        generator.ability_points_spent = 0
                        generator.item_history = []
                        generator.ability_history = []
                        generator.ability_levels = {sk_id: 0 for sk_id in generator.hero_abilities.keys()}
                        
                        generator.generate_full_build(max_items=24, strict_rules=False, temperature=temperature)
                    
                    # Format Items
                    items = []
                    for item_id in generator.inventory:
                        info = generator.shop_dict.get(str(item_id), {})
                        items.append({
                            "id": int(item_id),
                            "name": info.get("name", "Unknown"),
                            "cost": int(info.get("cost", 0)),
                            "slot": str(info.get("slot_type", "weapon")).capitalize()
                        })
                        
                    # Map S1/S2/S3/Ult
                    signatures = []
                    ult = None
                    for ab_id, ab_info in generator.hero_abilities.items():
                        if ab_info.get("type") == "ultimate":
                            ult = str(ab_id)
                        else:
                            signatures.append((str(ab_id), ab_info.get("name", "")))
                    # Sort signatures deterministically by ID (or name)
                    signatures.sort(key=lambda x: x[1])
                    ab_short_map = {ult: "Ult"}
                    for i, (sig_id, _) in enumerate(signatures):
                        ab_short_map[sig_id] = f"S{i+1}"

                    # Format Abilities
                    abilities = []
                    temp_levels = {ab_id: 0 for ab_id in generator.hero_abilities}
                    for ab_id in generator.ability_history:
                        str_id = str(ab_id)
                        temp_levels[str_id] += 1
                        ab_info = generator.hero_abilities.get(str_id, {})
                        abilities.append({
                            "id": int(ab_id),
                            "name": ab_info.get("name", "Unknown"),
                            "short_name": str(ab_short_map.get(str_id, "S1")),
                            "level_reached": int(temp_levels[str_id])
                        })

                return JsonResponse({
                    'success': True,
                    'hero_id': int(hero_id),
                    'archetype': f"Archetype {archetype}",
                    'items': items,
                    'abilities': abilities,
                    'cost': int(sum(i['cost'] for i in items))
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': f"ML Model error: {str(e)}"})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def items_list(request):
    try:
        with open(os.path.join(ml_path, 'django_ml_module', 'dictionary', 'shop_items_dict.json'), 'r', encoding='utf-8') as f:
            shop_dict = json.load(f)
    except Exception:
        shop_dict = {}

    categories = {
        'Weapon': {},
        'Vitality': {},
        'Spirit': {}
    }
    
    BLACKLISTED_ITEMS = {
        "conjure missiles", "endless magazine", "glass cannon v2", 
        "enduring spirit", "patron's healing", "bullet armor", 
        "toughness", "spirit armor", "hexafoil ward", 
        "majestic leap - disabled", "soul rebirth", "ammo scavenger", 
        "hex-sealed knuckles", "soul explosion", "rebirth"
    }
    
    for item_id, info in shop_dict.items():
        name = info.get('name', '')
        lower_name = name.lower()
        if lower_name.startswith('upgrade_') or lower_name.startswith('item_') or lower_name in BLACKLISTED_ITEMS:
            continue
            
        slot = str(info.get('slot_type', 'Weapon')).capitalize()
        cost = int(info.get('cost', 0))
        
        if slot not in categories:
            categories[slot] = {}
        if cost not in categories[slot]:
            categories[slot][cost] = []
            
        info['id'] = item_id
        categories[slot][cost].append(info)
        
    for cat in categories:
        # Sort items inside each cost group
        for cost in categories[cat]:
            categories[cat][cost] = sorted(categories[cat][cost], key=lambda x: x.get('name', ''))
        # Convert cost groups to a sorted list of tuples (cost, items) to ensure order 800, 1600, 3200...
        categories[cat] = sorted(categories[cat].items(), key=lambda x: x[0])
        
    return render(request, 'generator/items_list.html', {'categories': categories})
