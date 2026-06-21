import { useState } from 'react'
import PostModeration from './pages/PostModeration'
import CommentModeration from './pages/CommentModeration'
import LiveChat from './pages/LiveChat'
import Dashboard from './pages/Dashboard'
import './App.css'

const TABS = [
  { key: 'post',      label: 'Kiểm duyệt bài đăng' },
  { key: 'comment',   label: 'Kiểm duyệt bình luận' },
  { key: 'livechat',  label: 'Trò chuyện trực tiếp' },
  { key: 'dashboard', label: 'Bảng điều khiển' },
]

export default function App() {
  const [tab, setTab] = useState('post')

  return (
    <div style={{ fontFamily: "'Segoe UI', sans-serif", minHeight: '100vh', background: '#f0f2f5' }}>
      <header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: '#fff',
        padding: '20px 40px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.3)'
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <h1 style={{ margin: 0, fontSize: 24, letterSpacing: 1 }}>
            TCSA — Hệ thống Trợ lý Lọc nội dung độc hại
          </h1>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: '#aaa' }}>
            Phân tích cảm xúc và kiểm duyệt nội dung thời gian thực
          </p>
        </div>
      </header>

      <nav style={{ background: '#16213e', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'flex' }}>
          {TABS.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              style={{
                padding: '14px 24px',
                border: 'none',
                cursor: 'pointer',
                background: 'transparent',
                color: tab === t.key ? '#e94560' : '#aaa',
                fontWeight: tab === t.key ? 'bold' : 'normal',
                fontSize: 14,
                borderBottom: tab === t.key ? '3px solid #e94560' : '3px solid transparent',
                transition: 'all 0.2s'
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '36px 24px' }}>
        {tab === 'post'      && <PostModeration />}
        {tab === 'comment'   && <CommentModeration />}
        {tab === 'livechat'  && <LiveChat />}
        {tab === 'dashboard' && <Dashboard />}
      </main>

      <footer style={{ textAlign: 'center', padding: '20px', color: '#aaa', fontSize: 12, borderTop: '1px solid #ddd', background: '#fff' }}>
        TCSA — Dự án môn Trí tuệ Nhân tạo
      </footer>
    </div>
  )
}