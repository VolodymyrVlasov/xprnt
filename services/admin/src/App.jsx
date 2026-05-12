import { Admin, Resource } from 'react-admin';
import authProvider from './authProvider';
import dataProvider from './dataProvider';

import { UserList } from './resources/users/UserList';
import { UserShow } from './resources/users/UserShow';

import { CompanyList } from './resources/companies/CompanyList';
import { CompanyEdit } from './resources/companies/CompanyEdit';

import { CategoryList } from './resources/categories/CategoryList';
import { CategoryEdit } from './resources/categories/CategoryEdit';
import { CategoryCreate } from './resources/categories/CategoryCreate';

import { ProductList } from './resources/products/ProductList';
import { ProductEdit } from './resources/products/ProductEdit';
import { ProductCreate } from './resources/products/ProductCreate';

import { PriceList } from './resources/prices/PriceList';
import { PriceCreate } from './resources/prices/PriceCreate';

import { MultiplierList } from './resources/priceMultipliers/MultiplierList';
import { MultiplierEdit } from './resources/priceMultipliers/MultiplierEdit';
import { MultiplierCreate } from './resources/priceMultipliers/MultiplierCreate';

import { OrderList } from './resources/orders/OrderList';
import { OrderShow } from './resources/orders/OrderShow';

import { SizeList } from './resources/sizes/SizeList';
import { SizeEdit } from './resources/sizes/SizeEdit';
import { SizeCreate } from './resources/sizes/SizeCreate';

import { UnitList } from './resources/measurementUnits/UnitList';
import { UnitCreate } from './resources/measurementUnits/UnitCreate';

const App = () => (
  <Admin
    authProvider={authProvider}
    dataProvider={dataProvider}
    title="xprnt admin"
    requireAuth
  >
    <Resource
      name="users"
      list={UserList}
      show={UserShow}
    />
    <Resource
      name="companies"
      list={CompanyList}
      edit={CompanyEdit}
    />
    <Resource
      name="categories"
      list={CategoryList}
      edit={CategoryEdit}
      create={CategoryCreate}
    />
    <Resource
      name="products"
      list={ProductList}
      edit={ProductEdit}
      create={ProductCreate}
    />
    <Resource
      name="prices"
      list={PriceList}
      create={PriceCreate}
    />
    <Resource
      name="price_multipliers"
      list={MultiplierList}
      edit={MultiplierEdit}
      create={MultiplierCreate}
      options={{ label: 'Price Multipliers' }}
    />
    <Resource
      name="orders"
      list={OrderList}
      show={OrderShow}
    />
    <Resource
      name="sizes"
      list={SizeList}
      edit={SizeEdit}
      create={SizeCreate}
    />
    <Resource
      name="measurement_units"
      list={UnitList}
      create={UnitCreate}
      options={{ label: 'Measurement Units' }}
    />
  </Admin>
);

export default App;
