import React from "react";
import { COLORS } from "./data";

// ── Barra gradiente no rodape ────────────────────────────────────────────────
export const GradientBar: React.FC = () => (
  <div style={{
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "2.5%",
    background: `linear-gradient(90deg, ${COLORS.green} 0%, ${COLORS.tealBar} 33%, ${COLORS.pink} 66%, ${COLORS.orange} 100%)`,
  }} />
);

// ── Stripe gradiente no topo ─────────────────────────────────────────────────
export const TopStripe: React.FC = () => (
  <div style={{
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: "0.8%",
    background: `linear-gradient(90deg, ${COLORS.green} 0%, ${COLORS.tealBar} 100%)`,
  }} />
);

// ── Titulo + separador amarelo ───────────────────────────────────────────────
export const CardTitle: React.FC<{ title: string; fontSize?: number; marginTop?: number }> = ({
  title,
  fontSize = 72,
  marginTop = 90,
}) => (
  <div style={{ marginTop, marginLeft: 110, marginRight: 110 }}>
    <div style={{
      color: COLORS.white,
      fontWeight: 800,
      fontSize,
      lineHeight: 1.15,
      letterSpacing: "-0.5px",
      textTransform: "uppercase",
      fontFamily: '"Inter", "Segoe UI", sans-serif',
    }}>
      {title}
    </div>
    <div style={{
      marginTop: 20,
      width: 180,
      height: 6,
      backgroundColor: COLORS.yellow,
      borderRadius: 3,
    }} />
  </div>
);

// ── Frase destaque com borda amarela ─────────────────────────────────────────
export const Frase: React.FC<{ text: string; marginTop?: number }> = ({ text, marginTop = 40 }) => (
  <div style={{
    marginTop,
    marginLeft: 110,
    marginRight: 110,
    display: "flex",
    gap: 24,
  }}>
    <div style={{
      width: 8,
      minHeight: "100%",
      backgroundColor: COLORS.yellow,
      borderRadius: 4,
      flexShrink: 0,
    }} />
    <div style={{
      color: COLORS.yellow,
      fontSize: 48,
      fontStyle: "italic",
      lineHeight: 1.4,
      fontFamily: '"Inter", "Segoe UI", sans-serif',
    }}>
      {text}
    </div>
  </div>
);

// ── Card escuro (container de dados) ────────────────────────────────────────
export const DarkCard: React.FC<{
  children: React.ReactNode;
  accentColor?: string;
  style?: React.CSSProperties;
}> = ({ children, accentColor = COLORS.yellow, style }) => (
  <div style={{
    backgroundColor: COLORS.tealDark,
    borderRadius: 22,
    padding: "28px 36px",
    position: "relative",
    overflow: "hidden",
    ...style,
  }}>
    {/* Acento colorido no topo esquerdo */}
    <div style={{
      position: "absolute",
      top: 14,
      left: 14,
      width: 80,
      height: 8,
      backgroundColor: accentColor,
      borderRadius: 4,
    }} />
    {children}
  </div>
);

// ── Wrapper base para todos os cards ────────────────────────────────────────
export const CardBase: React.FC<{
  children: React.ReactNode;
  bgColor?: string;
}> = ({ children, bgColor = COLORS.teal }) => (
  <div style={{
    width: "100%",
    height: "100%",
    backgroundColor: bgColor,
    position: "relative",
    fontFamily: '"Inter", "Segoe UI", sans-serif',
    overflow: "hidden",
  }}>
    <TopStripe />
    {children}
    <GradientBar />
  </div>
);
