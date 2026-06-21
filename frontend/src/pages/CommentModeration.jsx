import { useState } from 'react'
import { predictFull } from '../services/api'

const SAMPLE_COMMENTS = [
  { user: 'Nguyễn Văn A', text: 'Sản phẩm rất tốt, giao hàng nhanh, sẽ mua lại!' },
  { user: 'Trần Thị B',   text: 'Chất lượng bình thường, không ấn tượng lắm' },
  { user: 'Lê Văn C',     text: 'Đồ ngu bán hàng biết gì không, hàng lỗi hết' },
  { user: 'Phạm D',       text: 'Tuyệt vời, đúng ý mô tả, rất hài lòng' },
  { user: 'Hoàng E',      text: 'Đóng gói an toàn, màu sắc đẹp, thương hiệu uy tín' },
]

export default function CommentModeration() {
  const [comments, setComments] = useState(
    SAMPLE_COMMENTS.map(c => ({ ...c, result: null, hidden: false, loading: false }))
  )
  const [newText, setNewText] = useState('')
  const [scanning, setScanning] = useState(false)

  // Phan tich 1 binh luan, tra ve object da cap nhat (khong setState ben trong de tranh xung dot khi goi song song)
  const fetchResultFor = async (comment) => {
    try {
      const data = await predictFull(comment.text)
      return {
        ...comment,
        result: data,
        hidden: data.toxic.label !== 'CLEAN',
        loading: false
      }
    } catch {
      return { ...comment, loading: false }
    }
  }

  const analyzeComment = async (index) => {
    setComments(prev => {
      const updated = [...prev]
      updated[index] = { ...updated[index], loading: true }
      return updated
    })

    const updatedComment = await fetchResultFor(comments[index])

    setComments(prev => {
      const updated = [...prev]
      updated[index] = updatedComment
      return updated
    })
  }

  // Quet tat ca binh luan CUNG LUC bang Promise.all, thay vi await tuan tu tung cai
  // Giam thoi gian cho tu O(n) lan goi noi tiep xuong gan O(1) lan goi (chay song song)
  const analyzeAll = async () => {
    setScanning(true)

    setComments(prev => prev.map(c => ({ ...c, loading: true })))

    const results = await Promise.all(
      comments.map(c => fetchResultFor(c))
    )

    setComments(results)
    setScanning(false)
  }

  const addComment = async () => {
    if (!newText.trim()) return
    const newComment = { user: 'Bạn', text: newText, result: null, hidden: false, loading: true }
    const updated = [...comments, newComment]
    setComments(updated)
    setNewText('')

    const finalComment = await fetchResultFor(newComment)
    setComments(prev => {
      const copy = [...prev]
      copy[copy.length - 1] = finalComment
      return copy
    })
  }

  const sentimentColor = (s) => s === 'POS' ? '#38a169' : s === 'NEG' ? '#e94560' : '#e2a500'
  const sentimentLabel = (s) => s === 'POS' ? 'Tích cực' : s === 'NEG' ? 'Tiêu cực' : 'Trung lập'

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ margin: '0 0 8px', color: '#1a1a2e', fontSize: 22 }}>Kiểm duyệt bình luận</h2>
        <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
          Mô phỏng khu vực đánh giá sản phẩm thương mại điện tử. Hệ thống tự động ẩn bình luận
          vi phạm và gắn nhãn cảm xúc để ban quản trị dễ dàng theo dõi.
        </p>
      </div>

      <button
        onClick={analyzeAll}
        disabled={scanning}
        style={{
          marginBottom: 20, padding: '11px 28px',
          background: scanning ? '#aaa' : '#0f3460',
          color: '#fff', border: 'none', borderRadius: 8,
          cursor: scanning ? 'not-allowed' : 'pointer',
          fontWeight: 600, fontSize: 14
        }}
      >
        {scanning ? 'Đang quét...' : 'Quét tất cả bình luận'}
      </button>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
        {comments.map((c, i) => (
          <div key={i} style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 10, padding: '16px 20px',
            boxShadow: '0 1px 4px rgba(0,0,0,0.06)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <div>
                <span style={{ fontWeight: 700, color: '#2d3748' }}>{c.user}</span>
                <span style={{ fontSize: 12, color: '#aaa', marginLeft: 8 }}>Khách hàng</span>
              </div>
              {c.result && (
                <span style={{
                  fontSize: 12, padding: '3px 12px', borderRadius: 20, fontWeight: 700,
                  background: sentimentColor(c.result.sentiment.label),
                  color: '#fff'
                }}>
                  {sentimentLabel(c.result.sentiment.label)}
                </span>
              )}
            </div>

            {c.loading ? (
              <div style={{ color: '#aaa', fontStyle: 'italic', fontSize: 14 }}>Đang phân tích...</div>
            ) : c.hidden ? (
              <div style={{
                background: '#f7fafc', border: '1px dashed #cbd5e0',
                borderRadius: 8, padding: 12, textAlign: 'center', color: '#a0aec0', fontSize: 13
              }}>
                Bình luận đã bị ẩn do vi phạm tiêu chuẩn cộng đồng
                <button
                  onClick={() => setComments(prev => {
                    const u = [...prev]
                    u[i] = { ...u[i], hidden: false }
                    return u
                  })}
                  style={{ marginLeft: 12, fontSize: 12, color: '#0f3460', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Xem nội dung
                </button>
              </div>
            ) : (
              <p style={{ margin: 0, color: c.result?.toxic.label !== 'CLEAN' ? '#e94560' : '#4a5568', fontSize: 15, lineHeight: 1.5 }}>
                {c.text}
              </p>
            )}

            {!c.result && !c.loading && (
              <button
                onClick={() => analyzeComment(i)}
                style={{ marginTop: 10, fontSize: 12, padding: '5px 14px', background: '#edf2f7', border: 'none', borderRadius: 6, cursor: 'pointer', color: '#4a5568' }}
              >
                Quét bình luận này
              </button>
            )}
          </div>
        ))}
      </div>

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, padding: '20px 24px', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
        <h4 style={{ margin: '0 0 14px', color: '#2d3748' }}>Thêm bình luận mới</h4>
        <input
          style={{
            width: '100%', padding: '11px 14px', borderRadius: 8,
            border: '1.5px solid #e2e8f0', boxSizing: 'border-box',
            fontSize: 14, outline: 'none', fontFamily: 'inherit'
          }}
          placeholder="Nhập bình luận của bạn..."
          value={newText}
          onChange={e => setNewText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addComment()}
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck="false"
        />
        <button
          onClick={addComment}
          disabled={!newText.trim()}
          style={{
            marginTop: 12, padding: '10px 24px',
            background: '#0f3460', color: '#fff',
            border: 'none', borderRadius: 8,
            cursor: 'pointer', fontWeight: 600, fontSize: 14
          }}
        >
          Gửi bình luận
        </button>
      </div>
    </div>
  )
}