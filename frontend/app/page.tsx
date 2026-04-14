"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

// ── Quiz Data ─────────────────────────────────────────────────────────────────
const QUIZ_QUESTIONS = [
  {
    id: 1,
    question: "What notes make up a C major triad?",
    options: ["C, D, G", "C, E, G", "C, Eb, G", "C, E, A"],
    correct: 1,
    scores: [0, 1, 0, 0],
  },
  {
    id: 2,
    question: "What is the interval between C and F#?",
    options: ["A perfect 5th", "A major 3rd", "A tritone", "A minor 7th"],
    correct: 2,
    scores: [0, 0, 2, 0],
  },
  {
    id: 3,
    question: "Which mode is built on the 2nd degree of the major scale?",
    options: ["Phrygian", "Lydian", "Dorian", "Mixolydian"],
    correct: 2,
    scores: [0, 0, 2, 0],
  },
  {
    id: 4,
    question: "In a ii-V-I in C major, what are the three chords?",
    options: [
      "Dm7 – G7 – Cmaj7",
      "Am7 – D7 – Gmaj7",
      "Em7 – A7 – Dmaj7",
      "Fm7 – Bb7 – Ebmaj7",
    ],
    correct: 0,
    scores: [3, 0, 0, 0],
  },
  {
    id: 5,
    question: "A tritone substitution replaces a dominant 7th chord with...",
    options: [
      "The chord a whole step below",
      "The relative minor chord",
      "A dominant 7th chord a tritone away",
      "A diminished 7th chord",
    ],
    correct: 2,
    scores: [0, 0, 4, 0],
  },
];

const SCORE_TO_LEVEL: { min: number; max: number; level: string }[] = [
  { min: 0,  max: 2,  level: "beginner" },
  { min: 3,  max: 6,  level: "intermediate" },
  { min: 7,  max: 12, level: "advanced" },
];

const LEVEL_CONFIG = {
  beginner: {
    icon: "🌱",
    label: "Beginner",
    badgeVariant: "success" as const,
    dotClass: "bg-emerald-400",
    ringClass: "ring-emerald-500/30",
    cardClass: "border-emerald-500/25 bg-emerald-500/5",
    message: "We'll start with the fundamentals and build from there — no jargon, just music.",
  },
  intermediate: {
    icon: "🎸",
    label: "Intermediate",
    badgeVariant: "warning" as const,
    dotClass: "bg-amber-400",
    ringClass: "ring-amber-500/30",
    cardClass: "border-amber-500/25 bg-amber-500/5",
    message: "You've got the basics. Let's dig into harmony, modes, and why music actually works.",
  },
  advanced: {
    icon: "🎷",
    label: "Advanced",
    badgeVariant: "default" as const,
    dotClass: "bg-primary",
    ringClass: "ring-primary/30",
    cardClass: "border-primary/25 bg-primary/5",
    message: "You know your stuff. Let's talk reharmonization, voice leading, Coltrane changes — peer to peer.",
  },
};

type Mode = "landing" | "quiz" | "result";

export default function Home() {
  const router = useRouter();
  const [mode, setMode]               = useState<Mode>("landing");
  const [currentQ, setCurrentQ]       = useState(0);
  const [selected, setSelected]       = useState<number | null>(null);
  const [answered, setAnswered]       = useState(false);
  const [totalScore, setTotalScore]   = useState(0);
  const [detectedLevel, setDetectedLevel] = useState<string>("beginner");
  const [loading, setLoading]         = useState(false);

  function getLevel(score: number): string {
    return SCORE_TO_LEVEL.find((r) => score >= r.min && score <= r.max)?.level ?? "beginner";
  }

  function handleAnswer(optionIndex: number) {
    if (answered) return;
    setSelected(optionIndex);
    setAnswered(true);
    const q = QUIZ_QUESTIONS[currentQ];
    const newScore = totalScore + (q.scores[optionIndex] ?? 0);
    setTotalScore(newScore);

    setTimeout(() => {
      if (currentQ + 1 < QUIZ_QUESTIONS.length) {
        setCurrentQ(currentQ + 1);
        setSelected(null);
        setAnswered(false);
      } else {
        const level = getLevel(newScore);
        setDetectedLevel(level);
        setMode("result");
      }
    }, 750);
  }

  async function startSession(level: string) {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tutor/session/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skill_level: level }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();

      localStorage.setItem("attune_session_id", data.session_id);
      localStorage.setItem("attune_skill_level", level);

      router.push(`/chat?session=${data.session_id}&level=${level}&intro=${encodeURIComponent(data.message)}`);
    } catch {
      setLoading(false);
    }
  }

  // ── Landing ────────────────────────────────────────────────────────────────
  if (mode === "landing") {
    return (
      <main className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
        {/* Aurora background */}
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
        <div className="aurora-blob aurora-blob-3" />

        <div className="relative z-10 w-full max-w-md animate-fade-in">
          {/* Label */}
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-6 text-center">
            AI Music Theory Tutor
          </p>

          {/* Headline */}
          <div className="text-center mb-10">
            <div className="text-4xl mb-5 opacity-90">𝄞</div>
            <h1 className="text-5xl font-extrabold tracking-tight leading-[1.08] mb-4">
              Learn music theory.
              <br />
              <span className="text-primary">Finally.</span>
            </h1>
            <p className="text-muted-foreground text-base leading-relaxed max-w-xs mx-auto">
              Ask anything. Hear song examples. Get better at music — at your own pace.
            </p>
          </div>

          {/* Primary CTA */}
          <div className="space-y-3 mb-6">
            <Button
              onClick={() => setMode("quiz")}
              size="lg"
              className="w-full text-base font-semibold"
            >
              Take the placement quiz →
            </Button>
            <p className="text-center text-muted-foreground text-xs">
              5 questions · 2 minutes · we'll place you automatically
            </p>
          </div>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-5">
            <div className="flex-1 h-px bg-border" />
            <span className="text-muted-foreground text-xs">or jump in as</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Level picker */}
          <div className="space-y-2">
            {(Object.entries(LEVEL_CONFIG) as [string, typeof LEVEL_CONFIG.beginner][]).map(([level, cfg]) => (
              <button
                key={level}
                onClick={() => startSession(level)}
                disabled={loading}
                className={cn(
                  "w-full text-left flex items-center gap-3 px-4 py-3 rounded-xl",
                  "border border-border bg-card hover:bg-surface hover:border-primary/30",
                  "transition-all duration-150 group disabled:opacity-50"
                )}
              >
                <span className={cn("w-2 h-2 rounded-full shrink-0", cfg.dotClass)} />
                <span className="text-sm font-medium text-foreground capitalize">{cfg.label}</span>
                <span className="ml-auto text-muted-foreground text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                  Start →
                </span>
              </button>
            ))}
          </div>

          <p className="mt-10 text-muted-foreground text-xs text-center">
            Powered by Claude · Part of{" "}
            <a
              href="https://www.seanwa.com/lab"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline underline-offset-2"
            >
              Sean's Lab
            </a>
          </p>
        </div>
      </main>
    );
  }

  // ── Quiz ───────────────────────────────────────────────────────────────────
  if (mode === "quiz") {
    const q = QUIZ_QUESTIONS[currentQ];
    const progress = (currentQ / QUIZ_QUESTIONS.length) * 100;

    return (
      <main className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
        <div className="aurora-blob aurora-blob-1" style={{ opacity: 0.25 }} />
        <div className="aurora-blob aurora-blob-2" style={{ opacity: 0.2 }} />

        <div className="relative z-10 w-full max-w-lg animate-fade-in">
          {/* Header */}
          <div className="flex items-center gap-2.5 mb-6">
            <span className="text-xl">𝄞</span>
            <span className="text-sm font-medium text-muted-foreground">Placement Quiz</span>
            <Badge variant="muted" className="ml-auto">
              {currentQ + 1} / {QUIZ_QUESTIONS.length}
            </Badge>
          </div>

          {/* Progress bar */}
          <div className="w-full h-1 bg-secondary rounded-full mb-8 overflow-hidden">
            <div
              className="h-1 bg-primary rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Question card */}
          <div className="rounded-xl border border-border bg-card p-6 mb-4">
            <h2 className="text-lg font-semibold leading-snug text-foreground mb-6">
              {q.question}
            </h2>

            <div className="space-y-2.5">
              {q.options.map((option, i) => {
                const isCorrect = i === q.correct;
                const isSelected = i === selected;
                const isWrong = answered && isSelected && !isCorrect;
                const isRight = answered && isCorrect;
                const isFaded = answered && !isCorrect && !isSelected;

                return (
                  <button
                    key={i}
                    onClick={() => handleAnswer(i)}
                    disabled={answered}
                    className={cn(
                      "w-full text-left flex items-center gap-3 px-4 py-3 rounded-lg border text-sm",
                      "transition-all duration-150",
                      !answered && "border-border bg-surface hover:border-primary/40 hover:bg-secondary",
                      isRight  && "border-emerald-500/50 bg-emerald-500/10 text-emerald-300",
                      isWrong  && "border-red-500/40 bg-red-500/10 text-red-300",
                      isFaded  && "border-border bg-surface opacity-40",
                    )}
                  >
                    <span className="text-xs font-bold text-muted-foreground w-4 shrink-0">
                      {String.fromCharCode(65 + i)}
                    </span>
                    <span className="text-foreground">{option}</span>
                    {isRight && <span className="ml-auto text-emerald-400">✓</span>}
                    {isWrong && <span className="ml-auto text-red-400">✗</span>}
                  </button>
                );
              })}
            </div>
          </div>

          <button
            onClick={() => { setMode("landing"); setCurrentQ(0); setTotalScore(0); setSelected(null); setAnswered(false); }}
            className="text-muted-foreground text-xs hover:text-foreground transition-colors"
          >
            ← Back
          </button>
        </div>
      </main>
    );
  }

  // ── Result ─────────────────────────────────────────────────────────────────
  const cfg = LEVEL_CONFIG[detectedLevel as keyof typeof LEVEL_CONFIG];

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
      <div className="aurora-blob aurora-blob-1" style={{ opacity: 0.3 }} />
      <div className="aurora-blob aurora-blob-2" style={{ opacity: 0.2 }} />

      <div className="relative z-10 w-full max-w-sm animate-fade-in">
        {/* Label */}
        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-6 text-center">
          Your Result
        </p>

        {/* Result card */}
        <div className={cn("rounded-xl border p-6 mb-6 text-center", cfg.cardClass)}>
          <div className="text-4xl mb-3">{cfg.icon}</div>
          <Badge variant={cfg.badgeVariant} className="mb-3">
            {cfg.label}
          </Badge>
          <p className="text-sm text-muted-foreground leading-relaxed mt-3">
            {cfg.message}
          </p>
          <p className="text-xs text-muted-foreground/60 mt-3">
            Score: {totalScore} / 12
          </p>
        </div>

        {/* CTA */}
        <Button
          onClick={() => startSession(detectedLevel)}
          disabled={loading}
          size="lg"
          className="w-full mb-4 text-base font-semibold"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              Starting…
            </span>
          ) : (
            "Start learning →"
          )}
        </Button>

        {/* Level override */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          {(Object.entries(LEVEL_CONFIG) as [string, typeof cfg][]).map(([level, c]) => (
            <button
              key={level}
              onClick={() => startSession(level)}
              disabled={loading || level === detectedLevel}
              className={cn(
                "flex flex-col items-center gap-1 py-2.5 px-2 rounded-lg border text-xs font-medium transition-all",
                level === detectedLevel
                  ? "border-primary/40 text-primary bg-primary/10 cursor-default"
                  : "border-border text-muted-foreground hover:border-primary/30 hover:text-foreground"
              )}
            >
              <span>{c.icon}</span>
              <span>{c.label}</span>
            </button>
          ))}
        </div>
        <p className="text-center text-muted-foreground text-xs">
          Override your level above if needed
        </p>
      </div>
    </main>
  );
}
