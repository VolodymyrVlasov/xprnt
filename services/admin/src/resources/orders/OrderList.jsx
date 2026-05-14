import {
  Datagrid,
  DateField,
  List,
  NumberField,
  SelectInput,
  TextField,
  FunctionField,
} from 'react-admin';

const ORDER_STATUSES = [
  'pending', 'paid', 'execution', 'printing', 'printed',
  'postprint', 'done', 'waiting_delivery', 'shipped',
  'successful', 'canceled', 'returned',
].map((s) => ({ id: s, name: s }));

const orderFilters = [
  <SelectInput source="status" choices={ORDER_STATUSES} alwaysOn />,
];

export const OrderList = () => (
  <List filters={orderFilters}>
    <Datagrid rowClick="show">
      <FunctionField label="Order #" render={(r) => r.orderNumberId || r.id?.slice(0, 8)} />
      <TextField source="status" />
      <NumberField source="totalPrice" options={{ style: 'decimal', minimumFractionDigits: 2 }} />
      <TextField source="currency" />
      <TextField source="companyId" label="Company ID" />
      <DateField source="createdAt" showTime />
    </Datagrid>
  </List>
);
