import {useEffect, useRef, useState} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {ArrowRight, Clock3, Headphones, Mic, MicOff, Pause, Play, Volume2} from 'lucide-react'
import {saveReport, type Message} from './session'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
const WS_URL = (import.meta.env.VITE_WS_URL || API_URL.replace(/^http/, 'ws')).replace(/\/$/, '')

type Recognition = {lang: string; continuous: boolean; interimResults: boolean; start(): void; stop(): void; onresult: ((event: any) => void) | null; onerror: ((event: any) => void) | null; onend: (() => void) | null}
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

export default function LiveInterview() {
  const navigate = useNavigate()
  const [setup] = useState(() => {try {return JSON.parse(sessionStorage.getItem('interview.setup') || '{}')} catch {return {}}})
  const [phase, setPhase] = useState<'ready'|'connecting'|'live'|'paused'>('ready')
  const [messages, setMessages] = useState<Message[]>([])
  const [answer, setAnswer] = useState('')
  const [seconds, setSeconds] = useState(0)
  const [note, setNote] = useState('Ready to connect')
  const [busy, setBusy] = useState(false)
  const [finishing, setFinishing] = useState(false)
  const [listening, setListening] = useState(false)
  const [voice, setVoice] = useState(true)
  const socket = useRef<WebSocket | null>(null)
  const recognition = useRef<Recognition | null>(null)
  const done = useRef(false)
  const answerRef = useRef('')
  const voiceRef = useRef(true)
  const transcript = useRef<HTMLDivElement>(null)
  useEffect(() => {answerRef.current = answer}, [answer])
  useEffect(() => {voiceRef.current = voice; if(!voice) window.speechSynthesis?.cancel()}, [voice])
  useEffect(() => {if(phase !== 'live') return; const id = setInterval(() => setSeconds(s => s+1),1000); return () => clearInterval(id)}, [phase])
  useEffect(() => {transcript.current?.scrollTo({top: transcript.current.scrollHeight, behavior:'smooth'})}, [messages])
  useEffect(() => {
    const id = setInterval(() => {if(socket.current?.readyState === WebSocket.OPEN) socket.current.send(JSON.stringify({event:'ping'}))}, 60000)
    return () => {clearInterval(id); done.current=true; socket.current?.close(); recognition.current?.stop(); window.speechSynthesis?.cancel()}
  }, [])
  const stopListening = () => {recognition.current?.stop(); setListening(false)}
  const speak = (text: string) => {
    stopListening()
    if(voiceRef.current && window.speechSynthesis) {
      window.speechSynthesis.cancel()
      const speech = new SpeechSynthesisUtterance(text); speech.lang='en-US'; speech.rate=1
      window.speechSynthesis.speak(speech)
    }
  }
  const start = async () => {
    done.current=false; setPhase('connecting'); setBusy(true); setNote('Waking the interview server… This may take a minute.'); setMessages([])
    try {
      const response = await fetch(`${API_URL}/health`, {signal: AbortSignal.timeout(120000)})
      if(!response.ok) throw new Error('The interview server is unavailable. Please retry.')
      if(!(await response.json()).ai_configured) throw new Error('AI credentials are missing on the server.')
      const ws = new WebSocket(`${WS_URL}/ws/interview`); socket.current=ws
      ws.onopen = () => {setNote('Preparing your first question…'); ws.send(JSON.stringify({candidate_name: setup.name || 'Candidate', role: setup.role || 'Software Engineer', focus:setup.type || 'Balanced', difficulty:setup.difficulty || 'Adaptive', duration:setup.duration || 30, resume:setup.resumeText || '', job_description:setup.jdText || ''}))}
      ws.onmessage = event => {
        const data=JSON.parse(event.data)
        if(data.event==='session_started') setNote('Connected · preparing your question…')
        if(data.event==='ai_question') {setPhase('live'); setBusy(false); setNote('Connected'); setMessages(v=>[...v,{role:'ai',content:data.content}]); speak(data.content)}
        if(data.event==='error') {setNote(data.content); setBusy(false); setFinishing(false)}
        if(data.event==='report') {
          done.current=true
          try {saveReport({...data.report,date:new Date().toISOString()}); navigate(`/reports/${data.report.id}`)}
          catch {setNote('Browser storage is full. Download your feedback below.'); const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([JSON.stringify(data.report,null,2)],{type:'application/json'})); a.download='interview-report.json'; a.click(); URL.revokeObjectURL(a.href); setFinishing(false)}
        }
      }
      ws.onerror = () => {setNote('Connection failed. Check your network and retry.'); setBusy(false); setPhase('ready')}
      ws.onclose = () => {if(!done.current) {setNote('Disconnected. Start a new session to reconnect.'); setBusy(false); setFinishing(false); setPhase('ready'); stopListening()}}
    } catch(error) {setNote(error instanceof Error ? error.message : 'Could not connect. Please retry.'); setBusy(false); setPhase('ready')}
  }
  const submit = () => {
    const text=answerRef.current.trim()
    if(!text || busy || phase!=='live' || socket.current?.readyState!==WebSocket.OPEN) return
    stopListening(); window.speechSynthesis?.cancel(); setMessages(v=>[...v,{role:'candidate',content:text}]); setAnswer(''); answerRef.current=''; setBusy(true); setNote('Thinking…')
    socket.current.send(JSON.stringify({content:text}))
  }
  const toggleMic = () => {
    if(listening) {stopListening(); return}
    if(!SpeechRecognition) {setNote('Speech recognition is unavailable in this browser. Use Chrome or type your answer.'); return}
    window.speechSynthesis?.cancel()
    const r: Recognition = new SpeechRecognition(); recognition.current=r; r.lang='en-US'; r.continuous=true; r.interimResults=false
    r.onresult = event => {let text=''; for(let i=event.resultIndex; i<event.results.length; i++) if(event.results[i].isFinal) text+=event.results[i][0].transcript+' '; setAnswer(v => (v+' '+text).trim()); setNote('Dictating · review your answer, then send')}
    r.onerror = event => {setNote(`Microphone: ${event.error}. You can still type your answer.`); setListening(false)}
    r.onend = () => setListening(false)
    try {r.start(); setListening(true); setNote('Listening · click the microphone again to stop')} catch {setNote('Could not start microphone. Please retry.')}
  }
  const finish = () => {
    if(busy || !messages.some(m=>m.role==='candidate') || socket.current?.readyState!==WebSocket.OPEN) return
    stopListening(); window.speechSynthesis?.cancel(); setBusy(true); setFinishing(true); setNote('Preparing feedback from your answers…'); socket.current.send(JSON.stringify({event:'finish'}))
  }
  const pause = () => {stopListening(); window.speechSynthesis?.cancel(); setPhase(p=>p==='paused'?'live':'paused')}
  const latest=[...messages].reverse().find(m=>m.role==='ai')
  const time=`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`
  return <div className="interview-room">
    <header className="room-header"><Link className="brand" to="/">interview</Link><div className="room-meta"><span className="status-pill green">{phase==='live'?'Live':phase==='paused'?'Paused':'Practice room'}</span><span>{setup.role}</span><span className="time"><Clock3 size={16}/>{time}</span></div><button className="button danger-soft" onClick={finish} disabled={busy || phase==='ready' || !messages.some(m=>m.role==='candidate')}>{finishing?'Preparing report…':'End interview'}</button></header>
    <main className="room-main">
      {phase==='ready' && <section className="lobby-card"><div className="lobby-visual"><div className="voice-orb large"><span/><span/><span/><span/><span/></div></div><span className="status-pill purple"><Headphones size={14}/> Private practice room</span><h1>Your interviewer is ready.</h1><p>Type your answers or use the microphone to dictate. AI questions can be read aloud. Microphone access is requested only when you click the mic.</p><p role="status">{note}</p><button className="button primary hero-button" onClick={start}>Start interview <ArrowRight size={19}/></button></section>}
      {phase==='connecting' && <section className="lobby-card"><div className="pulse-loader"><span/><span/><span/></div><h1>Opening the room…</h1><p role="status">{note}</p></section>}
      {(phase==='live'||phase==='paused') && <div className="conversation-layout"><section className="interviewer-stage"><div className="stage-top"><div><p className="eyebrow">AI interviewer</p><h2>Maya</h2></div><span className="connection" role="status">{note}</span></div><div className="avatar-orb"><div className="voice-bars"><i/><i/><i/><i/><i/><i/><i/></div></div><div className="question-card"><span>{seconds >= (setup.duration||30)*60 ? 'Time reached · finish when ready' : 'Current question'}</span><p>{latest?.content}</p></div></section><aside className="transcript-panel"><div className="panel-heading"><div><h3>Live transcript</h3><p>{listening?'Microphone is listening':'Review your answer before sending.'}</p></div><button className="icon-btn" aria-label={voice?'Disable spoken questions':'Enable spoken questions'} onClick={()=>setVoice(v=>!v)}><Volume2 size={20}/>{voice?'On':'Off'}</button></div><div className="transcript-list" ref={transcript}>{messages.map((m,i)=><div className={`message ${m.role}`} key={i}><div className="message-meta"><b>{m.role==='ai'?'Maya':'You'}</b></div><p>{m.content}</p></div>)}</div><div className="answer-box"><textarea value={answer} maxLength={12000} disabled={busy || phase==='paused'} onChange={e=>setAnswer(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();submit()}}} placeholder={busy?'Waiting for your interviewer…':'Type or dictate, then send your answer…'}/><button onClick={submit} disabled={busy || phase!=='live' || !answer.trim()} aria-label="Send answer"><ArrowRight/></button></div></aside></div>}
    </main>
    {(phase==='live'||phase==='paused') && <div className="room-controls"><button className={listening?'active':''} onClick={toggleMic} disabled={busy || phase==='paused'} aria-label={listening?'Stop dictation':'Dictate answer'}>{listening?<Mic/>:<MicOff/>}</button><button onClick={pause} disabled={busy} aria-label={phase==='paused'?'Resume':'Pause'}>{phase==='paused'?<Play/>:<Pause/>}</button><span>{phase==='paused'?'Interview paused':listening?'Dictating your answer':'Click mic to dictate · Enter to send'}</span></div>}
  </div>
}
