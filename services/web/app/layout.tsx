import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NahaLabs Field Intelligence",
  description: "Field-to-action operational intelligence demonstrator",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-ZA">
      <body>{children}</body>
    </html>
  );
}
