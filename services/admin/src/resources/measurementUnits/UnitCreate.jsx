import { Create, SimpleForm, TextInput } from 'react-admin';

export const UnitCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="measurementUnit" label="Unit" fullWidth />
      <TextInput source="classifier" fullWidth />
    </SimpleForm>
  </Create>
);
