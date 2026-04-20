import asyncio, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        page = ctx.pages[0]

        await page.goto('https://24321761-1316311.renderforestsites.com/', wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(5)
        for i in range(30):
            await page.mouse.wheel(0, 300)
            await asyncio.sleep(0.3)
        await asyncio.sleep(3)
        await page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)

        data = await page.evaluate(r'''() => {
            const sections = Array.from(document.querySelectorAll('section'));
            return sections.map((s, i) => {
                const h = s.querySelector('h1, h2, h3');
                const imgs = Array.from(s.querySelectorAll('img'))
                    .filter(img => img.src && !img.src.startsWith('data:') && !img.src.includes('rfstat'))
                    .map(img => ({
                        fname: img.src.split('/').pop(),
                        w: img.naturalWidth,
                        h: img.naturalHeight,
                        displayW: Math.round(img.getBoundingClientRect().width),
                        displayH: Math.round(img.getBoundingClientRect().height),
                    }));
                // bg-images
                const bgs = [];
                s.querySelectorAll('*').forEach(el => {
                    const bg = window.getComputedStyle(el).backgroundImage;
                    if (bg && bg !== 'none' && bg.includes('url(') && !bg.includes('data:') && !bg.includes('rfstat')) {
                        const matches = [...bg.matchAll(/url\(["']?([^"')]+)["']?\)/g)];
                        for (const m of matches) bgs.push(m[1].split('/').pop());
                    }
                });
                return {
                    idx: i,
                    title: h ? h.innerText.trim().slice(0, 50) : '(sem titulo)',
                    imgs,
                    bgs,
                    height: Math.round(s.getBoundingClientRect().height),
                };
            });
        }''')

        print('=== COMO O RF ORGANIZA AS FOTOS ===\n')
        total = 0
        for s in data:
            n = len(s['imgs']) + len(s['bgs'])
            total += n
            if n > 0 or s['title'] != '(sem titulo)':
                marker = '***' if n > 3 else ''
                print(f"SEÇÃO {s['idx']}: \"{s['title']}\" — {n} fotos {marker}")
                for img in s['imgs']:
                    print(f"    <img> {img['fname'][:35]} [{img['w']}x{img['h']}] → exibida {img['displayW']}x{img['displayH']}px")
                for bg in s['bgs']:
                    print(f"    bg    {bg[:35]}")
                print()
        print(f"TOTAL no RF: {total} fotos\n")

        # Now analyze MY v2
        print('=== COMO EU ORGANIZEI NA V2 ===\n')
        import re
        from pathlib import Path
        html = Path('g:/O meu disco/AUTOMAÇÕES/.tmp/migration/87_inovadora/index.html').read_text(encoding='utf-8')
        sections = re.split(r'<!-- .+? -->', html)
        # Find section titles and image counts
        for chunk in sections:
            # Find h1/h2 in chunk
            titles = re.findall(r'<h[12][^>]*>(.+?)</h[12]>', chunk, re.DOTALL)
            imgs_in_section = re.findall(r'FOTOS/([^"]+)', chunk)
            if titles or imgs_in_section:
                title = titles[0].strip().replace('\n', ' ')[:50] if titles else '(header/nav)'
                title = re.sub(r'<[^>]+>', '', title)  # strip tags
                print(f"SEÇÃO: \"{title}\" — {len(imgs_in_section)} fotos")
                for img in imgs_in_section:
                    print(f"    {img[:35]}")
                print()

asyncio.run(main())
