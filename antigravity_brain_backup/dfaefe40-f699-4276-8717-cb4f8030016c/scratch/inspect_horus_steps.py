import json

transcript_path = r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        idx = data.get("step_index", 0)
        if 1140 <= idx <= 1160 and data.get("type") in ["USER_INPUT", "PLANNER_RESPONSE"]:
            print(f"[{idx}] {data.get('type')}: {data.get('content', '')[:200]}")
