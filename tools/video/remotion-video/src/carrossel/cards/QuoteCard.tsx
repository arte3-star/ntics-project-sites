import React from "react";
import { COLORS } from "../data";
import { CardBase, CardTitle, Frase, DarkCard } from "../Shared";

interface Stat { valor: string; desc: string; }
interface Props {
  titulo: string;
  quote: string;
  subtexto: string;
  stats: Stat[];
  frase: string;
}

export const QuoteCard: React.FC<Props> = ({ titulo, quote, subtexto, stats, frase }) => (
  <CardBase>
    {/* Circulo decorativo de fundo */}
    <div style={{
      position: "absolute",
      top: "35%", left: "50%",
      transform: "translate(-50%, -50%)",
      width: 1100, height: 1100,
      borderRadius: "50%",
      border: `80px solid ${COLORS.tealBar}22`,
      pointerEvents: "none",
    }} />

    {/* Aspas decorativas */}
    <div style={{
      position: "absolute",
      top: 80, left: 60,
      fontSize: 400,
      fontWeight: 800,
      color: `${COLORS.yellow}1A`,
      lineHeight: 1,
      fontFamily: "Georgia, serif",
      userSelect: "none",
    }}>
      "
    </div>

    <CardTitle title={titulo} />

    {/* Linha separadora */}
    <div style={{
      margin: "36px auto 0",
      width: 300,
      height: 4,
      backgroundColor: COLORS.yellow,
      borderRadius: 2,
    }} />

    {/* Quote principal */}
    <div style={{
      marginTop: 48,
      marginLeft: 110, marginRight: 110,
      color: COLORS.white,
      fontSize: 80,
      fontWeight: 800,
      lineHeight: 1.18,
      textAlign: "center",
    }}>
      {quote}
    </div>

    {/* Aspas de fechamento */}
    <div style={{
      textAlign: "right",
      marginRight: 110,
      marginTop: 16,
      fontSize: 110,
      fontWeight: 800,
      color: COLORS.yellow,
      lineHeight: 0.6,
      fontFamily: "Georgia, serif",
    }}>
      "
    </div>

    {/* Subtexto */}
    <div style={{
      marginTop: 36,
      marginLeft: 110, marginRight: 110,
      color: COLORS.lightGray,
      fontSize: 52,
      lineHeight: 1.45,
      textAlign: "center",
    }}>
      {subtexto}
    </div>

    <Frase text={frase} marginTop={44} />

    {/* Mini-stats lado a lado */}
    <div style={{
      marginTop: 36,
      marginLeft: 110, marginRight: 110,
      display: "flex",
      gap: 24,
      flex: 1,
    }}>
      {stats.map((s, i) => (
        <DarkCard
          key={i}
          accentColor={i === 0 ? COLORS.yellow : COLORS.green}
          style={{ flex: 1, textAlign: "center", paddingTop: 40 }}
        >
          <div style={{
            color: i === 0 ? COLORS.yellow : COLORS.green,
            fontSize: 72,
            fontWeight: 800,
            lineHeight: 1,
          }}>
            {s.valor}
          </div>
          <div style={{
            color: COLORS.lightGray,
            fontSize: 36,
            lineHeight: 1.35,
            marginTop: 10,
          }}>
            {s.desc}
          </div>
        </DarkCard>
      ))}
    </div>
  </CardBase>
);
