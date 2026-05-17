---
name: capa-video
description: "Cria capa estatica (4:5 JPG) para video de projeto NTICS, gera 3 variacoes de layout via Leonardo AI usando foto real + logo do projeto + logo do patrocinador. Output em assets/projetos/{slug}/capa-video/."
user-invocable: true
---

> Referencia Leonardo AI: estrutura validada (PIE Guarulhos + Gastronomia Sustentavel, abr/2026). Se surgir erro de API ou resultado visual inesperado, consultar `workflows/marketing/referencia/leonardo_ai_core.md`.

Leia e execute o workflow completo em `workflows/marketing/producao/videos/capa_video.md`.

## Inputs

**Minimos (obrigatorios):**
1. **Slug do projeto** (ou numero), para localizar assets em `SecondBrain/projetos/{slug}/assets/`
2. **Foto principal** (path ou descricao para escolher de `SecondBrain/banco-fotos/`)
3. **Nome do projeto** (oficial, do TAP/release)
4. **Patrocinador**

**Opcionais (melhoram resultado):**
- Subtitulo / edicao (ex: "2ª Edição")
- Tagline curta (ex: "está chegando em Guarulhos")
- Cidade/UF
- Paleta especifica (se quiser sobrescrever a padrao do projeto)

## Saida

3 variacoes 4:5 (1856×2304 JPG) em `output/marketing/carrosseis/projetos/{slug}/capa-video/`:

| Versao | Layout |
|--------|--------|
| **v1** | Foto topo + curva onda + circulo branco do logo + painel branco bottom |
| **v2** | Bloco cor topo com logo dominante + curva + foto bottom + painel branco |
| **v3** | Foto fullbleed + logo flutuando no canto + painel branco bottom dominante |

Mais `geracao.log` com os `gen_id` (necessario para recuperar versoes apagadas via CDN).

## Regras de Consistencia Visual (aprendizados PIE/Gastronomia abr/2026)

1. **Headline SEMPRE em painel branco arredondado.** Texto solto sobre cor = ilegivel.
2. **Nome do projeto SEMPRE como texto** no painel branco (logo do projeto sozinho fica pequeno demais em mobile).
3. **Apenas "{PATROCINADOR} APRESENTA" no topo** (label unica, nao duplicar).
4. **3 image_references max** no nano-banana-2 (foto + logo projeto + logo patrocinador). Quarta = VALIDATION_ERROR.
5. **Prompt sub-1500 chars.** Prompts longos retornam VALIDATION_ERROR.
6. **Proibir regua tricolor** explicitamente: `DO NOT add any tricolor stripe ruler at the bottom edge`.
7. **Logos preservados pixel-fiel** via `preserved pixel-for-pixel exactly as the reference, keeping its original colors`.
8. **gen_id eh backup.** Salvar antes de qualquer `rm`. Recuperacao via GET `/api/rest/v1/generations/{gid}` no CDN.

## Fluxo

1. Identificar dados do projeto (nome, patrocinador, paleta, foto, logos)
2. Validacao com usuario do brief antes de gerar (custo: 3× US$ 0,058 ≈ US$ 0,18)
3. Gerar 3 variacoes em paralelo
4. Revisao visual obrigatoria (acentos, logos, regua, painel branco)
5. Apresentar ao usuario, regerar versao escolhida com ajustes pontuais
