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

/** What each setting means, shown once above the category list. */
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

const FIELDS: Record<Mode, (keyof CategorySettings)[]> = {
  auto: ['enabled', 'prefix', 'channel_size', 'empty_count'],
  custom: ['custom_enabled', 'custom_prefix'],
};

/** Show a filter box once the list is long enough that scanning it gets slow. */
const FILTER_THRESHOLD = 6;

export default function CategoryTable({ guildId, categories, mode, onUpdated }: Props) {
  const notify = useToast();
  const guideId = useId();
  const [query, setQuery] = useState('');

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

  const fields = FIELDS[mode];
  const helpId = (field: keyof CategorySettings) => `${guideId}-${field}`;
  const needle = query.trim().toLowerCase();
  const visible = needle ? categories.filter((c) => c.name.toLowerCase().includes(needle)) : categories;

  return (
    <>
      {/* Each setting is explained once here rather than repeated for every category. */}
      <dl className="settings-guide" aria-label="What each setting means">
        {fields.map((field) => (
          <div key={field} className="settings-guide-item" id={helpId(field)}>
            <dt className="setting-label">{HELP[field].label}</dt>
            <dd className="setting-help">{HELP[field].help}</dd>
            <dd className="setting-meta">
              {HELP[field].meta.map((m) => (
                <span key={m}>{m}</span>
              ))}
            </dd>
          </div>
        ))}
      </dl>

      {categories.length >= FILTER_THRESHOLD && (
        <div className="category-filter">
          <input
            type="search"
            className="form-control"
            placeholder="Filter categories"
            aria-label="Filter categories"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <p aria-live="polite">
            Showing {visible.length} of {categories.length} categories
          </p>
        </div>
      )}

      <div className={`category-list category-list-${mode}`}>
        <div className="category-list-header" aria-hidden="true">
          <span>Category</span>
          {fields.map((field) => (
            <span key={field}>{HELP[field].label}</span>
          ))}
        </div>
        {visible.length === 0 && <p className="category-list-empty">No categories match “{query.trim()}”.</p>}
        {visible.map((c) => (
          <section key={c.id} className="category-row" aria-labelledby={`category-${c.id}`}>
            <h3 id={`category-${c.id}`}>{c.name}</h3>
            {mode === 'auto' ? (
              <>
                <Cell field="enabled">
                  <Toggle
                    describedBy={helpId('enabled')}
                    label={`${c.name} enabled`}
                    checked={c.enabled}
                    onChange={(v) => save(c, 'enabled', v)}
                  />
                </Cell>
                <Cell field="prefix">
                  <SettingInput
                    describedBy={helpId('prefix')}
                    label={`${c.name} prefix`}
                    value={c.prefix}
                    maxLength={100}
                    onApply={(v) => save(c, 'prefix', v)}
                  />
                </Cell>
                <Cell field="channel_size">
                  <SettingInput
                    describedBy={helpId('channel_size')}
                    label={`${c.name} channel size`}
                    type="number"
                    value={c.channel_size}
                    min={0}
                    max={99}
                    onApply={(v) => save(c, 'channel_size', Number(v))}
                  />
                </Cell>
                <Cell field="empty_count">
                  <SettingInput
                    describedBy={helpId('empty_count')}
                    label={`${c.name} empty count`}
                    type="number"
                    value={c.empty_count}
                    min={1}
                    max={10}
                    onApply={(v) => save(c, 'empty_count', Number(v))}
                  />
                </Cell>
              </>
            ) : (
              <>
                <Cell field="custom_enabled">
                  <Toggle
                    describedBy={helpId('custom_enabled')}
                    label={`${c.name} custom channels enabled`}
                    checked={c.custom_enabled}
                    onChange={(v) => save(c, 'custom_enabled', v)}
                  />
                </Cell>
                <Cell field="custom_prefix">
                  <SettingInput
                    describedBy={helpId('custom_prefix')}
                    label={`${c.name} custom prefix`}
                    value={c.custom_prefix}
                    maxLength={10}
                    onApply={(v) => save(c, 'custom_prefix', v)}
                  />
                </Cell>
              </>
            )}
          </section>
        ))}
      </div>
    </>
  );
}

/** One setting in a category row. Its small label only shows when the column header is hidden. */
function Cell({ field, children }: { field: keyof CategorySettings; children: ReactNode }) {
  return (
    <div className="category-cell">
      <span className="category-cell-label" aria-hidden="true">
        {HELP[field].label}
      </span>
      {children}
    </div>
  );
}

function Spinner() {
  return <span className="spinner-border spinner-border-sm" aria-hidden="true" />;
}

function Toggle({
  describedBy,
  label,
  checked,
  onChange,
}: {
  describedBy: string;
  label: string;
  checked: boolean;
  onChange: (value: boolean) => Promise<boolean>;
}) {
  const [busy, setBusy] = useState(false);

  return (
    <div className="form-check form-switch d-flex align-items-center gap-2 ps-0">
      <input
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
      {busy && <Spinner />}
    </div>
  );
}

function SettingInput({
  describedBy,
  label,
  value,
  type = 'text',
  min,
  max,
  maxLength,
  onApply,
}: {
  describedBy: string;
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
