import { Edit, SimpleForm, TextInput } from 'react-admin';

export const MultiplierEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput
        source="values"
        label="Values (JSON array)"
        fullWidth
        multiline
        format={(v) => (typeof v === 'string' ? v : JSON.stringify(v))}
        parse={(v) => {
          try { return JSON.parse(v); } catch { return v; }
        }}
        helperText="e.g. [1.8, 1.6, 1.4]"
      />
    </SimpleForm>
  </Edit>
);
