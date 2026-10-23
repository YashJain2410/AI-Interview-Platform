export type Message = {role: 'ai' | 'candidate'; content: string}
export type InterviewReport = {
  id: string; role: string; focus: string; date: string; duration: number; question_count: number;
  total_score: number; summary: string; scores: Record<string, number>;
  strengths: string[]; weaknesses: string[]; improvement_suggestions: string[]; messages: Message[];
}
export function readReports(): InterviewReport[] {
  try { const value = JSON.parse(localStorage.getItem('interview.reports') || '[]'); return Array.isArray(value) ? value : [] }
  catch { return [] }
}
export function saveReport(report: InterviewReport) {
  localStorage.setItem('interview.reports', JSON.stringify([report, ...readReports().filter(r => r.id !== report.id)].slice(0, 30)))
}
