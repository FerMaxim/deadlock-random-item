import requests
import json
import re

def resolve_type(schema):
    if not schema:
        return ""
    
    t = schema.get("type", "")
    if isinstance(t, list):
        t = " | ".join(t)
    
    # Ссылки на объекты
    if not t and "$ref" in schema:
        t = schema["$ref"].split("/")[-1]
    
    if t == "array" and "items" in schema:
        item_t = resolve_type(schema["items"])
        t = f"array[{item_t}]"
        
    if "oneOf" in schema:
        types = [resolve_type(s) for s in schema["oneOf"]]
        t = " | ".join(filter(bool, types))
    
    if "anyOf" in schema:
        types = [resolve_type(s) for s in schema["anyOf"]]
        t = " | ".join(filter(bool, types))
        
    if "enum" in schema:
        enums = [str(e) for e in schema["enum"]]
        if t:
            t += f" (enum: {', '.join(enums)})"
        else:
            t = f"enum: {', '.join(enums)}"
            
    return t

def clean_text(text):
    if not text:
        return ""
    # Оставляем текст как есть, чтобы не потерять важную информацию, 
    # только убираем лишние символы новой строки по краям.
    return text.strip()

def fetch_and_parse_for_llm():
    url = "https://api.deadlock-api.com/openapi.json"
    print(f"Fetching OpenAPI spec from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    spec = response.json()

    output_file = "deadlock_api_llm.json"
    print(f"Generating comprehensive JSON for LLM in {output_file}...")

    llm_docs = {}

    paths = spec.get("paths", {})
    for path, methods in paths.items():
        llm_docs[path] = {}
        for method, details in methods.items():
            desc = clean_text(details.get("description", details.get("summary", "")))
            
            # Извлекаем параметры
            params = {}
            for param in details.get("parameters", []):
                name = param.get("name")
                if not name: continue
                
                schema = param.get("schema", {})
                param_type = resolve_type(schema)
                param_desc = clean_text(param.get("description", ""))
                
                params[name] = {
                    "type": param_type,
                    "req": param.get("required", False)
                }
                if param_desc:
                    params[name]["desc"] = param_desc
                    
                # Добавляем default, если есть
                if "default" in schema:
                    params[name]["default"] = schema["default"]

            # Извлекаем ответы
            responses = {}
            for status_code, resp_data in details.get("responses", {}).items():
                resp_desc = clean_text(resp_data.get("description", ""))
                content = resp_data.get("content", {})
                resp_type = ""
                for content_type, content_details in content.items():
                    r_schema = content_details.get("schema", {})
                    resp_type = resolve_type(r_schema)
                    if resp_type:
                        break # Берем первый найденный тип
                
                responses[status_code] = {"desc": resp_desc}
                if resp_type:
                    responses[status_code]["type"] = resp_type

            # Формируем компактную структуру
            llm_docs[path][method.upper()] = {
                "desc": desc
            }
            if params:
                llm_docs[path][method.upper()]["params"] = params
            if responses:
                llm_docs[path][method.upper()]["responses"] = responses

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(llm_docs, f, ensure_ascii=False, indent=2)

    print(f"LLM-optimized API docs saved to {output_file}")

if __name__ == "__main__":
    fetch_and_parse_for_llm()
