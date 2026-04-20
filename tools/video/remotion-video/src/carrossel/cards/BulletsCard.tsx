import React from "react";
import { COLORS } from "../data";
import { CardBase, CardTitle, Frase, DarkCard } from "../Shared";

const BULLET_COLORS = [COLORS.yellow, COLORS.green, COLORS.pink];
const NUM_TEXT_COLORS = [COLORS.teal, COLORS.white, COLORS.white];

interface Bullet {
  num: string;
  label: string;
  stat: string;
  statDesc: string;
  texto: string;
}

interface Props {
  titulo: string;
  bullets: Bullet[];
  frase: string;
}

export const BulletsCard: React.FC<Props> = ({ titulo, bullets, frase }) => (
  <CardBase>
    <CardTitle title={titulo} />

    {/* Bullets */}
    <div style={{
      marginTop: 48,
      marginLeft: 110,
      marginRight: 110,
      display: "flex",
      flexDirection: "column",
      gap: 32,
    }}>
      {bullets.map((bullet, i) => {
        const color = BULLET_COLORS[i] ?? COLORS.yellow;
        const numColor = NUM_TEXT_COLORS[i] ?? COLORS.teal;
        return (
          <DarkCard key={i} accentColor={color}>
            <div style={{ display: "flex", gap: 32, alignItems: "flex-start", paddingTop: 20 }}>
              {/* Circulo numerado */}
              <div style={{
                width: 110, height: 110,
                borderRadius: "50%",
                backgroundColor: color,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}>
                <span style={{
                  color: numColor,
                  fontSize: 60,
                  fontWeight: 800,
                  lineHeight: 1,
                }}>
                  {bullet.num}
                </span>
              </div>

              {/* Conteudo central */}
              <div style={{ flex: 1 }}>
                <div style={{
                  color: color,
                  fontSize: 52,
                  fontWeight: 700,
                  letterSpacing: "0.5px",
                }}>
                  {bullet.label}
                </div>
                <div style={{
                  color: COLORS.lightGray,
                  fontSize: 42,
                  lineHeight: 1.4,
                  marginTop: 8,
                }}>
                  {bullet.texto}
                </div>
              </div>

              {/* Stat lateral */}
              <div style={{
                width: 240,
                flexShrink: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                paddingLeft: 20,
                borderLeft: `3px solid ${color}44`,
              }}>
                <div style={{
                  color: color,
                  fontSize: 56,
                  fontWeight: 800,
                  lineHeight: 1,
                }}>
                  {bullet.stat}
                </div>
                <div style={{
                  color: COLORS.lightGray,
                  fontSize: 32,
                  textAlign: "center",
                  marginTop: 6,
                  lineHeight: 1.3,
                }}>
                  {bullet.statDesc}
                </div>
              </div>
            </div>
          </DarkCard>
        );
      })}
    </div>

    <Frase text={frase} marginTop={40} />
  </CardBase>
);
