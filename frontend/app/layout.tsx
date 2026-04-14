import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Attune — AI Music Theory Tutor",
  description: "A conversational AI tutor for music theory. Learn intervals, chords, harmony, jazz, and more.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
