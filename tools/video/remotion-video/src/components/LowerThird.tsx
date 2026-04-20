import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const NTICS_ACCENT = "#0f3460";

interface LowerThirdProps {
  text: string;
  subtitle?: string;
}

export const LowerThird: React.FC<LowerThirdProps> = ({ text, subtitle }) => {
  const frame = useCurrentFrame();

  // Slide in from left
  const translateX = interpolate(frame, [0, 12], [-400, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out at end
  const opacity = interpolate(frame, [0, 8, 75, 90], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "flex-start",
        padding: "0 40px 120px 40px",
      }}
    >
      <div
        style={{
          transform: `translateX(${translateX}px)`,
          opacity,
        }}
      >
        {/* Barra colorida */}
        <div
          style={{
            width: 4,
            height: subtitle ? 70 : 45,
            backgroundColor: NTICS_ACCENT,
            position: "absolute",
            left: -15,
            top: 5,
            borderRadius: 2,
          }}
        />

        <div
          style={{
            backgroundColor: "rgba(0,0,0,0.75)",
            backdropFilter: "blur(10px)",
            padding: "12px 24px",
            borderRadius: 8,
          }}
        >
          <div
            style={{
              color: "#ffffff",
              fontSize: 28,
              fontWeight: 600,
              lineHeight: 1.3,
            }}
          >
            {text}
          </div>
          {subtitle && (
            <div
              style={{
                color: "rgba(255,255,255,0.6)",
                fontSize: 20,
                fontWeight: 400,
                marginTop: 4,
              }}
            >
              {subtitle}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
