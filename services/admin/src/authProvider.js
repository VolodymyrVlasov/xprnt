const BASE_URL = '/api/v1';

function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
}

const authProvider = {
  login: async ({ username, password }) => {
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: username, password }),
    });
    if (!response.ok) {
      throw new Error('Invalid credentials');
    }
    const data = await response.json();
    const token = data.access_token;
    localStorage.setItem('token', token);
    const payload = parseJwt(token);
    const role = payload?.role || payload?.roles?.[0] || '';
    localStorage.setItem('role', role);
  },

  logout: async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
    }
  },

  checkAuth: () => {
    return localStorage.getItem('token')
      ? Promise.resolve()
      : Promise.reject();
  },

  checkError: ({ status }) => {
    if (status === 401 || status === 403) {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      return Promise.reject();
    }
    return Promise.resolve();
  },

  getPermissions: () => {
    const role = localStorage.getItem('role');
    return Promise.resolve(role || '');
  },

  getIdentity: async () => {
    const token = localStorage.getItem('token');
    if (!token) return Promise.reject();
    const response = await fetch(`${BASE_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return Promise.reject();
    const user = await response.json();
    return { id: user.id, fullName: user.name, avatar: null };
  },
};

export default authProvider;
