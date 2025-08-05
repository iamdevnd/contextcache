export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'ContextCache',
  appDescription: 'Persistent, explainable, modular AI memory with graphs, ranking, and full local control.',
  isProduction: process.env.NODE_ENV === 'production',
};

// Show a message if API is not configured
if (config.isProduction && config.apiUrl === 'http://localhost:8000') {
  console.warn('API URL not configured for production');
}

export const endpoints = {
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
    me: '/api/auth/me',
  },
  memory: {
    insert: '/api/memory/insert',
    query: '/api/memory/query',
    export: '/api/memory/export',
  },
  admin: {
    config: '/api/admin/config',
    logs: '/api/admin/logs',
    reset: '/api/admin/reset-memory',
  },
  health: '/health',
};
