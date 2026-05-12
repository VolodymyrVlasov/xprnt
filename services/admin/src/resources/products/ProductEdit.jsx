import {
  BooleanInput,
  Edit,
  ReferenceInput,
  SelectInput,
  SimpleForm,
  TextInput,
} from 'react-admin';

export const ProductEdit = () => (
  <Edit>
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
      <BooleanInput source="inStock" />
      <BooleanInput source="isDeliverable" />
    </SimpleForm>
  </Edit>
);
