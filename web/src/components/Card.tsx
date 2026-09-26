import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  variant?: 'default' | 'glass' | 'outline' | 'gradient';
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  children,
  className,
  variant = 'default',
  noPadding = false,
  ...props
}) => {
  const variantStyles = {
    default: 'bg-slate-900/80 dark:bg-slate-900/80 border border-slate-800 shadow-xl shadow-slate-950/20 text-slate-100',
    glass: 'glass-panel text-slate-100 shadow-xl shadow-cyan-950/10',
    outline: 'bg-transparent border border-slate-800 text-slate-100',
    gradient: 'bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/40 border border-cyan-500/20 text-slate-100 shadow-lg shadow-cyan-950/30'
  };

  return (
    <div
      className={clsx(
        'rounded-xl transition-all duration-200',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {(title || subtitle || action) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/80">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-100 tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={clsx(!noPadding && 'p-6')}>{children}</div>
    </div>
  );
};
