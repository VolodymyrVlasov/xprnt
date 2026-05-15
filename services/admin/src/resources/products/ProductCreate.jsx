import {
  BooleanInput,
  Create,
  ReferenceInput,
  SelectInput,
  SimpleForm,
  TextInput,
} from 'react-admin';

const transformProduct = (data) => ({
  name: data.name,
  shortName: data.shortName || null,
  description: data.description || null,
  category_id: data.categoryId || data.category_id,
  measurement_unit_id: data.measurementUnitId || data.measurement_unit_id,
  isDeliverable: data.isDeliverable ?? true,
  inStock: data.inStock ?? true,
});

export const ProductCreate = () => (
  <Create transform={transformProduct}>
    <SimpleForm>
      <TextInput source="name" fullWidth />
      <TextInput source="shortName" />
      <TextInput source="description" fullWidth multiline />
      <ReferenceInput source="categoryId" reference="categories">
        <SelectInput optionText="name" />
      </ReferenceInput>
      <ReferenceInput source="measurementUnitId" reference="measurement_units" label="Measurement Unit">
        <SelectInput optionText="measurementUnit" />
      </ReferenceInput>
      <BooleanInput source="inStock" defaultValue={true} />
      <BooleanInput source="isDeliverable" />
    </SimpleForm>
  </Create>
);
