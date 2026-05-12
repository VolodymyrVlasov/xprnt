import { Datagrid, EmailField, List, TextField } from 'react-admin';

export const CompanyList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="name" />
      <TextField source="edrpouCode" />
      <EmailField source="email" />
      <TextField source="phone1" />
    </Datagrid>
  </List>
);
