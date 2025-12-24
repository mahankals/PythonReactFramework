'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import ProfileContent from '@/components/ProfileContent'

interface UserProfile {
  id: string
  email: string
  first_name: string
  last_name: string
  phone: string | null
  company_name: string | null
  is_admin: boolean
}

export default function AdminProfilePage() {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<UserProfile | null>(null)

  useEffect(() => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const userData = JSON.parse(userStr)
        // If not admin, redirect to dashboard profile
        if (!userData.is_admin) {
          router.push('/dashboard/profile')
          return
        }
        setUser(userData)
      } catch {
        router.push(`/login?redirect=${encodeURIComponent(pathname)}`)
      }
    }
  }, [router, pathname])

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return <ProfileContent user={user} onUserUpdate={setUser} />
}
