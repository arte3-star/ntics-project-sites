"""
Substitui os 6 videos introdutorios das aulas no Tutor LMS por versoes
editadas (em C:\\Users\\lucas\\Downloads\\negocio-cultural-videos-introdutorios\\comprimidos).

Para cada arquivo:
1. Upload via wp/v2/media
2. Pega URL nova
3. Atualiza post_content das lessons (Itapoa + SP) com a URL nova,
   preservando o shortcode [video][/video]
"""
import os, sys, json, time, re
from pathlib import Path
import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'publishing'))
from negocio_cultural import _tutor_request

# Load .env manually
for line in open(ROOT / '.env', encoding='utf-8'):
    if '=' in line and not line.strip().startswith('#'):
        k, _, v = line.strip().partition('=')
        os.environ.setdefault(k.strip(), v.strip())

WP_URL = os.environ['WP2_URL'].rstrip('/')
WP_TOKEN = os.environ['WP2_TOKEN']

VIDEOS_DIR = Path(r'C:\Users\lucas\Downloads\negocio-cultural-videos-introdutorios\comprimidos')

# filename -> (lesson Itapoa, lesson SP, label)
MAPPING = [
    ('Aula_Empreendedorismo_MAnaus2025.mp4',     1126, 1529, 'EMPREENDEDORISMO'),
    ('AulaPlanodenegocioManaus-005.mp4',         1137, 1540, 'PLANO DE NEGOCIOS'),
    ('Aula_Vendas_Camboriu.mp4',                 1148, 1551, 'VENDAS'),
    ('Aula_Marketing_Penha.mp4',                 1163, 1566, 'MARKETING'),
    ('Aula_Financeiro_Camboriu.mp4',             1151, 1554, 'FINANCEIRO'),
    ('Aula_Sustentabilidade_Camboriu-003.mp4',   1170, 1573, 'SUSTENTABILIDADE'),
]

def upload_video(file_path: Path) -> dict:
    """Upload video to WP media library. Returns media object dict."""
    size_mb = file_path.stat().st_size / 1024 / 1024
    print(f'[UPLOAD] {file_path.name} ({size_mb:.1f} MB)...', flush=True)
    t0 = time.time()
    with open(file_path, 'rb') as f:
        r = requests.post(
            f'{WP_URL}/wp-json/wp/v2/media',
            headers={
                'X-WP-Token': WP_TOKEN,
                'Content-Type': 'video/mp4',
                'Content-Disposition': f'attachment; filename="{file_path.name}"',
            },
            data=f,
            verify=False,
            timeout=1800,  # 30 min
        )
    elapsed = time.time() - t0
    if r.status_code in (200, 201):
        j = r.json()
        print(f'  OK in {elapsed:.0f}s | id={j["id"]} | {j["source_url"]}', flush=True)
        return j
    else:
        print(f'  FAIL {r.status_code}: {r.text[:500]}', flush=True)
        return None

def get_lesson_content(lesson_id: int, course_id: int) -> str:
    """Read current post_content from course-contents API."""
    r = _tutor_request(f'tutor/v1/course-contents/{course_id}')
    data = r['data'] if isinstance(r, dict) and 'data' in r else r
    for t in data:
        for c in t.get('contents', []):
            if c.get('ID') == lesson_id:
                return c.get('post_content', '')
    return ''

def replace_video_url(content: str, new_url: str) -> str:
    """Replace mp4 URL inside [video] shortcode (handle nested/duplicate cases)."""
    # Normalize: extract any existing video tags and rebuild a clean one
    new_shortcode = f'[video width="1920" height="1080" mp4="{new_url}"][/video]'
    # If there's a [video] shortcode already, replace it
    if '[video' in content:
        content = re.sub(r'\[video[^\]]*?\](\[/video\])?', new_shortcode, content, count=1, flags=re.DOTALL)
        # Remove any leftover nested artifacts
        content = re.sub(r'\[/video\](?=[^\[]*\[/video\])', '', content)
        return content
    # No existing shortcode → wrap in <p>
    return f'<p>{new_shortcode}</p>\n' + content

def update_lesson(lesson_id: int, new_url: str):
    """Read content of lesson (from Itapoa course 1123 or SP course 1526), replace, push."""
    # Try both courses
    for course_id in (1123, 1526):
        content = get_lesson_content(lesson_id, course_id)
        if content:
            new_content = replace_video_url(content, new_url)
            r = _tutor_request(f'tutor/v1/lessons/{lesson_id}', method='POST',
                               data={'lesson_content': new_content})
            print(f'  [UPDATE] lesson {lesson_id}: {r.get("message","?")}', flush=True)
            return True
    print(f'  [UPDATE] lesson {lesson_id}: NOT FOUND', flush=True)
    return False

def main():
    results = {}
    for filename, lid_itapoa, lid_sp, label in MAPPING:
        print(f'\n=== {label} ===', flush=True)
        path = VIDEOS_DIR / filename
        if not path.exists():
            print(f'  SKIP: {path} not found', flush=True)
            continue
        media = upload_video(path)
        if not media:
            results[filename] = 'upload_failed'
            continue
        new_url = media['source_url']
        update_lesson(lid_itapoa, new_url)
        update_lesson(lid_sp, new_url)
        results[filename] = new_url

    print('\n\n=== SUMMARY ===', flush=True)
    for k, v in results.items():
        print(f'{k}: {v}', flush=True)

    # Write manifest
    out = ROOT / 'output' / 'negocio-cultural' / 'video-replace-manifest.json'
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\nManifest: {out}', flush=True)

if __name__ == '__main__':
    main()
