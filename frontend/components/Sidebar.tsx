"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export const TOPICS = [
  { label: "Intervals",     icon: "↕", prompt: "Teach me about intervals — what they are and how to hear them." },
  { label: "Scales & Modes", icon: "〜", prompt: "Walk me through the major scale and how modes are derived from it." },
  { label: "Chords",        icon: "♩", prompt: "Explain how chords are built, from triads to seventh chords." },
  { label: "Harmony",       icon: "♫", prompt: "Explain functional harmony — how chords relate and create tension and resolution." },
  { label: "ii-V-I",        icon: "③", prompt: "Break down the ii-V-I progression and why it's so important in jazz." },
  { label: "Jazz Theory",   icon: "♭", prompt: "Give me an overview of jazz harmony — what separates it from classical or pop harmony." },
  { label: "Blues",         icon: "⚡", prompt: "Explain the blues — the form, the scale, and the feel." },
  { label: "Song Examples", icon: "🎵", prompt: "Give me some great song examples that demonstrate interesting music theory." },
];

const LEVEL_CONFIG: Record<string, { dot: string; label: string; text: string }> = {
  beginner:     { dot: "bg-emerald-400", label: "Beginner",     text: "text-emerald-400" },
  intermediate: { dot: "bg-amber-400",   label: "Intermediate", text: "text-amber-400"   },
  advanced:     { dot: "bg-primary",     label: "Advanced",     text: "text-accent-foreground" },
};

interface SidebarProps {
  level: string;
  onTopicSelect: (prompt: string) => void;
  onNewSession: () => void;
  onPractice: () => void;
  practiceMode: boolean;
  coveredTopics?: string[];
  sessionStart?: string;
  messageCount?: number;
  onClose?: () => void;
}

export default function Sidebar({
  level,
  onTopicSelect,
  onNewSession,
  onPractice,
  practiceMode,
  coveredTopics = [],
  sessionStart,
  messageCount = 0,
  onClose,
}: SidebarProps) {
  const lvl = LEVEL_CONFIG[level] ?? LEVEL_CONFIG.beginner;
  const coveredSet = new Set(coveredTopics);

  return (
    <aside className="flex flex-col h-full w-64 shrink-0 bg-card border-r border-border">

      {/* ── Logo ──────────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2.5">
          <span className="text-xl text-primary leading-none">𝄞</span>
          <span className="font-semibold text-sm tracking-tight text-foreground">Attune</span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        )}
      </div>

      {/* ── Session meta ──────────────────────────────────────────────────── */}
      <div className="px-4 py-4 border-b border-border space-y-2">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          Session
        </p>
        <div className="flex items-center gap-2">
          <div className={cn("w-1.5 h-1.5 rounded-full shrink-0", lvl.dot)} />
          <span className={cn("text-sm font-medium", lvl.text)}>{lvl.label}</span>
        </div>
        <div className="space-y-0.5">
          {sessionStart && (
            <p className="text-xs text-muted-foreground/70">Started {sessionStart}</p>
          )}
          {messageCount > 0 && (
            <p className="text-xs text-muted-foreground/70">{messageCount} exchange{messageCount !== 1 ? "s" : ""}</p>
          )}
        </div>
      </div>

      {/* ── Practice mode toggle ──────────────────────────────────────────── */}
      <div className="px-4 py-3 border-b border-border">
        <button
          onClick={() => { onPractice(); onClose?.(); }}
          className={cn(
            "w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border text-sm font-medium transition-all",
            practiceMode
              ? "border-primary/40 bg-primary/10 text-accent-foreground"
              : "border-border bg-transparent text-muted-foreground hover:text-foreground hover:border-border/80 hover:bg-secondary"
          )}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <span>{practiceMode ? "Exit Practice Mode" : "Practice Mode"}</span>
          {practiceMode && (
            <span className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded bg-primary/20 text-primary uppercase tracking-wider">
              ON
            </span>
          )}
        </button>
      </div>

      {/* ── Topics ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-3 py-4">
        <div className="flex items-center justify-between px-2 mb-3">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
            Explore Topics
          </p>
          {coveredTopics.length > 0 && (
            <span className="text-[10px] font-semibold text-primary">
              {coveredTopics.length}/{TOPICS.length}
            </span>
          )}
        </div>

        <nav className="space-y-0.5">
          {TOPICS.map((topic) => {
            const covered = coveredSet.has(topic.label);
            return (
              <button
                key={topic.label}
                onClick={() => { onTopicSelect(topic.prompt); onClose?.(); }}
                className={cn(
                  "w-full text-left flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm",
                  "transition-all duration-150 group",
                  covered
                    ? "text-accent-foreground bg-primary/8 hover:bg-primary/12"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                )}
              >
                <span className={cn("w-5 text-center text-base shrink-0 transition-opacity", covered ? "opacity-100" : "opacity-50 group-hover:opacity-80")}>
                  {topic.icon}
                </span>
                <span className="flex-1 truncate">{topic.label}</span>
                {covered && (
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                    strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-primary">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <div className="px-4 py-4 border-t border-border space-y-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onNewSession}
          className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New session
        </Button>
        <p className="text-[10px] text-muted-foreground/40 text-center">Powered by Claude</p>
      </div>
    </aside>
  );
}
