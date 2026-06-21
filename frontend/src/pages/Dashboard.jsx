import { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, BarChart, Bar
} from 'recharts'
import { predictFull } from '../services/api'

const SAMPLE_TEXTS = [
  'Sản phẩm đẹp lắm, giao hàng nhanh',
  'Chất lượng kém, thất vọng',
  'Bình thường thôi, không có gì đặc biệt',
  'Rất hài lòng, sẽ giới thiệu cho bạn bè',
  'Đồ ngu, hàng lỗi hết mà không đổi',
  'Giá hợp lý, chất lượng tốt',
  'Giao hàng chậm, bực mình',
  'Tuyệt vời, xứng đáng 5 sao',
  'Sản phẩm không đúng mô tả',
  'Mua lần 2 rồi, vẫn rất ổn',
  'Shop tư vấn nhiệt tình, cảm ơn',
  'Màu sắc đẹp, đóng gói cẩn thận',
]

const COLORS = {
  POS: '#38a169', NEG: '#e94560', NEUTRAL: '#e2a500',
  CLEAN: '#38a169', OFFENSIVE: '#e94560', HATE: '#9b2335'
}

const TOP_KEYWORDS = [
  { word: 'lỗi', count: 28 },
  { word: 'chậm', count: 22 },
  { word: 'kém', count: 19 },
  { word: 'tệ', count: 15 },
  { word: 'thất vọng', count: 12 },
]

export default function Dashboard() {
  const [sentimentData, setSentimentData] = useState([])
  const [toxicData, setToxicData]         = useState([])
  const [lineData]                         = useState([
    { time: '08:00', violations: 2 },
    { time: '10:00', violations: 5 },
    { time: '12:00', violations: 8 },
    { time: '14:00', violations: 3 },
    { time: '16:00', violations: 11 },
    { time: '18:00', violations: 7 },
    { time: '20:00', violations: 14 },
    { time: '22:00', violations: 6 },
  ])
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState({ total: 0, pos: 0, neg: 0, toxic: 0 })

  const runAnalysis = async () => {
    setLoading(true)
    const results = []
    for (const text of SAMPLE_TEXTS) {
      try {
        const data = await predictFull(text)
        results.push(data)
      } catch {}
    }

    const sentCount = { POS: 0, NEG: 0, NEUTRAL: 0 }
    const toxCount  = { CLEAN: 0, OFFENSIVE: 0, HATE: 0 }
    results.forEach(r => {
      sentCount[r.sentiment.label] = (sentCount[r.sentiment.label] || 0) + 1
      toxCount[r.toxic.label]      = (toxCount[r.toxic.label] || 0) + 1
    })

    setSentimentData([
      { name: 'Tích cực', value: sentCount.POS },
      { name: 'Tiêu cực', value: sentCount.NEG },
      { name: 'Trung lập', value: sentCount.NEUTRAL },
    ])
    setToxicData([
      { name: 'Sạch',     value: toxCount.CLEAN },
      { name: 'Xúc phạm', value: toxCount.OFFENSIVE },
      { name: 'Thù ghét', value: toxCount.HATE },
    ])
    setSummary({
      total: results.length,
      pos: sentCount.POS,
      neg: sentCount.NEG,
      toxic: toxCount.OFFENSIVE + toxCount.HATE
    })
    setLoading(false)
  }

  useEffect(() => { runAnalysis() }, [])

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ margin: '0 0 8px', color: '#1a1a2e', fontSize: 22 }}>Bảng điều khiển phân tích</h2>
        <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
          Tổng quan thống kê cảm xúc người dùng và tỉ lệ vi phạm nội dung theo thời gian thực.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 }}>
        {[
          { label: 'Tổng phân tích', value: summary.total, color: '#0f3460' },
          { label: 'Tích cực',       value: summary.pos,   color: '#38a169' },
          { label: 'Tiêu cực',       value: summary.neg,   color: '#e94560' },
          { label: 'Vi phạm',        value: summary.toxic, color: '#e2a500' },
        ].map((s, i) => (
          <div key={i} style={{ background: '#fff', borderRadius: 10, padding: '18px 20px', textAlign: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', borderTop: `4px solid ${s.color}` }}>
            <div style={{ fontSize: 32, fontWeight: 800, color: s.color }}>{s.value}</div>
            <div style={{ color: '#718096', fontSize: 13, marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        <div style={{ background: '#fff', borderRadius: 10, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <h4 style={{ margin: '0 0 16px', color: '#2d3748' }}>Phân bổ cảm xúc</h4>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={sentimentData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {sentimentData.map((_, i) => <Cell key={i} fill={[COLORS.POS, COLORS.NEG, COLORS.NEUTRAL][i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: '#fff', borderRadius: 10, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
          <h4 style={{ margin: '0 0 16px', color: '#2d3748' }}>Phân loại nội dung</h4>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={toxicData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {toxicData.map((_, i) => <Cell key={i} fill={[COLORS.CLEAN, COLORS.OFFENSIVE, COLORS.HATE][i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', marginBottom: 20 }}>
        <h4 style={{ margin: '0 0 16px', color: '#2d3748' }}>Vi phạm theo khung giờ</h4>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={lineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="violations" stroke="#e94560" strokeWidth={2.5} dot={{ r: 4, fill: '#e94560' }} name="Số vi phạm" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ background: '#fff', borderRadius: 10, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.08)', marginBottom: 24 }}>
        <h4 style={{ margin: '0 0 16px', color: '#2d3748' }}>Top từ khóa tiêu cực</h4>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={TOP_KEYWORDS} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis type="number" tick={{ fontSize: 12 }} />
            <YAxis dataKey="word" type="category" tick={{ fontSize: 13 }} width={80} />
            <Tooltip />
            <Bar dataKey="count" fill="#e94560" radius={[0, 6, 6, 0]} name="Số lần xuất hiện" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ textAlign: 'right' }}>
        <button
          onClick={runAnalysis}
          disabled={loading}
          style={{ padding: '11px 28px', background: loading ? '#aaa' : '#0f3460', color: '#fff', border: 'none', borderRadius: 8, cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 600 }}
        >
          {loading ? 'Đang phân tích...' : 'Làm mới dữ liệu'}
        </button>
      </div>
    </div>
  )
}