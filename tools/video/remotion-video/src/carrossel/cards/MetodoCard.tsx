import React from "react";
import { COLORS } from "../data";
import { CardBase, DarkCard } from "../Shared";

interface Metrica { valor: string; desc: string; }
interface Props { frase: string; metricas: Metrica[]; }

export const MetodoCard: React.FC<Props> = ({ frase, metricas }) => (
  <CardBase>
    {/* Label */}
    <div style={{
      textAlign: "center",
      color: COLORS.tealBar,
      fontSize: 44,
      fontWeight: 400,
      letterSpacing: "2px",
      marginTop: 90,
    }}>
      METODO NTICS
    </div>

    {/* Frase principal */}
    <div style={{
      textAlign: "center",
      color: COLORS.white,
      fontSize: 72,
      fontWeight: 800,
      lineHeight: 1.15,
      marginTop: 28,
      marginLeft: 110, marginRight: 110,
    }}>
      {frase}
    </div>

    {/* Linha separadora */}
    <div style={{
      margin: "36px auto",
      width: 300,
      height: 4,
      backgroundColor: COLORS.yellow,
      borderRadius: 2,
    }} />

    {/* Grid 2x2 de metricas */}
    <div style={{
      marginLeft: 60, marginRight: 60,
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 28,
    }}>
      {metricas.slice(0, 4).map((m, i) => (
        <DarkCard
          key={i}
          accentColor={COLORS.yellow}
          style={{ textAlign: "center", paddingTop: 44, paddingBottom: 40 }}
        >
          <div style={{
            color: COLORS.yellow,
            fontSize: 116,
            fontWeight: 800,
            lineHeight: 1,
          }}>
            {m.valor}
          </div>
          <div style={{
            color: COLORS.white,
            fontSize: 40,
            marginTop: 14,
            lineHeight: 1.3,
          }}>
            {m.desc}
          </div>
        </DarkCard>
      ))}
    </div>

    {/* Selos */}
    <div style={{
      textAlign: "center",
      color: COLORS.lightGray,
      fontSize: 34,
      marginTop: 44,
    }}>
      Certificacao ISO 9001 &nbsp;|&nbsp; Pacto Global ONU &nbsp;|&nbsp; GRI Standards
    </div>
  </CardBase>
);
