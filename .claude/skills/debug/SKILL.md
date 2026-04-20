---
name: debug
description: "Investiga falhas de tools/APIs em 4 fases obrigatórias antes de qualquer fix — root cause first, sem trial-and-error"
user-invocable: true
---

## Quando usar

Invoque `/debug` sempre que uma tool ou API falhar: timeout Leonardo, rate-limit Perplexity, webhook ClickUp falho, script Python com traceback, falha de upload Drive, erro de autenticação Gmail.

**Regra:** Nenhum fix sem root cause confirmada. "Só tentar de novo" não é debug.

---

## As 4 Fases

### Fase 1 — Reproduzir e capturar
1. Execute o comando/tool que falhou **uma vez** — não repita até entender
2. Capture o erro completo: mensagem, stack trace, status code, headers de resposta
3. Documente: "Falhou em [data/hora] com: [erro literal]"

**Red flags — pare e reconsidere se você disser:**
- "Vou tentar de novo para ver se resolve"
- "Provavelmente é X" sem evidência

---

### Fase 2 — Analisar padrão
Verifique na ordem:
1. **Variáveis de ambiente** — API key presente? Token expirado? (`LEONARDO_API_KEY`, `PERPLEXITY_API_KEY`, etc.)
2. **Rate limits** — Quantas chamadas foram feitas nesta sessão? Qual o limite da API?
3. **Input inválido** — O payload enviado está correto? Tamanho, formato, campos obrigatórios?
4. **Docs da API** — O endpoint/modelo ainda existe? Mudou de nome recentemente?
5. **Logs anteriores** — O mesmo erro aconteceu antes? Há registro em `workflows/` ou na memória?

---

### Fase 3 — Formular hipótese
Escreva em 1 frase: **"Falhou porque ___"**

Exemplos válidos:
- "Falhou porque `LEONARDO_API_KEY` está undefined no ambiente atual"
- "Falhou porque excedemos 5 chamadas/minuto ao Perplexity (rate-limit)"
- "Falhou porque o modelo `phoenix` foi descontinuado — usar `phoenix-1.0`"

Se não conseguir formular hipótese em 1 frase → volte para a Fase 2.

---

### Fase 4 — Fix mínimo + verificação
1. Faça **uma mudança** baseada na hipótese
2. Execute o comando
3. Se resolveu: documente a causa e a solução no workflow relevante em `workflows/`
4. Se não resolveu: **não acumule mudanças** — reverta, forme nova hipótese, repita

**Regra dos 3 falhas:** Se 3 hipóteses consecutivas falharem, pare e escale para Lucas com:
- Erro literal capturado
- As 3 hipóteses testadas e por que falharam
- Sua teoria atual sobre causa sistêmica

---

## Após resolver

Atualize o workflow correspondente com o que aprendeu:
```markdown
## Troubleshooting
- **Erro X:** Causa Y → Fix Z (descoberto em [data])
```

Isso evita que o mesmo problema aconteça 3x.
