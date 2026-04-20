import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        page = ctx.pages[0]
        await page.goto('https://24321761-1313158.renderforestsites.com/', wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(5)
        for _ in range(4):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1.5)

        data = await page.evaluate(r'''() => {
            const secs = Array.from(document.querySelectorAll('section'));
            const results = [];
            for (const s of secs) {
                const text = s.innerText.toLowerCase();
                if (text.includes('vídeo') || text.includes('video') || text.includes('assista') || text.includes('democra')) {
                    const h = s.querySelector('h1,h2,h3');
                    const btns = Array.from(s.querySelectorAll('button, a')).map(b => ({text: b.textContent.trim().slice(0,40), href: b.href||''}));
                    const videos = Array.from(s.querySelectorAll('video')).map(v => v.src);
                    results.push({
                        title: h ? h.innerText.trim() : '',
                        fullText: s.innerText.trim().slice(0, 300),
                        btns: btns.slice(0, 5),
                        videos,
                        innerHTML: s.innerHTML.slice(0, 800),
                    });
                }
            }
            return results;
        }''')

        for vs in data:
            print(f'\n--- {vs["title"][:50]} ---')
            print(f'  text: {vs["fullText"][:200]}')
            print(f'  btns: {vs["btns"][:3]}')
            print(f'  videos: {vs["videos"]}')
            print(f'  html: {vs["innerHTML"][:300]}')

asyncio.run(main())
