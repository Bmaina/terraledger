import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('demo@terraledger.io')
  const [password, setPassword] = useState('TerraDemo2026')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch {
      setError('Invalid credentials. Use demo@terraledger.io / TerraDemo2026')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🌍</span>
          <span style={styles.logoText}>TerraLedger</span>
        </div>
        <p style={styles.subtitle}>EUDR Compliance Platform</p>
        <p style={styles.tagline}>Geo-verified supply chain traceability for East African coffee</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              style={styles.input}
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              style={styles.input}
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p style={styles.error}>{error}</p>}
          <button style={styles.btn} type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in →'}
          </button>
        </form>

        <div style={styles.demoNote}>
          <strong>Investor demo credentials pre-filled.</strong><br />
          Demo covers 9 real East African coffee parcels across Kenya, Ethiopia, Uganda & Rwanda.
        </div>
      </div>
    </div>
  )
}

const GREEN = '#0F6E56'
const styles: Record<string, React.CSSProperties> = {
  page: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f1efe8', padding: 24 },
  card: { background: '#fff', borderRadius: 16, padding: 40, width: '100%', maxWidth: 420, border: '0.5px solid #d3d1c7' },
  logo: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 },
  logoIcon: { fontSize: 28 },
  logoText: { fontSize: 24, fontWeight: 600, color: GREEN },
  subtitle: { color: '#5f5e5a', fontSize: 13, marginBottom: 6 },
  tagline: { color: '#888780', fontSize: 12, marginBottom: 28, lineHeight: 1.5 },
  form: { display: 'flex', flexDirection: 'column', gap: 16 },
  field: { display: 'flex', flexDirection: 'column', gap: 6 },
  label: { fontSize: 13, fontWeight: 500, color: '#3d3d3a' },
  input: { padding: '10px 12px', borderRadius: 8, border: '0.5px solid #b4b2a9', fontSize: 14, outline: 'none' },
  error: { color: '#993c1d', fontSize: 13 },
  btn: { padding: '12px 0', background: GREEN, color: '#fff', border: 'none', borderRadius: 8, fontSize: 15, fontWeight: 500, cursor: 'pointer', marginTop: 4 },
  demoNote: { marginTop: 24, padding: 14, background: '#e1f5ee', borderRadius: 8, fontSize: 12, color: '#0f6e56', lineHeight: 1.6 },
}
