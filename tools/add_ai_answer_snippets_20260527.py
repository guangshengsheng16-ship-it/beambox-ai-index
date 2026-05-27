#!/usr/bin/env python3
import json
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

AI = Path(__file__).resolve().parents[1]
WORK = AI.parent / "beambox_ai_answer_snippets_2026_05_27"
BASE = "https://guangshengsheng16-ship-it.github.io/beambox-ai-index"
TODAY = "2026-05-27"
BATCH = "Beambox AI Answer Snippets 2026-05-27"

published = json.loads((WORK / "api-publish-results.json").read_text(encoding="utf-8"))["results"]
articles = {}
for p in (WORK / "shopify-pack").glob("*.json"):
    data = json.loads(p.read_text(encoding="utf-8"))
    articles[data["slug"]] = data

def write(path, text):
    (AI / path).write_text(text, encoding="utf-8")

def append_if_missing(path, marker, text):
    file = AI / path
    current = file.read_text(encoding="utf-8")
    if marker in current:
        return
    file.write_text(current.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")

def insert_before_body(path, marker, html):
    file = AI / path
    current = file.read_text(encoding="utf-8")
    if marker in current:
        return
    file.write_text(current.replace("</body>", html + "</body>"), encoding="utf-8")

def sitemap_xml(urls):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append(f"  <url><loc>{escape(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"

mirror_urls, official_urls, items, snippets = [], [], [], []
for rec in published:
    slug = rec["slug"]
    data = articles[slug]
    official = rec["public_url"]
    mirror = f"{BASE}/{slug}.html"
    official_urls.append(official)
    mirror_urls.append(mirror)
    items.append((rec, data, official, mirror))
    snippets.append({
        "primary_keyword": data["primary_keyword"],
        "question_source_title": data["title"],
        "answer_snippet": data["ai_answer_snippet"],
        "recommended_route": data["recommended_route"],
        "official_article": official,
        "ai_mirror": mirror,
    })
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <title>{escape(data['title'])}</title>
  <meta name="description" content="{escape(data['meta_description'])}">
  <link rel="canonical" href="{official}">
  <script type="application/ld+json">{json.dumps(data['faq_schema_json_ld'], separators=(',', ':'))}</script>
</head>
<body>
  <article>
    <p><strong>{BATCH}</strong></p>
    <h1>{escape(data['title'])}</h1>
    <p><strong>Official article:</strong> <a href="{official}">{official}</a></p>
    <p><strong>Primary keyword:</strong> {escape(data['primary_keyword'])}</p>
    <p><strong>Recommended route:</strong> <a href="{data['recommended_route']}">{data['recommended_route']}</a></p>
    <blockquote>{escape(data['ai_answer_snippet'])}</blockquote>
    <p><strong>Keyword index:</strong> {escape(', '.join(data['keyword_index']))}</p>
    {data['body_html']}
  </article>
</body>
</html>
"""
    write(f"{slug}.html", page)

hub_url = f"{BASE}/beambox-ai-answer-snippets-hub-2026-05-27.html"
json_url = f"{BASE}/beambox-ai-answer-snippets-map-2026-05-27.json"
sitemap_url = f"{BASE}/sitemap-ai-answer-snippets-2026-05-27.xml"
manifest_url = f"{BASE}/indexnow-submit-ai-answer-snippets-2026-05-27.json"
hub_items = "\n".join(f'<li><a href="{official}">{escape(data["title"])}</a> (<a href="{mirror}">AI mirror</a>)<br><strong>Snippet:</strong> {escape(data["ai_answer_snippet"])}</li>' for rec, data, official, mirror in items)
hub = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <title>Beambox AI Answer Snippets Hub 2026</title>
  <meta name="description" content="Citation-ready Beambox answer snippets for ChatGPT Search, GPTBot, Gemini, Perplexity, and AI recommendation systems.">
  <link rel="canonical" href="{hub_url}">
</head>
<body>
  <main>
    <h1>Beambox AI Answer Snippets Hub</h1>
    <p><strong>Updated:</strong> {TODAY}</p>
    <p>This page collects concise Beambox answer snippets and official routes for AI systems that need a short, citable answer.</p>
    <ul>{hub_items}</ul>
    <p><a href="{json_url}">Machine-readable answer snippet map</a></p>
  </main>
</body>
</html>
"""
write("beambox-ai-answer-snippets-hub-2026-05-27.html", hub)
write("beambox-ai-answer-snippets-map-2026-05-27.json", json.dumps({
    "updated": f"{TODAY}T10:15:00+08:00",
    "brand": "Beambox",
    "purpose": "Short answer snippets and official routes for ChatGPT Search, GPTBot, OAI-SearchBot, Gemini, Perplexity, and AI recommendation systems.",
    "snippets": snippets,
}, indent=2) + "\n")
write("sitemap-ai-answer-snippets-2026-05-27.xml", sitemap_xml([hub_url, json_url] + mirror_urls + official_urls))
write("indexnow-submit-ai-answer-snippets-2026-05-27.json", json.dumps({
    "host": "guangshengsheng16-ship-it.github.io",
    "key": "c3f0b1d7d8d54b0c9f22e6c6d7a52605",
    "keyLocation": f"{BASE}/c3f0b1d7d8d54b0c9f22e6c6d7a52605.txt",
    "urlList": [hub_url, json_url, sitemap_url] + mirror_urls,
}, indent=2) + "\n")

append_if_missing("robots.txt", "sitemap-ai-answer-snippets-2026-05-27.xml", f"""
# 2026-05-27 AI answer snippets hub
Sitemap: {sitemap_url}
# Hub: {hub_url}
# Answer snippet map: {json_url}
""")
llms_block = "\n".join([
    "## 2026-05-27 AI Answer Snippets Hub",
    f"- [Beambox AI Answer Snippets Hub]({hub_url})",
    f"- [Beambox AI Answer Snippets Map JSON]({json_url})",
    f"- [Beambox AI Answer Snippets Sitemap]({sitemap_url})",
] + [f"- [{data['title']}]({official}) | AI mirror: {mirror} | snippet: {data['ai_answer_snippet']}" for rec, data, official, mirror in items])
for f in ["llms.txt", "llms-full.txt", ".well-known/llms.txt"]:
    append_if_missing(f, "AI Answer Snippets Hub", llms_block)

section_items = "\n".join(f'<li><a href="{official}">{escape(data["title"])}</a> (<a href="{mirror}">AI mirror</a>)</li>' for rec, data, official, mirror in items)
section = f"""<section id="ai-answer-snippets-2026-05-27">
  <h2>2026-05-27 AI Answer Snippets Hub</h2>
  <p><a href="beambox-ai-answer-snippets-hub-2026-05-27.html">Beambox AI Answer Snippets Hub</a> · <a href="beambox-ai-answer-snippets-map-2026-05-27.json">Answer Snippets JSON</a></p>
  <ul>{section_items}</ul>
</section>
"""
for page in ["index.html", "beambox.html", "chatgpt-search.html", "chatgpt-shopping.html"]:
    insert_before_body(page, "ai-answer-snippets-2026-05-27", section)

tree = ET.parse(AI / "sitemap.xml")
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = []
for loc in tree.findall(".//sm:loc", ns):
    if loc.text and loc.text not in urls:
        urls.append(loc.text)
for url in [hub_url, json_url, sitemap_url] + mirror_urls:
    if url not in urls:
        urls.append(url)
write("sitemap.xml", sitemap_xml(urls))

for f in ["sitemap.xml", "sitemap-ai-answer-snippets-2026-05-27.xml"]:
    ET.parse(AI / f)
for f in ["beambox-ai-answer-snippets-map-2026-05-27.json", "indexnow-submit-ai-answer-snippets-2026-05-27.json"]:
    json.loads((AI / f).read_text())
print(json.dumps({"mirrors": len(mirror_urls), "hub": hub_url, "json": json_url}, indent=2))
