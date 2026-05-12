import {
  BooleanField,
  BooleanInput,
  Datagrid,
  FilterForm,
  List,
  ReferenceInput,
  SelectInput,
  TextField,
} from 'react-admin';

const productFilters = [
  <ReferenceInput source="category_id" reference="categories" label="Category" alwaysOn>
    <SelectInput optionText="name" />
  </ReferenceInput>,
  <BooleanInput source="in_stock" label="In Stock" alwaysOn />,
];

export const ProductList = () => (
  <List filters={productFilters}>
    <Datagrid rowClick="edit">
      <TextField source="name" />
      <TextField source="shortName" />
      <TextField source="categoryId" label="Category ID" />
      <BooleanField source="inStock" />
      <BooleanField source="isDeliverable" />
    </Datagrid>
  </List>
);
