import { Create, SimpleForm, TextInput } from 'react-admin';

export const MultiplierCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput
        source="values"
        label="Values (JSON array)"
        fullWidth
        multiline
        parse={(v) => {
          try { return JSON.parse(v); } catch { return v; }
        }}
        helperText="e.g. [1.8, 1.6, 1.4]"
      />
    </SimpleForm>
  </Create>
);
