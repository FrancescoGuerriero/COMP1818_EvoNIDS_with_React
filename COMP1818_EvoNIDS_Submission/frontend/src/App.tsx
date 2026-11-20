import { useEffect, useMemo, useState } from 'react'
import { connections, predictions } from './data/demo'
import { api, type ApiConnection, type ReplayRecord } from './api'

type View = 'overview' | 'connections' | 'replay' | 'research'

const nav: { id: View; label: string; short: string }[] = [
  { id: 'overview', label: 'Overview', short: 'OV' },
  { id: 'connections', label: 'Live Connections', short: 'LC' },
  { id: 'replay', label: 'Model Replay', short: 'MR' },
  { id: 'research', label: 'Research Results', short: 'RR' },
]

const metrics = [
  { label: 'Joint PSO + RF Macro-F1', value: '0.8814', note: 'five-seed mean · corrected joint experiment' },
  { label: 'Selected Raw Features', value: '11.4', note: 'out of 42 predictors · joint PSO' },
  { label: 'Feature Reduction', value: '72.86%', note: 'joint PSO mean across 5 seeds' },
  { label: 'False Positive Rate', value: '0.2197', note: 'joint PSO · UNSW-NB15 held-out test' },
]

function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'neutral' | 'good' | 'warn' | 'danger' }) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}

function Overview() {
  return (
    <>
      <section className="hero card">
        <div>
          <span className="eyebrow">COMP-1818 · Artificial Intelligence Applications</span>
          <h1>Evolutionary feature selection for efficient intrusion detection.</h1>
          <p>
            EvoNIDS combines a reproducible UNSW-NB15 research pipeline with a passive Windows IDS prototype.
            Live socket telemetry is monitored separately from ML classification so incompatible feature spaces are not mixed.
          </p>
        </div>
        <div className="hero-status">
          <span className="pulse" />
          <div>
            <strong>Prototype ready</strong>
            <span>Passive monitoring · no traffic blocking</span>
          </div>
        </div>
      </section>

      <section className="metric-grid">
        {metrics.map((metric) => (
          <article className="metric card" key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <small>{metric.note}</small>
          </article>
        ))}
      </section>

      <section className="split-grid">
        <article className="card panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Architecture</span>
              <h2>Windows prototype pipeline</h2>
            </div>
            <Badge tone="good">Passive</Badge>
          </div>
          <div className="flow">
            <div><span>01</span><strong>Windows telemetry</strong><small>TCP/UDP sockets and processes</small></div>
            <b>→</b>
            <div><span>02</span><strong>Flow features</strong><small>Required integration layer</small></div>
            <b>→</b>
            <div><span>03</span><strong>RF classifier</strong><small>CSV replay with compatible features</small></div>
          </div>
          <p className="callout">
            Current live Windows socket data is not passed directly into the UNSW-NB15 classifier. Replay mode performs the ML classification using compatible feature schemas.
          </p>
        </article>

        <article className="card panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Best result</span>
              <h2>Joint PSO leads the corrected comparison</h2>
            </div>
          </div>
          <div className="tradeoff">
            <div className="tradeoff-row"><span>Joint PSO</span><div><i style={{ width: '100%' }} /></div><strong>0.8814</strong></div>
            <div className="tradeoff-row"><span>Joint GA</span><div><i style={{ width: '99.7%' }} /></div><strong>0.8789</strong></div>
            <div className="tradeoff-row"><span>Joint BPSO</span><div><i style={{ width: '99.5%' }} /></div><strong>0.8772</strong></div>
            <div className="tradeoff-row"><span>Full XGBoost</span><div><i style={{ width: '98.3%' }} /></div><strong>0.8668</strong></div>
          </div>
          <small className="muted">Five-seed mean test Macro-F1 from the corrected November 2026 experiment; displayed bar lengths are relative to the highest result.</small>
        </article>
      </section>
    </>
  )
}

function Connections() {
  const [liveRows, setLiveRows] = useState<ApiConnection[]>([])
  const [status, setStatus] = useState<'loading' | 'live' | 'demo' | 'error'>('loading')

  const refresh = async () => {
    try {
      const rows = await api.connections()
      setLiveRows(rows)
      setStatus('live')
    } catch {
      setLiveRows([])
      setStatus('demo')
    }
  }

  useEffect(() => {
    void refresh()
    const timer = window.setInterval(() => void refresh(), 3000)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <section className="card panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Passive Windows telemetry</span>
          <h2>Live connection monitor</h2>
        </div>
        <Badge tone={status === 'live' ? 'good' : status === 'demo' ? 'warn' : 'neutral'}>
          {status === 'live' ? 'Live API' : status === 'demo' ? 'Demo fallback' : 'Connecting'}
        </Badge>
      </div>
      <p className="muted">
        {status === 'live'
          ? 'Showing passive TCP/UDP socket telemetry from the Python backend. No traffic is blocked or modified.'
          : 'Python API is not currently reachable, so demonstration rows are shown instead.'}
      </p>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Protocol</th><th>Local endpoint</th><th>Remote endpoint</th><th>Status</th><th>Process</th><th>PID</th><th>Source</th></tr></thead>
          <tbody>
            {status === 'live' ? liveRows.slice(0, 100).map((row, index) => (
              <tr key={`${row.pid}-${row.local_address}-${index}`}>
                <td><Badge>{row.protocol}</Badge></td><td>{row.local_address || '—'}</td><td>{row.remote_address || '—'}</td><td>{row.status || '—'}</td><td>{row.process_name || 'Unknown'}</td><td>{row.pid ?? '—'}</td><td><Badge tone="good">Windows</Badge></td>
              </tr>
            )) : connections.map((row) => (
              <tr key={row.id}>
                <td><Badge>{row.protocol}</Badge></td><td>{row.local}</td><td>{row.remote}</td><td>{row.status}</td><td>{row.process}</td><td>{row.pid}</td><td><Badge tone="warn">Demo</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function Replay() {
  const [fileName, setFileName] = useState('No CSV selected')
  const [csvText, setCsvText] = useState('')
  const [rows, setRows] = useState<ReplayRecord[]>(predictions.map((row) => ({
    id: row.id,
    service: row.service,
    sbytes: row.srcBytes,
    dbytes: row.dstBytes,
    ids_prediction: row.prediction === 'Attack' ? 1 : 0,
    attack_probability: row.probability,
  })))
  const [running, setRunning] = useState(false)
  const [message, setMessage] = useState('Demo predictions are shown until a CSV is submitted to the Python API.')

  const attackCount = useMemo(() => rows.filter((row) => Number(row.ids_prediction) === 1).length, [rows])

  const selectFile = async (file?: File) => {
    if (!file) return
    setFileName(file.name)
    setCsvText(await file.text())
    setMessage('CSV ready. Run replay analysis to score it with the backend model.')
  }

  const runReplay = async () => {
    if (!csvText) {
      setMessage('Choose a CSV file first.')
      return
    }
    setRunning(true)
    try {
      const response = await api.replayCsv(csvText)
      setRows(response.rows)
      setMessage(`Scored ${response.count} rows with the configured IDS model.`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Replay request failed.')
    } finally {
      setRunning(false)
    }
  }

  return (
    <>
      <section className="split-grid replay-grid">
        <article className="card panel upload-card">
          <span className="eyebrow">Compatible feature input</span>
          <h2>Replay CSV through the IDS model</h2>
          <p>Select a CSV using the trained model's expected feature schema. The browser sends the CSV text to the local Python API; classification remains server-side.</p>
          <label className="file-control">
            <input type="file" accept=".csv,text/csv" onChange={(event) => void selectFile(event.target.files?.[0])} />
            <span>Choose CSV</span>
          </label>
          <div className="selected-file">{fileName}</div>
          <button className="primary" type="button" disabled={running} onClick={() => void runReplay()}>{running ? 'Scoring…' : 'Run replay analysis'}</button>
          <small className="muted">{message}</small>
        </article>

        <article className="card panel replay-summary">
          <span className="eyebrow">Classification summary</span>
          <h2>Replay summary</h2>
          <div className="summary-number"><strong>{rows.length}</strong><span>flows</span></div>
          <div className="summary-pair"><span>Normal</span><strong>{rows.length - attackCount}</strong></div>
          <div className="summary-pair"><span>Attack</span><strong>{attackCount}</strong></div>
          <div className="summary-pair"><span>Classifier</span><strong>Saved pipeline</strong></div>
        </article>
      </section>

      <section className="card panel">
        <div className="panel-heading"><div><span className="eyebrow">Predictions</span><h2>Model replay results</h2></div></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>#</th><th>Service</th><th>Source bytes</th><th>Destination bytes</th><th>Prediction</th><th>Attack probability</th></tr></thead>
            <tbody>
              {rows.slice(0, 100).map((row, index) => {
                const attack = Number(row.ids_prediction) === 1
                const probability = Number(row.attack_probability ?? 0)
                return <tr key={index}><td>{index + 1}</td><td>{String(row.service ?? '—')}</td><td>{String(row.sbytes ?? '—')}</td><td>{String(row.dbytes ?? '—')}</td><td><Badge tone={attack ? 'danger' : 'good'}>{attack ? 'Attack' : 'Normal'}</Badge></td><td>{Number.isFinite(probability) ? `${(probability * 100).toFixed(1)}%` : '—'}</td></tr>
              })}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}

function Research() {
  const methods = [
    ['Joint PSO + RF', '0.8814', '11.4', '72.86%'],
    ['Joint GA + RF', '0.8789', '9.8', '76.67%'],
    ['Joint BPSO + RF', '0.8772', '12.6', '70.00%'],
    ['XGBoost baseline', '0.8668', '42', '0%'],
    ['Random Forest baseline', '0.8641', '42', '0%'],
    ['Feature-only PSO + RF', '0.8643', '11.2', '73.33%'],
    ['Joint NSGA-II + RF', '0.8439', '6.0', '85.71%'],
  ]
  return (
    <section className="card panel">
      <div className="panel-heading"><div><span className="eyebrow">Five-seed final comparison</span><h2>Research results</h2></div><Badge>300 evaluations</Badge></div>
      <div className="table-wrap">
        <table><thead><tr><th>Method</th><th>Macro-F1</th><th>Mean features</th><th>Reduction</th></tr></thead>
          <tbody>{methods.map(([method, f1, features, reduction]) => <tr key={method}><td><strong>{method}</strong></td><td>{f1}</td><td>{features}</td><td>{reduction}</td></tr>)}</tbody></table>
      </div>
      <div className="research-notes">
        <p><strong>Interpretation.</strong> Corrected joint PSO + RF achieves the highest five-seed mean test Macro-F1 (0.8814), reducing 42 raw predictors to 11.4 on average. Joint NSGA-II selects the fewest features but has lower mean Macro-F1. Feature-only and joint experiments use equal 300-distinct-candidate evaluation budgets per method and seed, not equal computational time.</p>
        <p><strong>Statistical caution.</strong> For joint versus feature-only PSO, mean paired Macro-F1 gain is 0.0171 (paired t p = 0.0104; exact two-sided Wilcoxon p = 0.0625). Five seeds and multiple comparisons limit claims of statistical significance. These are static published benchmark summaries, not live IDS measurements.</p>
      </div>
    </section>
  )
}

export default function App() {
  const [view, setView] = useState<View>('overview')
  const content = view === 'overview' ? <Overview /> : view === 'connections' ? <Connections /> : view === 'replay' ? <Replay /> : <Research />

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">E</span><div><strong>EvoNIDS</strong><small>Windows IDS</small></div></div>
        <nav>{nav.map((item) => <button key={item.id} className={view === item.id ? 'active' : ''} onClick={() => setView(item.id)}><span>{item.short}</span>{item.label}</button>)}</nav>
        <div className="sidebar-foot"><span>Research prototype</span><small>UNSW-NB15 · GA/BPSO/PSO/NSGA-II</small></div>
      </aside>
      <main>
        <header className="topbar">
          <div><span className="eyebrow">EvoNIDS control centre</span><h2>{nav.find((item) => item.id === view)?.label}</h2></div>
          <div className="top-actions"><Badge>Research prototype</Badge><div className="avatar">FG</div></div>
        </header>
        <div className="content">{content}</div>
      </main>
    </div>
  )
}
