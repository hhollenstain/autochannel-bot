import type { ReactNode } from 'react';

export default function GuildHeader({ children, icon }: { children: ReactNode; icon?: string }) {
  return (
    <div className="page-header">
      <h2>
        {children}
        {icon && <img src={icon} width={64} height={64} className="img-circle ms-2" alt="" />}
      </h2>
    </div>
  );
}
