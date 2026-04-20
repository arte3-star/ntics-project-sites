#!/usr/bin/env python3
"""
lovable_add_videos.py — Adiciona vídeos YouTube aos projetos Lovable.
"""

import asyncio
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]

# YouTube IDs extracted from RF editor
VIDEOS = {
    86: ['MQZsiNH4VHI'],
    106: ['iv7G80PL-Wc', '3jvVVVENMz4'],
    87: ['tpnxsDmEn6I'],
    82: ['f6spw_mqa08', 'GTiTCQoJTWU'],
    104: ['qxMLY30odLA'],
    91: ['HhF9OWiG8I0', 'GyFnaB3XkFA', '-5A3nu5dcyI'],
    89: ['8nMSTOuBG4s'],
    98: ['NUPOLpoq3HE'],
    110: ['y_kJXYloXIU', '6uVyszMBAow', 'iXb4U9dyOM4', 'QgDjhcXx76w', '_rcp0sRhWl0', 'y0rTH0riXK8'],
}

# RF h2 titles for video sections
VIDEO_TITLES = {
    86: ['ASSISTA O VÍDEO'],
    106: ['ASSISTA O VÍDEO DO ESPETÁCULO', 'ASSISTA O VÍDEO DA OFICINA'],
    87: ['ASSISTA O VÍDEO'],
    82: ['ASSISTA O VÍDEO DO ESPETÁCULO - Com libras e audiodescrição', 'ASSISTA O VÍDEO DO ESPETÁCULO'],
    104: ['ASSISTA O VÍDEO'],
    91: ['ASSISTA O VÍDEO DA PALESTRA', 'ASSISTA O VÍDEO DO ESPETÁCULO', 'ASSISTA O VÍDEO DA OFICINA'],
    89: ['ASSISTA O VÍDEO'],
    98: ['ASSISTA O VÍDEO'],
    110: ['ASSISTA AO VÍDEO DA OFICINA', 'ASSISTA AO ESPETÁCULO TEATRAL', 'MOSTRA AUDIOVISUAL'],
}


def build_video_prompt(num: int) -> str:
    videos = VIDEOS.get(num, [])
    titles = VIDEO_TITLES.get(num, [])
    if not videos:
        return ''

    parts = ['Adicione vídeos YouTube ao site. Faça sem perguntar.\n']

    if len(videos) == 1:
        parts.append(f'Na seção "DEMOCRATIZAÇÃO DE ACESSO", após o texto de democratização, adicione um iframe YouTube:')
        parts.append(f'  <iframe src="https://www.youtube.com/embed/{videos[0]}" width="100%" height="400" frameborder="0" allowfullscreen></iframe>')
        parts.append(f'  Título acima do vídeo: "{titles[0] if titles else "ASSISTA O VÍDEO"}"')
    else:
        parts.append('Adicione as seguintes seções de vídeo na área de DEMOCRATIZAÇÃO DE ACESSO:')
        for i, vid in enumerate(videos):
            title = titles[i] if i < len(titles) else f'VÍDEO {i+1}'
            parts.append(f'\n  Seção {i+1}: título "{title}"')
            parts.append(f'  <iframe src="https://www.youtube.com/embed/{vid}" width="100%" height="400" frameborder="0" allowfullscreen></iframe>')

    parts.append('\n\nRegras:')
    parts.append('- O iframe deve ter aspect-ratio 16:9, responsivo (width 100%, max-width 800px)')
    parts.append('- Cada vídeo em sua própria seção com título')
    parts.append('- Posicione DEPOIS da seção de Democratização e ANTES da Galeria de Fotos')
    parts.append('- Também corrija: remova imagens duplicadas (cada foto deve aparecer 1x apenas)')

    return '\n'.join(parts)


async def click_allow(page):
    for _ in range(3):
        c = await page.evaluate(
            '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Allow"); if (b) { b.click(); return true; } return false; }'
        )
        if c:
            await asyncio.sleep(2)
        else:
            break


async def wait_idle(page, max_wait=300):
    elapsed = 0
    while elapsed < max_wait:
        await click_allow(page)
        busy = await page.evaluate(
            '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Editing") || t.includes("Generating") || t.includes("Thinking"); }'
        )
        if not busy:
            await asyncio.sleep(3)
            busy2 = await page.evaluate(
                '() => { const t = document.body.innerText; return t.includes("Building") || t.includes("Working") || t.includes("Editing"); }'
            )
            if not busy2:
                return True
        await asyncio.sleep(5)
        elapsed += 5
    return False


async def main():
    sites = json.loads((ROOT / 'tools/migration/sites_pendentes.json').read_text(encoding='utf-8'))
    batch = json.loads((ROOT / '.tmp/migration/lovable_batch_results.json').read_text(encoding='utf-8'))
    pid_map = {b['site']: b['project_id'] for b in batch}
    pid_map['Teatro dos Bons Hábitos'] = 'fed8254b-bbfd-42ad-9b74-9cf6a6a918a7'

    results = []
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        for site in sites:
            pid = pid_map.get(site['nome_planilha'])
            if not pid:
                continue
            num = site['numero_ntics']
            prompt = build_video_prompt(num)
            if not prompt:
                continue

            print(f"\n--- {num} {site['nome_planilha'][:35]} ({len(VIDEOS.get(num, []))} videos) ---", flush=True)

            await page.goto(f'https://lovable.dev/projects/{pid}', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(8)
            await page.bring_to_front()
            await page.keyboard.press('Escape')
            await asyncio.sleep(1)

            # Check build error
            build_err = await page.evaluate('() => document.body.innerText.includes("Build unsuccessful")')
            if build_err:
                print('    [BUILD FAILED - Try to fix]', flush=True)
                await page.evaluate(
                    '() => { const b = Array.from(document.querySelectorAll("button")).find(x => x.textContent.trim() === "Try to fix"); if (b) { b.click(); return true; } return false; }'
                )
                await asyncio.sleep(10)
                await wait_idle(page, max_wait=240)

            editor = page.locator('div.tiptap.ProseMirror').first
            try:
                await editor.click(timeout=15000)
            except Exception as e:
                print(f'    ERR editor: {e}', flush=True)
                results.append({'numero': num, 'error': str(e)})
                continue

            await asyncio.sleep(0.5)
            await page.keyboard.insert_text(prompt)
            await asyncio.sleep(1)
            await page.keyboard.press('Control+Enter')
            print('    [submitted]', flush=True)

            await asyncio.sleep(10)
            idle = await wait_idle(page, max_wait=300)
            print(f'    [idle: {idle}]', flush=True)
            results.append({'numero': num, 'submitted': True, 'idle': idle})

    (ROOT / '.tmp/migration/lovable_videos_results.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    print('\n=== SUMMARY ===', flush=True)
    for r in results:
        st = 'OK' if r.get('idle') else 'WARN'
        print(f'  {st} {r.get("numero")}: {r.get("error", "submitted")}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
