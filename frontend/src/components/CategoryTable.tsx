import { useEffect, useId, useState, type FormEvent, type ReactNode } from 'react';
import { api, ApiError, type Category, type CategorySettings } from '../api';
import { useToast } from '../toasts';
import { CheckIcon } from './icons';

type Mode = 'auto' | 'custom';

interface Props {
  guildId: string;
  categories: Category[];
  mode: Mode;
  onUpdated: (id: string, settings: Partial<CategorySettings>) => void;
}

const LABELS: Record<keyof CategorySettings, string> = {
  enabled: 'Enabled Category',
  custom_enabled: 'Enabled Custom Channels',
  prefix: 'Updated Prefix',
  custom_prefix: 'Updated Custom Prefix',
  channel_size: 'Updated Channel Size',
  empty_count: 'Updated empty channel count',
};

/** What each setting means, shown under its label. */
const HELP = {
  enabled: {
    label: 'Enabled',
    help: 'Auto-chan creates and cleans up voice channels in this category.',
    meta: ['Default: Off'],
  },
  prefix: {
    label: 'Prefix',
    help: 'Start of each created channel name. Must be unique for channels in this category.',
    meta: ['Default: AC!', 'Up to 100 characters'],
  },
  channel_size: {
    label: 'Channel size',
    help: 'How many users can join each created channel. 0 means unlimited.',
    meta: ['Default: 10', 'Range: 0–99'],
  },
  empty_count: {
    label: 'Empty count',
    help: 'How many empty channels Auto-chan keeps open in this category.',
    meta: ['Default: 1', 'Range: 1–10'],
  },
  custom_enabled: {
    label: 'Custom channels',
    help: 'Let members create their own named channels in this category.',
    meta: ['Default: Off'],
  },
  custom_prefix: {
    label: 'Custom prefix',
    help: 'Start of each custom channel name. Must be unique for channels in this category.',
    meta: ['Default: VC!', 'Up to 10 characters'],
  },
} satisfies Record<keyof CategorySettings, { label: string; help: string; meta: string[] }>;

export default function CategoryTable({ guildId, categories, mode, onUpdated }: Props) {
  const notify = useToast();

  async function save<K extends keyof CategorySettings>(
    category: Category,
    field: K,
    value: CategorySettings[K],
  ): Promise<boolean> {
    try {
      const { category: saved } = await api.updateCategory(guildId, category.id, { [field]: value });
      onUpdated(category.id, saved);
      notify('success', LABELS[field], `${category.name}: ${String(saved[field])}`);
      return true;
    } catch (e) {
      const reason = e instanceof ApiError ? (e.fields[field] ?? e.message) : 'Network error';
      notify('error', `Failed: ${LABELS[field]}`, `${category.name}: ${reason}`);
      return false;
    }
  }

  if (categories.length === 0) {
    return (
      <div className="state-panel surface">
        <h2>No categories yet</h2>
        <p className="mb-0">Create a category in Discord, then reload this page to set it up.</p>
      </div>
    );
  }

  return (
    <div className="settings-list">
      {categories.map((c) => (
        <section key={c.id} className="setting-card" aria-labelledby={`category-${c.id}`}>
          <header className="setting-card-header">
            <h3 id={`category-${c.id}`}>{c.name}</h3>
          </header>
          {mode === 'auto' ? (
            <>
              <SettingRow field="enabled">
                {(ids) => (
                  <Toggle
                    {...ids}
                    label={`${c.name} enabled`}
                    checked={c.enabled}
                    onChange={(v) => save(c, 'enabled', v)}
                  />
                )}
              </SettingRow>
              <SettingRow field="prefix">
                {(ids) => (
                  <SettingInput
                    {...ids}
                    label={`${c.name} prefix`}
                    value={c.prefix}
                    maxLength={100}
                    onApply={(v) => save(c, 'prefix', v)}
                  />
                )}
              </SettingRow>
              <SettingRow field="channel_size">
                {(ids) => (
                  <SettingInput
                    {...ids}
                    label={`${c.name} channel size`}
                    type="number"
                    value={c.channel_size}
                    min={0}
                    max={99}
                    onApply={(v) => save(c, 'channel_size', Number(v))}
                  />
                )}
              </SettingRow>
              <SettingRow field="empty_count">
                {(ids) => (
                  <SettingInput
                    {...ids}
                    label={`${c.name} empty count`}
                    type="number"
                    value={c.empty_count}
                    min={1}
                    max={10}
                    onApply={(v) => save(c, 'empty_count', Number(v))}
                  />
                )}
              </SettingRow>
            </>
          ) : (
            <>
              <SettingRow field="custom_enabled">
                {(ids) => (
                  <Toggle
                    {...ids}
                    label={`${c.name} custom channels enabled`}
                    checked={c.custom_enabled}
                    onChange={(v) => save(c, 'custom_enabled', v)}
                  />
                )}
              </SettingRow>
              <SettingRow field="custom_prefix">
                {(ids) => (
                  <SettingInput
                    {...ids}
                    label={`${c.name} custom prefix`}
                    value={c.custom_prefix}
                    maxLength={10}
                    onApply={(v) => save(c, 'custom_prefix', v)}
                  />
                )}
              </SettingRow>
            </>
          )}
        </section>
      ))}
    </div>
  );
}

interface ControlIds {
  id: string;
  describedBy: string;
}

function SettingRow({
  field,
  children,
}: {
  field: keyof CategorySettings;
  children: (ids: ControlIds) => ReactNode;
}) {
  const id = useId();
  const { label, help, meta } = HELP[field];

  return (
    <div className="setting-row">
      <div className="setting-text">
        <label className="setting-label" htmlFor={id}>
          {label}
        </label>
        <p className="setting-help" id={`${id}-help`}>
          {help}
        </p>
        <p className="setting-meta" id={`${id}-meta`}>
          {meta.map((m) => (
            <span key={m}>{m}</span>
          ))}
        </p>
      </div>
      <div className="setting-control">{children({ id, describedBy: `${id}-help ${id}-meta` })}</div>
    </div>
  );
}

function Spinner() {
  return <span className="spinner-border spinner-border-sm" aria-hidden="true" />;
}

function Toggle({
  id,
  describedBy,
  label,
  checked,
  onChange,
}: ControlIds & {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => Promise<boolean>;
}) {
  const [busy, setBusy] = useState(false);

  return (
    <div className="form-check form-switch d-flex align-items-center gap-2 ps-0">
      {busy && <Spinner />}
      <input
        id={id}
        className="form-check-input"
        type="checkbox"
        role="switch"
        aria-label={label}
        aria-describedby={describedBy}
        aria-busy={busy}
        checked={checked}
        disabled={busy}
        onChange={async (e) => {
          setBusy(true);
          await onChange(e.target.checked);
          setBusy(false);
        }}
      />
    </div>
  );
}

function SettingInput({
  id,
  describedBy,
  label,
  value,
  type = 'text',
  min,
  max,
  maxLength,
  onApply,
}: ControlIds & {
  label: string;
  value: string | number;
  type?: 'text' | 'number';
  min?: number;
  max?: number;
  maxLength?: number;
  onApply: (value: string) => Promise<boolean>;
}) {
  const [draft, setDraft] = useState(String(value));
  const [busy, setBusy] = useState(false);

  // Show what the server actually stored (e.g. a trimmed prefix).
  useEffect(() => setDraft(String(value)), [value]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    if (!(await onApply(draft))) setDraft(String(value));
    setBusy(false);
  }

  return (
    <form className="setting-form" onSubmit={submit}>
      <input
        id={id}
        className="form-control"
        aria-label={label}
        aria-describedby={describedBy}
        type={type}
        value={draft}
        min={min}
        max={max}
        maxLength={maxLength}
        required
        onChange={(e) => setDraft(e.target.value)}
      />
      <button
        type="submit"
        className="btn btn-primary"
        disabled={busy}
        aria-busy={busy}
        aria-label={`Save ${label}`}
      >
        {busy ? <Spinner /> : <CheckIcon />}
        Save
      </button>
    </form>
  );
}
