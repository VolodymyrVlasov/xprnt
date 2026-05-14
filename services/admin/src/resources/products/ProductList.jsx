import { useRef } from 'react';
import {
  BooleanField,
  BooleanInput,
  Datagrid,
  List,
  ReferenceInput,
  SelectInput,
  TextField,
  useRefresh,
} from 'react-admin';

const productFilters = [
  <ReferenceInput source="category_id" reference="categories" label="Category" alwaysOn>
    <SelectInput optionText="name" />
  </ReferenceInput>,
  <BooleanInput source="in_stock" label="In Stock" alwaysOn />,
];

const ImportButton = () => {
  const refresh = useRefresh();
  const inputRef = useRef(null);

  const handleClick = () => {
    inputRef.current.value = '';
    inputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/products/import', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        alert(`Import failed: ${err.detail || res.statusText}`);
        return;
      }

      const report = await res.json();
      let msg = `Import complete: ${report.created} created, ${report.skipped} skipped, ${report.errors} errors`;
      if (report.errors > 0) {
        const errorLines = report.rows
          .filter((r) => r.status === 'error')
          .map((r) => `  Row ${r.row}: ${r.reason}`)
          .join('\n');
        msg += `\n\nErrors:\n${errorLines}`;
      }
      alert(msg);
      refresh();
    } catch (err) {
      alert(`Import failed: ${err.message}`);
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <button
        onClick={handleClick}
        style={{
          marginLeft: '8px',
          padding: '6px 16px',
          background: '#1976d2',
          color: '#fff',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '0.875rem',
          fontWeight: 500,
        }}
      >
        Import CSV / XLSX
      </button>
    </>
  );
};

export const ProductList = () => (
  <List filters={productFilters} actions={<ListActions />}>
    <Datagrid rowClick="edit">
      <TextField source="name" />
      <TextField source="shortName" />
      <TextField source="categoryId" label="Category ID" />
      <BooleanField source="inStock" />
      <BooleanField source="isDeliverable" />
    </Datagrid>
  </List>
);

import { TopToolbar, CreateButton, ExportButton } from 'react-admin';

const ListActions = () => (
  <TopToolbar>
    <CreateButton />
    <ExportButton />
    <ImportButton />
  </TopToolbar>
);
