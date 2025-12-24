'use client'

import { useState } from 'react'
import { User, Lock, Save } from 'lucide-react'

interface UserProfile {
  id: string
  email: string
  first_name: string
  last_name: string
  phone: string | null
  company_name: string | null
  is_admin: boolean
}

interface ProfileContentProps {
  user: UserProfile
  onUserUpdate: (user: UserProfile) => void
}

export default function ProfileContent({ user, onUserUpdate }: ProfileContentProps) {
  // Profile form state
  const [firstName, setFirstName] = useState(user.first_name)
  const [lastName, setLastName] = useState(user.last_name)
  const [phone, setPhone] = useState(user.phone || '')
  const [companyName, setCompanyName] = useState(user.company_name || '')
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Password form state
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordSaving, setPasswordSaving] = useState(false)
  const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileSaving(true)
    setProfileMessage(null)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/auth/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          phone: phone || null,
          company_name: companyName || null
        })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to update profile')
      }

      const updatedUser = await response.json()
      localStorage.setItem('user', JSON.stringify(updatedUser))
      onUserUpdate(updatedUser)
      setProfileMessage({ type: 'success', text: 'Profile updated successfully' })
    } catch (err: any) {
      setProfileMessage({ type: 'error', text: err.message || 'Failed to update profile' })
    } finally {
      setProfileSaving(false)
    }
  }

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordSaving(true)
    setPasswordMessage(null)

    if (newPassword !== confirmPassword) {
      setPasswordMessage({ type: 'error', text: 'New passwords do not match' })
      setPasswordSaving(false)
      return
    }

    if (newPassword.length < 8) {
      setPasswordMessage({ type: 'error', text: 'Password must be at least 8 characters' })
      setPasswordSaving(false)
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${API_URL}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to change password')
      }

      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setPasswordMessage({ type: 'success', text: 'Password changed successfully' })
    } catch (err: any) {
      setPasswordMessage({ type: 'error', text: err.message || 'Failed to change password' })
    } finally {
      setPasswordSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Profile Settings</h1>

      {/* Two column layout - stacks on mobile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Details - Left Column */}
        <div className="bg-white rounded-xl border overflow-hidden">
          <div className="flex items-center gap-2 px-6 py-4 border-b bg-gray-50">
            <User size={18} className="text-primary" />
            <h2 className="font-semibold">Profile Details</h2>
          </div>
          <form onSubmit={handleProfileSubmit} className="p-6 space-y-4">
            {profileMessage && (
              <div className={`p-3 rounded-lg text-sm ${
                profileMessage.type === 'success'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}>
                {profileMessage.text}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={user.email}
                disabled
                className="w-full px-4 py-2 border rounded-lg bg-gray-50 text-gray-500"
              />
              <p className="text-xs text-muted-foreground mt-1">Email cannot be changed</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">First Name</label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Last Name</label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Phone</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="Optional"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Company Name</label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="Optional"
              />
            </div>

            <button
              type="submit"
              disabled={profileSaving}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition disabled:opacity-50"
            >
              <Save size={18} />
              {profileSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>

        {/* Change Password - Right Column */}
        <div className="bg-white rounded-xl border overflow-hidden h-fit">
          <div className="flex items-center gap-2 px-6 py-4 border-b bg-gray-50">
            <Lock size={18} className="text-primary" />
            <h2 className="font-semibold">Change Password</h2>
          </div>
          <form onSubmit={handlePasswordSubmit} className="p-6 space-y-4">
            {passwordMessage && (
              <div className={`p-3 rounded-lg text-sm ${
                passwordMessage.type === 'success'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}>
                {passwordMessage.text}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1">Current Password</label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="At least 8 characters"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                required
              />
            </div>

            <button
              type="submit"
              disabled={passwordSaving}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition disabled:opacity-50"
            >
              <Lock size={18} />
              {passwordSaving ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
