import {
  Create,
  NumberInput,
  ReferenceInput,
  SelectInput,
  SimpleForm,
  TextInput,
} from 'react-admin';

export const PriceCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="productId" label="Product ID (UUID)" fullWidth />
      <NumberInput source="primeCostEUR" label="Prime Cost EUR" />
      <NumberInput source="fxRateUsed" label="FX Rate Used" />
      <ReferenceInput source="priceMultiplierId" reference="price_multipliers" label="Price Multiplier">
        <SelectInput optionText="id" />
      </ReferenceInput>
      <TextInput
        source="values"
        label="Values (JSON array)"
        fullWidth
        multiline
        helperText='e.g. [{"qty": 1, "price": 100}]'
      />
    </SimpleForm>
  </Create>
);
