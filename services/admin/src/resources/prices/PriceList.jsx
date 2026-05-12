import {
  Datagrid,
  DateField,
  List,
  NumberField,
  TextInput,
  FilterForm,
} from 'react-admin';

const priceFilters = [
  <TextInput source="product_id" label="Product ID (required)" alwaysOn />,
];

export const PriceList = () => (
  <List filters={priceFilters} empty={<p style={{ padding: 16 }}>Enter a Product ID to load prices.</p>}>
    <Datagrid>
      <DateField source="startAt" showTime />
      <DateField source="finishAt" showTime emptyText="Active" />
      <NumberField source="primeCostEUR" options={{ style: 'decimal', minimumFractionDigits: 4 }} />
      <NumberField source="fxRateUsed" options={{ style: 'decimal', minimumFractionDigits: 6 }} />
    </Datagrid>
  </List>
);
