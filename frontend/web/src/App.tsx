import { useEffect, useState } from 'react'
import LiveInterview from './LiveInterview'
import Reports, {ReportRows} from './Reports'
import {readReports} from './session'
import { Link, NavLink, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, ArrowRight, BarChart3, BrainCircuit,
  Check, ChevronDown, Clock3, FileText, History,
  LayoutDashboard, Mic, MoreHorizontal, Plus,
  Settings, ShieldCheck, Sparkles, Target, UploadCloud, UserRound, X,
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type SetupState = {
  name: string
  role: string
  type: 'Balanced' | 'Technical' | 'Behavioral'
  difficulty: 'Adaptive' | 'Beginner' | 'Advanced'
  duration: number
  resume?: File
  jobDescription?: File
}

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
  const reports=readReports()
  const average=reports.length?Math.round(reports.reduce((n,r)=>n+r.total_score,0)/reports.length):null
  return <Shell><section className="page dashboard-page"><div className="page-heading split-heading"><div><p className="eyebrow">{new Date().toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric'})}</p><h1>Ready for your next move?</h1><p>Practice with an interviewer that listens, adapts, and helps you grow.</p></div><Link to="/interviews/new" className="button primary"><Plus size={19}/>New interview</Link></div><div className="hero-grid"><article className="start-card"><div className="orb-wrap"><div className="voice-orb"><span/><span/><span/><span/><span/></div><div className="orb-ring r1"/><div className="orb-ring r2"/></div><div className="start-copy"><StatusPill><Sparkles size={14}/>AI voice interview</StatusPill><h2>Practice the interview,<br/>not the script.</h2><p>Get a role-specific interview shaped by your resume, experience, and goals.</p><Link to="/interviews/new" className="button light">Start practicing <ArrowRight size={18}/></Link></div></article><article className="readiness-card"><p className="eyebrow">Your practice</p><h3>Interview readiness</h3><div className="score-row"><div className="score-ring"><span><b>{average ?? '—'}</b><small>/100</small></span></div><div><strong>{reports.length} completed interviews</strong><p>{average===null?'Complete your first session to get feedback.':'Average score across your completed sessions.'}</p></div></div><p>Reports are stored locally in this browser.</p></article></div><section className="section-block"><div className="section-heading"><div><h2>Recent interviews</h2><p>Build on your previous practice.</p></div><Link to="/history">See all <ArrowRight size={16}/></Link></div>{reports.length?<ReportRows reports={reports.slice(0,3)}/>:<div className="empty-feature"><h2>Your next interview starts here.</h2><Link to="/interviews/new" className="button primary">Set up an interview</Link></div>}</section></section></Shell>
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
    try { const saved=JSON.parse(sessionStorage.getItem('interview.setup') || '{}'); return {...defaultSetup, ...saved, ...JSON.parse(localStorage.getItem('interview.profile')||'{}'), resume:undefined, jobDescription:undefined} }
    catch { return defaultSetup }
  })
  const set = <K extends keyof SetupState>(key: K, value: SetupState[K]) => setSetup(v => ({...v, [key]: value}))
  const [uploading,setUploading]=useState(false)
  const [error,setError]=useState('')
  const begin = async () => {
    setUploading(true); setError('')
    try {
      const extract = async (file?:File) => {
        if(!file)return ''
        if(file.size>10*1024*1024)throw new Error('Files must be 10 MB or smaller.')
        const form=new FormData(); form.append('file',file)
        const response=await fetch(`${API_URL}/documents/extract`,{method:'POST',body:form,signal:AbortSignal.timeout(120000)})
        const data=await response.json()
        if(!response.ok)throw new Error(data.detail || 'Could not read the document.')
        return data.text as string
      }
      const [resumeText,jdText]=await Promise.all([extract(setup.resume),extract(setup.jobDescription)])
      sessionStorage.setItem('interview.setup',JSON.stringify({...setup,resume:undefined,jobDescription:undefined,resumeText,jdText}))
      navigate('/interview/live')
    } catch(e) {setError(e instanceof Error?e.message:'Could not prepare interview. Please retry.')} finally {setUploading(false)}
  }
  return <Shell><section className="page setup-page">
    <Link className="back-link" to="/interviews"><ArrowLeft size={17}/> Interviews</Link>
    <div className="setup-heading"><StatusPill><Sparkles size={14}/> Personalised practice</StatusPill><h1>Let’s shape your interview.</h1><p>A little context helps the interviewer ask much better questions.</p></div>
    <div className="setup-layout"><div className="setup-main">
      <section className="form-card"><div className="step-number">1</div><div className="form-content"><h2>What are you preparing for?</h2><p>Tell us the role you want to practice.</p><label className="field-label">Your name<input maxLength={100} value={setup.name} onChange={e => set('name', e.target.value)} placeholder="How should we address you?" /></label><label className="field-label">Target role<input maxLength={200} value={setup.role} onChange={e => set('role', e.target.value)} placeholder="e.g. Senior Backend Engineer" /></label><div className="field-label">Interview focus<div className="choice-grid">{(['Balanced','Technical','Behavioral'] as const).map(x => <button key={x} className={setup.type === x ? 'selected' : ''} onClick={() => set('type', x)}><span>{x === 'Balanced' ? <Sparkles/> : x === 'Technical' ? <BrainCircuit/> : <UserRound/>}</span><b>{x}</b><small>{x === 'Balanced' ? 'A complete interview loop' : x === 'Technical' ? 'Code, systems, and depth' : 'Stories, impact, and fit'}</small></button>)}</div></div></div></section>
      <section className="form-card"><div className="step-number">2</div><div className="form-content"><h2>Add your context</h2><p>Add documents to tailor your questions. Text is sent to the AI provider during this session.</p><div className="file-grid"><FileDrop label="Add your resume" file={setup.resume} onFile={f => set('resume', f)} accept=".pdf,.docx,.txt"/><FileDrop label="Add job description" file={setup.jobDescription} onFile={f => set('jobDescription', f)} accept=".pdf,.docx,.txt"/></div><div className="privacy-note"><ShieldCheck size={18}/><span><b>Session-only processing.</b> Processed in memory and sent to the AI provider for your interview.</span></div></div></section>
      <section className="form-card"><div className="step-number">3</div><div className="form-content"><h2>Choose your pace</h2><div className="two-fields"><div className="field-label">Difficulty<div className="segmented">{(['Adaptive','Beginner','Advanced'] as const).map(x=><button key={x} className={setup.difficulty===x?'active':''} onClick={()=>set('difficulty',x)}>{x}</button>)}</div></div><label className="field-label">Duration<select value={setup.duration} onChange={e=>set('duration',Number(e.target.value))}><option value={15}>15 minutes</option><option value={30}>30 minutes</option><option value={45}>45 minutes</option><option value={60}>60 minutes</option></select></label></div></div></section>
    </div><aside className="setup-summary"><p className="eyebrow">Your session</p><h3>{setup.role || 'Untitled role'}</h3><div className="summary-row"><span><Target/>Focus</span><b>{setup.type}</b></div><div className="summary-row"><span><BrainCircuit/>Difficulty</span><b>{setup.difficulty}</b></div><div className="summary-row"><span><Clock3/>Duration</span><b>{setup.duration} min</b></div><div className="summary-row"><span><FileText/>Context</span><b>{[setup.resume, setup.jobDescription].filter(Boolean).length}/2 added</b></div><button className="button primary full" disabled={uploading || !setup.name.trim() || !setup.role.trim()} onClick={begin}>{uploading?'Preparing documents…':'Enter interview room'} <ArrowRight size={18}/></button>{error && <p role="alert">{error}</p>}<p className="summary-foot"><Mic size={14}/> Type answers or dictate with your microphone.</p></aside></div>
  </section></Shell>
}

function HistoryPage() {
  const [filter,setFilter]=useState('All interviews')
  const reports=readReports().filter(r=>filter==='All interviews'||r.focus===filter)
  return <Shell><section className="page"><div className="page-heading"><p className="eyebrow">Your journey</p><h1>Interview history</h1><p>Your completed sessions, saved in this browser.</p></div><div className="filter-row">{['All interviews','Technical','Behavioral','Balanced'].map(x=><button key={x} className={`filter ${filter===x?'active':''}`} onClick={()=>setFilter(x)}>{x}</button>)}</div>{reports.length?<ReportRows reports={reports}/>:<div className="empty-feature"><h2>No completed interviews yet.</h2><Link to="/interviews/new" className="button primary">Start practicing</Link></div>}</section></Shell>
}

function SettingsPage() {
  const [profile,setProfile]=useState(()=>{try{return JSON.parse(localStorage.getItem('interview.profile')||'{}')}catch{return {}}})
  const [saved,setSaved]=useState(false)
  const save=()=>{try{localStorage.setItem('interview.profile',JSON.stringify(profile));setSaved(true)}catch{setSaved(false)}}
  return <Shell><section className="page settings-page"><div className="page-heading"><p className="eyebrow">Preferences</p><h1>Make it yours.</h1><p>Your defaults are saved in this browser.</p></div><section className="settings-card"><h2>Profile</h2><div className="two-fields"><label className="field-label">Your name<input value={profile.name||''} onChange={e=>{setProfile({...profile,name:e.target.value});setSaved(false)}}/></label><label className="field-label">Target role<input value={profile.role||''} onChange={e=>{setProfile({...profile,role:e.target.value});setSaved(false)}}/></label></div><div className="settings-actions"><button className="button primary" onClick={save}>{saved?'Saved':'Save changes'}</button></div></section></section></Shell>
}

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
    <Route path="/reports" element={<Shell><Reports/></Shell>}/>
    <Route path="/reports/:id" element={<Shell><Reports detail/></Shell>}/>
    <Route path="/history" element={<HistoryPage/>}/>
    <Route path="/settings" element={<SettingsPage/>}/>
    <Route path="*" element={<NotFound/>}/>
  </Routes>
}
