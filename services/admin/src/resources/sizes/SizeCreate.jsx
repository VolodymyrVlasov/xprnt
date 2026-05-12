import { Create, NumberInput, ReferenceInput, SelectInput, SimpleForm } from 'react-admin';

export const SizeCreate = () => (
  <Create>
    <SimpleForm>
      <ReferenceInput source="unitId" reference="measurement_units" label="Measurement Unit">
        <SelectInput optionText="measurementUnit" />
      </ReferenceInput>
      <NumberInput source="width" />
      <NumberInput source="height" />
      <NumberInput source="diameter" />
      <NumberInput source="radius" />
      <NumberInput source="volume" />
      <NumberInput source="rollWidth" />
      <NumberInput source="tShirtSizeEU" label="T-Shirt Size EU" />
      <NumberInput source="tShirtSizeAge" label="T-Shirt Size Age" />
    </SimpleForm>
  </Create>
);
