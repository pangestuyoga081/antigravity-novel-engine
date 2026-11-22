import json

transcript_path = r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\.system_generated\logs\transcript.jsonl"
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        idx = data.get("step_index", 0)
        if 1150 <= idx <= 1165:
            tc = data.get("tool_calls", [])
            if tc:
                for c in tc:
                    print(f"[{idx}] {c.get('name')}: {json.dumps(c.get('args', {}))[:120]}")
            elif data.get("content"):
                print(f"[{idx}] CONTENT: {data.get('content')[:120]}")
