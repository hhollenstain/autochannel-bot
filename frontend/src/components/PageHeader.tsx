import type { ReactNode } from 'react';
import { Link } from 'react-router';
import { ArrowLeftIcon } from './icons';

interface Props {
  title: ReactNode;
  description?: ReactNode;
  /** Server or page icon shown beside the title. */
  icon?: string;
  /** Optional "back" link shown above the title. */
  back?: { to: string; label: string };
  actions?: ReactNode;
}

/** The heading block every page starts with. */
export default function PageHeader({ title, description, icon, back, actions }: Props) {
  return (
    <div className="page-header">
      {icon && <img src={icon} width={64} height={64} className="page-header-icon avatar" alt="" />}
      <div className="page-header-text">
        {back && (
          <Link to={back.to} className="page-header-back">
            <ArrowLeftIcon /> {back.label}
          </Link>
        )}
        <h1>{title}</h1>
        {description && <p className="page-header-description">{description}</p>}
      </div>
      {actions && <div className="page-header-actions">{actions}</div>}
    </div>
  );
}
