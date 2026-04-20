import React from "react";
import { COLORS } from "../data";
import { CardBase, CardTitle, Frase } from "../Shared";

const BAR_COLORS = [COLORS.yellow, COLORS.green, COLORS.tealBar];

interface Barra { label: string; valor: number; sufixo: string; }
interface Props { titulo: string; barras: Barra[]; frase: string; }

export const BarrasCard: React.FC<Props> = ({ titulo, barras, frase }) => (
  <CardBase>
    <CardTitle title={titulo} />

    <div style={{
      marginTop: 60,
      marginLeft: 110, marginRight: 110,
      display: "flex",
      flexDirection: "column",
      gap: 72,
    }}>
      {barras.map((barra, i) => {
        const color = BAR_COLORS[i] ?? COLORS.yellow;
        const valText = `${barra.valor}${barra.sufixo}`;
        return (
          <div key={i}>
            {/* Label + valor */}
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
              marginBottom: 18,
            }}>
              <div style={{
                color: COLORS.white,
                fontSize: 50,
                fontWeight: 400,
                lineHeight: 1,
              }}>
                {barra.label}
              </div>
              <div style={{
                color: color,
                fontSize: 88,
                fontWeight: 800,
                lineHeight: 1,
              }}>
                {valText}
              </div>
            </div>

            {/* Barra */}
            <div style={{
              width: "100%",
              height: 96,
              backgroundColor: COLORS.tealDark,
              borderRadius: 48,
              overflow: "hidden",
            }}>
              <div style={{
                width: `${barra.valor}%`,
                height: "100%",
                backgroundColor: color,
                borderRadius: 48,
                boxShadow: `0 0 24px ${color}66`,
              }} />
            </div>
          </div>
        );
      })}
    </div>

    <Frase text={frase} marginTop={72} />
  </CardBase>
);
