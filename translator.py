import json
import sys
from deep_translator import GoogleTranslator


def translate_json(obj, translator):
    if isinstance(obj, dict):
        return {k: translate_json(v, translator) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [translate_json(item, translator) for item in obj]
    elif isinstance(obj, str):
        if not obj.strip():
            return obj
        return translator.translate(obj)
    else:
        return obj


def main():
    if len(sys.argv) < 3:
        print("İstifadə: python translator.py <input.json> <target_lang>")
        sys.exit(1)

    input_file = sys.argv[1]
    target_lang = sys.argv[2]

    translator = GoogleTranslator(source="auto", target=target_lang)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"'{input_file}' oxundu, tərcümə başlayır...")

    translated_data = translate_json(data, translator)

    output_file = input_file.replace(".json", f"_{target_lang}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Tərcümə tamamlandı: {output_file}")


if __name__ == "__main__":
    main()