import EmailDetail from '@/components/email-detail';

interface EmailPageProps {
    params: Promise<{
        id: string;
    }>;
}

export default async function EmailPage({ params }: EmailPageProps) {
    // In Next.js 15, params is a Promise that needs to be awaited
    const resolvedParams = await params;
    const id = resolvedParams.id;
    
    return <EmailDetail emailId={id} />;
} 