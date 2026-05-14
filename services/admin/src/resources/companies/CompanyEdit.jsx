import { Edit, SimpleForm, TextInput } from 'react-admin';

export const CompanyEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" fullWidth />
      <TextInput source="address1" fullWidth />
      <TextInput source="address2" fullWidth />
      <TextInput source="email" fullWidth />
      <TextInput source="phone1" />
      <TextInput source="phone2" />
    </SimpleForm>
  </Edit>
);
