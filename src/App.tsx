import { useEffect, useMemo, useState } from 'react'
import {
  ArrowUpRight, Bell, Bot, Check, ChevronRight, CircleDollarSign, Clock3,
  Home, MessageCircle, MoreHorizontal, Plus, Search, ShieldCheck, Sparkles,
  Target, UserRound, Users, Wallet, X,
} from 'lucide-react'

type Tab = 'home' | 'circles' | 'chat' | 'profile'
type Toast = { message: string; tone?: 'success' | 'info' }

export const naira = (amount: number) => `₦${amount.toLocaleString('en-NG')}`

const circleData = [
  { name: 'The Builders', members: 12, saved: 186000, goal: 300000, color: 'purple', initials: ['AK', 'TO', 'YM', '+9'] },
  { name: 'UNILAG Creatives', members: 8, saved: 92000, goal: 150000, color: 'blue', initials: ['EO', 'KI', 'ZA', '+5'] },
  { name: 'Market Women 2.0', members: 24, saved: 420000, goal: 500000, color: 'peach', initials: ['FA', 'BI', 'MO', '+21'] },
]

function App() {
  const [tab, setTab] = useState<Tab>('home')
  const [showCopilot, setShowCopilot] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [toast, setToast] = useState<Toast | null>(null)
  const [joined, setJoined] = useState(false)
  const [chatMessage, setChatMessage] = useState('')
  const [messages, setMessages] = useState([
    { author: 'Tomi Ade', text: 'Our savings goal is looking great! 🎉', time: '10:42 AM', mine: false },
    { author: 'You', text: 'Just made my weekly contribution.', time: '10:45 AM', mine: true },
  ])
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'unavailable'>('checking')

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    fetch(`${apiUrl}/api/health`)
      .then((response) => {
        if (!response.ok) throw new Error('health check failed')
        setApiStatus('connected')
      })
      .catch(() => setApiStatus('unavailable'))
  }, [])

  const notify = (message: string, tone: Toast['tone'] = 'success') => {
    setToast({ message, tone })
    window.setTimeout(() => setToast(null), 2800)
  }

  const sendMessage = () => {
    const text = chatMessage.trim()
    if (!text) return
    setMessages((current) => [...current, { author: 'You', text, time: 'now', mine: true }])
    setChatMessage('')
    notify('Message sent')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">C</span><span>campus<span>circle</span></span></div>
        <div className="side-profile"><div className="avatar avatar-lg">OA</div><div><strong>Olamide A.</strong><small>University of Lagos</small></div></div>
        <Navigation tab={tab} setTab={setTab} />
        <div className="sidebar-bottom">
          <div className="security-note"><ShieldCheck size={17} /><div><strong>Your circle is safe</strong><small>Protected by CampusCircle</small></div></div>
          <button className="logout-button" onClick={() => notify('No active session', 'info')}>Sign out</button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="mobile-brand"><span className="brand-mark">C</span><b>campus<span>circle</span></b></div>
          <div className="topbar-actions">
            <button className="icon-button" aria-label="Search" onClick={() => notify('Search is ready for circles and members', 'info')}><Search size={19} /></button>
            <button className="icon-button notification-button" aria-label="Notifications" onClick={() => notify('You have 3 new notifications', 'info')}><Bell size={19} /><i /></button>
            <div className="avatar">OA</div>
          </div>
        </header>

        {tab === 'home' && <HomeView apiStatus={apiStatus} onAdd={() => setShowAdd(true)} onCopilot={() => setShowCopilot(true)} onJoin={() => { setJoined(true); notify('Welcome to The Builders!') }} onNotify={notify} joined={joined} />}
        {tab === 'circles' && <CirclesView onAdd={() => setShowAdd(true)} onJoin={() => { setJoined(true); notify('Welcome to The Builders!') }} joined={joined} />}
        {tab === 'chat' && <ChatView messages={messages} value={chatMessage} setValue={setChatMessage} onSend={sendMessage} />}
        {tab === 'profile' && <ProfileView onNotify={notify} />}
      </main>

      <nav className="bottom-nav"><Navigation tab={tab} setTab={setTab} mobile /></nav>
      {showAdd && <CreateCircle onClose={() => setShowAdd(false)} onCreate={() => { setShowAdd(false); notify('Circle created — invite your friends!') }} />}
      {showCopilot && <Copilot onClose={() => setShowCopilot(false)} />}
      {toast && <div className={`toast ${toast.tone === 'info' ? 'toast-info' : ''}`}><Check size={16} />{toast.message}</div>}
    </div>
  )
}

function Navigation({ tab, setTab, mobile = false }: { tab: Tab; setTab: (tab: Tab) => void; mobile?: boolean }) {
  const items: { id: Tab; label: string; icon: typeof Home }[] = [
    { id: 'home', label: 'Home', icon: Home }, { id: 'circles', label: 'My circles', icon: Users },
    { id: 'chat', label: 'Chat', icon: MessageCircle }, { id: 'profile', label: 'Profile', icon: UserRound },
  ]
  return <div className={mobile ? 'mobile-nav-items' : 'nav-items'}>{items.map(({ id, label, icon: Icon }) => <button key={id} className={tab === id ? 'nav-item active' : 'nav-item'} onClick={() => setTab(id)}><Icon size={19} /><span>{label}</span>{id === 'chat' && <em>2</em>}</button>)}</div>
}

function HomeView({ apiStatus, onAdd, onCopilot, onJoin, onNotify, joined }: { apiStatus: 'checking' | 'connected' | 'unavailable'; onAdd: () => void; onCopilot: () => void; onJoin: () => void; onNotify: (message: string, tone?: Toast['tone']) => void; joined: boolean }) {
  return <div className="page">
    <section className="welcome-row"><div><p className="eyebrow">WEDNESDAY, 14 OCTOBER 2026</p><h1>Good morning, Olamide <span>✦</span></h1><p className="muted">Your money grows better together.</p></div><button className="primary-button desktop-only" onClick={onAdd}><Plus size={18} /> Start a circle</button></section>
    <div className="demo-banner"><Sparkles size={17} /><span><strong>{apiStatus === 'connected' ? 'Backend connected' : apiStatus === 'checking' ? 'Connecting' : 'Backend unavailable'}</strong> — {apiStatus === 'connected' ? 'secure account data will load after sign-in.' : 'sign in and provider-backed financial data are unavailable until the API is running.'}</span></div>
    <section className="balance-card"><div><p className="card-label">TOTAL SAVINGS <span className="live-dot" /></p><h2>{apiStatus === 'connected' ? '—' : 'Unavailable'}</h2><p className="positive"><Clock3 size={15} /> Authoritative balance requires sign-in</p></div><div className="balance-illustration"><div className="coin coin-one">₦</div><div className="coin coin-two">₦</div><div className="coin coin-three">₦</div></div><button className="balance-link" onClick={() => onNotify('Sign in to view your wallet', 'info')}>View wallet <ChevronRight size={15} /></button></section>
    <div className="stat-grid"><Stat icon={<Target />} label="Active goals" value="—" detail="Sign in to load goals" /><Stat icon={<CircleDollarSign />} label="This month" value="—" detail="Authoritative ledger data" /><Stat icon={<Wallet />} label="Available balance" value="—" detail="Sign in to load balance" /></div>
    <section className="section-heading"><div><h2>Your circles</h2><p className="muted">Keep showing up for your community.</p></div><button className="text-button" onClick={onAdd}>Create new <Plus size={16} /></button></section>
    <div className="circle-grid">{circleData.slice(0, 2).map((circle) => <CircleCard key={circle.name} circle={circle} />)}<JoinCard onJoin={onJoin} joined={joined} /></div>
    <section className="section-heading activity-heading"><div><h2>Recent activity</h2><p className="muted">Your latest circle updates.</p></div><button className="text-button">See all <ChevronRight size={16} /></button></section>
    <Activity />
    <button className="copilot-fab" onClick={onCopilot}><Bot size={20} /><span>Ask Copilot</span></button>
  </div>
}

function Stat({ icon, label, value, detail }: { icon: React.ReactNode; label: string; value: string; detail: string }) {
  return <div className="stat-card"><div className="stat-icon">{icon}</div><p>{label}</p><strong>{value}</strong><small>{detail}</small></div>
}

function CircleCard({ circle }: { circle: typeof circleData[number] }) {
  const percent = Math.round((circle.saved / circle.goal) * 100)
  return <article className="circle-card"><div className={`circle-cover ${circle.color}`}><span>{circle.name[0]}</span><button aria-label="More options"><MoreHorizontal size={18} /></button></div><div className="circle-body"><div className="circle-title"><div><h3>{circle.name}</h3><p><Users size={14} /> {circle.members} members</p></div><span className="status-pill">Active</span></div><div className="progress-meta"><span>Savings goal</span><b>{percent}%</b></div><div className="progress-track"><span style={{ width: `${percent}%` }} /></div><div className="circle-footer"><strong>{naira(circle.saved)} <small>of {naira(circle.goal)}</small></strong><div className="avatar-stack">{circle.initials.map((initial) => <span key={initial} className="mini-avatar">{initial}</span>)}</div></div></div></article>
}

function JoinCard({ onJoin, joined }: { onJoin: () => void; joined: boolean }) {
  return <article className="join-card"><div className="join-icon"><Plus size={20} /></div><h3>{joined ? 'You joined The Builders' : 'Join a new circle'}</h3><p>{joined ? 'Your new community is now on your dashboard.' : 'Find people who share your goals and grow together.'}</p><button className="secondary-button" onClick={onJoin}>{joined ? 'View circle' : 'Explore circles'} <ArrowUpRight size={16} /></button></article>
}

function Activity() {
  return <div className="activity-list"><div className="activity-item"><div className="activity-icon green"><Check size={16} /></div><div><strong>Contribution made</strong><p>You added ₦8,000 to The Builders</p></div><time>Today, 9:24 AM</time></div><div className="activity-item"><div className="activity-icon purple"><Users size={16} /></div><div><strong>New member joined</strong><p>Chisom joined UNILAG Creatives</p></div><time>Yesterday</time></div><div className="activity-item"><div className="activity-icon orange"><Clock3 size={16} /></div><div><strong>Loan repayment due soon</strong><p>Your ₦12,500 instalment is due in 5 days</p></div><time>Mon, 12 Oct</time></div></div>
}

function CirclesView({ onAdd, onJoin, joined }: { onAdd: () => void; onJoin: () => void; joined: boolean }) {
  return <div className="page"><section className="welcome-row"><div><p className="eyebrow">COMMUNITY</p><h1>Your circles</h1><p className="muted">Small steps. Shared goals. Real progress.</p></div><button className="primary-button desktop-only" onClick={onAdd}><Plus size={18} /> Start a circle</button></section><div className="filter-row"><div className="search-field"><Search size={17} /><input placeholder="Search circles" /></div><button className="filter-button">All circles <ChevronRight size={15} /></button></div><div className="circle-grid circle-grid-wide">{circleData.map((circle) => <CircleCard key={circle.name} circle={circle} />)}<JoinCard onJoin={onJoin} joined={joined} /></div><div className="empty-help"><Sparkles size={20} /><div><strong>Looking for your people?</strong><p>Search by university, interest, or invite code to find the right circle.</p></div><button className="text-button">Browse directory <ChevronRight size={15} /></button></div></div>
}

function ChatView({ messages, value, setValue, onSend }: { messages: { author: string; text: string; time: string; mine: boolean }[]; value: string; setValue: (value: string) => void; onSend: () => void }) {
  return <div className="page chat-page"><section className="welcome-row"><div><p className="eyebrow">YOUR CONVERSATIONS</p><h1>Circle chat</h1><p className="muted">Sign in to load private Circle conversations.</p></div></section><div className="chat-layout"><aside className="chat-list"><div className="chat-list-head"><h3>Messages</h3><button className="icon-button" aria-label="New conversation" disabled><Plus size={17} /></button></div><div className="conversation selected"><div className="circle-thumb purple">C</div><div><strong>Circle chat</strong><p>Secure messages appear here.</p></div></div></aside><section className="chat-window"><div className="chat-header"><div className="circle-thumb purple">C</div><div><strong>Circle chat</strong><p>Membership required</p></div><button className="icon-button" disabled><MoreHorizontal size={18} /></button></div><div className="chat-messages"><div className="day-divider">PRIVATE</div>{messages.length === 0 ? <p className="muted">No messages yet.</p> : messages.map((message, index) => <div className={`message-row ${message.mine ? 'mine' : ''}`} key={`${message.text}-${index}`}><div className="avatar avatar-sm">{message.mine ? 'You' : 'Member'}</div><div><small>{message.author}</small><div className="message-bubble">{message.text}</div><time>{message.time}</time></div></div>)}</div><div className="chat-compose"><button className="icon-button" aria-label="Attach file" disabled><Plus size={19} /></button><input value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') onSend() }} placeholder="Sign in to send a message..." disabled /><button className="voice-button" disabled aria-label="Voice notes unavailable"><span>●</span></button><button className="send-button" onClick={onSend} disabled><ArrowUpRight size={18} /></button></div></section></div></div>
}

function ProfileView({ onNotify }: { onNotify: (message: string, tone?: Toast['tone']) => void }) {
  return <div className="page"><section className="welcome-row"><div><p className="eyebrow">ACCOUNT</p><h1>Your profile</h1><p className="muted">Sign in to load your account details and security settings.</p></div></section><div className="profile-grid"><section className="profile-card"><div className="profile-hero"><div className="avatar avatar-xl">?</div><div><h2>Account details unavailable</h2><p>Authenticate to view private profile data.</p></div><button className="secondary-button" onClick={() => onNotify('Profile editing requires an authenticated session', 'info')}>Edit profile</button></div></section><section className="settings-card"><h3>Trust & safety</h3><div className="setting-row"><div className="setting-icon green"><ShieldCheck size={18} /></div><div><strong>Email verification</strong><p>Verified status appears after registration</p></div><Clock3 className="setting-check" size={18} /></div><div className="setting-row"><div className="setting-icon purple"><Wallet size={18} /></div><div><strong>Financial onboarding</strong><p>Provider-specific KYC is requested only when required</p></div><button className="text-button" onClick={() => onNotify('Sign in to begin onboarding', 'info')}>Start <ChevronRight size={15} /></button></div></section></div></div>
}

function CreateCircle({ onClose, onCreate }: { onClose: () => void; onCreate: () => void }) {
  const [name, setName] = useState('')
  return <div className="modal-backdrop"><div className="modal"><button className="modal-close" onClick={onClose}><X size={19} /></button><div className="modal-icon purple"><Users size={21} /></div><p className="eyebrow">NEW COMMUNITY</p><h2>Start a circle</h2><p className="muted">Create a safe space for your friends to save, plan and grow together.</p><label>Circle name<input autoFocus value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Final Year Crew" /></label><label>What are you saving for?<input placeholder="e.g. Group project or rent" /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={!name.trim()} onClick={onCreate}>Create circle <ArrowUpRight size={17} /></button></div></div></div>
}

function Copilot({ onClose }: { onClose: () => void }) {
  const [question, setQuestion] = useState('')
  const [asked, setAsked] = useState(false)
  const answer = useMemo(() => asked ? 'Your Builders circle has saved ₦186,000 of its ₦300,000 goal — that is 62% progress. You are on track to reach the goal if everyone keeps up their weekly contributions.' : '', [asked])
  return <div className="copilot-panel"><div className="copilot-header"><div className="copilot-title"><div className="bot-icon"><Bot size={19} /></div><div><strong>CampusCircle Copilot</strong><p>Helpful answers, grounded in your data</p></div></div><button className="icon-button" onClick={onClose}><X size={18} /></button></div><div className="copilot-content"><div className="copilot-intro"><Sparkles size={18} /><p>Hi Olamide! I can explain your savings, loan terms and circle activity in simple language.</p></div>{asked && <div className="copilot-answer"><strong>Copilot <span>SIMULATED</span></strong><p>{answer}</p></div>}<p className="suggestion-label">Try asking</p><div className="suggestions"><button onClick={() => { setQuestion('How is The Builders doing?'); setAsked(true) }}>How is my circle doing?</button><button onClick={() => { setQuestion('Explain my repayment'); setAsked(true) }}>Explain my repayment</button></div></div><div className="copilot-input"><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask anything..." onKeyDown={(event) => { if (event.key === 'Enter' && question.trim()) setAsked(true) }} /><button onClick={() => question.trim() && setAsked(true)}><ArrowUpRight size={18} /></button></div></div>
}

export default App
