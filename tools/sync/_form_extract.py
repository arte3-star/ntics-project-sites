"""Extrai perguntas de um Google Form."""
import sys, json
from playwright.sync_api import sync_playwright

URL = sys.argv[1]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4000)
    page.screenshot(path="g:/O meu disco/projects-os/tools/sync/_form_debug.png", full_page=True)
    html = page.content()
    with open("g:/O meu disco/projects-os/tools/sync/_form_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("URL final:", page.url)
    print("Title:", page.title())
    print("HTML length:", len(html))
    browser.close()
