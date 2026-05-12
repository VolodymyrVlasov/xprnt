import { Datagrid, DateField, EmailField, List, TextField, FunctionField } from 'react-admin';

export const UserList = () => (
  <List>
    <Datagrid rowClick="show">
      <TextField source="name" />
      <EmailField source="email" />
      <FunctionField label="Role" render={(r) => r.role?.role || r.roleId || ''} />
      <TextField source="phone1" />
      <DateField source="createdAt" showTime />
    </Datagrid>
  </List>
);
