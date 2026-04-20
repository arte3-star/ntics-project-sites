import React from "react";
import { COLORS } from "../data";
import { CardBase, CardTitle, Frase, DarkCard } from "../Shared";

interface StatSec { valor: string; desc: string; }
interface Props {
  titulo: string;
  statValor: string;
  statLabel: string;
  contexto: string;
  statsSecundarios: StatSec[];
  frase: string;
}

export const StatCard: React.FC<Props> = ({
  titulo, statValor, statLabel, contexto, statsSecundarios, frase,
}) => (
  <CardBase>
    {/* Blocos decorativos */}
    <div style={{
      position: "absolute", top: -90, right: -70,
      width: 380, height: 420,
      backgroundColor: COLORS.yellow,
      borderRadius: 60,
      transform: "rotate(8deg)",
      opacity: 0.9,
    }} />
    <div style={{
      position: "absolute", bottom: "8%", right: -80,
      width: 280, height: 280,
      backgroundColor: COLORS.green,
      borderRadius: "50%",
      opacity: 0.7,
    }} />

    <CardTitle title={titulo} />

    {/* Numero gigante com anel */}
    <div style={{
      position: "relative",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      marginTop: 50,
      height: 480,
    }}>
      {/* Anel decorativo */}
      <div style={{
        position: "absolute",
        width: 500, height: 500,
        borderRadius: "50%",
        border: `18px solid ${COLORS.yellow}33`,
      }} />
      {/* Numero */}
      <div style={{
        color: COLORS.yellow,
        fontSize: 340,
        fontWeight: 800,
        lineHeight: 1,
        letterSpacing: "-4px",
        zIndex: 1,
      }}>
        {statValor}
      </div>
    </div>

    {/* Label do stat */}
    <div style={{
      textAlign: "center",
      color: COLORS.white,
      fontSize: 56,
      fontWeight: 700,
      marginTop: 8,
    }}>
      {statLabel}
    </div>

    {/* Linha separadora */}
    <div style={{
      margin: "28px auto",
      width: 340,
      height: 4,
      backgroundColor: COLORS.yellow,
      borderRadius: 2,
    }} />

    {/* Contexto */}
    <div style={{
      marginLeft: 110, marginRight: 110,
      color: COLORS.lightGray,
      fontSize: 48,
      lineHeight: 1.45,
      textAlign: "center",
    }}>
      {contexto}
    </div>

    <Frase text={frase} marginTop={40} />

    {/* Stats secundarios */}
    <div style={{
      marginTop: 36,
      marginLeft: 110, marginRight: 110,
      display: "flex",
      gap: 24,
    }}>
      {statsSecundarios.map((s, i) => (
        <DarkCard
          key={i}
          accentColor={i === 0 ? COLORS.yellow : COLORS.green}
          style={{ flex: 1, textAlign: "center", paddingTop: 40, paddingBottom: 32 }}
        >
          <div style={{
            color: i === 0 ? COLORS.yellow : COLORS.green,
            fontSize: 70,
            fontWeight: 800,
            lineHeight: 1,
          }}>
            {s.valor}
          </div>
          <div style={{
            color: COLORS.lightGray,
            fontSize: 36,
            lineHeight: 1.35,
            marginTop: 8,
          }}>
            {s.desc}
          </div>
        </DarkCard>
      ))}
    </div>
  </CardBase>
);
