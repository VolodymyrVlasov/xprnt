import { Datagrid, FunctionField, List, TextField } from 'react-admin';

export const MultiplierList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <FunctionField
        label="Values"
        render={(r) =>
          r.values ? JSON.stringify(r.values) : ''
        }
      />
    </Datagrid>
  </List>
);
