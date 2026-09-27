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
    default: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100',
    glass: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800',
    outline: 'bg-transparent border border-slate-200 dark:border-slate-800',
    gradient: 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800'
  };

  return (
    <div
      className={clsx(
        'rounded-md transition-all duration-200',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {(title || subtitle || action) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100 tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={clsx(!noPadding && 'p-6')}>{children}</div>
    </div>
  );
};
