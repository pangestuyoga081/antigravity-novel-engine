import os
import urllib.request
import re

out_dir = r"D:\JV\novel yoga\The Expanse"
os.makedirs(out_dir, exist_ok=True)

books = [
    {
        "title": "The Expanse 1 - Leviathan Wakes.epub",
        "url": "https://vk.com/doc588886715_561272788?hash=kNgfC9GbBA8cMzcvPoEIuPDaFeRjb9BYcpFX4jRjOtc&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 2 - Caliban's War.epub",
        "url": "https://vk.com/doc588886715_561272775?hash=juv9RUigJSAs7gvhdSqtIfBd9rluSl77Vxxmn3ySQtg&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 3 - Abaddon's Gate.epub",
        "url": "https://vk.com/doc588886715_561272760?hash=U16ZL3lXj5pfkmoifLiWahTFjiMBbh3RYRnXucrgKpH&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 4 - Cibola Burn.epub",
        "url": "https://vk.com/doc588886715_561272780?hash=e0gmfs1aajcT0cTiYy9fIA07GjIPGBzKQ06oBcwDWrD&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 5 - Nemesis Games.epub",
        "url": "https://vk.com/doc588886715_561272792?hash=9lQvlIEZKjbUQrpYCAVMvIdNTA9Qkn4tvNERJE8z13P&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 6 - Babylon's Ashes.epub",
        "url": "https://vk.com/doc588886715_561272769?hash=mRranJUm6fx0wdtVFKJwZpCVI6zkYgaQazsRgGa1wIT&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 7 - Persepolis Rising.epub",
        "url": "https://vk.com/doc588886715_561272797?hash=o10Esoybn71wYMVJW3AVp5HJkMCX9eQkhCLkamQDO1c&api=1&no_preview=1"
    },
    {
        "title": "The Expanse 8 - Tiamat's Wrath.epub",
        "url": "https://vk.com/doc588886715_561272869?hash=eqzPzmVISZbc8cgSOywPveDrKyl28pZ8QCondqF3ccH&api=1&no_preview=1"
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

for b in books:
    dest = os.path.join(out_dir, b["title"])
    print(f"Downloading: {b['title']}...")
    try:
        req = urllib.request.Request(b["url"], headers=headers)
        with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        size = os.path.getsize(dest)
        print(f"  -> SUCCESS ({size / 1024:.1f} KB)")
    except Exception as e:
        print(f"  -> FAILED: {e}")
