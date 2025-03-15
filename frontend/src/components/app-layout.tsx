'use client';

import { ReactNode } from 'react';
import MainLayout from './layout/main-layout';

interface AppLayoutProps {
  children: ReactNode;
  userName?: string;
}

export default function AppLayout({ children, userName = 'User' }: AppLayoutProps) {
  return <MainLayout>{children}</MainLayout>;
} 