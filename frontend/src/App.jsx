import { useState } from 'react'
import MessageInput from './components/MessageInput'
import ExampleButtons from './components/ExampleButtons'
import AnalyzeButton from './components/AnalyzeButton'
import ResultCard from './components/ResultCard'
import { analyzeMessage, interpretContext } from './api/client'
import './App.css'

function parseRecipients(str) {
  if (!str || typeof str !== 'string') return []
  return str.split(',').map((s) => s.trim()).filter(Boolean)
}

function riskToStatus(riskLevel) {
  if (riskLevel === 'HIGH') return 'STOP_VERIFY'
  if (riskLevel === 'MEDIUM') return 'CHECK'
  return 'SAFE'
}

function App() {
  const [conversation, setConversation] = useState('')
  const [userContextDescription, setUserContextDescription] = useState('')
  const [recipientsStr, setRecipientsStr] = useState('')
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sent, setSent] = useState(false)

  const handleCheckEmail = async () => {
    setError(null)
    setLoading(true)
    try {
      let interpretedContext = {}
      if (userContextDescription.trim()) {
        interpretedContext = await interpretContext(userContextDescription.trim())
      }
      const recipients = parseRecipients(recipientsStr)
      const metadata = {
        conversation: conversation.trim(),
        source: 'web-simulated',
        recipients,
        attachments: [],
        user_context_description: userContextDescription.trim() || undefined,
        interpreted_context: Object.keys(interpretedContext).length > 0 ? interpretedContext : undefined,
      }
      const data = await analyzeMessage(text, metadata)
      setResult({
        ...data,
        interpreted_context: Object.keys(interpretedContext).length > 0 ? interpretedContext : undefined,
      })
    } catch (err) {
      setError(err.message || 'Analysis failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = () => {
    if (!result) {
      if (!window.confirm('You have not checked this email. Send anyway?')) return
    } else {
      const status = riskToStatus(result.risk_level)
      if (status === 'STOP_VERIFY') {
        if (!window.confirm('This action may have serious consequences. Send anyway?')) return
      }
    }
    setSent(true)
  }

  const handleComposeNew = () => {
    setConversation('')
    setUserContextDescription('')
    setRecipientsStr('')
    setText('')
    setResult(null)
    setError(null)
    setSent(false)
  }

  const handleExampleSelect = (example) => {
    if (example.text != null) setText(example.text)
    if (example.conversation != null) setConversation(example.conversation)
    if (example.situationDescription != null) setUserContextDescription(example.situationDescription)
  }

  if (sent) {
    return (
      <div className="app">
        <header className="app-header">
          <h1>PhishPup</h1>
        </header>
        <main className="app-main">
          <div className="sent-banner" role="status">Message sent</div>
          <button type="button" className="compose-btn" onClick={handleComposeNew}>
            Compose New Message
          </button>
        </main>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>PhishPup</h1>
      </header>
      <main className="app-main">
        <label className="context-label" htmlFor="conversation-context">
          Conversation Context
        </label>
        <textarea
          id="conversation-context"
          className="context-input"
          value={conversation}
          onChange={(e) => setConversation(e.target.value)}
          placeholder="Paste previous messages (optional)"
          rows={2}
          aria-label="Conversation context (optional)"
        />
        <label className="context-label" htmlFor="context-description">
          Situation Description
        </label>
        <textarea
          id="context-description"
          className="context-input"
          value={userContextDescription}
          onChange={(e) => setUserContextDescription(e.target.value)}
          placeholder="What kind of conversation is this? (optional)"
          rows={2}
          aria-label="What kind of conversation is this? (optional)"
        />
        <label className="context-label" htmlFor="recipients">
          Recipients
        </label>
        <input
          id="recipients"
          type="text"
          className="recipients-input"
          value={recipientsStr}
          onChange={(e) => setRecipientsStr(e.target.value)}
          placeholder="Comma-separated emails"
          aria-label="Recipients (comma-separated)"
        />
        <MessageInput value={text} onChange={setText} />
        <ExampleButtons onSelect={handleExampleSelect} />
        <div className="action-buttons">
          <AnalyzeButton label="Check Email" onClick={handleCheckEmail} disabled={loading} />
          <button type="button" className="send-btn" onClick={handleSend}>
            Send Email
          </button>
        </div>
        {loading && <p className="status">Analyzing…</p>}
        {error && <p className="error" role="alert">{error}</p>}
        <div>
          {result && (
            <ResultCard
              risk_level={result.risk_level}
              action={result.action}
              explanation={result.explanation}
              pressure_signals={result.pressure_signals}
              interpreted_context={result.interpreted_context}
            />
          )}
        </div>
      </main>
    </div>
  )
}

export default App
