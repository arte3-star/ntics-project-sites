import React from "react";
import { COLORS, S03 } from "../data";
import { CardBase, GradientBar } from "../Shared";

export const CapaCard: React.FC = () => (
  <div style={{
    width: "100%", height: "100%",
    backgroundColor: COLORS.teal,
    position: "relative",
    fontFamily: '"Inter", "Segoe UI", sans-serif',
    overflow: "hidden",
  }}>
    {/* Top stripe */}
    <div style={{
      position: "absolute", top: 0, left: 0, right: 0, height: "0.8%",
      background: `linear-gradient(90deg, ${COLORS.green} 0%, ${COLORS.tealBar} 100%)`,
    }} />

    {/* Bloco amarelo grande — canto superior direito */}
    <div style={{
      position: "absolute",
      top: -80, right: -70,
      width: 440, height: 480,
      backgroundColor: COLORS.yellow,
      borderRadius: 70,
      transform: "rotate(8deg)",
    }} />

    {/* Bloco teal_bar — lateral esquerda (meio-alto) */}
    <div style={{
      position: "absolute",
      top: "14%", left: -55,
      width: 200, height: 360,
      backgroundColor: COLORS.tealBar,
      borderRadius: 36,
      opacity: 0.9,
    }} />

    {/* Circulo verde — canto inferior direito */}
    <div style={{
      position: "absolute",
      bottom: "8%", right: -80,
      width: 340, height: 340,
      backgroundColor: COLORS.green,
      borderRadius: "50%",
      opacity: 0.85,
    }} />

    {/* Fundo escuro para zona de texto (56% inferior) */}
    <div style={{
      position: "absolute",
      top: "56%", left: 0, right: 0, bottom: "2.5%",
      background: `linear-gradient(180deg, transparent 0%, ${COLORS.tealDark} 18%, ${COLORS.tealDark} 100%)`,
    }} />

    {/* Conteudo de texto */}
    <div style={{
      position: "absolute",
      top: "59%", left: 0, right: 0,
      padding: "0 110px",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 24,
    }}>
      {/* Badge */}
      <div style={{
        backgroundColor: COLORS.green,
        color: COLORS.white,
        fontSize: 34,
        fontWeight: 700,
        letterSpacing: "0.5px",
        padding: "10px 28px",
        borderRadius: 30,
      }}>
        RESPONSABILIDADE SOCIAL QUE RESOLVE
      </div>

      {/* Titulo */}
      <div style={{
        color: COLORS.white,
        fontSize: 88,
        fontWeight: 800,
        lineHeight: 1.12,
        letterSpacing: "-1px",
        textTransform: "uppercase",
        textAlign: "center",
        marginTop: 8,
      }}>
        {S03.tema}
      </div>

      {/* Subtitulo */}
      <div style={{
        color: COLORS.lightGray,
        fontSize: 50,
        fontStyle: "italic",
        textAlign: "center",
        lineHeight: 1.4,
        marginTop: 4,
      }}>
        {S03.subtitulo}
      </div>
    </div>

    <GradientBar />
  </div>
);
