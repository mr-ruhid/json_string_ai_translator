import json
import sys
import time
import requests

from _api import API_KEYS


# ============ PROVIDER: LIBRE ============
def translate_batch_libre(texts, target_lang):
    url = "http://localhost:5000/translate"
    payload = {
        "q": texts,
        "source": "auto",
        "target": target_lang,
        "format": "text",
    }
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    return [item["translatedText"] for item in response.json()["translatedText"]]


# ============ PROVIDER: GEMINI ============
def translate_batch_gemini(texts, target_lang):
    import google.generativeai as genai

    api_key = API_KEYS.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 'api.json' faylında tapılmadı")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = (
        f"Aşağıdakı JSON siyahısındakı mətnləri {target_lang} dilinə tərcümə et. "
        f"Yalnız tərcümə olunmuş mətnləri eyni sıra ilə JSON massivi kimi qaytar. "
        f"Heç bir izah yazma.\n\n{json.dumps(texts, ensure_ascii=False)}"
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)


# ============ PROVIDER: GROQ ============
def translate_batch_groq(texts, target_lang):
    from groq import Groq

    api_key = API_KEYS.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY 'api.json' faylında tapılmadı")

    client = Groq(api_key=api_key)
    prompt = (
        f"Aşağıdakı JSON siyahısındakı mətnləri {target_lang} dilinə tərcümə et. "
        f"Yalnız tərcümə olunmuş mətnləri eyni sıra ilə JSON massivi kimi qaytar. "
        f"Heç bir izah yazma.\n\n{json.dumps(texts, ensure_ascii=False)}"
    )
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return json.loads(completion.choices[0].message.content)


PROVIDERS = {
    "libre":  translate_batch_libre,
    "gemini": translate_batch_gemini,
    "groq":   translate_batch_groq,
}


# ============ JSON KÖMƏKÇI FUNKSIYALAR ============
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


# ============ MAIN ============
def main():
    if len(sys.argv) < 3:
        print("İstifadə: python jsonai.py <input.json> <target_lang> [provider]")
        print("Provider seçimləri: libre (default), gemini, groq")
        sys.exit(1)

    input_file = sys.argv[1]
    target_lang = sys.argv[2]
    provider_name = sys.argv[3] if len(sys.argv) > 3 else "libre"

    if provider_name not in PROVIDERS:
        print(f"❌ Naməlum provider: {provider_name}")
        print(f"Mövcud provider-lər: {', '.join(PROVIDERS.keys())}")
        sys.exit(1)

    translate_fn = PROVIDERS[provider_name]

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_strings = []
    collect_strings(data, all_strings)
    print(f"Toplam {len(all_strings)} mətn tapıldı. Provider: {provider_name}")

    translated_strings = []
    batch_size = 100
    for i in range(0, len(all_strings), batch_size):
        batch = all_strings[i:i + batch_size]
        batch_no = i // batch_size + 1
        print(f"Batch {batch_no} göndərilir ({len(batch)} mətn)...")
        try:
            result = translate_fn(batch, target_lang)
            translated_strings.extend(result)
        except Exception as e:
            print(f"Batch xətası: {e}. 10 saniyə gözlənilir və təkrar cəhd...")
            time.sleep(10)
            result = translate_fn(batch, target_lang)
            translated_strings.extend(result)
        time.sleep(1)

    if len(translated_strings) != len(all_strings):
        print(f"⚠️ Xəbərdarlıq: tərcümə sayı uyğun deyil ({len(translated_strings)} vs {len(all_strings)})")

    translated_iter = iter(translated_strings)
    translated_data = replace_strings(data, translated_iter)

    output_file = input_file.replace(".json", f"_{target_lang}_{provider_name}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Tərcümə tamamlandı: {output_file}")


if __name__ == "__main__":
    main()