export type Connection = {
  id: number
  protocol: 'TCP' | 'UDP'
  local: string
  remote: string
  status: string
  process: string
  pid: number
  risk: 'Normal' | 'Review'
}

export type Prediction = {
  id: number
  service: string
  srcBytes: number
  dstBytes: number
  prediction: 'Normal' | 'Attack'
  probability: number
}

export const connections: Connection[] = [
  { id: 1, protocol: 'TCP', local: '192.168.1.20:51843', remote: '142.250.187.78:443', status: 'ESTABLISHED', process: 'chrome.exe', pid: 11840, risk: 'Normal' },
  { id: 2, protocol: 'TCP', local: '192.168.1.20:52091', remote: '20.190.155.132:443', status: 'ESTABLISHED', process: 'Code.exe', pid: 14652, risk: 'Normal' },
  { id: 3, protocol: 'UDP', local: '0.0.0.0:5353', remote: '*:*', status: 'LISTENING', process: 'svchost.exe', pid: 1840, risk: 'Review' },
  { id: 4, protocol: 'TCP', local: '127.0.0.1:5173', remote: '127.0.0.1:52103', status: 'ESTABLISHED', process: 'node.exe', pid: 22008, risk: 'Normal' }
]

export const predictions: Prediction[] = [
  { id: 1, service: 'http', srcBytes: 1520, dstBytes: 8340, prediction: 'Normal', probability: 0.08 },
  { id: 2, service: 'dns', srcBytes: 348, dstBytes: 1104, prediction: 'Normal', probability: 0.14 },
  { id: 3, service: 'ftp', srcBytes: 6840, dstBytes: 720, prediction: 'Attack', probability: 0.91 },
  { id: 4, service: 'ssh', srcBytes: 4128, dstBytes: 544, prediction: 'Attack', probability: 0.84 }
]
