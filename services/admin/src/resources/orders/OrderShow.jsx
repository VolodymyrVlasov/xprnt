import {
  ArrayField,
  ChipField,
  Datagrid,
  DateField,
  FunctionField,
  NumberField,
  Show,
  SimpleShowLayout,
  SingleFieldList,
  TextField,
} from 'react-admin';

export const OrderShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="orderNumberId" label="Order Number ID" />
      <TextField source="status" />
      <NumberField source="totalPrice" />
      <TextField source="currency" />
      <TextField source="companyId" label="Company ID" />
      <TextField source="customerId" label="Customer ID" />
      <TextField source="sellerId" label="Seller ID" />
      <DateField source="createdAt" showTime />
      <DateField source="finishAt" showTime />
      <DateField source="doneAt" showTime />
      <FunctionField
        label="Cart Items"
        render={(record) => {
          const items = record.cart?.items;
          if (!items || !items.length) return 'No items';
          return (
            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr>
                  {['Name', 'Amount', 'Unit Price', 'Total Price'].map((h) => (
                    <th key={h} style={{ border: '1px solid #ccc', padding: '4px 8px' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td style={{ border: '1px solid #ccc', padding: '4px 8px' }}>{item.name}</td>
                    <td style={{ border: '1px solid #ccc', padding: '4px 8px' }}>{item.amount}</td>
                    <td style={{ border: '1px solid #ccc', padding: '4px 8px' }}>{item.unitPrice}</td>
                    <td style={{ border: '1px solid #ccc', padding: '4px 8px' }}>{item.totalPrice}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          );
        }}
      />
    </SimpleShowLayout>
  </Show>
);
