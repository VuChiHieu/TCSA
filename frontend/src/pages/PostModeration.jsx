import { useState } from 'react'
import { predictBatch } from '../services/api'

export default function PostModeration() {
  const [text, setText] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    setResults(null)
    try {
      const sentences = text.split(/[.!?\n]+/).map(s => s.trim()).filter(s => s.length > 2)
      const data = await predictBatch(sentences)
      setResults(data.results)
    } catch {
      setError('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại backend.')
    }
    setLoading(false)
  }

  const hasViolation = results?.some(r => r.toxic !== 'CLEAN')

  const toxicLabel = (label) => {
    if (label === 'HATE') return 'Thù ghét'
    if (label === 'OFFENSIVE') return 'Xúc phạm'
    return 'Sạch'
  }

  const sentimentLabel = (label) => {
    if (label === 'POS') return 'Tích cực'
    if (label === 'NEG') return 'Tiêu cực'
    return 'Trung lập'
  }

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ margin: '0 0 8px', color: '#1a1a2e', fontSize: 22 }}>Kiểm duyệt bài đăng</h2>
        <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
          Nhập nội dung bài viết bên dưới. Hệ thống sẽ quét toàn bộ văn bản trước khi cho phép đăng,
          phát hiện các câu vi phạm và phân tích cảm xúc từng đoạn.
        </p>
      </div>

      <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', marginBottom: 20 }}>
        <label style={{ display: 'block', fontWeight: 600, marginBottom: 10, color: '#333' }}>
          Nội dung bài viết
        </label>
        <textarea
          rows={10}
          style={{
            width: '100%', padding: 14, fontSize: 15, borderRadius: 8,
            border: '1.5px solid #ddd', boxSizing: 'border-box',
            resize: 'vertical', lineHeight: 1.6, outline: 'none',
            fontFamily: 'inherit'
          }}
          placeholder="Nhập nội dung bài viết của bạn tại đây..."
          value={text}
          onChange={e => setText(e.target.value)}
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck="false"
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 14 }}>
          <span style={{ fontSize: 13, color: '#aaa' }}>{text.length} ký tự</span>
          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            style={{
              padding: '11px 32px',
              background: loading ? '#aaa' : '#0f3460',
              color: '#fff', border: 'none', borderRadius: 8,
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: 15, fontWeight: 600,
              transition: 'background 0.2s'
            }}
          >
            {loading ? 'Đang kiểm tra...' : 'Đăng bài'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: '#fff0f0', border: '1px solid #e94560', borderRadius: 8, padding: 14, marginBottom: 16, color: '#e94560' }}>
          {error}
        </div>
      )}

      {results && (
        <div>
          {hasViolation ? (
            <div style={{ background: '#fff0f0', border: '1.5px solid #e94560', borderRadius: 10, padding: '16px 20px', marginBottom: 20 }}>
              <div style={{ fontWeight: 700, color: '#e94560', fontSize: 16 }}>Bài viết bị từ chối — Phát hiện nội dung vi phạm</div>
              <div style={{ color: '#666', fontSize: 13, marginTop: 6 }}>Vui lòng chỉnh sửa các đoạn được đánh dấu đỏ bên dưới trước khi đăng lại.</div>
            </div>
          ) : (
            <div style={{ background: '#f0fff4', border: '1.5px solid #38a169', borderRadius: 10, padding: '16px 20px', marginBottom: 20 }}>
              <div style={{ fontWeight: 700, color: '#38a169', fontSize: 16 }}>Bài viết hợp lệ — Đã đăng thành công</div>
              <div style={{ color: '#666', fontSize: 13, marginTop: 6 }}>Nội dung không vi phạm tiêu chuẩn cộng đồng.</div>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {results.map((r, i) => (
              <div key={i} style={{
                padding: '14px 18px',
                borderRadius: 8,
                background: r.toxic !== 'CLEAN' ? '#fff5f5' : '#fff',
                border: `1px solid ${r.toxic !== 'CLEAN' ? '#feb2b2' : '#e2e8f0'}`,
                borderLeft: `5px solid ${r.toxic !== 'CLEAN' ? '#e94560' : r.sentiment === 'POS' ? '#38a169' : '#e2a500'}`,
                boxShadow: '0 1px 4px rgba(0,0,0,0.05)'
              }}>
                <div style={{ color: r.toxic !== 'CLEAN' ? '#c53030' : '#2d3748', fontSize: 15, marginBottom: 6 }}>
                  {r.text}
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                  <span style={{
                    fontSize: 11, padding: '2px 10px', borderRadius: 12, fontWeight: 600,
                    background: r.toxic !== 'CLEAN' ? '#fed7d7' : '#c6f6d5',
                    color: r.toxic !== 'CLEAN' ? '#c53030' : '#276749'
                  }}>
                    {toxicLabel(r.toxic)}
                  </span>
                  <span style={{
                    fontSize: 11, padding: '2px 10px', borderRadius: 12, fontWeight: 600,
                    background: r.sentiment === 'POS' ? '#c6f6d5' : r.sentiment === 'NEG' ? '#fed7d7' : '#fefcbf',
                    color: r.sentiment === 'POS' ? '#276749' : r.sentiment === 'NEG' ? '#c53030' : '#744210'
                  }}>
                    {sentimentLabel(r.sentiment)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}