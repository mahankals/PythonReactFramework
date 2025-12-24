'use client'

import { useEffect, useState } from 'react'
import { Pencil, X, UserPlus } from 'lucide-react'

interface Role {
  id: string
  name: string
  display_name: string
}

interface AdminUser {
  id: string
  email: string
  first_name: string
  last_name: string
  phone?: string
  company_name?: string
  is_active: boolean
  is_admin: boolean
  roles: Role[]
  created_at: string
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null)
  const [saving, setSaving] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)

  // Form state
  const [formFirstName, setFormFirstName] = useState('')
  const [formLastName, setFormLastName] = useState('')
  const [formPhone, setFormPhone] = useState('')
  const [formCompanyName, setFormCompanyName] = useState('')
  const [formIsActive, setFormIsActive] = useState(true)
  const [formRoles, setFormRoles] = useState<string[]>([])

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    // Get current user ID from localStorage
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        setCurrentUserId(user.id)
      } catch (e) {
        console.error('Failed to parse user from localStorage')
      }
    }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token')
      const headers = { Authorization: `Bearer ${token}` }

      const [usersRes, rolesRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/users`, { headers }),
        fetch(`${API_URL}/api/admin/rbac/roles`, { headers })
      ])

      if (usersRes.ok) setUsers(await usersRes.json())
      if (rolesRes.ok) setRoles(await rolesRes.json())
    } catch (err) {
      console.error('Failed to fetch data:', err)
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (user: AdminUser) => {
    setEditingUser(user)
    setFormFirstName(user.first_name)
    setFormLastName(user.last_name)
    setFormPhone(user.phone || '')
    setFormCompanyName(user.company_name || '')
    setFormIsActive(user.is_active)
    setFormRoles(user.roles?.map(r => r.id) || [])
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return
    setSaving(true)

    try {
      const token = localStorage.getItem('token')
      const headers = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      }

      const response = await fetch(`${API_URL}/api/admin/users/${editingUser.id}`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({
          first_name: formFirstName,
          last_name: formLastName,
          phone: formPhone || undefined,
          company_name: formCompanyName || undefined,
          is_active: formIsActive,
        })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to update user')
      }

      // Update roles
      // First, remove all current roles
      for (const role of editingUser.roles || []) {
        await fetch(`${API_URL}/api/admin/rbac/users/${editingUser.id}/roles/${role.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        })
      }

      // Then add new roles
      for (const roleId of formRoles) {
        await fetch(`${API_URL}/api/admin/rbac/users/${editingUser.id}/roles/${roleId}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` }
        })
      }

      await fetchData()
      setShowModal(false)
    } catch (err: any) {
      alert(err.message || 'Failed to update user')
    } finally {
      setSaving(false)
    }
  }

  const toggleUserActive = async (user: AdminUser) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/admin/users/${user.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !user.is_active })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to update user')
      }

      setUsers(users.map(u =>
        u.id === user.id ? { ...u, is_active: !u.is_active } : u
      ))
    } catch (err: any) {
      alert(err.message || 'Failed to update user')
    }
  }

  const toggleRole = (roleId: string) => {
    setFormRoles(prev =>
      prev.includes(roleId)
        ? prev.filter(id => id !== roleId)
        : [...prev, roleId]
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        <span className="text-sm text-muted-foreground">{users.length} users</span>
      </div>

      <div className="bg-white rounded-xl border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">User</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground hidden md:table-cell">Roles</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
              <th className="text-right px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div>
                    <p className="font-medium">{user.first_name} {user.last_name}</p>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                  </div>
                </td>
                <td className="px-4 py-3 hidden md:table-cell">
                  <div className="flex flex-wrap gap-1">
                    {user.roles?.map((role) => (
                      <span
                        key={role.id}
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                          role.name === 'admin' || role.name === 'superadmin'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {role.display_name}
                      </span>
                    ))}
                    {(!user.roles || user.roles.length === 0) && (
                      <span className="text-sm text-muted-foreground">No roles</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                    user.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  {user.id === currentUserId ? (
                    <span className="text-xs text-muted-foreground italic">You</span>
                  ) : (
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => openEditModal(user)}
                        className="p-2 text-gray-500 hover:text-primary hover:bg-gray-100 rounded-lg transition"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        onClick={() => toggleUserActive(user)}
                        className={`text-sm px-3 py-1 rounded-lg transition ${
                          user.is_active
                            ? 'text-red-600 hover:bg-red-50'
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      {showModal && editingUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">Edit User</h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input
                  type="email"
                  value={editingUser.email}
                  disabled
                  className="w-full px-4 py-2 border rounded-lg bg-gray-50 text-gray-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">First Name</label>
                  <input
                    type="text"
                    value={formFirstName}
                    onChange={(e) => setFormFirstName(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Last Name</label>
                  <input
                    type="text"
                    value={formLastName}
                    onChange={(e) => setFormLastName(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Phone</label>
                <input
                  type="tel"
                  value={formPhone}
                  onChange={(e) => setFormPhone(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Company Name</label>
                <input
                  type="text"
                  value={formCompanyName}
                  onChange={(e) => setFormCompanyName(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                />
              </div>

              <div className="flex gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formIsActive}
                    onChange={(e) => setFormIsActive(e.target.checked)}
                    className="rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span className="text-sm">Active</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Roles</label>
                <div className="border rounded-lg p-2 space-y-2 max-h-40 overflow-y-auto">
                  {roles.map((role) => (
                    <label
                      key={role.id}
                      className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={formRoles.includes(role.id)}
                        onChange={() => toggleRole(role.id)}
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                      />
                      <span className="text-sm">{role.display_name}</span>
                    </label>
                  ))}
                  {roles.length === 0 && (
                    <p className="text-sm text-muted-foreground p-2">No roles available</p>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
