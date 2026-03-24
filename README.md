# NTICS — Sites de Projetos

Sites institucionais dos projetos NTICS Projetos, via Lei Rouanet.

## Projetos

| Pasta | Projeto | Patrocinador | Cidade(s) |
|-------|---------|-------------|-----------|
| `116_cultura_robotica/` | Cultura Robotica | Aster Maquinas | — |
| `117_teatro_robotica/` | Teatro e Oficina Robotica nas Escolas 4a Ed | Whirlpool | Rio Claro/SP, Joinville/SC |
| `119_pec/` | PEC EU FACO PARTE 2a Ed | Sylvamo | Mogi Guacu/SP, Guatapara/SP |
| `125_gastronomia/` | Gastronomia tambem e Arte 2a Ed | GRU Airport | Guarulhos/SP |
| `127_pie_guarulhos/` | P.I.E Empreendedorismo e Arte (Cota GRU) | GRU Airport | Guarulhos/SP |
| `127_pie_serra/` | P.I.E Empreendedorismo e Arte (Cota SOTREQ) | SOTREQ | Serra/ES |

## Estrutura

Cada pasta e um site independente:

```
{projeto}/
├── index.html          # Site completo (HTML + CSS + JS inline)
└── assets/
    ├── logos/           # Logo do projeto
    ├── reguas/          # Regua de logos (patrocinador + realizador + governo)
    ├── imagens/         # KV e fotos das cidades (adicionar)
    └── galeria/         # Fotos do projeto (adicionar)
```

## Deploy

Cada pasta pode ser importada no Lovable como projeto independente, ou deployada como site estatico (Netlify, GitHub Pages, Vercel).
