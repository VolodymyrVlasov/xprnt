import { useRef } from 'react';
import {
  BooleanField,
  BooleanInput,
  CreateButton,
  Datagrid,
  List,
  ReferenceInput,
  SelectInput,
  TextField,
  TopToolbar,
  useNotify,
  useRefresh,
} from 'react-admin';
import { Button } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const productFilters = [
  <ReferenceInput source="category_id" reference="categories" label="Category" alwaysOn>
    <SelectInput optionText="name" />
  </ReferenceInput>,
  <BooleanInput source="in_stock" label="In Stock" alwaysOn />,
];

const ProductListActions = () => {
  const refresh = useRefresh();
  const notify = useNotify();
  const fileInputRef = useRef(null);

  const handleImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    event.target.value = '';

    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/products/import', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) {
        notify(`Import failed: ${data.detail || res.statusText}`, { type: 'error' });
        return;
      }

      const { created, updated, skipped, errors, rows } = data;
      let msg = `Import complete: ${created} created, ${updated} updated, ${skipped} skipped, ${errors} errors`;

      if (errors > 0) {
        const errLines = rows
          .filter(r => r.action === 'error')
          .map(r => `Row ${r.row}: ${r.reason}`)
          .join('\n');
        msg += `\n\nErrors:\n${errLines}`;
      }

      alert(msg);
      refresh();
    } catch (err) {
      notify(`Import error: ${err.message}`, { type: 'error' });
    }
  };

  return (
    <TopToolbar>
      <CreateButton />
      <Button
        size="small"
        startIcon={<UploadFileIcon />}
        onClick={() => fileInputRef.current.click()}
      >
        Import CSV
      </Button>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx"
        style={{ display: 'none' }}
        onChange={handleImport}
      />
    </TopToolbar>
  );
};

export const ProductList = () => (
  <List filters={productFilters} actions={<ProductListActions />}>
    <Datagrid rowClick="edit">
      <TextField source="name" />
      <TextField source="shortName" />
      <TextField source="categoryId" label="Category ID" />
      <BooleanField source="inStock" />
      <BooleanField source="isDeliverable" />
    </Datagrid>
  </List>
);
