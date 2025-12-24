'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [redirectUrl, setRedirectUrl] = useState<string | null>(null)

  useEffect(() => {
    // Get redirect URL from query parameter
    const redirect = searchParams.get('redirect')
    if (redirect) {
      // Sanitize redirect URL - only allow relative paths starting with /
      // This prevents open redirect vulnerabilities and protocol handler issues
      let safePath: string | null = null

      // If it already starts with /, use it directly
      if (redirect.startsWith('/') && !redirect.startsWith('//')) {
        safePath = redirect
      } else {
        // Try to parse as URL and extract path
        try {
          // Handle cases like "localhost:3000/admin/roles" or "http://localhost:3000/admin/roles"
          const urlToParse = redirect.includes('://') ? redirect : `http://${redirect}`
          const url = new URL(urlToParse)
          // Only use the path portion
          safePath = url.pathname + url.search + url.hash
        } catch {
          // Invalid URL, ignore
        }
      }

      // Only set if we got a valid path starting with /
      if (safePath && safePath.startsWith('/')) {
        setRedirectUrl(safePath)
      }
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await api.auth.login(email, password)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      // Redirect to specified URL if provided, otherwise based on user type
      if (redirectUrl) {
        router.push(redirectUrl)
      } else {
        router.push(data.user.is_admin ? '/admin' : '/dashboard')
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary">SampleApp</h1>
            <p className="text-muted-foreground mt-2">Sign in to your account</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label htmlFor="password" className="block text-sm font-medium">
                  Password
                </label>
                <Link href="/forgot-password" className="text-sm text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link href="/signup" className="text-primary font-medium hover:underline">
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  )
}
