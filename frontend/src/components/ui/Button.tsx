import React from 'react';
import { Spinner } from './Spinner';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantStyles: Record<Variant, React.CSSProperties & { '--btn-hover-bg'?: string }> = {
  primary: {
    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    color: '#ffffff',
    border: '1px solid transparent',
  },
  secondary: {
    background: 'rgba(99, 102, 241, 0.1)',
    color: '#6366f1',
    border: '1px solid rgba(99, 102, 241, 0.3)',
  },
  danger: {
    background: 'rgba(239, 68, 68, 0.1)',
    color: '#ef4444',
    border: '1px solid rgba(239, 68, 68, 0.3)',
  },
  ghost: {
    background: 'transparent',
    color: '#94a3b8',
    border: '1px solid rgba(148, 163, 184, 0.2)',
  },
};

const sizeStyles: Record<Size, React.CSSProperties> = {
  sm: { fontSize: '12px', padding: '6px 12px', borderRadius: '6px', gap: '6px' },
  md: { fontSize: '14px', padding: '9px 18px', borderRadius: '8px', gap: '8px' },
  lg: { fontSize: '15px', padding: '12px 24px', borderRadius: '10px', gap: '10px' },
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  style,
  ...rest
}) => {
  const isDisabled = disabled || loading;

  return (
    <button
      disabled={isDisabled}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'var(--font-sans)',
        fontWeight: 500,
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        transition: 'all 200ms ease',
        outline: 'none',
        opacity: isDisabled ? 0.6 : 1,
        whiteSpace: 'nowrap',
        letterSpacing: '0.01em',
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...style,
      }}
      onMouseEnter={(e) => {
        if (isDisabled) return;
        const el = e.currentTarget;
        if (variant === 'primary') {
          el.style.filter = 'brightness(1.15)';
          el.style.boxShadow = '0 4px 20px rgba(99, 102, 241, 0.4)';
          el.style.transform = 'translateY(-1px)';
        } else if (variant === 'secondary') {
          el.style.background = 'rgba(99, 102, 241, 0.2)';
          el.style.transform = 'translateY(-1px)';
        } else if (variant === 'danger') {
          el.style.background = 'rgba(239, 68, 68, 0.2)';
          el.style.transform = 'translateY(-1px)';
        } else {
          el.style.background = 'rgba(148, 163, 184, 0.1)';
        }
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget;
        el.style.filter = '';
        el.style.boxShadow = '';
        el.style.transform = '';
        if (variant === 'secondary') el.style.background = 'rgba(99, 102, 241, 0.1)';
        else if (variant === 'danger') el.style.background = 'rgba(239, 68, 68, 0.1)';
        else if (variant === 'ghost') el.style.background = 'transparent';
      }}
      onMouseDown={(e) => {
        if (!isDisabled) e.currentTarget.style.transform = 'translateY(0)';
      }}
      onMouseUp={(e) => {
        if (!isDisabled) e.currentTarget.style.transform = 'translateY(-1px)';
      }}
      {...rest}
    >
      {loading ? (
        <Spinner size="sm" color="currentColor" />
      ) : (
        leftIcon
      )}
      {children && <span>{children}</span>}
      {!loading && rightIcon}
    </button>
  );
};
