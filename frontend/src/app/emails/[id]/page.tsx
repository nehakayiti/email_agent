import EmailDetail from '@/components/email-detail';

interface EmailPageProps {
    params: {
        id: string;
    };
}

export default async function EmailPage({ params }: EmailPageProps) {
    // We need to use Promise.resolve to properly handle params in Next.js App Router
    // This fixes the "params should be awaited" error
    const resolvedParams = await Promise.resolve(params);
    const id = resolvedParams.id;
    
    return <EmailDetail emailId={id} />;
} 