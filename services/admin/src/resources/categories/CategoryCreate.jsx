import { Create, SimpleForm, TextInput } from 'react-admin';

export const CategoryCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" fullWidth />
      <TextInput source="description" fullWidth multiline />
      <TextInput source="classifier" />
    </SimpleForm>
  </Create>
);
