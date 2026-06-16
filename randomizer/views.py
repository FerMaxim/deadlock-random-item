from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

# Добавляем путь к ml_logic для импорта генератора
ml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'deadlock_project', 'ml_logic')
if ml_path not in sys.path:
    sys.path.append(ml_path)

def index(request):
    return render(request, 'randomizer/index.html', {'room_code': ''})

def room(request, room_code):
    return render(request, 'randomizer/index.html', {'room_code': room_code.upper()})

@csrf_exempt
def api_generate_build(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hero_id_str = data.get('hero_id', '')
            temperature = float(data.get('temperature', 2.0))
            
            try:
                from generate_build import DeadlockBuildGenerator
                import random
                import glob
                
                # If no hero selected, pick a random one that has a model
                ml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'deadlock_project', 'ml_logic')
                if not hero_id_str:
                    models_path = os.path.join(ml_path, 'models', 'xgb_items_hero_*.json')
                    available_models = glob.glob(models_path)
                    if available_models:
                        # Extract hero IDs from filenames (e.g. xgb_items_hero_15.json)
                        available_ids = [int(os.path.basename(m).split('_')[-1].split('.')[0]) for m in available_models]
                        hero_id = random.choice(available_ids)
                    else:
                        hero_id = 15 # Fallback
                else:
                    hero_id = int(hero_id_str)
                    
                # Pick a random archetype (usually 0, 1, or 2)
                archetype = random.randint(0, 2)
                archetype_name = f"Archetype {archetype}"

                generator = DeadlockBuildGenerator(hero_id=hero_id, archetype=archetype)
                generator.generate_full_build(max_items=24, strict_rules=False, temperature=temperature)
                
                return JsonResponse({
                    'success': True,
                    'hero_id': hero_id,
                    'archetype': archetype_name,
                    'inventory': generator.item_history,
                    'ability_history': generator.ability_history,
                    'hero_abilities': generator.hero_abilities
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': f"ML Model error: {str(e)}"})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
