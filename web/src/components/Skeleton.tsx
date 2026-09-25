import React from 'react';
import { clsx } from 'clsx';

export interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'circle' | 'table';
}

export const Skeleton: React.FC<SkeletonProps> = ({ className, variant = 'text' }) => {
  if (variant === 'circle') {
    return <div className={clsx('animate-pulse rounded-full bg-slate-800', className)} />;
  }

  if (variant === 'card') {
    return (
      <div className={clsx('animate-pulse rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4', className)}>
        <div className="h-4 w-1/3 bg-slate-800 rounded" />
        <div className="h-8 w-1/2 bg-slate-800 rounded" />
        <div className="h-3 w-2/3 bg-slate-800/80 rounded" />
      </div>
    );
  }

  if (variant === 'table') {
    return (
      <div className={clsx('animate-pulse rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3', className)}>
        <div className="h-6 w-full bg-slate-800 rounded" />
        <div className="h-4 w-full bg-slate-800/60 rounded" />
        <div className="h-4 w-full bg-slate-800/60 rounded" />
        <div className="h-4 w-full bg-slate-800/60 rounded" />
      </div>
    );
  }

  return <div className={clsx('animate-pulse rounded bg-slate-800 h-4 w-full', className)} />;
};
