import { useState, useRef, useEffect } from 'react'
import { Send, Bot, Paperclip, ChevronDown, LogOut, User, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('jwt_token'))
  const [authMode, setAuthMode] = useState('login')
  const [authUsername, setAuthUsername] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authError, setAuthError] = useState('')

  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am LLM Router. How can I help you today?', model: 'System' }
  ])
  const [input, setInput] = useState('')
  const [model, setModel] = useState('auto')
  const [isLoading, setIsLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMsg = input.trim()
    setInput('')

    setMessages(prev => [
      ...prev,
      { role: 'user', content: userMsg },
      { role: 'ai', content: '', model: '', isStreaming: true }
    ])
    setIsLoading(true)

    // Gather history (exclude 'system' role or streaming placeholders)
    const history = messages
      .filter(m => m.role !== 'system' && !m.isStreaming)
      .map(m => ({ role: m.role, content: m.content }));

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: userMsg, model, history })
      })

      if (response.status === 401) {
        handleLogout()
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let done = false
      let metaModel = ''

      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        const chunkValue = decoder.decode(value)

        const lines = chunkValue.split('\n').filter(line => line.trim() !== '')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6)
            if (dataStr === '[DONE]') {
              setMessages(prev => {
                const newMsgs = [...prev]
                const lastIdx = newMsgs.length - 1
                newMsgs[lastIdx] = { ...newMsgs[lastIdx], isStreaming: false }
                return newMsgs
              })
              break
            }
            try {
              const data = JSON.parse(dataStr)
              if (data.type === 'meta') {
                metaModel = data.model_used
                setMessages(prev => {
                  const newMsgs = [...prev]
                  const lastIdx = newMsgs.length - 1
                  newMsgs[lastIdx] = { ...newMsgs[lastIdx], model: metaModel }
                  return newMsgs
                })
              } else if (data.type === 'chunk') {
                setMessages(prev => {
                  const newMsgs = [...prev]
                  const lastIdx = newMsgs.length - 1
                  newMsgs[lastIdx] = {
                    ...newMsgs[lastIdx],
                    content: newMsgs[lastIdx].content + data.content
                  }
                  return newMsgs
                })
              }
            } catch (err) { }
          }
        }
      }

    } catch (error) {
      setMessages(prev => {
        const newMsgs = [...prev]
        newMsgs[newMsgs.length - 1].content = `Error: ${error.message}. Is the backend running?`
        newMsgs[newMsgs.length - 1].model = 'error'
        newMsgs[newMsgs.length - 1].isStreaming = false
        return newMsgs
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('jwt_token')
    setToken(null)
  }

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const url = authMode === 'login' ? 'http://localhost:8000/login' : 'http://localhost:8000/register';
      const body = { username: authUsername, password: authPassword };
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await response.json();
      if (response.ok) {
        if (authMode === 'login') {
          localStorage.setItem('jwt_token', data.access_token);
          setToken(data.access_token);
        } else {
          setAuthMode('login');
          setAuthError('Registration successful! Please login.');
        }
      } else {
        setAuthError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setAuthError('Network error');
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploadStatus('Uploading...')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.status === 401) {
        handleLogout()
        return
      }

      if (response.ok) {
        setUploadStatus('Uploaded!')
        setTimeout(() => setUploadStatus(''), 3000)
      } else {
        const error = await response.json()
        setUploadStatus(`Error: ${error.detail}`)
      }
    } catch (error) {
      setUploadStatus('Upload failed')
    }
    e.target.value = null
  }

  if (!token) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <div className="logo-container auth-logo">
            <Bot size={48} color="#a78bfa" className="glowing-icon" />
            <span className="logo-text">LLM Router</span>
          </div>
          <h2>{authMode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
          {authError && <div className="auth-error">{authError}</div>}
          <form onSubmit={handleAuth} className="auth-form">
            <div className="input-group">
              <input
                type="text"
                placeholder="Username"
                value={authUsername}
                onChange={e => setAuthUsername(e.target.value)}
                required
              />
            </div>
            <div className="input-group">
              <input
                type="password"
                placeholder="Password"
                value={authPassword}
                onChange={e => setAuthPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="auth-submit premium-btn">
              {authMode === 'login' ? 'Sign In' : 'Register'}
            </button>
          </form>
          <div className="auth-toggle">
            {authMode === 'login' ? (
              <p>Don't have an account? <span onClick={() => { setAuthMode('register'); setAuthError(''); }}>Register</span></p>
            ) : (
              <p>Already have an account? <span onClick={() => { setAuthMode('login'); setAuthError(''); }}>Login</span></p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-container">
          <Bot size={32} color="#a78bfa" className="glow-icon" />
          <span className="logo-text">LLM Router</span>
        </div>

        <div className="controls">
          {uploadStatus && <span className="upload-status">{uploadStatus}</span>}
          <div className="upload-wrapper">
            <button
              className="action-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Upload Support Docs"
            >
              <Paperclip size={18} />
              <span>Context</span>
            </button>
            <input
              type="file"
              ref={fileInputRef}
              className="upload-input"
              accept=".pdf,.txt"
              onChange={handleFileUpload}
            />
          </div>

          <div className="select-wrapper">
            <select
              className="model-select action-btn"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              <option value="auto">Auto Router ✨</option>
              <option value="gemini">Gemini Pro</option>
              <option value="mistral">Mistral Fast</option>
              <option value="granite">Granite Local</option>
            </select>
            <ChevronDown size={14} className="select-arrow" />
          </div>
          <button className="action-btn logout-btn" onClick={handleLogout} title="Logout">
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages-area">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'ai' ? <Bot size={20} /> : <User size={20} />}
              </div>
              <div className="message-content">
                {msg.role === 'ai' && msg.model && (
                  <div className="model-badge">{msg.model}</div>
                )}
                <div className={`message-bubble ${msg.role} ${msg.isStreaming ? 'streaming' : ''}`}>
                  {msg.role === 'ai' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content || (msg.isStreaming ? '...' : '')}
                    </ReactMarkdown>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && !messages[messages.length - 1]?.content && (
            <div className="message-wrapper ai">
              <div className="avatar"><Bot size={20} /></div>
              <div className="message-content">
                <div className="message-bubble ai typing">
                  <Loader2 className="spinner" size={20} /> Generating...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} className="scroll-anchor" />
        </div>

        <div className="input-area">
          <form className="input-form" onSubmit={handleSend}>
            <input
              type="text"
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message LLM Router..."
              disabled={isLoading && !messages[messages.length - 1]?.isStreaming}
            />
            <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
              <Send size={20} />
            </button>
          </form>
          <div className="footer-note">LLM Router can make mistakes. Consider verifying important information.</div>
        </div>
      </main>
    </div>
  )
}

export default App
