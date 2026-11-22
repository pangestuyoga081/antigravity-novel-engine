with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\vk_found.html", encoding="utf-8") as f:
    html = f.read()

import re
# Look for page_post, post_content, or data-post-id
posts = re.findall(r'id="post-196255529_6050".*?class="like_wrap', html, re.DOTALL)
if posts:
    print("Found post block, len:", len(posts[0]))
    with open(r"C:\Users\Eevyx\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c\scratch\post_block.html", "w", encoding="utf-8") as f:
        f.write(posts[0])
else:
    print("Post block not found by regex")
