import json

transcript_path = r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("type") == "USER_INPUT":
            txt = data.get("content", "")
            if "Horus" in txt or "penjelasan" in txt or "agent" in txt:
                print(f"Step {data.get('step_index')}: {txt[:150]}")
