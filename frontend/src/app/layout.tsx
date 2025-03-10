import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import MainLayout from "@/components/layout/main-layout";
import { CategoryProvider } from "@/lib/category-context";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Email Agent",
  description: "Your intelligent email assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CategoryProvider>
          <MainLayout>{children}</MainLayout>
        </CategoryProvider>
      </body>
    </html>
  );
}
