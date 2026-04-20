// Dados S03 — 5 sinais de maturidade em Responsabilidade Social

export const COLORS = {
  teal:      "#005F73",
  tealDark:  "#003D4C",
  tealMid:   "#00506A",
  yellow:    "#F5B800",
  white:     "#FFFFFF",
  green:     "#3DAA35",
  tealBar:   "#00A5B8",
  pink:      "#D41A6A",
  orange:    "#E86428",
  lightGray: "#C8C8C8",
  offWhite:  "#F0F0F0",
} as const;

export const S03 = {
  tema:      "5 sinais de maturidade em Responsabilidade Social",
  subtitulo: "Como identificar se sua empresa esta no caminho certo",
  ctaPergunta: "Quer aplicar esses 5 sinais na sua empresa?",
  metodofrase: "24 ANOS DE METODO QUE ENTREGA",
  metodoMetricas: [
    { valor: "1.060+", desc: "projetos executados" },
    { valor: "11,4M",  desc: "pessoas impactadas" },
    { valor: "9,32",   desc: "nota media satisfacao" },
    { valor: "88",     desc: "NPS dos clientes" },
  ],
  cards: [
    {
      slug: "02-programa",
      titulo: "TRATA COMO PROGRAMA, NAO EVENTO",
      tipo: "bullets",
      bullets: [
        { num: "1", label: "INICIO",  stat: "100%", statDesc: "diagnostico antes de agir",
          texto: "Mapeamento profundo do contexto e das necessidades reais do territorio" },
        { num: "2", label: "MEIO",    stat: "9,32", statDesc: "nota media de execucao",
          texto: "Execucao com indicadores de transformacao, nao apenas de presenca" },
        { num: "3", label: "LEGADO",  stat: "68%",  statDesc: "projetos com continuidade ativa",
          texto: "Avaliacao de impacto cultivada pelo proprio territorio apos o programa" },
      ],
      frase: "Acao pontual passa. Programa transforma.",
    },
    {
      slug: "03-envolve",
      titulo: "ENVOLVE QUEM SERA IMPACTADO",
      tipo: "quote",
      quote: "A comunidade nao e objeto do projeto. Ela e coautora.",
      subtexto: "Quando as pessoas participam da construcao, o resultado e delas.",
      stats: [
        { valor: "87%",  desc: "dos beneficiarios participaram ativamente da construcao" },
        { valor: "3,4x", desc: "mais engajamento em projetos co-criados vs tradicionais" },
      ],
      frase: "Co-criar e respeitar.",
    },
    {
      slug: "04-mede",
      titulo: "MEDE O QUE REALMENTE IMPORTA",
      tipo: "barras",
      barras: [
        { label: "Mudanca de comportamento",     valor: 78, sufixo: "%" },
        { label: "Satisfacao dos beneficiarios", valor: 93, sufixo: "%" },
        { label: "Projetos com legado ativo",    valor: 65, sufixo: "%" },
      ],
      frase: "Indicadores de transformacao, nao de presenca.",
    },
    {
      slug: "05-comunica",
      titulo: "COMUNICA COM TRANSPARENCIA",
      tipo: "timeline",
      etapas: [
        { label: "DOCUMENTA",   cor: "#F5B800",
          texto: "Registra resultados com indicadores verificaveis e metodologia clara" },
        { label: "COMPARTILHA", cor: "#3DAA35",
          texto: "Publica os dados — os bons e os aprendizados — sem filtro editorial" },
        { label: "CONSTROI",    cor: "#D41A6A",
          texto: "Transparencia gera confianca, confianca gera autoridade no setor" },
      ],
      frase: "Quem tem dados, tem credibilidade.",
    },
    {
      slug: "06-conecta",
      titulo: "CONECTA AO NEGOCIO",
      tipo: "stat",
      statValor: "88",
      statLabel: "NPS dos clientes NTICS",
      contexto: "RS madura melhora o rating ESG, fortalece a marca empregadora e cria valor mensuravel.",
      statsSecundarios: [
        { valor: "2,3x", desc: "mais facilidade em atrair talentos" },
        { valor: "41%",  desc: "menos turnover com RS madura" },
      ],
      frase: "RS nao e custo. E diferencial competitivo.",
    },
  ],
};
