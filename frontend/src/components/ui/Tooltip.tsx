import React, { useState, useRef } from 'react';

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  placement = 'top',
}) => {
  const [visible, setVisible] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLSpanElement>(null);

  const handleMouseEnter = (e: React.MouseEvent) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    if (placement === 'top') {
      setPos({ x: rect.left + rect.width / 2, y: rect.top - 8 });
    } else if (placement === 'bottom') {
      setPos({ x: rect.left + rect.width / 2, y: rect.bottom + 8 });
    }
    setVisible(true);
  };

  const handleMouseLeave = () => setVisible(false);

  return (
    <span
      ref={containerRef}
      style={{ position: 'relative', display: 'inline-flex' }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      {visible && content && (
        <span
          style={{
            position: 'fixed',
            left: pos.x,
            top: pos.y,
            transform: placement === 'top' ? 'translate(-50%, -100%)' : 'translate(-50%, 0)',
            background: '#0f172a',
            color: '#f1f5f9',
            border: '1px solid #1e293b',
            borderRadius: '6px',
            padding: '6px 10px',
            fontSize: '12px',
            fontWeight: 500,
            whiteSpace: 'nowrap',
            zIndex: 9999,
            pointerEvents: 'none',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            animation: 'fadeInFast 150ms ease forwards',
          }}
        >
          {content}
        </span>
      )}
    </span>
  );
};
