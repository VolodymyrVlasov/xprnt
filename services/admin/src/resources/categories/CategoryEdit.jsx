import { Edit, SimpleForm, TextInput } from 'react-admin';

export const CategoryEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" fullWidth />
      <TextInput source="description" fullWidth multiline />
      <TextInput source="classifier" />
    </SimpleForm>
  </Edit>
);
