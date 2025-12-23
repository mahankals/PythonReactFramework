'use client'

import { useEffect, useState } from 'react'
import { Save } from 'lucide-react'

// Custom Broom icon
const BroomIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L12 10" />
    <path d="M8 10h8l1 12H7l1-12z" />
    <path d="M9 14v4" />
    <path d="M12 14v4" />
    <path d="M15 14v4" />
  </svg>
)

interface ConfigItem {
  id: string
  key: string
  value: string | null
  description: string
  value_type: string
  category: string
  is_secret: boolean
  is_editable: boolean
  updated_at: string
}

interface ConfigCategory {
  category: string
  items: ConfigItem[]
}

export default function AdminSettingsPage() {
  const [categories, setCategories] = useState<ConfigCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [editedValues, setEditedValues] = useState<Record<string, string>>({})

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/admin/config/by-category`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setCategories(data)
        // Initialize edited values
        const values: Record<string, string> = {}
        data.forEach((cat: ConfigCategory) => {
          cat.items.forEach((item: ConfigItem) => {
            values[item.key] = item.value || ''
          })
        })
        setEditedValues(values)
      }
    } catch (err) {
      console.error('Failed to fetch config:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)

    try {
      const token = localStorage.getItem('token')

      // Build the configs object with only changed values
      const configs: Record<string, string> = {}
      categories.forEach((cat) => {
        cat.items.forEach((item) => {
          if (item.is_editable && editedValues[item.key] !== item.value) {
            configs[item.key] = editedValues[item.key]
          }
        })
      })

      if (Object.keys(configs).length === 0) {
        setMessage({ type: 'success', text: 'No changes to save' })
        setSaving(false)
        return
      }

      const response = await fetch(`${API_URL}/api/admin/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ configs })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to save settings')
      }

      await fetchConfig()
      setMessage({ type: 'success', text: 'Settings saved successfully' })
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to save settings' })
    } finally {
      setSaving(false)
    }
  }

  const handleClearCache = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/admin/config/clear-cache`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to clear cache')
      }

      const result = await response.json()
      await fetchConfig()
      setMessage({ type: 'success', text: result.message })
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to clear cache' })
    }
  }

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      general: 'General',
      email: 'Email / SMTP',
      security: 'Security',
      features: 'Features'
    }
    return labels[category] || category.charAt(0).toUpperCase() + category.slice(1)
  }

  const renderInput = (item: ConfigItem) => {
    const value = editedValues[item.key] || ''
    const onChange = (newValue: string) => {
      setEditedValues(prev => ({ ...prev, [item.key]: newValue }))
    }

    if (item.value_type === 'bool') {
      return (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={!item.is_editable}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none disabled:bg-gray-50 disabled:text-gray-500"
        >
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      )
    }

    if (item.value_type === 'int') {
      return (
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={!item.is_editable}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none disabled:bg-gray-50 disabled:text-gray-500"
        />
      )
    }

    return (
      <input
        type={item.is_secret ? 'password' : 'text'}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={!item.is_editable}
        placeholder={item.is_secret ? '••••••••' : ''}
        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none disabled:bg-gray-50 disabled:text-gray-500"
      />
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
        <h1 className="text-2xl font-bold">Settings</h1>
        <div className="flex gap-2">
          <button
            onClick={handleClearCache}
            className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
          >
            <BroomIcon size={16} />
            Clear Cache
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition disabled:opacity-50"
          >
            <Save size={16} />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success'
            ? 'bg-green-50 text-green-800 border border-green-200'
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <div className="space-y-6">
        {categories.map((category) => (
          <div key={category.category} className="bg-white rounded-xl border p-6">
            <h2 className="text-lg font-semibold mb-4">{getCategoryLabel(category.category)}</h2>
            <div className="space-y-4">
              {category.items.map((item) => (
                <div key={item.key} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
                  <div>
                    <label className="block text-sm font-medium">{item.key}</label>
                    {item.description && (
                      <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                    )}
                  </div>
                  <div className="md:col-span-2">
                    {renderInput(item)}
                  </div>
                </div>
              ))}
              {category.items.length === 0 && (
                <p className="text-muted-foreground">No settings in this category</p>
              )}
            </div>
          </div>
        ))}

        {categories.length === 0 && (
          <div className="bg-white rounded-xl border p-8 text-center">
            <p className="text-muted-foreground mb-4">No configuration found.</p>
            <button
              onClick={handleClearCache}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
            >
              <BroomIcon size={16} />
              Initialize Configuration
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
