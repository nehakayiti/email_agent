import EmailDetail from '@/components/email-detail';

interface EmailPageProps {
    params: {
        id: string;
    };
}

export default async function EmailPage({ params }: EmailPageProps) {
    // Await params to fix the "params should be awaited before using its properties" error
    const { id } = params;
    return <EmailDetail emailId={id} />;
} 