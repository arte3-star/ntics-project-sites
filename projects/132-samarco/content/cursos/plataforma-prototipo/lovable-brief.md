# Brief de construção da plataforma na Lovable

**Aplicação:** Plataforma de cursos digitais NTICS Projetos
**Programa inicial:** Estação Samarco, Territórios do Futuro
**Status do brief:** v1.0, abril de 2026
**Referência visual:** Protótipo HTML estático em `plataforma-prototipo/` (este diretório)

---

## 1. O que é

Plataforma web de cursos digitais que cumpre **3 funções**:

1. **Vitrine institucional pública.** Apresenta os cursos a interessados, parceiros e participantes ainda não inscritos.
2. **LMS (sistema de aprendizado) para participantes inscritos.** Login individual, vídeos, atividades, quizzes, materiais, controle de progresso, certificação.
3. **Página pública de validação de certificado.** Qualquer pessoa pode digitar o código do certificado e ver se é válido.

Cumpre o requisito do projeto Estação Samarco de que cada participante precisa cumprir **22 horas digitais** com login, controle de acesso e evidência de conclusão para receber o certificado de 50 horas.

---

## 2. Páginas e fluxos

### 2.1 Públicas (não requer login)

- **/ (Landing).** Apresenta os cursos, integra logos do programa, CTA para login. Referência: `index.html`.
- **/login.** Formulário CPF + senha. Referência: `login.html`.
- **/cadastro.** Formulário de primeiro acesso (CPF + e-mail + senha + aceite de termos), só liberado se o CPF estiver na lista de inscritos.
- **/recuperar-senha.** Por e-mail.
- **/validar-certificado.** Campo de código + resultado da validação. Referência: `certificado-validar.html`.

### 2.2 Privadas (requer login do aluno)

- **/painel.** Dashboard do aluno. Mostra curso atual, progresso geral, módulos digitais com status, jornada presencial. Referência: `dashboard.html`.
- **/modulo/:id.** Dentro de um módulo digital. Vídeo player, lista de vídeos do módulo, atividades, materiais para download, quiz. Referência: `modulo.html`.
- **/atividades.** Visão geral de todas as atividades pendentes e entregues.
- **/perfil.** Dados pessoais editáveis, foto, configurações de notificação.
- **/certificado.** Quando todos os requisitos estão cumpridos, exibe o certificado em alta qualidade para download.
- **/suporte.** Formulário de chamado.

### 2.3 Privadas (requer login admin/coordenação)

- **/admin/turmas.** Lista de turmas, criação de novas turmas, vinculação a cidade e curso.
- **/admin/participantes.** Lista de inscritos por turma, upload em lote (CSV), gestão de presença, gestão de progresso.
- **/admin/relatorios.** Geração do Relatório de Execução de Turma (Anexo X) com base nos dados da plataforma.
- **/admin/certificados.** Aprovação manual ou automática de certificados após cumprimento dos requisitos.
- **/admin/conteudo.** Gestão dos vídeos e atividades dos módulos digitais.

---

## 3. Modelos de dados (entidades principais)

```
Programa
  id, nome, patrocinador, kv (assets), inicio, fim

Curso
  id, programa_id, slug, nome_tecnico, nome_comercial, carga_horaria,
  modalidade, ativo

Modulo
  id, curso_id, codigo (D1-D8 ou M1-M5 presencial), tipo (digital/presencial),
  nome, carga_horaria, descricao

Video
  id, modulo_id, ordem, nome, duracao_min, url_video, transcricao

Atividade
  id, modulo_id, ordem, tipo (quiz/upload/reflexao), nome,
  descricao, obrigatoria, criterio_aprovacao

Turma
  id, curso_id, cidade, uf, periodo_inicio, periodo_fim,
  facilitador, coordenador

Participante
  id, nome, cpf, data_nascimento, email, telefone,
  endereco, comunidade, foto_url

Inscricao
  id, participante_id, turma_id, status (inscrito/iniciante/concluinte/desistente),
  aceite_regulamento_em, aceite_imagem_em

Presenca
  id, inscricao_id, modulo_presencial_id, data, status (presente/ausente)

ProgressoVideo
  id, inscricao_id, video_id, completo, ultima_posicao_segundos, atualizado_em

ProgressoAtividade
  id, inscricao_id, atividade_id, status (pendente/entregue/aprovado),
  conteudo_entregue, observacao_avaliador

Certificado
  id, inscricao_id, codigo, emitido_em, conceito, pdf_url, status (valido/revogado)
```

---

## 4. Identidade visual

- **Cores principais:** verde NTICS `#3DAA35`, azul petróleo `#005F73`, rosa `#D41A6A`. Conforme [`brand/NTICS-cheatsheet.md`](../../../../brand/NTICS-cheatsheet.md).
- **Logos:** logo Samarco (soberano em peças do programa), logo NTICS (realização).
- **Tipografia:** Inter (Google Fonts) como base. Pode evoluir para tipografia institucional NTICS quando manual da Samarco for definido.
- **Tom institucional:** profissional, acessível, sem excesso. Referência integral em [`brand/NTICS-cheatsheet.md`](../../../../brand/NTICS-cheatsheet.md).
- **Regra hard:** **NÃO usar travessão (em-dash) em nenhum texto da plataforma.** Substituir por vírgula, ponto ou reescrever.

---

## 5. Integrações

- **Validação de certificado:** integração com a plataforma **e-certificado.com** (já em uso pela NTICS). Cada certificado gera código único, vinculado e consultável.
- **E-mail transacional:** SendGrid, Resend ou similar. Envia confirmação de cadastro, lembretes de inatividade, certificado emitido, recuperação de senha.
- **WhatsApp (opcional):** integração com Twilio ou WPPConnect para lembretes de inatividade e suporte. Avaliar custo.
- **Player de vídeo:** Vimeo (player profissional, sem anúncios, controle de privacidade) ou YouTube unlisted. Vimeo é preferível pelo controle.
- **Storage:** Cloudflare R2, S3 ou Supabase Storage para PDFs e materiais.
- **Auth:** preferencial Supabase Auth ou Clerk, com login por CPF + senha.

---

## 6. Acessibilidade

- Legendas em português obrigatórias em todos os vídeos.
- Contraste de cor adequado (WCAG AA mínimo).
- Navegação por teclado funcional.
- Texto alternativo em todas as imagens.
- Material em PDF para download offline.
- Versão mobile responsiva (a maioria dos participantes acessa pelo celular).

---

## 7. Critérios de conclusão da plataforma (para certificação)

Conforme **Anexo VI** do projeto pedagógico:

1. Todos os 8 módulos digitais com 100% dos vídeos obrigatórios assistidos.
2. Todas as atividades obrigatórias entregues.
3. Quiz de cada módulo aprovado (com possibilidade de até 3 tentativas).
4. Projeto de aplicação prática (D8) entregue.

A plataforma deve calcular automaticamente o status de elegibilidade ao certificado a cada conclusão de módulo.

---

## 8. Lembretes automáticos

- Sem acesso há 7 dias: lembrete por e-mail.
- Sem acesso há 14 dias: lembrete por e-mail + WhatsApp (se opt-in).
- Sem acesso há 21 dias: contato direto da coordenação.
- 7 dias antes do prazo final: lembrete urgente.
- Após emissão do certificado: parabenização + convite para grupos de continuidade.

---

## 9. Conformidade LGPD

- Consentimento explícito no cadastro.
- Política de privacidade pública e em linguagem acessível.
- Direitos do titular (acesso, correção, exclusão) acessíveis no perfil.
- Logs de acesso e ação para auditoria.
- Prazo de guarda dos dados: 5 anos após conclusão (alinhado com regulamento, Anexo VIII).
- Exclusão automática ou anonimização após o prazo.

---

## 10. Roadmap sugerido para construção

### Fase 1, MVP (4 a 6 semanas)

- Landing pública.
- Cadastro e login com CPF.
- Painel do aluno com módulos e progresso.
- Player de vídeo integrado.
- Quizzes simples.
- Upload de atividades.
- Geração de certificado (PDF) ao cumprir requisitos.
- Validação pública de certificado.

### Fase 2, Operação (6 a 8 semanas)

- Painel admin com gestão de turmas e participantes.
- Upload em lote de inscritos via CSV.
- Geração de Relatório de Execução de Turma (Anexo X).
- Lembretes automáticos.
- Integração e-certificado.com.
- Dashboard institucional para o patrocinador.

### Fase 3, Aprimoramento (contínuo)

- Aplicativo mobile (PWA inicialmente, app nativo se for necessário).
- Comunidade/fórum entre alunos da mesma turma.
- Conteúdos extras pós-conclusão.
- Internacionalização (caso o programa expanda).

---

## 11. Indicações para a Lovable

Ao gerar o app na Lovable, pedir explicitamente:

- Stack: React + TypeScript + Tailwind CSS + Supabase (Auth + DB + Storage).
- Componentes: usar shadcn/ui como base.
- Cores: aplicar as cores NTICS no `tailwind.config.ts`.
- Tipografia: Inter via Google Fonts.
- Páginas iniciais: replicar o protótipo HTML em React.
- Integração: Supabase para auth e banco.
- Responsividade: mobile first.

Prompt sugerido inicial para a Lovable:

> "Construa uma plataforma LMS chamada 'Plataforma NTICS Projetos' com login por CPF/senha, dashboard de aluno com módulos digitais e progresso, página de módulo com player de vídeo e atividades, e página pública de validação de certificado. Use Tailwind com as cores #3DAA35 (verde primário), #005F73 (azul institucional), #D41A6A (rosa). Tipografia Inter. Mobile first. Use o protótipo HTML que vou compartilhar como referência visual exata. Banco em Supabase com as entidades: Programa, Curso, Módulo, Vídeo, Atividade, Turma, Participante, Inscrição, Presença, ProgressoVídeo, ProgressoAtividade, Certificado."

---

## 12. Referências dentro do repositório

- **Protótipo visual:** este diretório (`plataforma-prototipo/`).
- **Cheatsheet de marca:** [`brand/NTICS-cheatsheet.md`](../../../../brand/NTICS-cheatsheet.md).
- **PPP base:** [`../00-projeto-pedagogico-v1.md`](../00-projeto-pedagogico-v1.md).
- **Conteúdo dos módulos digitais:** [`../digital/`](../digital/).
- **Anexos pedagógicos:** [`../anexos/`](../anexos/).

---

*Brief versão 1.0. Será revisado conforme decisões da coordenação institucional sobre LMS final (Lovable confirmado em PLAYBOOK do projeto, mas hipóteses alternativas podem ser avaliadas).*
