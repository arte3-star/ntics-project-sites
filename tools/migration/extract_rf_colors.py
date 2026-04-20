#!/usr/bin/env python3
"""
extract_rf_colors.py — Extrai cores CSS reais dos headings e buttons de cada site RF.

Navega para cada site RF, lê computed styles dos h1/h2/h3/buttons,
grava cores.json com as cores dominantes reais.
"""

import asyncio
import io
import json
import os
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]


def parse_rgba(s):
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', s or '')
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if (r, g, b) == (255, 255, 255) or (r, g, b) == (0, 0, 0):
            return None
        return f"#{r:02X}{g:02X}{b:02X}"
    return None


def darken_hex(hex_color, factor=0.5):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"#{int(r*factor):02X}{int(g*factor):02X}{int(b*factor):02X}"


def lighten_hex(hex_color, factor=0.85):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r2 = int(r + (255 - r) * factor)
    g2 = int(g + (255 - g) * factor)
    b2 = int(b + (255 - b) * factor)
    return f"#{r2:02X}{g2:02X}{b2:02X}"


async def extract_one(page, rf_url: str) -> dict:
    await page.goto(rf_url, wait_until='domcontentloaded', timeout=60000)
    await asyncio.sleep(5)
    # Scroll to load
    for _ in range(2):
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(1)

    data = await page.evaluate('''() => {
        const colors = [];
        // All headings
        document.querySelectorAll('h1, h2, h3').forEach(h => {
            const c = window.getComputedStyle(h).color;
            colors.push({type: 'heading', color: c, text: h.innerText.trim().slice(0, 40)});
        });
        // All buttons/links that look like buttons
        document.querySelectorAll('button, a[class*="btn"], [class*="button"]').forEach(b => {
            const cs = window.getComputedStyle(b);
            colors.push({type: 'button_bg', color: cs.backgroundColor});
            colors.push({type: 'button_fg', color: cs.color});
        });
        // Nav/header bg
        const nav = document.querySelector('nav, header, [class*="navbar"]');
        if (nav) {
            colors.push({type: 'nav_bg', color: window.getComputedStyle(nav).backgroundColor});
        }
        // Sections with bg-color
        document.querySelectorAll('section').forEach((s, i) => {
            const bg = window.getComputedStyle(s).backgroundColor;
            if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                colors.push({type: 'section_bg', color: bg, idx: i});
            }
        });
        return colors;
    }''')

    # Parse and find dominant non-white/black colors
    color_counts = {}
    for item in data:
        c = parse_rgba(item.get('color'))
        if c:
            color_counts[c] = color_counts.get(c, 0) + 1

    # Sort by frequency
    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
    return sorted_colors


async def main():
    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for s in sites:
            num = s['numero_ntics']
            print(f"\n=== {num} {s['nome_planilha'][:35]} ===")
            colors = await extract_one(page, s['rf_url'])
            print(f"  Top colors:")
            for c, count in colors[:6]:
                print(f"    {c} ({count}x)")

            # Build palette from top colors
            top = [c for c, _ in colors if c]
            if not top:
                print("  NO COLORS FOUND — using logo palette")
                continue

            primary = top[0]
            secondary = top[1] if len(top) > 1 else darken_hex(primary, 0.7)
            accent = top[2] if len(top) > 2 else lighten_hex(primary, 0.4)
            dark = darken_hex(primary, 0.5)
            light = lighten_hex(primary, 0.85)

            palette = {
                "primary": primary,
                "secondary": secondary,
                "accent": accent,
                "dark": dark,
                "light": light,
                "source": "renderforest_css",
            }

            # Save
            folder = None
            for d in os.listdir(ROOT / 'assets' / 'projetos'):
                if d.startswith(f'{num}. '):
                    folder = d
                    break
            if folder:
                out = ROOT / 'assets' / 'projetos' / folder / 'cores.json'
                out.write_text(json.dumps(palette, indent=2, ensure_ascii=False), encoding='utf-8')
                print(f"  Saved: {palette['primary']} / {palette['secondary']} / {palette['accent']}")


if __name__ == '__main__':
    asyncio.run(main())
