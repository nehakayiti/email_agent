import EmailDetail from '@/components/email-detail';

interface EmailPageProps {
    params: {
        id: string;
    };
}

export default function EmailPage({ params }: EmailPageProps) {
    return <EmailDetail emailId={params.id} />;
} 