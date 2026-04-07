import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tl_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('tl_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// ── Typed API calls ───────────────────────────────────────────────────────────

export interface Parcel {
  id: string
  name: string
  farmer_name?: string
  cooperative?: string
  commodity: string
  country: string
  region?: string
  centroid_lat: number
  centroid_lon: number
  area_ha?: number
  deforestation_score?: number
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH'
  eudr_compliant?: boolean
  created_at: string
}

export interface Batch {
  id: string
  batch_code: string
  commodity: string
  quantity_kg: number
  harvest_date: string
  destination_country?: string
  all_parcels_compliant?: boolean
  dds_generated: boolean
  dds_reference?: string
  created_at: string
}

export interface CustodyEvent {
  id: string
  event_type: string
  event_timestamp: string
  location_name?: string
  gps_lat?: number
  gps_lon?: number
  actor_name?: string
  notes?: string
}

export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string }>('/auth/token', 
      new URLSearchParams({ username: email, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ),
}

export const parcelsApi = {
  list: () => api.get<Parcel[]>('/parcels/'),
  get: (id: string) => api.get<Parcel>(`/parcels/${id}`),
  rescore: (id: string) => api.post(`/parcels/${id}/rescore`),
}

export const batchesApi = {
  list: () => api.get<Batch[]>('/batches/'),
  custody: (id: string) => api.get(`/batches/${id}/custody`),
}

export const ddsApi = {
  generate: (batchId: string, operatorName: string, operatorCountry: string) =>
    api.post('/dds/generate', 
      { batch_id: batchId, operator_name: operatorName, operator_country: operatorCountry },
      { responseType: 'blob' }
    ),
}
