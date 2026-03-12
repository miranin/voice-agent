import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Voice AI — Алматы",
  description: "Голосовой помощник по мероприятиям в Алматы",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="min-h-dvh flex items-center justify-center">
        {children}
      </body>
    </html>
  );
}
