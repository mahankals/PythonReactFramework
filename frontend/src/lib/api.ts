const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  })
  if (!response.ok) {
    const err = await response.json().catch(()=>({detail:'API Error'}))
    throw new Error(err.detail || `HTTP ${response.status}`)
  }
  if (response.status === 204) return {} as T
  return response.json()
}

export interface User { id: string; email: string; first_name: string; last_name: string; is_admin: boolean; is_active: boolean }

export const api = {
  auth: {
    login: async (email: string, password: string) => {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password: password })
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Login failed' }))
        throw new Error(err.detail || `HTTP ${response.status}`)
      }
      return response.json()
    },
    signup: (data: any) => fetchAPI('/api/auth/signup', { method: 'POST', body: JSON.stringify(data) }),
    me: () => fetchAPI('/api/auth/me'),
    forgotPassword: (email: string) => fetchAPI('/api/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }),
    resetPassword: (token: string, new_password: string) => fetchAPI('/api/auth/reset-password', { method: 'POST', body: JSON.stringify({ token, new_password }) }),
  },
  users: {
    getProfile: () => fetchAPI('/api/users/profile'),
    updateProfile: (data: any) => fetchAPI('/api/users/profile',{method:'PATCH', body: JSON.stringify(data)}),
    changePassword: (current:string,newp:string) => fetchAPI('/api/users/change-password',{method:'POST', body: JSON.stringify({current_password:current,new_password:newp})}),
  },
  admin: {
    users: {
      list: () => fetchAPI('/api/admin/users'),
      get: (id:string) => fetchAPI(`/api/admin/users/${id}`),
      update: (id:string,data:any) => fetchAPI(`/api/admin/users/${id}`,{method:'PATCH', body: JSON.stringify(data)}),
    },
    rbac: {
      permissions: () => fetchAPI('/api/admin/rbac/permissions'),
      roles: () => fetchAPI('/api/admin/rbac/roles'),
    },
    config: {
      list: (category?: string) => fetchAPI(`/api/admin/config${category ? `?category=${category}` : ''}`),
      getByCategory: () => fetchAPI('/api/admin/config/by-category'),
      get: (key: string) => fetchAPI(`/api/admin/config/${key}`),
      update: (key: string, value: string) => fetchAPI(`/api/admin/config/${key}`, { method: 'PUT', body: JSON.stringify({ value }) }),
      bulkUpdate: (configs: Record<string, string>) => fetchAPI('/api/admin/config', { method: 'PUT', body: JSON.stringify({ configs }) }),
      seed: () => fetchAPI('/api/admin/config/seed', { method: 'POST' }),
    }
  }
}

export default api
