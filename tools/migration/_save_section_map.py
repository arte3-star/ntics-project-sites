import asyncio, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright
from pathlib import Path

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        page = ctx.pages[0]
        print('URL:', page.url[:60])

        data = await page.evaluate(r'''() => {
            const sections = Array.from(document.querySelectorAll('section'));
            return sections.map((s, i) => {
                const h = s.querySelector('h1, h2, h3');
                const imgs = Array.from(s.querySelectorAll('img'))
                    .filter(img => img.src && !img.src.startsWith('data:') && !img.src.includes('rfstat'))
                    .map(img => img.src.split('/').pop());
                const bgs = [];
                s.querySelectorAll('*').forEach(el => {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (bg && bg !== 'none' && bg.includes('url(')) {
                        const re = /url\(["']?([^"')]+)["']?\)/g;
                        let m;
                        while ((m = re.exec(bg)) !== null) {
                            if (!m[1].startsWith('data:') && !m[1].includes('rfstat')) {
                                bgs.push(m[1].split('/').pop());
                            }
                        }
                    }
                });
                return { idx: i, title: h ? h.innerText.trim() : '', imgs, bgs };
            });
        }''')

        Path('g:/O meu disco/AUTOMAÇÕES/.tmp/migration/87_rf_section_map.json').write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        print('Saved section map')
        for s in data:
            n = len(s['imgs']) + len(s['bgs'])
            if n > 0:
                print(f"  [{s['idx']}] {s['title'][:40]}: {n} photos")

asyncio.run(main())
