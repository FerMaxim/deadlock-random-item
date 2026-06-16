from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
import io
from contextlib import redirect_stdout

# Add ML logic to path
ml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ml_path not in sys.path:
    sys.path.append(ml_path)

from functools import lru_cache
from main.simulator.generate_build import DeadlockBuildGenerator
import random

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
                if not hero_id_str:
                    hero_id = random.choice([15, 1, 3, 18, 4]) # Random defaults if none selected
                else:
                    hero_id = int(hero_id_str)
                    
                archetype = random.randint(0, 2)
                
                f = io.StringIO()
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
