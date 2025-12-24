'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import {
  LogOut,
  Menu,
  X,
  LayoutDashboard,
  Users,
  UserCircle
} from 'lucide-react'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<User | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')

    if (!token) {
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`)
      return
    }

    // Always validate token with API
    const validateAndFetchUser = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Invalid token')
        const userData = await response.json()
        localStorage.setItem('user', JSON.stringify(userData))

        // Admin users should use admin dashboard
        if (userData.is_admin) {
          router.push('/admin')
          return
        }

        setUser(userData)
      } catch {
        // Token invalid, clear and redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push(`/login?redirect=${encodeURIComponent(pathname)}`)
      }
    }
    validateAndFetchUser()
  }, [router, pathname])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ]

  const adminItems = [
    { href: '/admin', icon: LayoutDashboard, label: 'Admin Panel' },
  ]

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white border-r transform transition-transform duration-200
        lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-6 border-b">
            <Link href="/dashboard" className="text-xl font-bold text-primary">
              SampleApp
            </Link>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 hover:bg-gray-100 rounded"
            >
              <X size={20} />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition
                  ${pathname === item.href 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-gray-600 hover:bg-gray-100'
                  }
                `}
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            ))}

            {/* Admin section - commented out as admin users redirect to admin dashboard
            {user.is_admin && (
              <>
                <div className="pt-4 pb-2">
                  <p className="px-3 text-xs font-semibold text-gray-400 uppercase">
                    Admin
                  </p>
                </div>
                {adminItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`
                      flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition
                      ${pathname === item.href
                        ? 'bg-primary/10 text-primary'
                        : 'text-gray-600 hover:bg-gray-100'
                      }
                    `}
                  >
                    <item.icon size={18} />
                    {item.label}
                  </Link>
                ))}
              </>
            )}
            */}
          </nav>

          {/* User section */}
          <div className="p-4 border-t">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-primary font-medium">
                  {user.first_name[0]}{user.last_name[0]}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user.email}
                </p>
              </div>
            </div>
            <div className="space-y-1">
              <Link
                href="/dashboard/profile"
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <UserCircle size={18} />
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <LogOut size={18} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="h-16 bg-white border-b flex items-center px-4 lg:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
          >
            <Menu size={20} />
          </button>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
