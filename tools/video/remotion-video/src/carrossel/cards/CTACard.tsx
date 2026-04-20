import React from "react";
import { COLORS } from "../data";
import { CardBase } from "../Shared";

interface Props { pergunta: string; }

export const CTACard: React.FC<Props> = ({ pergunta }) => (
  <CardBase>
    {/* Elementos decorativos nos cantos */}
    <div style={{
      position: "absolute",
      right: -40, top: "48%",
      width: 260, height: 220,
      backgroundColor: COLORS.tealBar,
      borderRadius: 30,
      opacity: 0.6,
    }} />
    <div style={{
      position: "absolute",
      left: -40, top: "51%",
      width: 240, height: 200,
      backgroundColor: COLORS.green,
      borderRadius: 30,
      opacity: 0.5,
    }} />

    {/* Logo placeholder (texto se nao houver imagem) */}
    <div style={{
      marginTop: 120,
      textAlign: "center",
    }}>
      {/* Simbolo da lampada simplificado */}
      <div style={{
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 6,
      }}>
        <div style={{
          width: 90, height: 90,
          borderRadius: "50%",
          backgroundColor: COLORS.white,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 52,
        }}>
          💡
        </div>
        <div style={{
          color: COLORS.white,
          fontSize: 56,
          fontWeight: 800,
          letterSpacing: "2px",
          marginTop: 8,
        }}>
          NTICS
        </div>
        <div style={{
          color: COLORS.lightGray,
          fontSize: 36,
          letterSpacing: "4px",
          fontWeight: 400,
        }}>
          PROJETOS
        </div>
      </div>
    </div>

    {/* Linha sutil */}
    <div style={{
      margin: "56px 200px 0",
      height: 2,
      backgroundColor: `${COLORS.yellow}28`,
      borderRadius: 1,
    }} />

    {/* Pergunta CTA */}
    <div style={{
      marginTop: 64,
      marginLeft: 110, marginRight: 110,
      color: COLORS.white,
      fontSize: 74,
      fontWeight: 800,
      lineHeight: 1.2,
      textAlign: "center",
    }}>
      {pergunta}
    </div>

    {/* Fale com a NTICS */}
    <div style={{
      marginTop: 56,
      textAlign: "center",
      color: COLORS.white,
      fontSize: 56,
      fontWeight: 400,
    }}>
      Fale com a NTICS
    </div>

    {/* Botao URL */}
    <div style={{
      marginTop: 44,
      display: "flex",
      justifyContent: "center",
    }}>
      <div style={{
        border: `5px solid ${COLORS.white}`,
        borderRadius: 50,
        padding: "18px 72px",
        color: COLORS.white,
        fontSize: 52,
        fontWeight: 700,
        letterSpacing: "0.5px",
      }}>
        ntics.com.br
      </div>
    </div>

    {/* Handle */}
    <div style={{
      marginTop: 44,
      textAlign: "center",
      color: COLORS.lightGray,
      fontSize: 48,
    }}>
      @nticsprojetos
    </div>

    {/* Tagline */}
    <div style={{
      marginTop: 24,
      textAlign: "center",
      color: COLORS.lightGray,
      fontSize: 44,
      fontStyle: "italic",
    }}>
      Novo olhar para o mundo
    </div>
  </CardBase>
);
