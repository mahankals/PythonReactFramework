'use client'

import Link from 'next/link'

export default function AdminHome() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link href="/admin/users" className="p-6 bg-white rounded-lg border">Users</Link>
        <Link href="/admin/rbac" className="p-6 bg-white rounded-lg border">RBAC</Link>
      </div>
    </div>
  )
}
