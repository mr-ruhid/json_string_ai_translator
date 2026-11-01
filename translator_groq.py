import json
import sys
import time
from groq import Groq

client = Groq(api_key="SİZİN_GROQ_API_KEY")  # https://console.groq.com/keys


def translate_batch(texts, target_lang):
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


# collect_strings və replace_strings funksiyaları Variant 1 ilə eynidir

def main():
    if len(sys.argv) < 3:
        print("İstifadə: python translator_groq.py <input.json> <target_lang>")
        sys.exit(1)

    input_file = sys.argv[1]
    target_lang = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_strings = []
    collect_strings(data, all_strings)
    print(f"Toplam {len(all_strings)} mətn tapıldı.")

    translated_strings = []
    batch_size = 100
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
        time.sleep(1)

    translated_iter = iter(translated_strings)
    translated_data = replace_strings(data, translated_iter)

    output_file = input_file.replace(".json", f"_{target_lang}_groq.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Tərcümə tamamlandı: {output_file}")


if __name__ == "__main__":
    main()