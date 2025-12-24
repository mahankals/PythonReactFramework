'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export default function ProfilePage() {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Redirect to appropriate profile page based on user type
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        router.replace(user.is_admin ? '/admin/profile' : '/dashboard/profile')
      } catch {
        router.replace(`/login?redirect=${encodeURIComponent(pathname)}`)
      }
    } else {
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`)
    }
  }, [router, pathname])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="animate-pulse text-muted-foreground">Redirecting...</div>
    </div>
  )
}
