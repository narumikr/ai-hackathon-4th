'use client';

import { TABLE_LABELS } from '@/constants/ui';
import type { ColumnDef, SortDirection, SortState, TableProps } from '@/types/ui';
import { useCallback, useMemo, useState } from 'react';
import { Checkbox } from './Checkbox';
import { LoadingSpinner } from './LoadingSpinner';

const getAlignClass = (align: 'left' | 'center' | 'right' = 'left') => {
  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  };
  return alignClasses[align];
};

function SortIcon({ direction }: { direction: SortDirection }) {
  return (
    <span className="ml-1 inline-flex h-4 w-4 flex-col items-center justify-center">
      <svg
        className={`h-3 w-3 transition-colors ${
          direction === 'asc' ? 'text-primary-600' : 'text-neutral-300'
        }`}
        viewBox="0 0 12 12"
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M6 2L10 7H2L6 2Z" />
      </svg>
      <svg
        className={`-mt-1 h-3 w-3 transition-colors ${
          direction === 'desc' ? 'text-primary-600' : 'text-neutral-300'
        }`}
        viewBox="0 0 12 12"
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M6 10L2 5H10L6 10Z" />
      </svg>
    </span>
  );
}

export function Table<T extends object>({
  columns,
  data,
  sortable = false,
  selectable = false,
  selectedKeys = [],
  onSelectionChange,
  onRowClick,
  rowKey,
  loading = false,
  emptyMessage = TABLE_LABELS.EMPTY_MESSAGE,
  striped = false,
  hoverable = true,
  className = '',
}: TableProps<T>) {
  const [sortState, setSortState] = useState<SortState>({
    key: null,
    direction: null,
  });

  const getRowKey = useCallback(
    (row: T, index: number): string => {
      if (rowKey) {
        return rowKey(row, index);
      }
      if ('id' in row) {
        return String(row.id);
      }
      return String(index);
    },
    [rowKey]
  );

  const handleSort = useCallback(
    (column: ColumnDef<T>) => {
      if (!sortable || column.sortable === false) return;

      setSortState(prev => {
        if (prev.key !== column.key) {
          return { key: column.key, direction: 'asc' };
        }
        if (prev.direction === 'asc') {
          return { key: column.key, direction: 'desc' };
        }
        return { key: null, direction: null };
      });
    },
    [sortable]
  );

  const sortedData = useMemo(() => {
    if (!sortState.key || !sortState.direction) {
      return data;
    }

    const sortKey = sortState.key;
    if (!sortKey) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortKey as keyof T];
      const bValue = b[sortKey as keyof T];

      if (aValue === bValue) return 0;
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      const comparison = aValue < bValue ? -1 : 1;
      return sortState.direction === 'asc' ? comparison : -comparison;
    });
  }, [data, sortState]);

  const handleSelectAll = useCallback(() => {
    if (!onSelectionChange) return;

    const allKeys = data.map((row, index) => getRowKey(row, index));
    const allSelected = allKeys.every(key => selectedKeys.includes(key));

    if (allSelected) {
      onSelectionChange([]);
    } else {
      onSelectionChange(allKeys);
    }
  }, [data, getRowKey, selectedKeys, onSelectionChange]);

  const handleSelectRow = useCallback(
    (key: string) => {
      if (!onSelectionChange) return;

      if (selectedKeys.includes(key)) {
        onSelectionChange(selectedKeys.filter(k => k !== key));
      } else {
        onSelectionChange([...selectedKeys, key]);
      }
    },
    [selectedKeys, onSelectionChange]
  );

  const isAllSelected = useMemo(() => {
    if (data.length === 0) return false;
    const allKeys = data.map((row, index) => getRowKey(row, index));
    return allKeys.every(key => selectedKeys.includes(key));
  }, [data, getRowKey, selectedKeys]);

  const isIndeterminate = useMemo(() => {
    if (data.length === 0) return false;
    const allKeys = data.map((row, index) => getRowKey(row, index));
    const selectedCount = allKeys.filter(key => selectedKeys.includes(key)).length;
    return selectedCount > 0 && selectedCount < allKeys.length;
  }, [data, getRowKey, selectedKeys]);

  const getCellValue = (row: T, column: ColumnDef<T>, rowIndex: number) => {
    const value = row[column.key as keyof T & string];
    if (column.render) {
      return column.render(value as T[keyof T & string], row, rowIndex);
    }
    if (value === null || value === undefined) {
      return '-';
    }
    return String(value);
  };

  const baseTableStyles = [
    'w-full',
    'border-collapse',
    'bg-white',
    'rounded-lg',
    'overflow-hidden',
    'shadow-sm',
    'border border-neutral-200',
  ].join(' ');

  const headerCellStyles = [
    'px-4 py-3',
    'bg-primary-50',
    'border-b border-primary-200',
    'font-semibold',
    'text-primary-800',
    'text-sm',
  ].join(' ');

  const bodyCellStyles = [
    'px-4 py-3',
    'border-b border-neutral-100',
    'text-sm',
    'text-neutral-700',
  ].join(' ');

  const getRowStyles = (index: number, isSelected: boolean) => {
    const styles = ['transition-colors duration-150'];

    if (isSelected) {
      styles.push('bg-primary-100');
    } else if (striped && index % 2 === 1) {
      styles.push('bg-neutral-50');
    }

    if (hoverable && !isSelected) {
      styles.push('hover:bg-primary-50');
    }

    if (onRowClick) {
      styles.push('cursor-pointer');
    }

    return styles.join(' ');
  };

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className={baseTableStyles}>
        <thead>
          <tr>
            {selectable && (
              <th className={`${headerCellStyles} w-12`}>
                <Checkbox
                  checked={isAllSelected}
                  indeterminate={isIndeterminate}
                  onChange={handleSelectAll}
                  aria-label={TABLE_LABELS.SELECT_ALL_ROWS}
                />
              </th>
            )}
            {columns.map(column => {
              const isSortable = sortable && column.sortable !== false;
              const isSorted = sortState.key === column.key;

              return (
                <th
                  key={column.key}
                  className={`${headerCellStyles} ${getAlignClass(column.align)} ${
                    isSortable ? 'cursor-pointer select-none hover:bg-primary-100' : ''
                  }`}
                  style={column.width ? { width: column.width } : undefined}
                  onClick={() => isSortable && handleSort(column)}
                  onKeyDown={e => {
                    if (isSortable && (e.key === 'Enter' || e.key === ' ')) {
                      e.preventDefault();
                      handleSort(column);
                    }
                  }}
                  tabIndex={isSortable ? 0 : undefined}
                  aria-sort={
                    isSorted
                      ? sortState.direction === 'asc'
                        ? 'ascending'
                        : 'descending'
                      : undefined
                  }
                >
                  <span className="inline-flex items-center">
                    {column.title}
                    {isSortable && <SortIcon direction={isSorted ? sortState.direction : null} />}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td
                colSpan={columns.length + (selectable ? 1 : 0)}
                className="px-4 py-12 text-center"
              >
                <div className="flex items-center justify-center">
                  <LoadingSpinner size="lg" />
                </div>
              </td>
            </tr>
          ) : sortedData.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length + (selectable ? 1 : 0)}
                className="px-4 py-12 text-center text-neutral-500"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sortedData.map((row, rowIndex) => {
              const key = getRowKey(row, rowIndex);
              const isSelected = selectedKeys.includes(key);

              return (
                <tr
                  key={key}
                  className={getRowStyles(rowIndex, isSelected)}
                  onClick={() => onRowClick?.(row, rowIndex)}
                  onKeyDown={e => {
                    if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
                      e.preventDefault();
                      onRowClick(row, rowIndex);
                    }
                  }}
                  tabIndex={onRowClick ? 0 : undefined}
                >
                  {selectable && (
                    <td
                      className={bodyCellStyles}
                      onClick={e => e.stopPropagation()}
                      onKeyDown={e => e.stopPropagation()}
                    >
                      <Checkbox
                        checked={isSelected}
                        onChange={() => handleSelectRow(key)}
                        aria-label={TABLE_LABELS.SELECT_ROW(rowIndex + 1)}
                      />
                    </td>
                  )}
                  {columns.map(column => (
                    <td
                      key={column.key}
                      className={`${bodyCellStyles} ${getAlignClass(column.align)}`}
                    >
                      {getCellValue(row, column, rowIndex)}
                    </td>
                  ))}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
