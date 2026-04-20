import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { TitleCard } from "./components/TitleCard";
import { EndCard } from "./components/EndCard";
import { LowerThird } from "./components/LowerThird";
import { TransitionFade } from "./components/TransitionFade";
import { TextOverlay } from "./components/TextOverlay";

// Schema para props (validação)
export const VideoAssemblySchema = z.object({
  clips: z.array(
    z.object({
      id: z.string(),
      src: z.string(),
      durationInSeconds: z.number(),
      transition: z.string().default("cut"),
      label: z.string().default(""),
    })
  ),
  narration: z.string().nullable(),
  titleCard: z.object({
    projeto: z.string(),
    patrocinador: z.string().default(""),
  }),
  endCard: z.object({
    realizacao: z.string(),
    redes: z.string().default(""),
  }),
  lowerThirds: z.array(
    z.object({
      text: z.string(),
      subtitle: z.string().default(""),
      startFrame: z.number(),
      durationFrames: z.number().default(90),
    })
  ),
  totalDurationInSeconds: z.number(),
});

type Props = z.infer<typeof VideoAssemblySchema>;

export const VideoAssembly: React.FC<Props> = ({
  clips,
  narration,
  titleCard,
  endCard,
  lowerThirds,
  totalDurationInSeconds,
}) => {
  const { fps } = useVideoConfig();

  // Calcular frames para cada clip
  let currentFrame = 0;
  const titleDuration = 3 * fps; // 3s para cartela de abertura
  const endDuration = 3 * fps; // 3s para cartela de fechamento
  const transitionDuration = Math.round(0.5 * fps); // 0.5s crossfade

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Narração (áudio ao longo de todo o vídeo) */}
      {narration && (
        <Audio src={staticFile(narration)} volume={1} />
      )}

      {/* Cartela de abertura */}
      <Sequence from={0} durationInFrames={titleDuration}>
        <TitleCard
          projeto={titleCard.projeto}
          patrocinador={titleCard.patrocinador}
        />
      </Sequence>

      {/* Clips de B-roll com transições */}
      {clips.map((clip, index) => {
        const startFrame = titleDuration + clips
          .slice(0, index)
          .reduce((acc, c) => acc + Math.round(c.durationInSeconds * fps), 0);
        const clipDuration = Math.round(clip.durationInSeconds * fps);

        return (
          <Sequence
            key={clip.id}
            from={startFrame}
            durationInFrames={clipDuration}
          >
            {clip.transition === "crossfade" && index > 0 ? (
              <TransitionFade durationInFrames={transitionDuration}>
                {clip.src ? (
                  <OffthreadVideo src={staticFile(clip.src)} />
                ) : (
                  <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }} />
                )}
              </TransitionFade>
            ) : (
              <>
                {clip.src ? (
                  <OffthreadVideo src={staticFile(clip.src)} />
                ) : (
                  <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }} />
                )}
              </>
            )}
          </Sequence>
        );
      })}

      {/* Lower thirds */}
      {lowerThirds.map((lt, index) => (
        <Sequence
          key={`lt-${index}`}
          from={lt.startFrame}
          durationInFrames={lt.durationFrames}
        >
          <LowerThird text={lt.text} subtitle={lt.subtitle} />
        </Sequence>
      ))}

      {/* Cartela de fechamento */}
      <Sequence
        from={Math.round(totalDurationInSeconds * fps) - endDuration}
        durationInFrames={endDuration}
      >
        <EndCard
          realizacao={endCard.realizacao}
          redes={endCard.redes}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
