import React from "react";
import { COLORS } from "../data";
import { CardBase, CardTitle, Frase } from "../Shared";

interface Etapa { label: string; cor: string; texto: string; }
interface Props { titulo: string; etapas: Etapa[]; frase: string; }

const DOT_R = 44;
const LINE_X = 110 + DOT_R;

export const TimelineCard: React.FC<Props> = ({ titulo, etapas, frase }) => (
  <CardBase>
    <CardTitle title={titulo} />

    <div style={{
      marginTop: 60,
      marginLeft: 110,
      marginRight: 110,
      position: "relative",
      display: "flex",
      flexDirection: "column",
      gap: 0,
    }}>
      {/* Linha vertical de conexao */}
      <div style={{
        position: "absolute",
        left: DOT_R,
        top: DOT_R,
        width: 8,
        bottom: DOT_R + 80,
        backgroundColor: `${COLORS.tealBar}55`,
        borderRadius: 4,
        zIndex: 0,
      }} />

      {etapas.map((etapa, i) => (
        <div key={i} style={{
          display: "flex",
          alignItems: "flex-start",
          gap: 56,
          marginBottom: i < etapas.length - 1 ? 64 : 0,
          position: "relative",
          zIndex: 1,
        }}>
          {/* Dot */}
          <div style={{
            width: DOT_R * 2,
            height: DOT_R * 2,
            borderRadius: "50%",
            border: `6px solid ${etapa.cor}`,
            backgroundColor: COLORS.teal,
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <div style={{
              width: DOT_R - 14,
              height: DOT_R - 14,
              borderRadius: "50%",
              backgroundColor: etapa.cor,
            }} />
          </div>

          {/* Conteudo */}
          <div style={{ flex: 1, paddingTop: 4 }}>
            {/* Linha horizontal do dot ao label */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 20,
              marginBottom: 12,
            }}>
              <div style={{
                width: 60,
                height: 4,
                backgroundColor: etapa.cor,
                borderRadius: 2,
              }} />
              <div style={{
                color: etapa.cor,
                fontSize: 60,
                fontWeight: 700,
                letterSpacing: "0.5px",
                lineHeight: 1,
              }}>
                {etapa.label}
              </div>
            </div>

            {/* Texto */}
            <div style={{
              color: COLORS.lightGray,
              fontSize: 46,
              lineHeight: 1.45,
            }}>
              {etapa.texto}
            </div>
          </div>
        </div>
      ))}
    </div>

    <Frase text={frase} marginTop={52} />
  </CardBase>
);
