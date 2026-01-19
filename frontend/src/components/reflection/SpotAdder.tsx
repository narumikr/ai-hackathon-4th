'use client';

import { Button, TextField } from '@/components/ui';
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
    <div className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-6">
      <h3 className="mb-4 font-bold text-neutral-900 text-lg">スポットを追加する</h3>
      <p className="mb-4 text-sm text-neutral-600">
        計画になかった立ち寄り場所や、特に印象に残った場所を追加して記録に残しましょう。
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1">
          <TextField
            value={name}
            onChange={setName}
            placeholder="スポット名を入力 (例: 原爆ドーム近くのカフェ)"
            fullWidth
          />
        </div>
        <Button type="submit" variant="secondary" disabled={!name.trim()}>
          追加
        </Button>
      </form>
    </div>
  );
};
