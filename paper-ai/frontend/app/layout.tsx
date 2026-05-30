import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI论文格式修改Agent",
  description: "Upload a paper and let the agent format, review, and export the final Word file.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
