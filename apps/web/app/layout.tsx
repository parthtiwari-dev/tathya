import type { Metadata } from "next";
import { IBM_Plex_Serif, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";

const plexSerif = IBM_Plex_Serif({
  variable: "--font-plex-serif",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const plexSans = IBM_Plex_Sans({
  variable: "--font-plex-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Tathya — तथ्य",
  description:
    "An autonomous, non-partisan civic record of the Government of India. We don't tell you who's right. We record what was said, who said it, and what's verifiable.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${plexSerif.variable} ${plexSans.variable}`}
    >
      <body className="min-h-screen bg-paper font-sans text-ink antialiased transition-colors duration-200">
        <SiteHeader />
        <main className="mx-auto max-w-5xl px-6">{children}</main>
        <footer className="mx-auto mt-16 max-w-5xl border-t border-border px-6 py-8 text-xs text-ink-muted">
          Tathya is an autonomous record, not a news outlet. No topic is chosen by hand. Every claim links to its source.
        </footer>
      </body>
    </html>
  );
}
