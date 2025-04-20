import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowPathIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InboxIcon,
  UserIcon,
  ServerStackIcon,
  CalendarDaysIcon,
  BoltIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

interface SyncHistoryEntry {
  time: Date;
  direction: 'Gmail → EA' | 'EA → Gmail' | 'Bi-directional';
  result: 'success' | 'error';
  emailsSynced: number;
  changes: number;
  error?: string;
}

interface SyncDetails {
  lastSync: Date | null;
  direction: 'Gmail → EA' | 'EA → Gmail' | 'Bi-directional';
  durationSec: number | null;
  emailsSynced: number;
  changesDetected: number;
  changesApplied: number;
  pendingEAChanges: string[]; // e.g., ["3 to Trash", "2 label updates"]
  syncHistory: SyncHistoryEntry[];
  lastError?: string;
  nextScheduledSync?: Date | null;
  lastSyncType: 'Manual' | 'Automatic';
  accountEmail: string;
  backendVersion: string;
  dataFreshnessSec: number | null;
}

interface SyncStatusBarProps {
  status: 'idle' | 'syncing' | 'success' | 'error';
  lastSync: Date | null;
  error?: string | null;
  onSync?: () => void;
  onRetry?: () => void;
  onLogin?: () => void;
  details?: SyncDetails;
}

function isAuthError(error?: string | null): boolean {
  if (!error) return false;
  const msg = error.toLowerCase();
  return msg.includes('auth') || msg.includes('token') || msg.includes('401');
}

export function SyncStatusBar({ status, lastSync, error, onSync, onRetry, onLogin, details, loading, errorMsg }: SyncStatusBarProps & { loading?: boolean; errorMsg?: string }) {
  const [popoverOpen, setPopoverOpen] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);

  // Debug logs
  useEffect(() => {
    if (loading) console.log('SyncStatusBar: loading...');
    if (errorMsg) console.log('SyncStatusBar: error:', errorMsg);
    if (details) console.log('SyncStatusBar: details:', details);
  }, [loading, errorMsg, details]);

  // Close popover on outside click or Escape
  useEffect(() => {
    if (!popoverOpen) return;
    function handleClick(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setPopoverOpen(false);
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setPopoverOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleKey);
    };
  }, [popoverOpen]);

  let statusText = '';
  let statusColor = '';
  let icon = null;
  const authError = isAuthError(error);

  switch (status) {
    case 'syncing':
      statusText = 'Syncing with Gmail…';
      statusColor = 'text-blue-700';
      icon = (
        <svg className="animate-spin h-5 w-5 text-blue-600 mr-2" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
      );
      break;
    case 'success':
      statusText = 'Sync complete';
      statusColor = 'text-green-700';
      icon = (
        <svg className="h-5 w-5 text-green-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      );
      break;
    case 'error':
      statusText = authError ? 'Session expired' : 'Sync failed';
      statusColor = 'text-red-700';
      icon = (
        <svg className="h-5 w-5 text-red-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
      break;
    default:
      statusText = 'Idle';
      statusColor = 'text-gray-600';
      icon = (
        <svg className="h-5 w-5 text-gray-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
        </svg>
      );
  }

  return (
    <div className="relative">
      <button
        className={`flex items-center px-3 py-1 rounded-lg shadow bg-white border ${statusColor} text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500`}
        onClick={() => setPopoverOpen((open) => !open)}
        aria-haspopup="dialog"
        aria-expanded={popoverOpen}
        title="View sync details"
        type="button"
      >
        {icon}
        <span className="mr-2">{statusText}</span>
        {lastSync && (
          <span className="text-xs text-gray-500 ml-1">{formatRelativeTime(lastSync)}</span>
        )}
      </button>
      {popoverOpen && (
        <SyncDetailsPopover
          details={details}
          onClose={() => setPopoverOpen(false)}
          status={status}
          error={error}
          onSync={onSync}
          onRetry={onRetry}
          onLogin={onLogin}
          popoverRef={popoverRef as React.RefObject<HTMLDivElement>}
          loading={loading}
          errorMsg={errorMsg}
        />
      )}
    </div>
  );
}

function formatRelativeTime(date: Date) {
  const now = new Date();
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (diff < 60) return `${diff} sec${diff !== 1 ? 's' : ''} ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)} min${Math.floor(diff / 60) !== 1 ? 's' : ''} ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hour${Math.floor(diff / 3600) !== 1 ? 's' : ''} ago`;
  return `${Math.floor(diff / 86400)} day${Math.floor(diff / 86400) !== 1 ? 's' : ''} ago`;
}

function SyncDetailsPopover({ details, onClose, status, error, onSync, onRetry, onLogin, popoverRef, loading, errorMsg }: {
  details?: any;
  onClose: () => void;
  status: 'idle' | 'syncing' | 'success' | 'error';
  error?: string | null;
  onSync?: () => void;
  onRetry?: () => void;
  onLogin?: () => void;
  popoverRef: React.RefObject<HTMLDivElement>;
  loading?: boolean;
  errorMsg?: string;
}) {
  if (loading) {
    return (
      <div ref={popoverRef} className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4 flex items-center justify-center" role="dialog" tabIndex={-1}>
        <span className="text-gray-500">Loading sync details…</span>
      </div>
    );
  }
  if (errorMsg) {
    return (
      <div ref={popoverRef} className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4 flex items-center justify-center" role="dialog" tabIndex={-1}>
        <span className="text-red-600">{errorMsg}</span>
      </div>
    );
  }
  if (!details) {
    return (
      <div ref={popoverRef} className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4 flex items-center justify-center" role="dialog" tabIndex={-1}>
        <span className="text-gray-500">No sync details available.</span>
      </div>
    );
  }
  const isAuthError = error && (error.toLowerCase().includes('auth') || error.toLowerCase().includes('token') || error.toLowerCase().includes('401'));
  return (
    <div ref={popoverRef} className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4" role="dialog" tabIndex={-1}>
      <div className="flex justify-between items-center mb-2">
        <span className="font-semibold text-gray-800 flex items-center gap-2">
          <ArrowPathIcon className="h-5 w-5 text-blue-500" /> Sync Details
        </span>
      </div>
      <ul className="text-sm text-gray-700 space-y-2 divide-y divide-gray-100 pb-2">
        <li className="flex items-center gap-2 pt-2">
          <ArrowPathIcon className="h-4 w-4 text-blue-500" />
          <span><strong>Direction:</strong> {details.direction}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <ClockIcon className="h-4 w-4 text-gray-500" />
          <span><strong>Last sync:</strong> {details.lastSync ? formatRelativeTime(details.lastSync) : 'Never'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <BoltIcon className="h-4 w-4 text-yellow-500" />
          <span><strong>Duration:</strong> {details.durationSec != null ? `${details.durationSec.toFixed(1)} sec` : '-'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <InboxIcon className="h-4 w-4 text-green-500" />
          <span><strong>Emails synced:</strong> {details.emailsSynced ?? '-'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <InformationCircleIcon className="h-4 w-4 text-blue-400" />
          <span><strong>Changes detected:</strong> {details.changesDetected ?? '-'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <ArrowUpTrayIcon className="h-4 w-4 text-indigo-500" />
          <span><strong>Changes applied:</strong> {details.changesApplied ?? '-'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <ArrowDownTrayIcon className="h-4 w-4 text-indigo-500" />
          <span><strong>Pending EA changes:</strong> {details.pendingEAChanges?.length ? details.pendingEAChanges.join(', ') : 'None'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <CalendarDaysIcon className="h-4 w-4 text-gray-500" />
          <span><strong>Next scheduled sync:</strong> {details.nextScheduledSync ? formatRelativeTime(details.nextScheduledSync) : 'N/A'}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <BoltIcon className="h-4 w-4 text-yellow-500" />
          <span><strong>Last sync type:</strong> {details.lastSyncType}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <UserIcon className="h-4 w-4 text-gray-700" />
          <span><strong>Account:</strong> {details.accountEmail}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <ServerStackIcon className="h-4 w-4 text-gray-700" />
          <span><strong>Backend version:</strong> {details.backendVersion}</span>
        </li>
        <li className="flex items-center gap-2 pt-2">
          <ClockIcon className="h-4 w-4 text-gray-500" />
          <span><strong>Data freshness:</strong> {details.dataFreshnessSec != null ? formatRelativeTime(new Date(Date.now() - (details.dataFreshnessSec * 1000))) : '-'}</span>
        </li>
      </ul>
      {/* Error details */}
      {details.lastError && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-4 w-4 mt-0.5 text-red-500" />
          <span><strong>Last error:</strong> {details.lastError}</span>
        </div>
      )}
      {/* Sync history */}
      {details.syncHistory?.length > 0 && (
        <div className="mt-3">
          <div className="font-semibold text-gray-700 mb-1 flex items-center gap-2">
            <ArrowPathIcon className="h-4 w-4 text-blue-500" /> Sync History
          </div>
          <ul className="text-xs text-gray-600 space-y-1 max-h-24 overflow-y-auto">
            {details.syncHistory.slice(0, 3).map((entry: any, idx: number) => (
              <li key={idx} className="flex items-center gap-2">
                <ClockIcon className="h-3 w-3 text-gray-400" />
                <span>{formatRelativeTime(entry.time)}</span>
                <span className="ml-1">{entry.direction}</span>
                <span className={`ml-1 ${entry.result === 'success' ? 'text-green-600' : 'text-red-600'}`}>{entry.result}</span>
                <span className="ml-1">{entry.emailsSynced} emails</span>
                <span className="ml-1">{entry.changes} changes</span>
                {entry.error && <span className="ml-1 text-red-500">{entry.error}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
      {/* Footer: Sync Now/Retry/Log In button */}
      <div className="mt-4 flex justify-end">
        {status !== 'syncing' && !isAuthError && onSync && (
          <button
            className="px-4 py-2 rounded bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition"
            onClick={onSync}
          >
            Sync Now
          </button>
        )}
        {status === 'syncing' && (
          <button
            className="px-4 py-2 rounded bg-blue-400 text-white text-sm font-medium cursor-not-allowed flex items-center gap-2"
            disabled
          >
            <ArrowPathIcon className="h-4 w-4 animate-spin" /> Syncing…
          </button>
        )}
        {status === 'error' && !isAuthError && onRetry && (
          <button
            className="px-4 py-2 rounded bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition ml-2"
            onClick={onRetry}
          >
            Retry
          </button>
        )}
        {status === 'error' && isAuthError && onLogin && (
          <button
            className="px-4 py-2 rounded bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition ml-2"
            onClick={onLogin}
          >
            Log In
          </button>
        )}
      </div>
    </div>
  );
} 