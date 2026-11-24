import { useEffect, useState, type FormEvent } from 'react';
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
    return <p className="text-center mt-3">This server has no categories yet.</p>;
  }

  return (
    <table className="table discord-dark-col">
      <thead>
        <tr className="text-center">
          <th title="Name of Categories in your server">Name</th>
          {mode === 'auto' ? (
            <>
              <th title="Toggle to enable or disable the autochannel bot in this category (default Off)">
                Enabled
              </th>
              <th title="The prefix of the created channel, must be unique for channels in this category (default AC!)">
                Prefix
              </th>
              <th title="Number of users that can be in each channel, 0-99 where 0 is unlimited (default 10)">
                Channel Size
              </th>
              <th title="Number of empty channels AutoChannel keeps in category (default 1)">Empty Count</th>
            </>
          ) : (
            <>
              <th title="Toggle to enable or disable custom channel creation for this category (default Off)">
                Enabled
              </th>
              <th title="The prefix of the created channel, must be unique for channels in this category (default VC!)">
                Custom Prefix
              </th>
            </>
          )}
        </tr>
      </thead>
      <tbody>
        {categories.map((c) => (
          <tr key={c.id}>
            <td className="text-center align-middle">{c.name}</td>
            {mode === 'auto' ? (
              <>
                <td className="text-center align-middle">
                  <Toggle label={`${c.name} enabled`} checked={c.enabled} onChange={(v) => save(c, 'enabled', v)} />
                </td>
                <td>
                  <SettingInput
                    label={`${c.name} prefix`}
                    value={c.prefix}
                    maxLength={100}
                    width={200}
                    onApply={(v) => save(c, 'prefix', v)}
                  />
                </td>
                <td>
                  <SettingInput
                    label={`${c.name} channel size`}
                    type="number"
                    value={c.channel_size}
                    min={0}
                    max={99}
                    width={110}
                    onApply={(v) => save(c, 'channel_size', Number(v))}
                  />
                </td>
                <td>
                  <SettingInput
                    label={`${c.name} empty count`}
                    type="number"
                    value={c.empty_count}
                    min={1}
                    max={10}
                    width={110}
                    onApply={(v) => save(c, 'empty_count', Number(v))}
                  />
                </td>
              </>
            ) : (
              <>
                <td className="text-center align-middle">
                  <Toggle
                    label={`${c.name} custom channels enabled`}
                    checked={c.custom_enabled}
                    onChange={(v) => save(c, 'custom_enabled', v)}
                  />
                </td>
                <td>
                  <SettingInput
                    label={`${c.name} custom prefix`}
                    value={c.custom_prefix}
                    maxLength={10}
                    width={200}
                    onApply={(v) => save(c, 'custom_prefix', v)}
                  />
                </td>
              </>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Toggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => Promise<boolean>;
}) {
  const [busy, setBusy] = useState(false);

  return (
    <div className="form-check form-switch d-inline-block">
      <input
        className="form-check-input"
        type="checkbox"
        role="switch"
        aria-label={label}
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
  label,
  value,
  type = 'text',
  min,
  max,
  maxLength,
  width,
  onApply,
}: {
  label: string;
  value: string | number;
  type?: 'text' | 'number';
  min?: number;
  max?: number;
  maxLength?: number;
  width: number;
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
    <form className="input-group mx-auto" style={{ width }} onSubmit={submit}>
      <input
        className="form-control"
        aria-label={label}
        type={type}
        value={draft}
        min={min}
        max={max}
        maxLength={maxLength}
        required
        onChange={(e) => setDraft(e.target.value)}
      />
      <button type="submit" className="btn btn-primary" disabled={busy} aria-label={`Save ${label}`}>
        <CheckIcon />
      </button>
    </form>
  );
}
