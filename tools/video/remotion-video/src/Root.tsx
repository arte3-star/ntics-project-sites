import React from "react";
import { Composition } from "remotion";
import { VideoAssembly, VideoAssemblySchema } from "./VideoAssembly";
import { S03, COLORS } from "./carrossel/data";
import { CapaCard }     from "./carrossel/cards/CapaCard";
import { BulletsCard }  from "./carrossel/cards/BulletsCard";
import { QuoteCard }    from "./carrossel/cards/QuoteCard";
import { BarrasCard }   from "./carrossel/cards/BarrasCard";
import { TimelineCard } from "./carrossel/cards/TimelineCard";
import { StatCard }     from "./carrossel/cards/StatCard";
import { MetodoCard }   from "./carrossel/cards/MetodoCard";
import { CTACard }      from "./carrossel/cards/CTACard";

const W = 1856;
const H = 2304;
const SINGLE_FRAME = { durationInFrames: 1, fps: 30 };

// Dados tipados dos cards de conteudo
const card02 = S03.cards[0] as any;
const card03 = S03.cards[1] as any;
const card04 = S03.cards[2] as any;
const card05 = S03.cards[3] as any;
const card06 = S03.cards[4] as any;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ── Video original ── */}
      <Composition
        id="VideoAssembly"
        component={VideoAssembly}
        durationInFrames={30 * 60}
        fps={30}
        width={1080}
        height={1920}
        schema={VideoAssemblySchema}
        defaultProps={{
          clips: [],
          narration: null,
          titleCard: { projeto: "Projeto NTICS", patrocinador: "" },
          endCard: { realizacao: "NTICS Projetos", redes: "@nticsprojetos" },
          lowerThirds: [],
          totalDurationInSeconds: 60,
        }}
      />

      {/* ── Carrossel Educativo S03 — 8 cards estáticos ── */}
      <Composition
        id="Card01Capa"
        component={CapaCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{}}
      />

      <Composition
        id="Card02Programa"
        component={BulletsCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          titulo: card02.titulo,
          bullets: card02.bullets,
          frase: card02.frase,
        }}
      />

      <Composition
        id="Card03Envolve"
        component={QuoteCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          titulo: card03.titulo,
          quote: card03.quote,
          subtexto: card03.subtexto,
          stats: card03.stats,
          frase: card03.frase,
        }}
      />

      <Composition
        id="Card04Mede"
        component={BarrasCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          titulo: card04.titulo,
          barras: card04.barras,
          frase: card04.frase,
        }}
      />

      <Composition
        id="Card05Comunica"
        component={TimelineCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          titulo: card05.titulo,
          etapas: card05.etapas,
          frase: card05.frase,
        }}
      />

      <Composition
        id="Card06Conecta"
        component={StatCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          titulo: card06.titulo,
          statValor: card06.statValor,
          statLabel: card06.statLabel,
          contexto: card06.contexto,
          statsSecundarios: card06.statsSecundarios,
          frase: card06.frase,
        }}
      />

      <Composition
        id="Card07Metodo"
        component={MetodoCard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          frase: S03.metodofrase,
          metricas: S03.metodoMetricas,
        }}
      />

      <Composition
        id="Card08CTA"
        component={CTACard}
        {...SINGLE_FRAME} width={W} height={H}
        defaultProps={{
          pergunta: S03.ctaPergunta,
        }}
      />
    </>
  );
};
