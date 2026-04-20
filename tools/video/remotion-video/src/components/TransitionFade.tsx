import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

interface TransitionFadeProps {
  durationInFrames?: number;
  children: React.ReactNode;
}

export const TransitionFade: React.FC<TransitionFadeProps> = ({
  durationInFrames = 15,
  children,
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      {children}
    </AbsoluteFill>
  );
};
