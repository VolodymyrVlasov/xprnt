const BASE_URL = '/api/v1';

function getToken() {
  return localStorage.getItem('token') || '';
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getToken()}`,
  };
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

// Map resource names to API paths
function resourcePath(resource) {
  const map = {
    users: '/users/',
    companies: '/companies/',
    categories: '/categories/',
    products: '/products/',
    prices: '/prices/',
    price_multipliers: '/price-multipliers/',
    orders: '/orders/',
    sizes: '/references/sizes',
    measurement_units: '/references/measurement-units',
  };
  return map[resource];
}

const dataProvider = {
  getList: async (resource, params) => {
    const { pagination = {}, filter = {} } = params;
    const { page = 1, perPage = 25 } = pagination;
    const skip = (page - 1) * perPage;
    const limit = perPage;

    if (resource === 'prices') {
      if (!filter.product_id) {
        return { data: [], total: 0 };
      }
      const data = await apiFetch(`/prices/product/${filter.product_id}`);
      const list = Array.isArray(data) ? data : [];
      return { data: list.map(normalizeId), total: list.length };
    }

    let path = resourcePath(resource);
    const qs = new URLSearchParams({ skip, limit });

    if (resource === 'products') {
      if (filter.category_id) qs.set('category_id', filter.category_id);
      if (filter.in_stock !== undefined) qs.set('in_stock', filter.in_stock);
    }
    if (resource === 'orders') {
      if (filter.status) qs.set('status', filter.status);
    }

    // sizes supports unit_id filter
    if (resource === 'sizes' && filter.unit_id) {
      qs.set('unit_id', filter.unit_id);
    }

    const data = await apiFetch(`${path}?${qs}`);
    const list = Array.isArray(data) ? data : [];
    return { data: list.map(normalizeId), total: list.length };
  },

  getOne: async (resource, params) => {
    let path;
    if (resource === 'sizes') {
      path = `/references/sizes/${params.id}`;
    } else if (resource === 'measurement_units') {
      // no getOne endpoint — return from list
      const list = await apiFetch('/references/measurement-units');
      const item = list.find((u) => u.id === params.id);
      return { data: normalizeId(item || { id: params.id }) };
    } else if (resource === 'prices') {
      path = `/prices/${params.id}`;
    } else {
      path = `${resourcePath(resource)}${params.id}`;
    }
    const data = await apiFetch(path);
    return { data: normalizeId(data) };
  },

  getMany: async (resource, params) => {
    const results = await Promise.all(
      params.ids.map(async (id) => {
        try {
          const { data } = await dataProvider.getOne(resource, { id });
          return data;
        } catch {
          return { id };
        }
      })
    );
    return { data: results };
  },

  getManyReference: async (resource, params) => {
    return dataProvider.getList(resource, {
      pagination: params.pagination,
      sort: params.sort,
      filter: { ...params.filter, [params.target]: params.id },
    });
  },

  create: async (resource, params) => {
    let path;
    if (resource === 'sizes') path = '/references/sizes';
    else if (resource === 'measurement_units') path = '/references/measurement-units';
    else path = resourcePath(resource);

    const data = await apiFetch(path, {
      method: 'POST',
      body: JSON.stringify(params.data),
    });
    return { data: normalizeId(data) };
  },

  update: async (resource, params) => {
    let path;
    if (resource === 'sizes') path = `/references/sizes/${params.id}`;
    else path = `${resourcePath(resource)}${params.id}`;

    const data = await apiFetch(path, {
      method: 'PUT',
      body: JSON.stringify(params.data),
    });
    return { data: normalizeId(data) };
  },

  updateMany: async (resource, params) => {
    const results = await Promise.all(
      params.ids.map((id) =>
        dataProvider.update(resource, { id, data: params.data })
      )
    );
    return { data: results.map((r) => r.data.id) };
  },

  delete: async (resource, params) => {
    const path = `${resourcePath(resource)}${params.id}`;
    await apiFetch(path, { method: 'DELETE' });
    return { data: { id: params.id } };
  },

  deleteMany: async (resource, params) => {
    await Promise.all(
      params.ids.map((id) => dataProvider.delete(resource, { id }))
    );
    return { data: params.ids };
  },
};

function normalizeId(record) {
  if (!record) return record;
  // react-admin needs an `id` field
  return { ...record, id: record.id || record.uuid };
}

export default dataProvider;
