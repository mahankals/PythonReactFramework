'use client'

import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, X, Shield } from 'lucide-react'

interface Permission {
  id: string
  name: string
  display_name: string
  resource: string
  action: string
}

interface Role {
  id: string
  name: string
  display_name: string
  description: string
  is_system: boolean
  is_active: boolean
  permissions: Permission[]
  created_at: string
}

export default function AdminRolesPage() {
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingRole, setEditingRole] = useState<Role | null>(null)
  const [saving, setSaving] = useState(false)

  // Form state
  const [formName, setFormName] = useState('')
  const [formDisplayName, setFormDisplayName] = useState('')
  const [formDescription, setFormDescription] = useState('')
  const [formPermissions, setFormPermissions] = useState<string[]>([])

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token')
      const headers = { Authorization: `Bearer ${token}` }

      const [rolesRes, permsRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/rbac/roles`, { headers }),
        fetch(`${API_URL}/api/admin/rbac/permissions`, { headers })
      ])

      if (rolesRes.ok) setRoles(await rolesRes.json())
      if (permsRes.ok) setPermissions(await permsRes.json())
    } catch (err) {
      console.error('Failed to fetch data:', err)
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setEditingRole(null)
    setFormName('')
    setFormDisplayName('')
    setFormDescription('')
    setFormPermissions([])
    setShowModal(true)
  }

  const openEditModal = (role: Role) => {
    setEditingRole(role)
    setFormName(role.name)
    setFormDisplayName(role.display_name)
    setFormDescription(role.description || '')
    setFormPermissions(role.permissions.map(p => p.id))
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      const token = localStorage.getItem('token')
      const headers = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      }

      const body = {
        name: formName,
        display_name: formDisplayName,
        description: formDescription || undefined,
        permission_ids: formPermissions
      }

      let response
      if (editingRole) {
        response = await fetch(`${API_URL}/api/admin/rbac/roles/${editingRole.id}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(body)
        })
      } else {
        response = await fetch(`${API_URL}/api/admin/rbac/roles`, {
          method: 'POST',
          headers,
          body: JSON.stringify(body)
        })
      }

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to save role')
      }

      await fetchData()
      setShowModal(false)
    } catch (err: any) {
      alert(err.message || 'Failed to save role')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (role: Role) => {
    if (role.is_system) {
      alert('Cannot delete system roles')
      return
    }

    if (!confirm(`Are you sure you want to delete the role "${role.display_name}"?`)) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/admin/rbac/roles/${role.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to delete role')
      }

      await fetchData()
    } catch (err: any) {
      alert(err.message || 'Failed to delete role')
    }
  }

  const togglePermission = (permId: string) => {
    setFormPermissions(prev =>
      prev.includes(permId)
        ? prev.filter(id => id !== permId)
        : [...prev, permId]
    )
  }

  // Group permissions by resource
  const groupedPermissions = permissions.reduce((acc, perm) => {
    if (!acc[perm.resource]) acc[perm.resource] = []
    acc[perm.resource].push(perm)
    return acc
  }, {} as Record<string, Permission[]>)

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
        <h1 className="text-2xl font-bold">Roles</h1>
        <button
          onClick={openCreateModal}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
        >
          <Plus size={18} />
          Add Role
        </button>
      </div>

      <div className="bg-white rounded-xl border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Role</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground hidden md:table-cell">Permissions</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
              <th className="text-right px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {roles.map((role) => (
              <tr key={role.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Shield size={16} className="text-primary" />
                    <div>
                      <p className="font-medium">{role.display_name}</p>
                      <p className="text-sm text-muted-foreground">{role.name}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 hidden md:table-cell">
                  <span className="text-sm text-muted-foreground">
                    {role.permissions.length} permissions
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    {role.is_system && (
                      <span className="inline-flex px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        System
                      </span>
                    )}
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      role.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {role.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => openEditModal(role)}
                      className="p-2 text-gray-500 hover:text-primary hover:bg-gray-100 rounded-lg transition"
                    >
                      <Pencil size={16} />
                    </button>
                    {!role.is_system && (
                      <button
                        onClick={() => handleDelete(role)}
                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">
                {editingRole ? 'Edit Role' : 'Create Role'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name (slug)</label>
                  <input
                    type="text"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value.toLowerCase().replace(/\s+/g, '_'))}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    placeholder="e.g., manager"
                    required
                    disabled={editingRole?.is_system}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Display Name</label>
                  <input
                    type="text"
                    value={formDisplayName}
                    onChange={(e) => setFormDisplayName(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                    placeholder="e.g., Manager"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                  rows={2}
                  placeholder="Optional description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Permissions</label>
                <div className="border rounded-lg max-h-64 overflow-y-auto">
                  {Object.entries(groupedPermissions).map(([resource, perms]) => (
                    <div key={resource} className="border-b last:border-b-0">
                      <div className="px-4 py-2 bg-gray-50 font-medium text-sm capitalize">
                        {resource}
                      </div>
                      <div className="p-2 grid grid-cols-2 gap-2">
                        {perms.map((perm) => (
                          <label
                            key={perm.id}
                            className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={formPermissions.includes(perm.id)}
                              onChange={() => togglePermission(perm.id)}
                              className="rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <span className="text-sm">{perm.display_name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                  {Object.keys(groupedPermissions).length === 0 && (
                    <div className="p-4 text-center text-muted-foreground">
                      No permissions available
                    </div>
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
                  {saving ? 'Saving...' : editingRole ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
