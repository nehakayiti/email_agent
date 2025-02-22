import { Email } from '@/lib/api';

interface EmailCardProps {
    email: Email;
    onClick: () => void;
}

export function EmailCard({ email, onClick }: EmailCardProps) {
    return (
        <div className="p-4 bg-white rounded-2xl shadow-md border border-gray-200 cursor-pointer" onClick={onClick}>
            <p className="text-sm text-gray-600">From: <span className="font-medium">{email.from_email}</span></p>
            <p className="text-xs text-gray-500">{new Date(email.received_at).toLocaleString()}</p>
            <h2 className="text-lg font-medium text-gray-800 mt-2">{email.subject || '(No subject)'}</h2>
            <p className="text-sm text-gray-700 mt-1">{email.snippet}</p>
            <div className="flex space-x-2 mt-2">
                {email.category && (
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-600 rounded-full">{email.category}</span>
                )}
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-600 rounded-full">
                    {email.is_read ? 'Read' : 'Unread'}
                </span>
            </div>
        </div>
    );
} 