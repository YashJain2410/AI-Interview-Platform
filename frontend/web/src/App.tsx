import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, NavLink, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, ArrowRight, BarChart3, Bell, BrainCircuit, BriefcaseBusiness,
  Check, ChevronDown, ChevronRight, Clock3, FileText, Headphones, History,
  LayoutDashboard, Mic, MicOff, MoreHorizontal, Pause, Play, Plus, Search,
  Settings, ShieldCheck, Sparkles, Target, UploadCloud, UserRound, Volume2, X,
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS_URL = import.meta.env.VITE_WS_URL || API_URL.replace(/^http/, 'ws')

type SetupState = {
  name: string
  role: string
  type: 'Balanced' | 'Technical' | 'Behavioral'
  difficulty: 'Adaptive' | 'Beginner' | 'Advanced'
  duration: number
  resume?: File
  jobDescription?: File
}

type Message = { role: 'ai' | 'candidate'; content: string }

const defaultSetup: SetupState = {
  name: 'Yash', role: 'AI / ML Engineer', type: 'Balanced', difficulty: 'Adaptive', duration: 30,
}

function Brand() {
  return <Link className="brand" to="/" aria-label="Interview home">
    <span className="ghost-mark" aria-hidden="true"><i /><i /><i /></span>
    <span>interview</span>
  </Link>
}

const primaryNav = [
  ['/', 'Overview', LayoutDashboard],
  ['/interviews', 'Interviews', Mic],
  ['/reports', 'Reports', BarChart3],
  ['/history', 'History', History],
] as const

function Shell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  useEffect(() => setMobileOpen(false), [location.pathname])
  return <div className="app-shell">
    <header className="topbar">
      <Brand />
      <nav className="desktop-nav" aria-label="Primary">
        {primaryNav.map(([to, label]) => <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>)}
      </nav>
      <div className="top-actions">
        <button className="icon-btn" aria-label="Search"><Search size={20} /></button>
        <button className="icon-btn notification" aria-label="Notifications"><Bell size={20} /><span /></button>
        <Link className="profile-pill" to="/settings"><span>YJ</span><span className="profile-copy"><b>Yash Jain</b><small>Candidate</small></span><ChevronDown size={17} /></Link>
        <button className="menu-btn" aria-label="Toggle menu" onClick={() => setMobileOpen(v => !v)}>{mobileOpen ? <X /> : <MoreHorizontal />}</button>
      </div>
    </header>
    {mobileOpen && <nav className="mobile-nav" aria-label="Mobile navigation">
      {primaryNav.map(([to, label, Icon]) => <NavLink key={to} to={to} end={to === '/'}><Icon size={19} />{label}</NavLink>)}
      <NavLink to="/settings"><Settings size={19} />Settings</NavLink>
    </nav>}
    <main>{children}</main>
  </div>
}

function StatusPill({ children, tone = 'purple' }: { children: React.ReactNode; tone?: 'purple' | 'green' | 'neutral' }) {
  return <span className={`status-pill ${tone}`}>{children}</span>
}

function Dashboard() {
  return <Shell>
    <section className="page dashboard-page">
      <div className="page-heading split-heading">
        <div><p className="eyebrow">Friday, September 5</p><h1>Ready for your next move?</h1><p>Practice with an interviewer that listens, adapts, and helps you grow.</p></div>
        <Link to="/interviews/new" className="button primary"><Plus size={19} /> New interview</Link>
      </div>

      <div className="hero-grid">
        <article className="start-card">
          <div className="orb-wrap"><div className="voice-orb"><span /><span /><span /><span /><span /></div><div className="orb-ring r1" /><div className="orb-ring r2" /></div>
          <div className="start-copy">
            <StatusPill><Sparkles size={14} /> AI voice interview</StatusPill>
            <h2>Practice the interview,<br />not the script.</h2>
            <p>Get a live, role-specific interview shaped by your resume, experience, and goals.</p>
            <Link to="/interviews/new" className="button light">Start practicing <ArrowRight size={18} /></Link>
          </div>
        </article>
        <article className="readiness-card">
          <div className="card-title"><div><p className="eyebrow">Interview readiness</p><h3>Your weekly pulse</h3></div><button className="round-more" aria-label="More options"><MoreHorizontal /></button></div>
          <div className="score-row"><div className="score-ring"><span><b>78</b><small>/100</small></span></div><div><strong>On the right track</strong><p>Up 8 points this week</p><StatusPill tone="green">+10%</StatusPill></div></div>
          <div className="mini-bars"><span><i style={{height:'44%'}} /></span><span><i style={{height:'62%'}} /></span><span><i style={{height:'54%'}} /></span><span><i style={{height:'76%'}} /></span><span><i style={{height:'68%'}} /></span><span><i style={{height:'88%'}} /></span><span><i style={{height:'78%'}} /></span></div>
          <div className="week-labels"><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span></div>
        </article>
      </div>

      <section className="section-block">
        <div className="section-heading"><div><h2>Keep your momentum</h2><p>Focused practice based on your recent performance.</p></div><Link to="/reports">View insights <ArrowRight size={16} /></Link></div>
        <div className="practice-grid">
          <PracticeCard icon={<BrainCircuit />} color="lilac" title="System design" meta="12 min · Advanced" progress={68} copy="Explain tradeoffs with more structure." />
          <PracticeCard icon={<BriefcaseBusiness />} color="mint" title="Behavioral stories" meta="8 min · Adaptive" progress={82} copy="Make your impact easier to measure." />
          <PracticeCard icon={<Target />} color="peach" title="Technical depth" meta="15 min · Intermediate" progress={54} copy="Go one layer deeper on implementation." />
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading"><div><h2>Recent interviews</h2><p>Pick up where you left off.</p></div><Link to="/history">See all <ArrowRight size={16} /></Link></div>
        <div className="recent-table">
          <div className="table-head"><span>Role</span><span>Focus</span><span>Date</span><span>Score</span><span /></div>
          <RecentRow role="Senior ML Engineer" focus="Technical" date="Sep 3" score="86" tone="green" />
          <RecentRow role="Backend Engineer" focus="System design" date="Aug 29" score="78" tone="purple" />
          <RecentRow role="AI Engineer" focus="Balanced" date="Aug 24" score="72" tone="neutral" />
        </div>
      </section>
    </section>
  </Shell>
}

function PracticeCard({ icon, color, title, meta, copy, progress }: { icon: React.ReactNode; color: string; title: string; meta: string; copy: string; progress: number }) {
  return <article className="practice-card"><div className={`practice-icon ${color}`}>{icon}</div><div className="practice-top"><StatusPill tone="neutral">Recommended</StatusPill><button className="round-more"><MoreHorizontal /></button></div><h3>{title}</h3><p className="practice-meta">{meta}</p><p>{copy}</p><div className="progress"><i style={{width:`${progress}%`}} /></div><div className="practice-foot"><span>{progress}% readiness</span><Link to="/interviews/new" aria-label={`Practice ${title}`}><ArrowRight size={18} /></Link></div></article>
}

function RecentRow({ role, focus, date, score, tone }: { role: string; focus: string; date: string; score: string; tone: 'green'|'purple'|'neutral' }) {
  return <Link to="/reports/latest" className="table-row"><span className="role-cell"><span className="role-icon"><BriefcaseBusiness size={18} /></span><b>{role}</b></span><span>{focus}</span><span>{date}</span><span><StatusPill tone={tone}>{score}/100</StatusPill></span><span><ChevronRight size={18} /></span></Link>
}

function Interviews() {
  return <Shell><section className="page"><div className="page-heading split-heading"><div><p className="eyebrow">Practice room</p><h1>Your interviews</h1><p>Prepare for a specific role or sharpen one skill at a time.</p></div><Link to="/interviews/new" className="button primary"><Plus size={19}/> New interview</Link></div><div className="empty-feature"><div className="big-mark"><Mic /></div><h2>A better answer starts with a real question.</h2><p>Choose a role, add your context, and your interviewer will take it from there.</p><Link to="/interviews/new" className="button dark">Set up an interview <ArrowRight size={18}/></Link></div></section></Shell>
}

function FileDrop({ label, file, onFile, accept }: { label: string; file?: File; onFile: (f?: File) => void; accept: string }) {
  const id = label.toLowerCase().replace(/\W/g, '-')
  return <label className={`file-drop ${file ? 'has-file' : ''}`} htmlFor={id}>
    <input id={id} type="file" accept={accept} onChange={e => onFile(e.target.files?.[0])} />
    <span className="upload-icon">{file ? <Check /> : <UploadCloud />}</span>
    <span><b>{file ? file.name : label}</b><small>{file ? `${Math.max(1, Math.round(file.size / 1024))} KB · Ready` : 'PDF, DOCX, or TXT · up to 10 MB'}</small></span>
    {file && <button type="button" aria-label={`Remove ${label}`} onClick={e => {e.preventDefault(); onFile(undefined)}}><X size={17}/></button>}
  </label>
}

function NewInterview() {
  const navigate = useNavigate()
  const [setup, setSetup] = useState<SetupState>(() => {
    try { return {...defaultSetup, ...JSON.parse(sessionStorage.getItem('interview.setup') || '{}')} }
    catch { return defaultSetup }
  })
  const set = <K extends keyof SetupState>(key: K, value: SetupState[K]) => setSetup(v => ({...v, [key]: value}))
  const begin = () => { sessionStorage.setItem('interview.setup', JSON.stringify({...setup, resume: setup.resume?.name, jobDescription: setup.jobDescription?.name})); navigate('/interview/live') }
  return <Shell><section className="page setup-page">
    <Link className="back-link" to="/interviews"><ArrowLeft size={17}/> Interviews</Link>
    <div className="setup-heading"><StatusPill><Sparkles size={14}/> Personalised practice</StatusPill><h1>Let’s shape your interview.</h1><p>A little context helps the interviewer ask much better questions.</p></div>
    <div className="setup-layout"><div className="setup-main">
      <section className="form-card"><div className="step-number">1</div><div className="form-content"><h2>What are you preparing for?</h2><p>Tell us the role you want to practice.</p><label className="field-label">Your name<input value={setup.name} onChange={e => set('name', e.target.value)} placeholder="How should we address you?" /></label><label className="field-label">Target role<input value={setup.role} onChange={e => set('role', e.target.value)} placeholder="e.g. Senior Backend Engineer" /></label><div className="field-label">Interview focus<div className="choice-grid">{(['Balanced','Technical','Behavioral'] as const).map(x => <button key={x} className={setup.type === x ? 'selected' : ''} onClick={() => set('type', x)}><span>{x === 'Balanced' ? <Sparkles/> : x === 'Technical' ? <BrainCircuit/> : <UserRound/>}</span><b>{x}</b><small>{x === 'Balanced' ? 'A complete interview loop' : x === 'Technical' ? 'Code, systems, and depth' : 'Stories, impact, and fit'}</small></button>)}</div></div></div></section>
      <section className="form-card"><div className="step-number">2</div><div className="form-content"><h2>Add your context</h2><p>Optional now, powerful when resume and JD ingestion are connected.</p><div className="file-grid"><FileDrop label="Add your resume" file={setup.resume} onFile={f => set('resume', f)} accept=".pdf,.doc,.docx,.txt"/><FileDrop label="Add job description" file={setup.jobDescription} onFile={f => set('jobDescription', f)} accept=".pdf,.doc,.docx,.txt"/></div><div className="privacy-note"><ShieldCheck size={18}/><span><b>Your files stay private.</b> They’re used only to tailor this interview.</span></div></div></section>
      <section className="form-card"><div className="step-number">3</div><div className="form-content"><h2>Choose your pace</h2><div className="two-fields"><div className="field-label">Difficulty<div className="segmented">{(['Adaptive','Beginner','Advanced'] as const).map(x=><button key={x} className={setup.difficulty===x?'active':''} onClick={()=>set('difficulty',x)}>{x}</button>)}</div></div><label className="field-label">Duration<select value={setup.duration} onChange={e=>set('duration',Number(e.target.value))}><option value={15}>15 minutes</option><option value={30}>30 minutes</option><option value={45}>45 minutes</option><option value={60}>60 minutes</option></select></label></div></div></section>
    </div><aside className="setup-summary"><p className="eyebrow">Your session</p><h3>{setup.role || 'Untitled role'}</h3><div className="summary-row"><span><Target/>Focus</span><b>{setup.type}</b></div><div className="summary-row"><span><BrainCircuit/>Difficulty</span><b>{setup.difficulty}</b></div><div className="summary-row"><span><Clock3/>Duration</span><b>{setup.duration} min</b></div><div className="summary-row"><span><FileText/>Context</span><b>{[setup.resume, setup.jobDescription].filter(Boolean).length}/2 added</b></div><button className="button primary full" disabled={!setup.name.trim() || !setup.role.trim()} onClick={begin}>Enter interview room <ArrowRight size={18}/></button><p className="summary-foot"><Mic size={14}/> You’ll check your microphone before starting.</p></aside></div>
  </section></Shell>
}

function LiveInterview() {
  const navigate = useNavigate()
  const [setup] = useState<SetupState>(() => { try { return {...defaultSetup, ...JSON.parse(sessionStorage.getItem('interview.setup') || '{}')} } catch { return defaultSetup } })
  const [phase, setPhase] = useState<'ready'|'connecting'|'live'|'paused'|'ended'>('ready')
  const [messages, setMessages] = useState<Message[]>([])
  const [answer, setAnswer] = useState('')
  const [seconds, setSeconds] = useState(0)
  const [muted, setMuted] = useState(false)
  const [connectionNote, setConnectionNote] = useState('Ready to connect')
  const socketRef = useRef<WebSocket | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const pcRef = useRef<RTCPeerConnection | null>(null)

  useEffect(() => { if (phase !== 'live') return; const id=setInterval(()=>setSeconds(s=>s+1),1000); return ()=>clearInterval(id) }, [phase])
  useEffect(() => () => { socketRef.current?.close(); streamRef.current?.getTracks().forEach(t=>t.stop()); pcRef.current?.close() }, [])

  const connectVoice = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false})
    streamRef.current = stream
    const pc = new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]})
    pcRef.current = pc
    stream.getTracks().forEach(track => pc.addTrack(track, stream))
    pc.ontrack = event => { const audio = new Audio(); audio.srcObject = event.streams[0]; audio.autoplay = true; void audio.play() }
    const offer = await pc.createOffer({offerToReceiveAudio:true}); await pc.setLocalDescription(offer)
    const response = await fetch(`${API_URL}/webrtc/offer`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sdp:offer.sdp,type:offer.type})})
    if (!response.ok) throw new Error('Voice connection failed')
    const remote = await response.json(); await pc.setRemoteDescription(remote)
  }

  const start = async () => {
    setPhase('connecting'); setConnectionNote('Connecting to your interviewer…')
    try {
      try { await connectVoice() } catch { /* text socket remains fully usable */ }
      const ws = new WebSocket(`${WS_URL}/ws/interview`); socketRef.current = ws
      ws.onopen = () => ws.send(JSON.stringify({candidate_name: setup.name}))
      ws.onmessage = event => { const data=JSON.parse(event.data); if(data.event==='session_started'){setPhase('live');setConnectionNote('Live · connection secure')} if(data.event==='ai_question') setMessages(v=>[...v,{role:'ai',content:data.content}]) }
      ws.onerror = () => { setPhase('live'); setConnectionNote('Demo mode · backend unavailable'); setMessages([{role:'ai',content:`Hi ${setup.name}. Let’s start with your background. What drew you to ${setup.role} work?`}]) }
    } catch { setPhase('live'); setConnectionNote('Demo mode · backend unavailable'); setMessages([{role:'ai',content:`Hi ${setup.name}. Let’s start with your background. What drew you to ${setup.role} work?`}]) }
  }
  const submit = () => { const text=answer.trim(); if(!text)return; setMessages(v=>[...v,{role:'candidate',content:text}]); setAnswer(''); if(socketRef.current?.readyState===WebSocket.OPEN) socketRef.current.send(JSON.stringify({content:text})); else setTimeout(()=>setMessages(v=>[...v,{role:'ai',content:'That gives me useful context. Can you walk me through one technical decision you made, the tradeoffs you considered, and the result?'}]),550) }
  const finish = () => { socketRef.current?.close(); streamRef.current?.getTracks().forEach(t=>t.stop()); pcRef.current?.close(); setPhase('ended'); setTimeout(()=>navigate('/reports/latest'),450) }
  const toggleMute = () => { const next=!muted; streamRef.current?.getAudioTracks().forEach(t=>t.enabled=!next); setMuted(next) }
  const time = `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`
  const latestAi = [...messages].reverse().find(m=>m.role==='ai')

  return <div className="interview-room">
    <header className="room-header"><Brand/><div className="room-meta"><StatusPill tone={phase==='live'?'green':'neutral'}><span className="live-dot"/>{phase==='live'?'Live':phase==='connecting'?'Connecting':'Practice room'}</StatusPill><span>{setup.role}</span><span className="time"><Clock3 size={16}/>{time}</span></div><button className="button danger-soft" onClick={finish} disabled={phase==='ready'||phase==='connecting'}>End interview</button></header>
    <main className="room-main">
      {phase==='ready' && <section className="lobby-card"><div className="lobby-visual"><div className="voice-orb large"><span/><span/><span/><span/><span/></div></div><StatusPill><Headphones size={14}/> Private practice room</StatusPill><h1>Your interviewer is ready.</h1><p>Find a quiet space, check your microphone, and answer as naturally as you would in the real interview.</p><div className="checks"><span><Check/>Microphone access requested on start</span><span><Check/>{setup.duration}-minute {setup.type.toLowerCase()} session</span><span><Check/>Adaptive follow-up questions</span></div><button className="button primary hero-button" onClick={start}><Mic size={19}/> Start interview</button></section>}
      {phase==='connecting' && <section className="lobby-card"><div className="pulse-loader"><span/><span/><span/></div><h1>Opening the room…</h1><p>{connectionNote}</p></section>}
      {(phase==='live'||phase==='paused') && <div className="conversation-layout"><section className="interviewer-stage"><div className="stage-top"><div><p className="eyebrow">AI interviewer</p><h2>Maya</h2></div><span className="connection"><i/>{connectionNote}</span></div><div className="avatar-orb"><div className="voice-bars"><i/><i/><i/><i/><i/><i/><i/></div></div><div className="question-card"><span>Current question</span><p>{latestAi?.content || 'Take a breath. Your first question is on the way.'}</p></div></section><aside className="transcript-panel"><div className="panel-heading"><div><h3>Live transcript</h3><p>Your conversation appears here.</p></div><Volume2 size={20}/></div><div className="transcript-list">{messages.map((m,i)=><div className={`message ${m.role}`} key={i}><div className="message-meta"><b>{m.role==='ai'?'Maya':'You'}</b><small>{i===0?'Now':`${i}m`}</small></div><p>{m.content}</p></div>)}</div><div className="answer-box"><textarea value={answer} onChange={e=>setAnswer(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();submit()}}} placeholder="Type an answer, or respond by voice…"/><button onClick={submit} aria-label="Send answer"><ArrowRight/></button></div></aside></div>}
    </main>
    {(phase==='live'||phase==='paused') && <div className="room-controls"><button className={muted?'active':''} onClick={toggleMute} aria-label={muted?'Unmute':'Mute'}>{muted?<MicOff/>:<Mic/>}</button><button onClick={()=>setPhase(p=>p==='paused'?'live':'paused')} aria-label={phase==='paused'?'Resume':'Pause'}>{phase==='paused'?<Play/>:<Pause/>}</button><span>{phase==='paused'?'Interview paused':'Maya is listening'}</span></div>}
  </div>
}

const scoreData = [
  ['Technical correctness', 84, 'Strong'], ['Depth of understanding', 76, 'Good'], ['Communication', 91, 'Excellent'], ['Confidence', 72, 'Growing'],
] as const

function Reports({ detail = false }: { detail?: boolean }) {
  if (!detail) return <Shell><section className="page"><div className="page-heading"><p className="eyebrow">Performance</p><h1>Reports</h1><p>See the patterns behind every answer and decide what to practice next.</p></div><div className="report-list"><Link to="/reports/latest" className="report-list-card"><div className="report-date"><b>03</b><span>SEP</span></div><div><h3>Senior ML Engineer</h3><p>Technical · 30 minutes · 14 questions</p></div><div className="report-score">86<small>/100</small></div><ChevronRight/></Link><Link to="/reports/latest" className="report-list-card"><div className="report-date muted"><b>29</b><span>AUG</span></div><div><h3>Backend Engineer</h3><p>System design · 45 minutes · 11 questions</p></div><div className="report-score">78<small>/100</small></div><ChevronRight/></Link></div></section></Shell>
  return <Shell><section className="page report-detail">
    <Link className="back-link" to="/reports"><ArrowLeft size={17}/> Reports</Link>
    <div className="report-hero"><div><StatusPill tone="green"><Check size={14}/> Interview complete</StatusPill><h1>A strong interview<br/>with room to go deeper.</h1><p>Senior ML Engineer · Technical · September 3, 2026</p></div><div className="big-score"><span><b>86</b><small>/100</small></span><p>Great work</p></div></div>
    <div className="report-grid"><section className="report-card score-breakdown"><div className="card-title"><div><p className="eyebrow">Score breakdown</p><h2>How you showed up</h2></div><BarChart3/></div>{scoreData.map(([label,value,note])=><div className="score-line" key={label}><div><b>{label}</b><span>{note}</span></div><div className="score-track"><i style={{width:`${value}%`}}/></div><strong>{value}</strong></div>)}</section><section className="report-card verdict-card"><p className="eyebrow">Hiring signal</p><h2>Strong yes</h2><p>You communicated clearly, grounded answers in real experience, and showed strong technical judgment.</p><div className="signal-dots"><i/><i/><i/><i/><i className="off"/></div></section></div>
    <div className="insight-grid"><section className="insight-card strengths"><span className="insight-icon"><Sparkles/></span><p className="eyebrow">What worked</p><h2>Your strongest signals</h2><ul><li><b>Clear mental models</b><span>You explained complex systems in a way that was easy to follow.</span></li><li><b>Practical tradeoffs</b><span>You connected architecture choices to latency, cost, and reliability.</span></li><li><b>Calm communication</b><span>Your pace and structure made answers feel confident.</span></li></ul></section><section className="insight-card improve"><span className="insight-icon"><Target/></span><p className="eyebrow">Where to grow</p><h2>Your next edge</h2><ul><li><b>Quantify the outcome</b><span>Attach metrics to the impact of your decisions.</span></li><li><b>Go one level deeper</b><span>Be ready to explain implementation details after the overview.</span></li><li><b>Close with reflection</b><span>Share what you would change with what you know now.</span></li></ul></section></div>
    <section className="next-step"><div><p className="eyebrow">Recommended next</p><h2>Turn feedback into progress.</h2><p>Practice a focused 15-minute system design round.</p></div><Link to="/interviews/new" className="button dark">Practice again <ArrowRight/></Link></section>
  </section></Shell>
}

function HistoryPage() { return <Shell><section className="page"><div className="page-heading"><p className="eyebrow">Your journey</p><h1>Interview history</h1><p>Every session, question, and improvement in one place.</p></div><div className="filter-row"><button className="filter active">All interviews</button><button className="filter">Technical</button><button className="filter">Behavioral</button><button className="filter">System design</button></div><div className="recent-table large"><div className="table-head"><span>Role</span><span>Focus</span><span>Date</span><span>Score</span><span/></div><RecentRow role="Senior ML Engineer" focus="Technical" date="Sep 3" score="86" tone="green"/><RecentRow role="Backend Engineer" focus="System design" date="Aug 29" score="78" tone="purple"/><RecentRow role="AI Engineer" focus="Balanced" date="Aug 24" score="72" tone="neutral"/><RecentRow role="Software Engineer" focus="Behavioral" date="Aug 16" score="81" tone="green"/></div></section></Shell> }

function SettingsPage() { const [saved,setSaved]=useState(false); return <Shell><section className="page settings-page"><div className="page-heading"><p className="eyebrow">Preferences</p><h1>Make it yours.</h1><p>Set the defaults your future interviews will start with.</p></div><div className="settings-layout"><aside><a className="active"><UserRound/>Profile</a><a><Mic/>Voice & audio</a><a><Bell/>Notifications</a><a><ShieldCheck/>Privacy</a></aside><section className="settings-card"><h2>Profile</h2><p>This information personalises your practice experience.</p><div className="profile-editor"><span>YJ</span><div><b>Profile photo</b><small>JPG or PNG, up to 5 MB</small></div><button className="button secondary">Change</button></div><div className="two-fields"><label className="field-label">Full name<input defaultValue="Yash Jain"/></label><label className="field-label">Target role<input defaultValue="AI / ML Engineer"/></label></div><label className="field-label">Experience level<select defaultValue="mid"><option value="junior">Early career</option><option value="mid">Mid level</option><option value="senior">Senior</option><option value="lead">Staff / Lead</option></select></label><div className="settings-actions"><button className="button primary" onClick={()=>{setSaved(true);setTimeout(()=>setSaved(false),1800)}}>{saved?<><Check/>Saved</>:<>Save changes</>}</button></div></section></div></section></Shell> }

function NotFound() { return <Shell><section className="page"><div className="empty-feature"><h1>That page wandered off.</h1><p>Let’s get you back to your interview practice.</p><Link to="/" className="button primary">Back home</Link></div></section></Shell> }

export default function App() {
  const location = useLocation()
  const navigate = useNavigate()
  useEffect(() => { window.scrollTo({ top: 0, left: 0 }) }, [location.pathname])
  useEffect(() => {
    if (!document.modelContext?.registerTool) return
    const lifecycle = new AbortController()
    const typeValues = ['Balanced', 'Technical', 'Behavioral']
    const difficultyValues = ['Adaptive', 'Beginner', 'Advanced']
    void Promise.resolve(document.modelContext.registerTool({
      name: 'configure_interview',
      title: 'Configure interview',
      description: 'Prepare the visible interview setup form with a candidate name, target role, focus, difficulty, and duration.',
      inputSchema: {
        type: 'object',
        properties: {
          name: { type: 'string' }, role: { type: 'string' },
          focus: { type: 'string', enum: typeValues },
          difficulty: { type: 'string', enum: difficultyValues },
          duration: { type: 'number', enum: [15, 30, 45, 60] },
        },
        required: ['name', 'role'], additionalProperties: false,
      },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      execute(input) {
        const value = input as Record<string, unknown>
        if (typeof value.name !== 'string' || !value.name.trim() || typeof value.role !== 'string' || !value.role.trim()) throw new Error('Name and role are required.')
        if (value.focus && !typeValues.includes(String(value.focus))) throw new Error('Unsupported interview focus.')
        if (value.difficulty && !difficultyValues.includes(String(value.difficulty))) throw new Error('Unsupported difficulty.')
        if (value.duration && ![15,30,45,60].includes(Number(value.duration))) throw new Error('Duration must be 15, 30, 45, or 60 minutes.')
        const configured = {...defaultSetup, name:value.name.trim(), role:value.role.trim(), type:(value.focus || 'Balanced') as SetupState['type'], difficulty:(value.difficulty || 'Adaptive') as SetupState['difficulty'], duration:Number(value.duration || 30)}
        sessionStorage.setItem('interview.setup', JSON.stringify(configured))
        navigate('/interviews/new')
        return { status: 'ready', role: configured.role, focus: configured.type, duration: configured.duration }
      },
    }, { signal: lifecycle.signal })).catch(() => undefined)
    return () => lifecycle.abort()
  }, [navigate])
  return <Routes>
    <Route path="/" element={<Dashboard/>}/>
    <Route path="/interviews" element={<Interviews/>}/>
    <Route path="/interviews/new" element={<NewInterview/>}/>
    <Route path="/interview/live" element={<LiveInterview/>}/>
    <Route path="/reports" element={<Reports/>}/>
    <Route path="/reports/latest" element={<Reports detail/>}/>
    <Route path="/history" element={<HistoryPage/>}/>
    <Route path="/settings" element={<SettingsPage/>}/>
    <Route path="*" element={<NotFound/>}/>
  </Routes>
}
