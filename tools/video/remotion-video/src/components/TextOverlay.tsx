import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

interface TextOverlayProps {
  text: string;
  fontSize?: number;
  position?: "center" | "top" | "bottom";
  color?: string;
}

export const TextOverlay: React.FC<TextOverlayProps> = ({
  text,
  fontSize = 48,
  position = "center",
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 10, 80, 90], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(frame, [0, 12], [0.95, 1], {
    extrapolateRight: "clamp",
  });

  const justifyContent =
    position === "top" ? "flex-start" :
    position === "bottom" ? "flex-end" : "center";

  const padding =
    position === "top" ? "120px 40px 40px" :
    position === "bottom" ? "40px 40px 120px" : "40px";

  return (
    <AbsoluteFill
      style={{
        justifyContent,
        alignItems: "center",
        padding,
      }}
    >
      <div
        style={{
          color,
          fontSize,
          fontWeight: 700,
          textAlign: "center",
          textShadow: "0 2px 8px rgba(0,0,0,0.5)",
          opacity,
          transform: `scale(${scale})`,
          maxWidth: "85%",
          lineHeight: 1.3,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
