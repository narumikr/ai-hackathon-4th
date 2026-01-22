'use client';

import { Button, TextField } from '@/components/ui';
import { BUTTON_LABELS, HELP_TEXTS, PLACEHOLDERS, SECTION_TITLES } from '@/constants';
import type React from 'react';
import { useState } from 'react';

interface SpotAdderProps {
  onAdd: (name: string) => void;
}

export const SpotAdder: React.FC<SpotAdderProps> = ({ onAdd }) => {
  const [name, setName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onAdd(name.trim());
      setName('');
    }
  };

  return (
    <div className="rounded-lg border border-neutral-300 border-dashed bg-neutral-50 p-6">
      <h3 className="mb-4 font-bold text-lg text-neutral-900">{SECTION_TITLES.ADD_SPOT}</h3>
      <p className="mb-4 text-neutral-600 text-sm">{HELP_TEXTS.ADD_SPOT_INSTRUCTION}</p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1">
          <TextField
            value={name}
            onChange={setName}
            placeholder={PLACEHOLDERS.SPOT_NAME}
            fullWidth
          />
        </div>
        <Button type="submit" variant="secondary" disabled={!name.trim()}>
          {BUTTON_LABELS.ADD}
        </Button>
      </form>
    </div>
  );
};
