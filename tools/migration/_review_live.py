import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright
from pathlib import Path

SLUGS = [
    (86, 'teatro-dos-bons-habitos-ferroporte'),
    (106, 'teatro-oficina-robotica-2aed-cnh'),
    (87, 'exposicao-culinaria-sustentavel-imetame'),
    (82, 'robotica-cultural-nas-escolas'),
    (104, 'pec-3aed-porto-itapoa'),
    (91, 'teatro-dos-ods'),
    (89, 'oficina-teatro-sustentavel-ferroport'),
    (98, 'conhecendo-os-ods'),
    (110, 'caminhao-cultura-sustentabilidade-jaepel'),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})

        for num, slug in SLUGS:
            url = f'https://ntics.com.br/{slug}/'
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            except: pass
            await asyncio.sleep(3)
            h = await page.evaluate('() => document.body.scrollHeight')
            for y in range(0, h + 500, 400):
                await page.evaluate(f'window.scrollTo(0, {y})')
                await asyncio.sleep(0.3)
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(2)
            try:
                await page.wait_for_function('() => Array.from(document.querySelectorAll("img")).every(i => i.complete)', timeout=30000)
            except: pass
            await asyncio.sleep(2)

            broken = await page.evaluate('''() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                return imgs.filter(i => i.complete && i.naturalHeight === 0).map(i => i.src.split('/').pop());
            }''')

            # Also check logo hero size and regua footer size
            meta = await page.evaluate('''() => {
                // Find hero logo (big logo in first section)
                const hero = document.querySelector('section:first-of-type, #home');
                let heroLogo = null;
                if (hero) {
                    const logos = Array.from(hero.querySelectorAll('img')).filter(i => i.src.includes('LOGOS') || i.src.toLowerCase().includes('logo'));
                    if (logos.length) {
                        const rect = logos[0].getBoundingClientRect();
                        heroLogo = { w: rect.width, h: rect.height, src: logos[0].src.split('/').pop() };
                    }
                }
                // Find regua in footer
                const footer = document.querySelector('footer');
                let regua = null;
                if (footer) {
                    const reguas = Array.from(footer.querySelectorAll('img')).filter(i => i.src.includes('REGUAS') || i.src.toLowerCase().includes('regua'));
                    if (reguas.length) {
                        const rect = reguas[0].getBoundingClientRect();
                        regua = { w: rect.width, h: rect.height, src: reguas[0].src.split('/').pop() };
                    }
                }
                return { heroLogo, regua };
            }''')

            await page.screenshot(path=f'g:/O meu disco/AUTOMAÇÕES/.tmp/migration/live-{num}.png', full_page=True)
            print(f'{num} ({slug[:35]}):')
            print(f'  broken imgs: {len(broken)}')
            for b in broken[:5]:
                print(f'    BROKEN: {b}')
            if meta.get('heroLogo'):
                hl = meta['heroLogo']
                print(f"  hero logo: {hl['w']:.0f}x{hl['h']:.0f}px ({hl['src'][:30]})")
            else:
                print('  hero logo: MISSING')
            if meta.get('regua'):
                r = meta['regua']
                print(f"  footer regua: {r['w']:.0f}x{r['h']:.0f}px ({r['src'][:30]})")
            else:
                print('  footer regua: MISSING')

        await browser.close()

asyncio.run(main())
