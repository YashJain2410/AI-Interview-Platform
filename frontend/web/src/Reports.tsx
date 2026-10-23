import {Link, useParams} from 'react-router-dom'
import {ArrowRight, BarChart3, Download, FileText} from 'lucide-react'
import {readReports, type InterviewReport} from './session'

export function ReportRows({reports}: {reports: InterviewReport[]}) {
  return <div className="report-list">{reports.map(r=><Link key={r.id} to={`/reports/${r.id}`} className="report-list-card"><div className="report-date"><b>{new Date(r.date).getDate()}</b><span>{new Date(r.date).toLocaleString(undefined,{month:'short'})}</span></div><div><h3>{r.role}</h3><p>{r.focus} · {r.duration} min · {r.question_count} answers</p></div><div className="report-score">{r.total_score}<small>/100</small></div><ArrowRight/></Link>)}</div>
}
export default function Reports({detail=false}: {detail?:boolean}) {
  const {id} = useParams()
  const reports = readReports()
  const report = id==='latest' ? reports[0] : reports.find(r=>r.id===id)
  const download = () => {
    const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}))
    const a=document.createElement('a'); a.href=url; a.download='interview-report.json'; a.click(); URL.revokeObjectURL(url)
  }
  if(!detail) return <section className="page"><div className="page-heading"><p className="eyebrow">Performance</p><h1>Reports</h1><p>Feedback from your completed interviews. Saved in this browser.</p></div>{reports.length ? <ReportRows reports={reports}/> : <Empty/>}</section>
  if(!report) return <section className="page"><Empty/></section>
  return <section className="page report-detail"><Link className="back-link" to="/reports">← Reports</Link><div className="report-hero"><div><span className="status-pill green">Interview complete</span><h1>Your interview feedback.</h1><p>{report.role} · {report.focus} · {new Date(report.date).toLocaleDateString()}</p></div><div className="big-score"><span><b>{report.total_score}</b><small>/100</small></span><p>Practice score</p></div></div><p>{report.summary}</p><div className="report-grid"><section className="report-card score-breakdown"><div className="card-title"><h2>Score breakdown</h2><BarChart3/></div>{Object.entries(report.scores).map(([label,value])=><div className="score-line" key={label}><div><b>{label.replace(/_/g,' ')}</b></div><div className="score-track"><i style={{width:`${value}%`}}/></div><strong>{value}</strong></div>)}</section><section className="report-card"><p className="eyebrow">Your session</p><h2>{report.question_count} answers</h2><p>{report.duration} minutes of practice</p><button className="button secondary" onClick={download}><Download size={18}/>Download report</button><p>AI feedback is for practice and can make mistakes.</p></section></div><div className="insight-grid"><section className="insight-card strengths"><h2>Your strongest signals</h2><ul>{report.strengths.map((s,i)=><li key={i}>{s}</li>)}</ul></section><section className="insight-card improve"><h2>Your next edge</h2><ul>{[...report.weaknesses,...report.improvement_suggestions].map((s,i)=><li key={i}>{s}</li>)}</ul></section></div><section className="report-card"><h2>Conversation</h2>{report.messages.map((m,i)=><div key={i}><b>{m.role==='ai'?'Maya':'You'}</b><p>{m.content}</p></div>)}</section><section className="next-step"><div><h2>Turn feedback into progress.</h2><p>Practice again to build on this session.</p></div><Link to="/interviews/new" className="button dark">Practice again <ArrowRight/></Link></section></section>
}
function Empty() {return <div className="empty-feature"><FileText size={36}/><h2>Your first report starts with a conversation.</h2><p>Complete an interview to see feedback based on your answers.</p><Link to="/interviews/new" className="button primary">Start an interview <ArrowRight size={18}/></Link></div>}
