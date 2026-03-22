import type { TailnetDevice } from "@/types/tailnet";

type Props = {
  devices: TailnetDevice[];
};

/** Lightweight CSS 3D “devices in space” — no WebGL; pairs with the Mermaid tab. */
export function TailnetOrbit({ devices }: Props) {
  const n = Math.max(devices.length, 1);
  const r = 140;

  return (
    <div className="relative">
      <style>{`
        @keyframes orbit-rotate {
          from { transform: rotateX(58deg) rotateZ(-12deg) rotateY(0deg); }
          to { transform: rotateX(58deg) rotateZ(-12deg) rotateY(360deg); }
        }
        @keyframes node-float {
          0%, 100% { transform: translateZ(0px) scale(1); }
          50% { transform: translateZ(12px) scale(1.03); }
        }
        .orbit-scene {
          perspective: 1100px;
          perspective-origin: 50% 40%;
        }
        .orbit-world {
          transform-style: preserve-3d;
          animation: orbit-rotate 90s linear infinite;
        }
        .orbit-node {
          transform-style: preserve-3d;
          animation: node-float 4s ease-in-out infinite;
        }
      `}</style>

      <div className="orbit-scene relative h-[min(480px,70vh)] w-full overflow-hidden rounded-xl border border-slate-800 bg-[radial-gradient(ellipse_at_center,_#1e1b4b_0%,_#0f172a_45%,_#020617_100%)]">
        <div className="pointer-events-none absolute inset-0 opacity-40 [background-image:radial-gradient(1px_1px_at_20%_30%,#fff,transparent),radial-gradient(1px_1px_at_60%_70%,#fff,transparent),radial-gradient(1px_1px_at_80%_20%,#fff,transparent)]" />

        <div className="absolute left-1/2 top-[42%] h-64 w-64 -translate-x-1/2 -translate-y-1/2">
          <div className="orbit-world relative h-full w-full">
            <div
              className="absolute left-1/2 top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-500/90 shadow-[0_0_24px_rgba(59,130,246,0.8)] ring-2 ring-blue-300/50"
              title="Tailnet"
            />
            {devices.map((d, i) => {
              const angle = (2 * Math.PI * i) / n;
              const x = Math.cos(angle) * r;
              const z = Math.sin(angle) * r;
              const y = (d.online ? -1 : 1) * 18;
              const delay = `${(i * 0.35) % 4}s`;
              return (
                <div
                  key={d.id ?? `${d.name}-${i}`}
                  className="orbit-node absolute left-1/2 top-1/2 w-0"
                  style={{
                    transform: `translate3d(${x}px, ${y}px, ${z}px)`,
                    animationDelay: delay,
                  }}
                >
                  <div
                    className={`relative -translate-x-1/2 -translate-y-1/2 whitespace-nowrap rounded-lg border px-2.5 py-1.5 text-xs font-medium shadow-lg backdrop-blur-sm ${
                      d.online
                        ? "border-emerald-500/40 bg-emerald-950/80 text-emerald-100"
                        : "border-rose-500/35 bg-rose-950/70 text-rose-100"
                    }`}
                    title={d.name ?? d.id ?? "device"}
                  >
                    <span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-current opacity-80" />
                    {(d.name ?? d.id ?? `device-${i}`).slice(0, 28)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <p className="absolute bottom-3 left-0 right-0 text-center text-[11px] text-slate-500">
          Decorative layout — not geographic. Use the Mermaid tab for topology-style detail.
        </p>
      </div>
    </div>
  );
}
