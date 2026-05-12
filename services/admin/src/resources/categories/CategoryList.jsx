import { Datagrid, List, TextField } from 'react-admin';

export const CategoryList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="name" />
      <TextField source="classifier" />
      <TextField source="description" />
    </Datagrid>
  </List>
);
