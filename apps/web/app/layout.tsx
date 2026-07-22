import type { Metadata } from "next";
import { IBM_Plex_Serif, IBM_Plex_Sans, Noto_Sans_Devanagari } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { LanguageProvider } from "@/lib/i18n";
import { CommandK } from "@/components/CommandK";

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

const notoDevanagari = Noto_Sans_Devanagari({
  variable: "--font-noto-devanagari",
  subsets: ["devanagari"],
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
      className={`${plexSerif.variable} ${plexSans.variable} ${notoDevanagari.variable}`}
    >
      <body className="min-h-screen bg-paper font-sans text-ink antialiased transition-colors duration-200">
        <LanguageProvider>
          <CommandK />
          <SiteHeader />
          <main className="mx-auto max-w-5xl px-4 sm:px-6">{children}</main>
          <SiteFooter />
        </LanguageProvider>
      </body>
    </html>
  );
}