import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '../utils/api'

interface AuthCtx {
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthCtx>({} as AuthCtx)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('tl_token'))

  const login = async (email: string, password: string) => {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('tl_token', data.access_token)
    setToken(data.access_token)
  }

  const logout = () => {
    localStorage.removeItem('tl_token')
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
