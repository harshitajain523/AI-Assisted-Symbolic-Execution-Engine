import { PropsWithChildren } from "react";

interface SectionProps extends PropsWithChildren {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function Section({ title, subtitle, actions, children }: SectionProps) {
  return (
    <section className="section">
      <header className="section__header">
        <div>
          <h2>{title}</h2>
          {subtitle && <p className="section__subtitle">{subtitle}</p>}
        </div>
        {actions && <div className="section__actions">{actions}</div>}
      </header>
      <div className="section__body">{children}</div>
    </section>
  );
}

