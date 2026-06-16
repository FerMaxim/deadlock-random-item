import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import os
import io
from contextlib import redirect_stdout

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main.simulator.generate_build import DeadlockBuildGenerator

class BuildAPIHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return super().do_GET()
            
        if self.path.startswith('/api/generate'):
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                hero_id = int(query_params.get('hero_id', [15])[0])
                archetype_param = query_params.get('archetype', ['random'])[0]
                temperature = float(query_params.get('temperature', [1.0])[0])
                
                # Определяем доступные архетипы для героя
                report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main', 'training', 'temp', 'all_archetypes_report.txt'))
                num_archetypes = 1
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if f"(ID: {hero_id})" in line or f"(ID: {hero_id} |" in line:
                                import re
                                parts = line.split(":")
                                if len(parts) >= 3:
                                    try:
                                        num_archetypes = int(parts[-1].replace('=', '').strip())
                                    except:
                                        pass
                                break
                
                # Рандомим архетип, если нужно
                import random
                if archetype_param == 'random':
                    archetype = random.randint(0, max(0, num_archetypes - 1))
                else:
                    archetype = int(archetype_param)

                # Глушим print чтобы не мусорить в консоли
                f = io.StringIO()
                with redirect_stdout(f):
                    generator = DeadlockBuildGenerator(hero_id=hero_id, archetype=archetype)
                    generator.generate_full_build(max_items=24, strict_rules=False, temperature=temperature)

                # Собираем данные инвентаря
                items = []
                for item_id in generator.inventory:
                    info = generator.shop_dict.get(str(item_id), {})
                    items.append({
                        "id": item_id,
                        "name": info.get("name", "Unknown"),
                        "cost": info.get("cost", 0),
                        "slot": info.get("slot", "Weapon")
                    })
                    
                # Собираем данные скиллов (порядок прокачки)
                abilities = []
                temp_levels = {ab_id: 0 for ab_id in generator.hero_abilities}
                for ab_id in generator.ability_history:
                    str_id = str(ab_id)
                    temp_levels[str_id] += 1
                    ab_info = generator.hero_abilities.get(str_id, {})
                    abilities.append({
                        "id": ab_id,
                        "name": ab_info.get("name", "Unknown"),
                        "level_reached": temp_levels[str_id]
                    })
                
                response = {
                    "status": "success",
                    "hero_id": hero_id,
                    "archetype": archetype,
                    "temperature": temperature,
                    "items": items,
                    "abilities": abilities
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return
            
        return super().do_GET()

if __name__ == '__main__':
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, BuildAPIHandler)
    # Смена директории на test_website чтобы сервились файлы
    os.chdir(os.path.dirname(__file__))
    print(f"Сервер запущен на http://localhost:{port}")
    httpd.serve_forever()
