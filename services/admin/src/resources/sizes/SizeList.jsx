import { Datagrid, List, NumberField, TextField } from 'react-admin';

export const SizeList = () => (
  <List>
    <Datagrid rowClick="edit">
      <NumberField source="width" />
      <NumberField source="height" />
      <NumberField source="diameter" />
      <NumberField source="volume" />
      <TextField source="unitId" label="Unit ID" />
    </Datagrid>
  </List>
);
