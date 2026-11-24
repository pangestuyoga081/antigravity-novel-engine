import os
import yaml

def update_living_profile(profile_path, new_casts, new_glossaries):
    """
    Menyuntikkan hasil Scout per Bab ke dalam profile semesta YAML secara dinamis.
    Profile akan terus berevolusi seiring berjalannya bab cerita.
    """
    if not os.path.exists(profile_path):
        return
    with open(profile_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    key_chars = data.get('key_characters', [])
    existing_char_names = {c['name'].lower(): i for i, c in enumerate(key_chars)}

    for name, faction, desc in new_casts:
        low_name = name.lower()
        if low_name in existing_char_names:
            idx = existing_char_names[low_name]
            key_chars[idx]['role'] = desc
        else:
            key_chars.append({
                'name': name,
                'dialog_format': f'{name}: "..."',
                'role': desc
            })
            existing_char_names[low_name] = len(key_chars) - 1

    data['key_characters'] = key_chars

    locations = data.get('locations_and_factions', [])
    loanwords = data.get('loanwords', [])
    existing_loc_terms = {l.split('(')[0].strip().lower() for l in locations}
    existing_loan_terms = {w.split('(')[0].strip().lower() for w in loanwords}

    for term, desc in new_glossaries:
        low_term = term.lower()
        formatted_entry = f"{term} ({desc})"
        if any(w in low_term for w in ['stasiun', 'jalur', 'ordo', 'faksi', 'polis', 'vdnkh', 'hanza', 'reich', 'line']):
            if low_term not in existing_loc_terms:
                locations.append(formatted_entry)
                existing_loc_terms.add(low_term)
        else:
            if low_term not in existing_loan_terms:
                loanwords.append(formatted_entry)
                existing_loan_terms.add(low_term)

    data['locations_and_factions'] = locations
    data['loanwords'] = loanwords

    with open(profile_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✅ Living Profile '{os.path.basename(profile_path)}' berkembang: {len(key_chars)} Tokoh, {len(locations)} Lokasi, {len(loanwords)} Glosarium.")
