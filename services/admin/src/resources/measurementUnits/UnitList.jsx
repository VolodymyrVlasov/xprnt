import { Datagrid, List, TextField } from 'react-admin';

export const UnitList = () => (
  <List>
    <Datagrid>
      <TextField source="measurementUnit" label="Unit" />
      <TextField source="classifier" />
    </Datagrid>
  </List>
);
