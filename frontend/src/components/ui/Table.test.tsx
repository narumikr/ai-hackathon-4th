import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Table } from './Table';
import type { ColumnDef } from '@/types/ui';

interface TestData {
  id: number;
  name: string;
  age: number;
  city: string;
}

const testColumns: ColumnDef<TestData>[] = [
  { key: 'name', title: '名前' },
  { key: 'age', title: '年齢' },
  { key: 'city', title: '都市' },
];

const testData: TestData[] = [
  { id: 1, name: '田中太郎', age: 30, city: '東京' },
  { id: 2, name: '鈴木花子', age: 25, city: '大阪' },
  { id: 3, name: '佐藤一郎', age: 35, city: '名古屋' },
];

describe('Table', () => {
  describe('基本的なレンダリング', () => {
    it('テーブルがレンダリングされること', () => {
      render(<Table columns={testColumns} data={testData} />);
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('カラムヘッダーが表示されること', () => {
      render(<Table columns={testColumns} data={testData} />);
      expect(screen.getByText('名前')).toBeInTheDocument();
      expect(screen.getByText('年齢')).toBeInTheDocument();
      expect(screen.getByText('都市')).toBeInTheDocument();
    });

    it('データが表示されること', () => {
      render(<Table columns={testColumns} data={testData} />);
      expect(screen.getByText('田中太郎')).toBeInTheDocument();
      expect(screen.getByText('鈴木花子')).toBeInTheDocument();
      expect(screen.getByText('佐藤一郎')).toBeInTheDocument();
    });

    it('正しい行数が表示されること', () => {
      render(<Table columns={testColumns} data={testData} />);
      const tbody = screen.getByRole('table').querySelector('tbody');
      const rows = tbody?.querySelectorAll('tr');
      expect(rows).toHaveLength(3);
    });
  });

  describe('Props: emptyMessage', () => {
    it('データが空の場合、デフォルトメッセージが表示されること', () => {
      render(<Table columns={testColumns} data={[]} />);
      expect(screen.getByText('データがありません')).toBeInTheDocument();
    });

    it('カスタムemptyMessageが表示されること', () => {
      render(<Table columns={testColumns} data={[]} emptyMessage="結果が見つかりませんでした" />);
      expect(screen.getByText('結果が見つかりませんでした')).toBeInTheDocument();
    });
  });

  describe('Props: loading', () => {
    it('loading時にスピナーが表示されること', () => {
      render(<Table columns={testColumns} data={[]} loading />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('loading時にデータ行が表示されないこと', () => {
      render(<Table columns={testColumns} data={testData} loading />);
      expect(screen.queryByText('田中太郎')).not.toBeInTheDocument();
    });
  });

  describe('Props: sortable', () => {
    it('sortable=falseの場合、ソートアイコンが表示されないこと', () => {
      render(<Table columns={testColumns} data={testData} sortable={false} />);
      const headers = screen.getAllByRole('columnheader');
      headers.forEach((header) => {
        expect(header.querySelector('svg')).not.toBeInTheDocument();
      });
    });

    it('sortable=trueの場合、ソートアイコンが表示されること', () => {
      render(<Table columns={testColumns} data={testData} sortable />);
      const headers = screen.getAllByRole('columnheader');
      headers.forEach((header) => {
        expect(header.querySelectorAll('svg').length).toBe(2);
      });
    });

    it('ソート可能なカラムをクリックすると昇順でソートされること', () => {
      render(<Table columns={testColumns} data={testData} sortable />);
      const ageHeader = screen.getByText('年齢');
      fireEvent.click(ageHeader);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const rows = tbody?.querySelectorAll('tr');
      const firstRowCells = rows?.[0].querySelectorAll('td');
      expect(firstRowCells?.[1].textContent).toBe('25');
    });

    it('ソート可能なカラムを2回クリックすると降順でソートされること', () => {
      render(<Table columns={testColumns} data={testData} sortable />);
      const ageHeader = screen.getByText('年齢');
      fireEvent.click(ageHeader);
      fireEvent.click(ageHeader);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const rows = tbody?.querySelectorAll('tr');
      const firstRowCells = rows?.[0].querySelectorAll('td');
      expect(firstRowCells?.[1].textContent).toBe('35');
    });

    it('ソート可能なカラムを3回クリックするとソートがリセットされること', () => {
      render(<Table columns={testColumns} data={testData} sortable />);
      const ageHeader = screen.getByText('年齢');
      fireEvent.click(ageHeader);
      fireEvent.click(ageHeader);
      fireEvent.click(ageHeader);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const rows = tbody?.querySelectorAll('tr');
      const firstRowCells = rows?.[0].querySelectorAll('td');
      expect(firstRowCells?.[1].textContent).toBe('30');
    });

    it('カラムにsortable=falseを指定するとそのカラムはソートできないこと', () => {
      const columnsWithNonSortable: ColumnDef<TestData>[] = [
        { key: 'name', title: '名前', sortable: false },
        { key: 'age', title: '年齢' },
        { key: 'city', title: '都市' },
      ];
      render(<Table columns={columnsWithNonSortable} data={testData} sortable />);

      const nameHeader = screen.getByText('名前').closest('th');
      expect(nameHeader?.querySelectorAll('svg').length).toBe(0);
    });
  });

  describe('Props: selectable', () => {
    it('selectable=trueの場合、チェックボックスカラムが表示されること', () => {
      render(<Table columns={testColumns} data={testData} selectable />);
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBe(4);
    });

    it('ヘッダーのチェックボックスをクリックすると全行が選択されること', () => {
      const handleSelectionChange = vi.fn();
      render(
        <Table
          columns={testColumns}
          data={testData}
          selectable
          onSelectionChange={handleSelectionChange}
        />
      );

      const headerCheckbox = screen.getAllByRole('checkbox')[0];
      fireEvent.click(headerCheckbox);

      expect(handleSelectionChange).toHaveBeenCalledWith(['1', '2', '3']);
    });

    it('行のチェックボックスをクリックするとその行が選択されること', () => {
      const handleSelectionChange = vi.fn();
      render(
        <Table
          columns={testColumns}
          data={testData}
          selectable
          onSelectionChange={handleSelectionChange}
        />
      );

      const rowCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(rowCheckboxes[1]);

      expect(handleSelectionChange).toHaveBeenCalledWith(['1']);
    });

    it('選択済みの行のチェックボックスをクリックすると選択が解除されること', () => {
      const handleSelectionChange = vi.fn();
      render(
        <Table
          columns={testColumns}
          data={testData}
          selectable
          selectedKeys={['1']}
          onSelectionChange={handleSelectionChange}
        />
      );

      const rowCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(rowCheckboxes[1]);

      expect(handleSelectionChange).toHaveBeenCalledWith([]);
    });

    it('全選択状態でヘッダーチェックボックスをクリックすると全選択解除されること', () => {
      const handleSelectionChange = vi.fn();
      render(
        <Table
          columns={testColumns}
          data={testData}
          selectable
          selectedKeys={['1', '2', '3']}
          onSelectionChange={handleSelectionChange}
        />
      );

      const headerCheckbox = screen.getAllByRole('checkbox')[0];
      fireEvent.click(headerCheckbox);

      expect(handleSelectionChange).toHaveBeenCalledWith([]);
    });
  });

  describe('Props: onRowClick', () => {
    it('行をクリックするとonRowClickが呼ばれること', () => {
      const handleRowClick = vi.fn();
      render(<Table columns={testColumns} data={testData} onRowClick={handleRowClick} />);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const firstRow = tbody?.querySelector('tr');
      if (firstRow) {
        fireEvent.click(firstRow);
      }

      expect(handleRowClick).toHaveBeenCalledWith(testData[0], 0);
    });

    it('チェックボックスをクリックしてもonRowClickが呼ばれないこと', () => {
      const handleRowClick = vi.fn();
      render(
        <Table columns={testColumns} data={testData} selectable onRowClick={handleRowClick} />
      );

      const rowCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(rowCheckboxes[1]);

      expect(handleRowClick).not.toHaveBeenCalled();
    });
  });

  describe('Props: rowKey', () => {
    it('カスタムrowKey関数が使用されること', () => {
      const handleSelectionChange = vi.fn();
      const customRowKey = (row: TestData) => `custom-${row.id}`;

      render(
        <Table
          columns={testColumns}
          data={testData}
          selectable
          rowKey={customRowKey}
          onSelectionChange={handleSelectionChange}
        />
      );

      const rowCheckboxes = screen.getAllByRole('checkbox');
      fireEvent.click(rowCheckboxes[1]);

      expect(handleSelectionChange).toHaveBeenCalledWith(['custom-1']);
    });
  });

  describe('Props: striped', () => {
    it('striped=trueの場合、交互に背景色が適用されること', () => {
      render(<Table columns={testColumns} data={testData} striped />);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const rows = tbody?.querySelectorAll('tr');

      expect(rows?.[0]).not.toHaveClass('bg-neutral-50');
      expect(rows?.[1]).toHaveClass('bg-neutral-50');
      expect(rows?.[2]).not.toHaveClass('bg-neutral-50');
    });
  });

  describe('Props: hoverable', () => {
    it('デフォルトでhoverable=trueであること', () => {
      render(<Table columns={testColumns} data={testData} />);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const firstRow = tbody?.querySelector('tr');
      expect(firstRow).toHaveClass('hover:bg-primary-50');
    });

    it('hoverable=falseの場合、ホバースタイルが適用されないこと', () => {
      render(<Table columns={testColumns} data={testData} hoverable={false} />);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const firstRow = tbody?.querySelector('tr');
      expect(firstRow).not.toHaveClass('hover:bg-primary-50');
    });
  });

  describe('Props: className', () => {
    it('カスタムclassNameが適用されること', () => {
      const { container } = render(
        <Table columns={testColumns} data={testData} className="custom-table" />
      );

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('custom-table');
    });
  });

  describe('カラム設定', () => {
    it('カラムにwidth指定がある場合、スタイルが適用されること', () => {
      const columnsWithWidth: ColumnDef<TestData>[] = [
        { key: 'name', title: '名前', width: '200px' },
        { key: 'age', title: '年齢' },
        { key: 'city', title: '都市' },
      ];
      render(<Table columns={columnsWithWidth} data={testData} />);

      const nameHeader = screen.getByText('名前').closest('th');
      expect(nameHeader).toHaveStyle({ width: '200px' });
    });

    it('カラムにalign指定がある場合、セルに適用されること', () => {
      const columnsWithAlign: ColumnDef<TestData>[] = [
        { key: 'name', title: '名前', align: 'left' },
        { key: 'age', title: '年齢', align: 'center' },
        { key: 'city', title: '都市', align: 'right' },
      ];
      render(<Table columns={columnsWithAlign} data={testData} />);

      const headers = screen.getAllByRole('columnheader');
      expect(headers[0]).toHaveClass('text-left');
      expect(headers[1]).toHaveClass('text-center');
      expect(headers[2]).toHaveClass('text-right');
    });

    it('カラムにrenderがある場合、カスタムレンダリングされること', () => {
      const columnsWithRender: ColumnDef<TestData>[] = [
        { key: 'name', title: '名前' },
        {
          key: 'age',
          title: '年齢',
          render: (value) => <span data-testid="custom-age">{value}歳</span>,
        },
        { key: 'city', title: '都市' },
      ];
      render(<Table columns={columnsWithRender} data={testData} />);

      const customAges = screen.getAllByTestId('custom-age');
      expect(customAges[0]).toHaveTextContent('30歳');
    });
  });

  describe('アクセシビリティ', () => {
    it('ソートされたカラムにaria-sort属性が設定されること', () => {
      render(<Table columns={testColumns} data={testData} sortable />);
      const ageHeader = screen.getByText('年齢').closest('th');
      fireEvent.click(ageHeader!);

      expect(ageHeader).toHaveAttribute('aria-sort', 'ascending');
    });

    it('降順ソート時にaria-sort="descending"が設定されること', () => {
      render(<Table columns={testColumns} data={testData} sortable />);
      const ageHeader = screen.getByText('年齢').closest('th');
      fireEvent.click(ageHeader!);
      fireEvent.click(ageHeader!);

      expect(ageHeader).toHaveAttribute('aria-sort', 'descending');
    });

    it('チェックボックスにaria-labelが設定されていること', () => {
      render(<Table columns={testColumns} data={testData} selectable />);
      const checkboxes = screen.getAllByRole('checkbox');

      expect(checkboxes[0]).toHaveAttribute('aria-label', 'すべての行を選択');
      expect(checkboxes[1]).toHaveAttribute('aria-label', '行1を選択');
    });
  });

  describe('選択状態のスタイル', () => {
    it('選択された行に選択スタイルが適用されること', () => {
      render(<Table columns={testColumns} data={testData} selectable selectedKeys={['1']} />);

      const tbody = screen.getByRole('table').querySelector('tbody');
      const firstRow = tbody?.querySelector('tr');
      expect(firstRow).toHaveClass('bg-primary-100');
    });
  });

  describe('null/undefinedの値の扱い', () => {
    it('null値が"-"として表示されること', () => {
      interface NullableData {
        id: number;
        name: string | null;
      }
      const nullableColumns: ColumnDef<NullableData>[] = [
        { key: 'id', title: 'ID' },
        { key: 'name', title: '名前' },
      ];
      const nullableData: NullableData[] = [{ id: 1, name: null }];

      render(<Table columns={nullableColumns} data={nullableData} />);
      expect(screen.getByText('-')).toBeInTheDocument();
    });
  });
});
