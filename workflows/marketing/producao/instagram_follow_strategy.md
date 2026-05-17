# Workflow: Seguir Contas Estratégicas no Instagram

**Área:** Marketing / Redes Sociais  
**Conta:** @nticsprojetos  
**Objetivo:** Construir rede de 500 contas ESG/sustentabilidade para aumentar visibilidade B2B

---

## Regras de Segurança (aprendidas em campo)

### Volume diário
- **Máximo:** 50-60 follows/dia para conta com ~6K seguidores
- **Mínimo entre follows:** 10-22 segundos (aleatório)
- **Parar imediatamente** se aparecer "Tente novamente mais tarde"
- Não rodar mais de uma sessão por dia

### Verificação obrigatória antes de seguir
**NUNCA seguir sem verificar.** Handles comuns têm namesquatters com poucos seguidores.

Critérios de verificação:
1. Conta existe (sem erro 404)
2. Nome do perfil condiz com a marca esperada
3. Mínimo 500 seguidores (filtro anti-fake)
4. Se seguidores < 5.000 para uma marca grande, investigar antes

**Casos reais de handles errados descobertos:**
| Handle tentado | Era na verdade | Handle correto |
|---|---|---|
| @vale | Val Rosati (triatleta) | @valenobrasil |
| @agenciabrasil | Andre Bezerra (pessoa) | @agencia.brasil |
| @fgv_oficial | Fake com emoji | @fgv.oficial |
| @b3oficial | "Billzinho gospel" | @b3_oficial |
| @vivobr | Conta com 52 seguidores | verificar |

---

## Ferramentas

- **Script principal:** `tmp/instagram_follow_100.py`
- **Estado persistido:** `tmp/instagram_follow_state.json`
- **Unfollow:** `tmp/instagram_unfollow_playwright.py`
- **Verificação de handles:** `tmp/verify_handles.py`
- **Skill de browser:** `/editar-site-web` (Playwright + CDP na porta 9222)

---

## Como executar

### Pré-requisito: Chrome aberto com porta de debug
```powershell
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList "--remote-debugging-port=9222","--user-data-dir=C:\Users\lucas\AppData\Local\Temp\browser-session","--no-first-run","https://www.instagram.com"
```

### Rodar sessão diária
```bash
cd "g:\O meu disco\Claude-NTICS-Projetos"
python tmp/instagram_follow_100.py
```

O script:
1. Carrega estado de `instagram_follow_state.json` (não repete contas já processadas)
2. Para cada handle: acessa o perfil, verifica seguidores, filtra contas com < 500 seguidores
3. Segue com pausa aleatória de 10-22s
4. Para automaticamente ao atingir a meta ou ao detectar bloqueio
5. Salva estado após cada ação

### Unfollow de conta errada
```bash
python tmp/instagram_unfollow_playwright.py
```
Editar a lista `UNFOLLOW` no script antes de rodar.

---

## Listas de handles verificados por categoria

### Categoria 1 — Corporações ESG
```
valenobrasil, natura, grupoboticarionews, ambev, nestlebrasil,
suzano, engiebrasil, bancodobrasil, unileverbrasil, bradesco,
itau, gerdau, petrobras, magazineluiza, totvs, cpflenergia,
danone_br, mercadolivre, klabin, embraer, votorantimbr, raizen
```

### Categoria 2 — Veículos ESG
```
exame.esg, esginsights, infomoney, valoreconomico, nexojornal,
agencia.brasil, fgv.oficial, b3_oficial, folha, estadao,
cnnbrasil, bloomberg_linea, seudinheiro, reporterbrasil
```

### Categoria 3 — Entidades e Institutos
```
abrinq, institutoethos, gife, idis_br, institutoalana,
institutoigarape, fundacaonatura, institutotim, itaucultural,
institutounibanco, sebrae, senai_br, sescbrasil, sesi_br,
fundacaobradesco, fundacaovale, ungcbrasil
```

---

## Estado atual
- Seguindo: ver `tmp/instagram_follow_state.json`
- Meta total: 500 contas
- Ritmo: ~50/dia = ~10 dias para completar

---

## Checklist de verificação de novo handle
Antes de adicionar um handle à lista:
- [ ] Acessar instagram.com/{handle} manualmente
- [ ] Confirmar que o nome do perfil é a marca esperada
- [ ] Confirmar que tem histórico de posts da empresa
- [ ] Confirmar que tem seguidores condizentes (ex: Petrobras > 100K)
- [ ] Se tiver badge de verificação azul/cinza: sinal positivo
