import { useState, useEffect, useRef } from 'react'
import { predictFull } from '../services/api'

const FAKE_USERS = ['Minh', 'Lan', 'Tuấn', 'Hương', 'Đức', 'Mai', 'Long', 'Hoa', 'Nam', 'Linh']
const FAKE_MESSAGES = [
  'Sản phẩm này đẹp quá!',
  'Bao nhiêu tiền vậy bạn ơi?',
  'Đồ ngu bán hàng gì mà tệ thế',
  'Mua ở đâu vậy mọi người?',
  'Chất lượng tốt lắm, đáng mua',
  'Sao hàng lâu giao thế, tức chết đi được',
  'Ủng hộ shop nhé mọi người',
  'Giá hợp lý, chất lượng ổn',
  'Thằng bán hàng này gian lận',
  'Đẹp thật sự, sẽ quay lại mua thêm',
]

const maskText = (text) => {
  const badWords = ['ngu', 'tệ', 'tức', 'gian lận', 'thằng', 'chết']
  let masked = text
  badWords.forEach(word => {
    const regex = new RegExp(word, 'gi')
    masked = masked.replace(regex, '*'.repeat(word.length))
  })
  return masked
}

export default function LiveChat() {
  const [messages, setMessages] = useState([])
  const [running, setRunning] = useState(false)
  const [stats, setStats] = useState({ total: 0, blocked: 0 })
  const intervalRef = useRef(null)
  const bottomRef = useRef(null)

  const addMessage = async () => {
    const user = FAKE_USERS[Math.floor(Math.random() * FAKE_USERS.length)]
    const text = FAKE_MESSAGES[Math.floor(Math.random() * FAKE_MESSAGES.length)]
    try {
      const data = await predictFull(text)
      const isToxic = data.toxic.label !== 'CLEAN' || data.sentiment.label === 'NEG'
      const displayText = isToxic ? maskText(text) : text
      setMessages(prev => [...prev.slice(-60), {
        user, text: displayText, toxic: isToxic,
        sentiment: data.sentiment.label,
        time: new Date().toLocaleTimeString('vi-VN')
      }])
      setStats(prev => ({ total: prev.total + 1, blocked: prev.blocked + (isToxic ? 1 : 0) }))
    } catch {
      setMessages(prev => [...prev.slice(-60), {
        user, text, toxic: false, sentiment: 'NEG',
        time: new Date().toLocaleTimeString('vi-VN')
      }])
    }
  }

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(addMessage, 1200)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [running])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sentColor = (s) => s === 'POS' ? '#68d391' : s === 'NEG' ? '#fc8181' : '#f6e05e'
  const sentLabel = (s) => s === 'POS' ? 'Tích cực' : s === 'NEG' ? 'Tiêu cực' : 'Trung lập'

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ margin: '0 0 8px', color: '#1a1a2e', fontSize: 22 }}>Kiểm duyệt trò chuyện trực tiếp</h2>
        <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
          Mô phỏng luồng chat tốc độ cao như YouTube hoặc TikTok Live. Hệ thống tự động
          che từ ngữ vi phạm bằng ký tự đặc biệt mà không làm gián đoạn trải nghiệm.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 20 }}>
        {[
          { label: 'Tổng tin nhắn', value: stats.total, color: '#0f3460' },
          { label: 'Đã che mờ', value: stats.blocked, color: '#e94560' },
          { label: 'Tỉ lệ sạch', value: stats.total > 0 ? Math.round((1 - stats.blocked / stats.total) * 100) + '%' : '100%', color: '#38a169' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, padding: '16px', textAlign: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
            <div style={{ fontSize: 30, fontWeight: 800, color: s.color }}>{s.value}</div>
            <div style={{ color: '#718096', fontSize: 13, marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ background: '#1a1a2e', borderRadius: 12, padding: '16px 20px', height: 420, overflowY: 'auto', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
        {messages.length === 0 && (
          <div style={{ color: '#4a5568', textAlign: 'center', marginTop: 180, fontSize: 14 }}>
            Bấm "Bắt đầu" để xem luồng chat trực tiếp...
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 10, display: 'flex', gap: 10, alignItems: 'baseline' }}>
            <span style={{ color: '#e94560', fontWeight: 700, minWidth: 70, fontSize: 13 }}>{m.user}:</span>
            <span style={{ color: m.toxic ? '#fc8181' : '#e2e8f0', fontSize: 14, flex: 1 }}>{m.text}</span>
            <span style={{ fontSize: 11, color: sentColor(m.sentiment), minWidth: 60, textAlign: 'right' }}>
              {sentLabel(m.sentiment)}
            </span>
            <span style={{ fontSize: 11, color: '#4a5568', minWidth: 65, textAlign: 'right' }}>{m.time}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
        <button
          onClick={() => setRunning(r => !r)}
          style={{
            padding: '11px 32px',
            background: running ? '#e94560' : '#38a169',
            color: '#fff', border: 'none', borderRadius: 8,
            cursor: 'pointer', fontSize: 15, fontWeight: 700,
            transition: 'background 0.2s'
          }}
        >
          {running ? 'Dừng lại' : 'Bắt đầu'}
        </button>
        <button
          onClick={() => { setMessages([]); setStats({ total: 0, blocked: 0 }) }}
          style={{ padding: '11px 20px', background: '#edf2f7', border: 'none', borderRadius: 8, cursor: 'pointer', color: '#4a5568', fontWeight: 600 }}
        >
          Xóa chat
        </button>
      </div>
    </div>
  )
}