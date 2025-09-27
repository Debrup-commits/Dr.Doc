import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { ChatProvider } from "@/contexts/ChatContext";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ChatSidebar from "@/components/ChatSidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ASI:One Agentic AI",
  description: "Build your next AI Agent using ASI:One to enable communication and collaboration with AI Agents.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
<<<<<<< HEAD
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-900 text-slate-100`}
=======
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white dark:bg-slate-900 text-gray-900 dark:text-gray-100`}
>>>>>>> 1d392c7 (mcp crude implementation)
      >
        <ThemeProvider>
          <ChatProvider>
            <Header />
<<<<<<< HEAD
            <main className="pt-16">
=======
            <main className="pt-20">
>>>>>>> 1d392c7 (mcp crude implementation)
              {children}
            </main>
            <Footer />
            <ChatSidebar />
          </ChatProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
