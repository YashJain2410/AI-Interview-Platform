"""Hosted contracts: run python -m unittest discover -s tests/deployment."""
import io
import json
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from backend.api.main import app
from backend.api import interviews

class HostedAPITest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        interviews.starts.clear()

    def test_health_and_cors(self):
        self.assertEqual(self.client.get('/health').json()['status'], 'ok')
        response=self.client.options('/documents/extract',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'POST'})
        self.assertEqual(response.headers['access-control-allow-origin'],'http://localhost:5173')
        self.assertNotIn('access-control-allow-origin',self.client.get('/health',headers={'Origin':'https://untrusted.example'}).headers)

    def test_extract_and_reject_files(self):
        response=self.client.post('/documents/extract',files={'file':('resume.txt',b'Python engineer with FastAPI experience.','text/plain')})
        self.assertIn('FastAPI',response.json()['text'])
        self.assertEqual(self.client.post('/documents/extract',files={'file':('bad.exe',b'bad')}).status_code,400)
        self.assertEqual(self.client.post('/documents/extract',files={'file':('bad.pdf',b'bad')}).status_code,400)
        self.assertEqual(self.client.post('/documents/extract',files={'file':('empty.txt',b'')}).status_code,400)
        self.assertEqual(self.client.post('/documents/extract',files={'file':('big.txt',b'x'*(10*1024*1024+1))}).status_code,413)
        from docx import Document
        doc=Document(); doc.add_paragraph('Backend project'); buffer=io.BytesIO(); doc.save(buffer)
        response=self.client.post('/documents/extract',files={'file':('resume.docx',buffer.getvalue())})
        self.assertIn('Backend project',response.json()['text'])

    def test_lifecycle_and_context(self):
        prompts=[]
        async def fake(prompt,structured=False):
            prompts.append(prompt)
            if structured:
                return json.dumps({'scores':dict.fromkeys(['technical_correctness','depth_of_understanding','communication','confidence'],75),'summary':'Useful practice.','strengths':['Clear answer'],'weaknesses':['Needs detail'],'improvement_suggestions':['Give a metric']})
            return 'What tradeoff did you make?' if len(prompts)==1 else 'Unanswered final follow-up?'
        with patch.object(interviews,'generate',fake), self.client.websocket_connect('/ws/interview',headers={'origin':'http://localhost:5173'}) as ws:
            ws.send_json({'candidate_name':'Test','role':'Backend Engineer','resume':'Built a queue processor'})
            self.assertEqual(ws.receive_json()['event'],'session_started')
            self.assertEqual(ws.receive_json()['event'],'ai_question')
            ws.send_json({'event':'finish'})
            self.assertEqual(ws.receive_json()['event'],'error')
            ws.send_json({'content':'I used idempotency keys to prevent duplicate processing.'})
            self.assertEqual(ws.receive_json()['event'],'ai_question')
            ws.send_json({'event':'ping'})
            self.assertEqual(ws.receive_json()['event'],'pong')
            ws.send_json({'event':'finish'})
            report=ws.receive_json()['report']
            self.assertEqual(report['total_score'],75)
            self.assertEqual(report['role'],'Backend Engineer')
            self.assertEqual(report['question_count'],1)
            self.assertEqual(len(report['messages']),3)
        self.assertIn('queue processor',prompts[0])
        self.assertIn('idempotency',prompts[1])
        self.assertNotIn('Unanswered final follow-up?',prompts[-1])
        self.assertFalse(interviews.active_sessions)

    def test_disconnect_before_init_and_invalid_origin(self):
        with self.client.websocket_connect('/ws/interview'):
            pass
        self.assertFalse(interviews.active_sessions)
        with self.assertRaises(WebSocketDisconnect):
            with self.client.websocket_connect('/ws/interview',headers={'origin':'https://untrusted.example'}):
                pass

    def test_provider_failure_is_visible(self):
        async def fail(*args): raise RuntimeError('unavailable')
        with patch.object(interviews,'generate',fail), self.client.websocket_connect('/ws/interview') as ws:
            ws.send_json({'candidate_name':'Test'})
            self.assertEqual(ws.receive_json()['event'],'session_started')
            self.assertEqual(ws.receive_json()['event'],'error')
        self.assertFalse(interviews.active_sessions)

if __name__ == '__main__': unittest.main()
