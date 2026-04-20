import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const NTICS_BLUE = "#1a1a2e";
const NTICS_ACCENT = "#0f3460";

interface EndCardProps {
  realizacao: string;
  redes?: string;
}

export const EndCard: React.FC<EndCardProps> = ({ realizacao, redes }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  const scale = interpolate(frame, [0, 20], [0.9, 1], {
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
          color: "rgba(255,255,255,0.6)",
          fontSize: 24,
          fontWeight: 400,
          textTransform: "uppercase",
          letterSpacing: 4,
          marginBottom: 20,
        }}
      >
        Realização
      </div>

      <div
        style={{
          color: "#ffffff",
          fontSize: 56,
          fontWeight: 700,
          textAlign: "center",
          transform: `scale(${scale})`,
        }}
      >
        {realizacao}
      </div>

      {redes && (
        <div
          style={{
            color: "rgba(255,255,255,0.5)",
            fontSize: 28,
            marginTop: 40,
          }}
        >
          {redes}
        </div>
      )}
    </AbsoluteFill>
  );
};
