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
import { updateSyncCadence } from '@/lib/api';
import { toast } from 'react-hot-toast';

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
  // Cadence state (in minutes)
  const [cadence, setCadenceState] = useState<number>(() => {
    if (typeof window !== 'undefined') {
      const stored = window.localStorage?.getItem('syncCadence');
      return stored ? Number(stored) : 3;
    }
    return 3;
  });
  const setCadence = async (n: number) => {
    try {
      const result = await updateSyncCadence(n);
      if (result && typeof result.sync_cadence === 'number') {
        setCadenceState(result.sync_cadence);
      } else {
        throw new Error('Failed to update sync cadence');
      }
    } catch (err: any) {
      toast.error(err?.message || 'Failed to update sync cadence');
    }
  };
  // Next scheduled sync timestamp
  const [nextSync, setNextSync] = useState<Date | null>(null);
  // Track if sync is in progress
  const [isSyncing, setIsSyncing] = useState(false);
  // Track last sync request time (local, not from backend)
  const [lastSyncRequestedAt, setLastSyncRequestedAt] = useState<number>(Date.now());
  // Track last sync type
  const [lastSyncType, setLastSyncType] = useState<'Manual' | 'Automatic'>('Manual');
  // Live countdown state
  const [countdown, setCountdown] = useState<string>('');

  // Timer effect for auto sync (fixed logic)
  useEffect(() => {
    if (!onSync) return;
    if (isSyncing || status === 'syncing') return;
    if (cadence === 0) return; // Prevent infinite loop when sync is off
    const now = Date.now();
    const msSinceLast = now - lastSyncRequestedAt;
    const msUntilNext = Math.max(0, cadence * 60 * 1000 - msSinceLast);
    setNextSync(new Date(now + msUntilNext));
    const timer = setTimeout(() => {
      setIsSyncing(true);
      setLastSyncRequestedAt(Date.now());
      setLastSyncType('Automatic');
      onSync();
    }, msUntilNext);
    return () => clearTimeout(timer);
  }, [cadence, lastSyncRequestedAt, onSync, isSyncing, status]);

  // Live countdown effect
  useEffect(() => {
    if (!nextSync) {
      setCountdown('N/A');
      return;
    }
    const updateCountdown = () => {
      const now = new Date();
      const diff = Math.floor((nextSync.getTime() - now.getTime()) / 1000);
      if (diff <= 0) {
        setCountdown('Syncing now');
      } else if (diff < 60) {
        setCountdown(`${diff} second${diff !== 1 ? 's' : ''}`);
      } else if (diff < 3600) {
        setCountdown(`${Math.floor(diff / 60)} minute${Math.floor(diff / 60) !== 1 ? 's' : ''} ${diff % 60 ? (diff % 60) + ' sec' : ''}`);
      } else {
        setCountdown(`${Math.floor(diff / 3600)} hour${Math.floor(diff / 3600) !== 1 ? 's' : ''}`);
      }
    };
    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [nextSync]);

  // Reset isSyncing after sync completes
  useEffect(() => {
    if (status !== 'syncing') setIsSyncing(false);
  }, [status]);

  // Persist cadence to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage?.setItem('syncCadence', String(cadence));
    }
  }, [cadence]);

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

  // Manual sync handler (update lastSyncRequestedAt and type)
  const handleManualSync = () => {
    setIsSyncing(true);
    setLastSyncRequestedAt(Date.now());
    setLastSyncType('Manual');
    onSync?.();
  };

  // Helper for next scheduled sync display (now uses live countdown)
  function formatNextSyncTime() {
    return countdown;
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
        {/* Live countdown on main bar, only if not session expired */}
        {countdown && countdown !== 'N/A' && status !== 'error' && !isAuthError(error) && (
          <span className="text-xs text-blue-500 ml-3">| Next check in: {countdown}</span>
        )}
      </button>
      {popoverOpen && (
        <SyncDetailsPopover
          details={{
            ...details,
            nextScheduledSync: nextSync,
            cadence,
            lastSyncType: lastSyncType,
          }}
          onClose={() => setPopoverOpen(false)}
          status={status}
          error={error}
          onSync={handleManualSync}
          onRetry={onRetry}
          onLogin={onLogin}
          popoverRef={popoverRef as React.RefObject<HTMLDivElement>}
          loading={loading}
          errorMsg={errorMsg}
          cadence={cadence}
          setCadence={setCadence}
          formatNextSyncTime={formatNextSyncTime}
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

type SyncDetailsPopoverProps = {
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
  cadence: number;
  setCadence: (n: number) => void;
  formatNextSyncTime: () => string;
};

function SyncDetailsPopover({ details, onClose, status, error, onSync, onRetry, onLogin, popoverRef, loading, errorMsg, cadence, setCadence, formatNextSyncTime }: SyncDetailsPopoverProps) {
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
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="This shows which way your changes are being synced.">Direction</span>
          <span>{details.direction === 'EA → Gmail' ? 'Changes from Email Agent are sent to Gmail.' : details.direction}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="The last time your emails were checked for updates.">Last checked</span>
          <span>{details.lastSync ? formatRelativeTime(details.lastSync) : 'Never'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="How long the last check took.">Check duration</span>
          <span>{details.durationSec != null ? `${details.durationSec.toFixed(1)} seconds` : '-'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="How many emails were looked at during the last check.">Emails checked</span>
          <span>{details.emailsSynced ?? '-'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="Number of new or changed emails found.">Updates found</span>
          <span>{details.changesDetected ?? '-'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="How many emails were updated in Gmail.">Emails updated</span>
          <span>{details.changesApplied ?? '-'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="Emails waiting to be updated next time.">Waiting to update</span>
          <span>{details.pendingEAChanges?.length ? details.pendingEAChanges.join(', ') : 'None'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="How long until your emails are checked again.">Next check in</span>
          <span>{formatNextSyncTime()}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="How often your emails are checked automatically.">Check frequency</span>
          <span>Every {cadence} minute{cadence !== 1 ? 's' : ''}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="Shows if you started the check or if it happened automatically.">How was last check started?</span>
          <span>{details.lastSyncType === 'Manual' ? 'You clicked "Check Now"' : 'Automatic (checked for you)'}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="The email account being checked.">Account</span>
          <span>{details.accountEmail}</span>
        </li>
        <li className="flex flex-col pt-2">
          <span className="font-semibold" title="The version of the app you're using.">App version</span>
          <span>{details.backendVersion}</span>
        </li>
      </ul>
      {/* Error details */}
      {details.lastError && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-4 w-4 mt-0.5 text-red-500" />
          <span><strong>Last error:</strong> {details.lastError} <span className="text-gray-500">(If this keeps happening, try again or check your connection.)</span></span>
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
              <li key={idx} className="flex flex-col gap-0.5 border-b border-gray-100 pb-1 mb-1">
                <span>
                  <span className="font-semibold">{formatRelativeTime(entry.time)}</span> — {entry.direction} — {entry.result === 'success' ? 'All good' : 'Error'}
                  {entry.result === 'error' && entry.error && <span className="text-red-500 ml-1">({entry.error})</span>}
                </span>
                <span className="text-gray-500">{entry.result === 'success' ? (entry.emailsSynced === 0 ? 'No new emails or changes.' : `${entry.emailsSynced} emails checked, ${entry.changes} updated.`) : 'There was a problem during this check.'}</span>
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
            Check Now
          </button>
        )}
        {status === 'syncing' && (
          <button
            className="px-4 py-2 rounded bg-blue-400 text-white text-sm font-medium cursor-not-allowed flex items-center gap-2"
            disabled
          >
            <ArrowPathIcon className="h-4 w-4 animate-spin" /> Checking…
          </button>
        )}
        {status === 'error' && !isAuthError && onRetry && (
          <button
            className="px-4 py-2 rounded bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition ml-2"
            onClick={onRetry}
          >
            Try Again
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
      {/* Cadence slider */}
      <div className="mt-4">
        <label htmlFor="cadence-slider" className="block text-xs font-medium text-gray-700 mb-1">How often to check for new emails</label>
        <div className="flex items-center gap-3">
          <input
            id="cadence-slider"
            type="range"
            min={0}
            max={5}
            step={1}
            value={cadence}
            onChange={e => setCadence(Number(e.target.value))}
            className="w-32 accent-blue-500"
            aria-valuenow={cadence}
            aria-valuemin={0}
            aria-valuemax={5}
          />
          <span className="text-sm text-gray-700">
            {cadence === 0 ? <span className="text-red-600 font-semibold">Off</span> : `${cadence} minute${cadence !== 1 ? 's' : ''}`}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {cadence === 0
            ? <span>Automatic sync is <span className="text-red-600 font-semibold">off</span>. Emails will not be checked automatically.</span>
            : <>Your emails will be checked automatically every {cadence} minute{cadence !== 1 ? 's' : ''}. Move the slider to change how often this happens.</>
          }
        </p>
      </div>
    </div>
  );
} 