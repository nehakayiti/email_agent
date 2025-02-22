import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Email Agent - Smart Email Management",
  description: "Intelligent email organization with AI-powered categorization and importance scoring",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-gray-50">
      <body className={`${inter.className} h-full antialiased`}>
        <div className="min-h-full">
          <Header />
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
