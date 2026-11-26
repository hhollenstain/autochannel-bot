import type { ReactNode } from 'react';

// Small inline SVG icons. All are decorative; give the surrounding control its name.

function Svg({ children, viewBox = '0 0 24 24' }: { children: ReactNode; viewBox?: string }) {
  return (
    <svg className="icon" viewBox={viewBox} width="1em" height="1em" aria-hidden="true" focusable="false">
      {children}
    </svg>
  );
}

const stroke = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
} as const;

export function CheckIcon() {
  return (
    <Svg>
      <path {...stroke} d="M20 6 9 17l-5-5" />
    </Svg>
  );
}

export function SunIcon() {
  return (
    <Svg>
      <circle {...stroke} cx="12" cy="12" r="4" />
      <path
        {...stroke}
        d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
      />
    </Svg>
  );
}

export function MoonIcon() {
  return (
    <Svg>
      <path {...stroke} d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </Svg>
  );
}

export function ChevronRightIcon() {
  return (
    <Svg>
      <path {...stroke} d="m9 18 6-6-6-6" />
    </Svg>
  );
}

export function ChevronDownIcon() {
  return (
    <Svg>
      <path {...stroke} d="m6 9 6 6 6-6" />
    </Svg>
  );
}

export function ArrowLeftIcon() {
  return (
    <Svg>
      <path {...stroke} d="M19 12H5M12 19l-7-7 7-7" />
    </Svg>
  );
}

export function ServerIcon() {
  return (
    <Svg>
      <rect {...stroke} x="3" y="4" width="18" height="7" rx="2" />
      <rect {...stroke} x="3" y="13" width="18" height="7" rx="2" />
      <path {...stroke} d="M7 7.5h.01M7 16.5h.01" />
    </Svg>
  );
}
