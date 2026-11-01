import json
import sys
from deep_translator import GoogleTranslator


def collect_strings(obj, strings):
    if isinstance(obj, dict):
        for v in obj.values():
            collect_strings(v, strings)
    elif isinstance(obj, list):
        for item in obj:
            collect_strings(item, strings)
    elif isinstance(obj, str) and obj.strip():
        strings.append(obj)


def replace_strings(obj, translated_iter):
    if isinstance(obj, dict):
        return {k: replace_strings(v, translated_iter) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_strings(item, translated_iter) for item in obj]
    elif isinstance(obj, str) and obj.strip():
        return next(translated_iter)
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

    print(f"'{input_file}' oxundu, mətnlər toplanır...")

    all_strings = []
    collect_strings(data, all_strings)
    print(f"Toplam {len(all_strings)} mətn tapıldı, toplu tərcümə başlayır...")

    translated_strings = []
    batch_size = 50
    for i in range(0, len(all_strings), batch_size):
        batch = all_strings[i:i + batch_size]
        translated_batch = translator.translate_batch(batch)
        translated_strings.extend(translated_batch)

    translated_iter = iter(translated_strings)
    translated_data = replace_strings(data, translated_iter)

    output_file = input_file.replace(".json", f"_{target_lang}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Tərcümə tamamlandı: {output_file}")


if __name__ == "__main__":
    main()