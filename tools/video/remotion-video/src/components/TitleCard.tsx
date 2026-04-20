import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// Cores NTICS (do brand-book)
const NTICS_BLUE = "#1a1a2e";
const NTICS_ACCENT = "#0f3460";
const NTICS_TEXT = "#ffffff";

interface TitleCardProps {
  projeto: string;
  patrocinador?: string;
}

export const TitleCard: React.FC<TitleCardProps> = ({
  projeto,
  patrocinador,
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 15, 75, 90], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(frame, [5, 20], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const subtitleOpacity = interpolate(frame, [20, 35], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${NTICS_BLUE} 0%, ${NTICS_ACCENT} 100%)`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: 60,
        opacity,
      }}
    >
      <div
        style={{
          color: NTICS_TEXT,
          fontSize: 64,
          fontWeight: 700,
          textAlign: "center",
          lineHeight: 1.2,
          transform: `translateY(${titleY}px)`,
          maxWidth: "90%",
        }}
      >
        {projeto}
      </div>

      {patrocinador && (
        <div
          style={{
            color: "rgba(255,255,255,0.7)",
            fontSize: 32,
            fontWeight: 400,
            marginTop: 30,
            opacity: subtitleOpacity,
            textAlign: "center",
          }}
        >
          {patrocinador}
        </div>
      )}
    </AbsoluteFill>
  );
};
