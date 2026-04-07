import { useEffect, useState, useCallback } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { parcelsApi, batchesApi, ddsApi, Parcel, Batch } from '../utils/api'
import { useAuth } from '../hooks/useAuth'

const GREEN = '#0F6E56'
const AMBER = '#854F0B'
const RED = '#993C1D'
const LIGHT = '#E1F5EE'

function riskColor(risk?: string) {
  if (risk === 'LOW') return GREEN
  if (risk === 'MEDIUM') return AMBER
  return RED
}

function Badge({ level }: { level?: string }) {
  const color = riskColor(level)
  return (
    <span style={{ background: `${color}22`, color, padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600 }}>
      {level || '—'}
    </span>
  )
}

function CompliancePill({ compliant }: { compliant?: boolean }) {
  if (compliant === undefined || compliant === null) return <span style={{ color: '#888' }}>—</span>
  return (
    <span style={{ background: compliant ? '#e1f5ee' : '#fcebeb', color: compliant ? GREEN : RED, padding: '2px 10px', borderRadius: 12, fontSize: 11, fontWeight: 700 }}>
      {compliant ? '✓ Compliant' : '⚠ Flagged'}
    </span>
  )
}

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div style={{ background: '#f1efe8', borderRadius: 10, padding: '14px 18px', flex: 1, minWidth: 120 }}>
      <div style={{ fontSize: 11, color: '#888780', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 600, color: color || '#2c2c2a', lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: '#888780', marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

export default function DashboardPage() {
  const { logout } = useAuth()
  const [parcels, setParcels] = useState<Parcel[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [activeTab, setActiveTab] = useState<'map' | 'parcels' | 'batches'>('map')
  const [selectedParcel, setSelectedParcel] = useState<Parcel | null>(null)
  const [ddsLoading, setDdsLoading] = useState<string | null>(null)
  const [rescoring, setRescoring] = useState<string | null>(null)
  const [toast, setToast] = useState('')

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(''), 3000)
  }

  const load = useCallback(async () => {
    try {
      const [pRes, bRes] = await Promise.all([parcelsApi.list(), batchesApi.list()])
      setParcels(pRes.data)
      setBatches(bRes.data)
    } catch {
      showToast('Failed to load data. Is the backend running?')
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleRescore = async (parcelId: string) => {
    setRescoring(parcelId)
    try {
      await parcelsApi.rescore(parcelId)
      await load()
      showToast('Satellite rescore complete')
    } finally {
      setRescoring(null)
    }
  }

  const handleGenerateDDS = async (batch: Batch) => {
    setDdsLoading(batch.id)
    try {
      const res = await ddsApi.generate(batch.id, 'TerraLedger Demo Operator', 'Kenya')
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `${batch.batch_code}-DDS.pdf`
      a.click()
      URL.revokeObjectURL(url)
      showToast('DDS downloaded successfully')
      await load()
    } catch {
      showToast('DDS generation failed')
    } finally {
      setDdsLoading(null)
    }
  }

  const compliantCount = parcels.filter(p => p.eudr_compliant).length
  const flaggedCount = parcels.filter(p => p.eudr_compliant === false).length
  const avgScore = parcels.length
    ? Math.round(parcels.reduce((s, p) => s + (p.deforestation_score || 0), 0) / parcels.length)
    : 0

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
      {/* Toast */}
      {toast && (
        <div style={{ position: 'fixed', top: 16, right: 16, background: '#2c2c2a', color: '#fff', padding: '10px 18px', borderRadius: 8, zIndex: 9999, fontSize: 13 }}>
          {toast}
        </div>
      )}

      {/* Nav */}
      <nav style={{ background: '#fff', borderBottom: '0.5px solid #d3d1c7', padding: '0 24px', display: 'flex', alignItems: 'center', gap: 24, height: 54 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginRight: 16 }}>
          <span style={{ fontSize: 20 }}>🌍</span>
          <span style={{ fontWeight: 700, color: GREEN, fontSize: 16 }}>TerraLedger</span>
          <span style={{ background: LIGHT, color: GREEN, fontSize: 10, fontWeight: 600, padding: '2px 7px', borderRadius: 10, marginLeft: 2 }}>MVP</span>
        </div>
        {(['map', 'parcels', 'batches'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: activeTab === tab ? LIGHT : 'transparent',
              color: activeTab === tab ? GREEN : '#5f5e5a',
              border: 'none', padding: '6px 14px', borderRadius: 8, cursor: 'pointer',
              fontSize: 13, fontWeight: activeTab === tab ? 600 : 400, textTransform: 'capitalize'
            }}
          >
            {tab === 'map' ? '🗺 Map' : tab === 'parcels' ? '🌱 Parcels' : '📦 Batches'}
          </button>
        ))}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 12, alignItems: 'center' }}>
          <span style={{ fontSize: 12, color: '#888' }}>demo@terraledger.io</span>
          <button onClick={logout} style={{ fontSize: 12, color: '#888', background: 'none', border: '0.5px solid #d3d1c7', padding: '4px 10px', borderRadius: 6, cursor: 'pointer' }}>
            Sign out
          </button>
        </div>
      </nav>

      {/* Stats bar */}
      <div style={{ background: '#fff', borderBottom: '0.5px solid #d3d1c7', padding: '12px 24px', display: 'flex', gap: 12 }}>
        <StatCard label="Total parcels" value={parcels.length} sub="East Africa" />
        <StatCard label="Compliant" value={compliantCount} sub="EUDR verified" color={GREEN} />
        <StatCard label="Flagged" value={flaggedCount} sub="Needs review" color={flaggedCount > 0 ? RED : '#888'} />
        <StatCard label="Avg risk score" value={`${avgScore}/100`} sub="Deforestation index" />
        <StatCard label="Batches" value={batches.length} sub="Traceable lots" />
        <StatCard label="DDS generated" value={batches.filter(b => b.dds_generated).length} sub="EU-ready" color={GREEN} />
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>

        {/* MAP TAB */}
        {activeTab === 'map' && (
          <div style={{ height: '100%', display: 'flex' }}>
            <div style={{ flex: 1 }}>
              <MapContainer
                center={[1.5, 36.0]}
                zoom={5}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {parcels.map(p => (
                  <CircleMarker
                    key={p.id}
                    center={[p.centroid_lat, p.centroid_lon]}
                    radius={10}
                    pathOptions={{
                      fillColor: riskColor(p.risk_level),
                      color: '#fff',
                      weight: 2,
                      fillOpacity: 0.85,
                    }}
                    eventHandlers={{ click: () => setSelectedParcel(p) }}
                  >
                    <Popup>
                      <strong>{p.name}</strong><br />
                      {p.country} · {p.cooperative}<br />
                      Score: {p.deforestation_score?.toFixed(1)}/100 · {p.risk_level}<br />
                      <span style={{ color: p.eudr_compliant ? GREEN : RED, fontWeight: 600 }}>
                        {p.eudr_compliant ? '✓ EUDR Compliant' : '⚠ Flagged'}
                      </span>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>

            {/* Side panel */}
            {selectedParcel && (
              <div style={{ width: 320, background: '#fff', borderLeft: '0.5px solid #d3d1c7', padding: 20, overflowY: 'auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                  <h3 style={{ fontSize: 15, fontWeight: 600, color: '#2c2c2a' }}>{selectedParcel.name}</h3>
                  <button onClick={() => setSelectedParcel(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#888', fontSize: 18 }}>×</button>
                </div>

                <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                  <Badge level={selectedParcel.risk_level} />
                  <CompliancePill compliant={selectedParcel.eudr_compliant} />
                </div>

                {[
                  ['Farmer', selectedParcel.farmer_name],
                  ['Cooperative', selectedParcel.cooperative],
                  ['Country', selectedParcel.country],
                  ['Region', selectedParcel.region],
                  ['Commodity', selectedParcel.commodity?.toUpperCase()],
                  ['Area', selectedParcel.area_ha ? `${selectedParcel.area_ha} ha` : '—'],
                  ['GPS', `${selectedParcel.centroid_lat.toFixed(4)}, ${selectedParcel.centroid_lon.toFixed(4)}`],
                  ['Deforestation score', `${selectedParcel.deforestation_score?.toFixed(1) ?? '—'} / 100`],
                  ['Risk level', selectedParcel.risk_level],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '0.5px solid #f1efe8', fontSize: 13 }}>
                    <span style={{ color: '#888780' }}>{k}</span>
                    <span style={{ fontWeight: 500 }}>{v || '—'}</span>
                  </div>
                ))}

                <div style={{ marginTop: 16, padding: 12, background: '#f8f7f3', borderRadius: 8, fontSize: 12, color: '#5f5e5a', lineHeight: 1.6 }}>
                  <strong style={{ color: '#2c2c2a', display: 'block', marginBottom: 4 }}>AI Explanation (XAI)</strong>
                  {selectedParcel['xai_explanation' as keyof Parcel] as string || 'No explanation available.'}
                </div>

                <button
                  onClick={() => handleRescore(selectedParcel.id)}
                  disabled={rescoring === selectedParcel.id}
                  style={{ marginTop: 16, width: '100%', padding: '10px 0', background: GREEN, color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer' }}
                >
                  {rescoring === selectedParcel.id ? '🛰 Rescoring…' : '🛰 Re-run Satellite Score'}
                </button>
              </div>
            )}

            {/* Legend */}
            <div style={{ position: 'absolute', bottom: 24, left: 24, background: '#fff', border: '0.5px solid #d3d1c7', borderRadius: 10, padding: '10px 14px', zIndex: 999, fontSize: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 6, color: '#2c2c2a' }}>Deforestation risk</div>
              {[['LOW', GREEN], ['MEDIUM', AMBER], ['HIGH', RED]].map(([label, color]) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: color }} />
                  <span style={{ color: '#5f5e5a' }}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PARCELS TAB */}
        {activeTab === 'parcels' && (
          <div style={{ padding: 24, overflowY: 'auto', height: '100%' }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: '#2c2c2a' }}>Farm Parcels</h2>
            <div style={{ background: '#fff', border: '0.5px solid #d3d1c7', borderRadius: 12, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ background: '#f1efe8' }}>
                    {['Parcel', 'Cooperative', 'Country', 'Commodity', 'Area (ha)', 'Risk score', 'Risk level', 'EUDR status', 'Action'].map(h => (
                      <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: '#5f5e5a', borderBottom: '0.5px solid #d3d1c7' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {parcels.map((p, i) => (
                    <tr key={p.id} style={{ background: i % 2 === 0 ? '#fff' : '#fafaf8' }}>
                      <td style={{ padding: '10px 14px', fontWeight: 500 }}>
                        <div>{p.name}</div>
                        <div style={{ fontSize: 11, color: '#888' }}>{p.farmer_name}</div>
                      </td>
                      <td style={{ padding: '10px 14px', color: '#5f5e5a' }}>{p.cooperative || '—'}</td>
                      <td style={{ padding: '10px 14px' }}>{p.country}</td>
                      <td style={{ padding: '10px 14px' }}>{p.commodity?.toUpperCase()}</td>
                      <td style={{ padding: '10px 14px' }}>{p.area_ha ?? '—'}</td>
                      <td style={{ padding: '10px 14px', fontWeight: 600 }}>{p.deforestation_score?.toFixed(1) ?? '—'}</td>
                      <td style={{ padding: '10px 14px' }}><Badge level={p.risk_level} /></td>
                      <td style={{ padding: '10px 14px' }}><CompliancePill compliant={p.eudr_compliant} /></td>
                      <td style={{ padding: '10px 14px' }}>
                        <button
                          onClick={() => handleRescore(p.id)}
                          disabled={rescoring === p.id}
                          style={{ background: LIGHT, color: GREEN, border: `0.5px solid ${GREEN}`, padding: '4px 10px', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 500 }}
                        >
                          {rescoring === p.id ? '…' : '🛰 Rescore'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* BATCHES TAB */}
        {activeTab === 'batches' && (
          <div style={{ padding: 24, overflowY: 'auto', height: '100%' }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: '#2c2c2a' }}>Commodity Batches & DDS</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {batches.map(b => (
                <div key={b.id} style={{ background: '#fff', border: '0.5px solid #d3d1c7', borderRadius: 12, padding: 20 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 15, color: '#2c2c2a', fontFamily: 'monospace' }}>{b.batch_code}</div>
                      <div style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
                        {b.commodity?.toUpperCase()} · {b.quantity_kg.toLocaleString()} kg · → {b.destination_country}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <CompliancePill compliant={b.all_parcels_compliant} />
                      {b.dds_generated && (
                        <span style={{ background: '#e1f5ee', color: GREEN, fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 10 }}>
                          DDS issued
                        </span>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 16, marginBottom: 14, fontSize: 12, color: '#5f5e5a' }}>
                    <span>Harvest: {new Date(b.harvest_date).toLocaleDateString()}</span>
                    {b.dds_reference && <span>Ref: {b.dds_reference}</span>}
                  </div>

                  <button
                    onClick={() => handleGenerateDDS(b)}
                    disabled={ddsLoading === b.id}
                    style={{
                      padding: '9px 18px',
                      background: b.all_parcels_compliant ? GREEN : '#888',
                      color: '#fff',
                      border: 'none',
                      borderRadius: 8,
                      cursor: b.all_parcels_compliant ? 'pointer' : 'not-allowed',
                      fontSize: 13,
                      fontWeight: 500,
                    }}
                  >
                    {ddsLoading === b.id
                      ? '⏳ Generating…'
                      : b.dds_generated
                        ? '📄 Re-download DDS PDF'
                        : '📄 Generate EUDR DDS PDF'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
