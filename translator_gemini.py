import json
import sys
import time
import google.generativeai as genai

# API açarınızı buraya yazın (https://aistudio.google.com/apikey)
genai.configure(api_key="SİZİN_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-1.5-flash")


def translate_batch(texts, target_lang):
    prompt = (
        f"Aşağıdakı JSON siyahısındakı mətnləri {target_lang} dilinə tərcümə et. "
        f"Yalnız tərcümə olunmuş mətnləri eyni sıra ilə JSON massivi kimi qaytar. "
        f"Heç bir izah yazma.\n\n{json.dumps(texts, ensure_ascii=False)}"
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)


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
        print("İstifadə: python translator_gemini.py <input.json> <target_lang>")
        sys.exit(1)

    input_file = sys.argv[1]
    target_lang = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_strings = []
    collect_strings(data, all_strings)
    print(f"Toplam {len(all_strings)} mətn tapıldı.")

    translated_strings = []
    batch_size = 100  # 100-100 parça
    for i in range(0, len(all_strings), batch_size):
        batch = all_strings[i:i + batch_size]
        print(f"Batch {i // batch_size + 1} göndərilir ({len(batch)} mətn)...")
        try:
            result = translate_batch(batch, target_lang)
            translated_strings.extend(result)
        except Exception as e:
            print(f"Batch xətası: {e}. 10 saniyə gözlənilir...")
            time.sleep(10)
            result = translate_batch(batch, target_lang)
            translated_strings.extend(result)
        time.sleep(2)  # Rate limit üçün

    translated_iter = iter(translated_strings)
    translated_data = replace_strings(data, translated_iter)

    output_file = input_file.replace(".json", f"_{target_lang}_gemini.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Tərcümə tamamlandı: {output_file}")


if __name__ == "__main__":
    main()