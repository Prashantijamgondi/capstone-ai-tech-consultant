import os
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from agents.agent_team import (
    TranscriptAnalystAgent, ProductFeasibilityAgent,
    ScopeAndEstimationAgent, ScopeOfWork, Requirement
)
from scope_diff.differ import scope_differ, ScopeDiffReport

app = FastAPI(title='Meeting to Scope of Work API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

analyst = TranscriptAnalystAgent()
feasibility = ProductFeasibilityAgent()
estimator = ScopeAndEstimationAgent()

current_baseline: Optional[ScopeOfWork] = None

class MeetingProcessRequest(BaseModel):
    client_name: str
    transcript_text: str
    meeting_type: str = 'discovery' # 'discovery' or 'follow_up'

class ApprovalRequest(BaseModel):
    approved_by: str = 'Senior Consultant'

@app.get('/health')
def health():
    return {'status': 'healthy', 'service': 'Task 3: Meeting to Scope of Work (Python)'}

@app.post('/process-transcript', response_model=ScopeOfWork)
async def process_transcript(req: MeetingProcessRequest):
    global current_baseline
    extracted = analyst.analyze(req.transcript_text)
    enriched = []
    for r in extracted:
        fe = await feasibility.check_feasibility(r)
        enriched.append({**r, **fe})
    
    sow = estimator.build_sow(req.client_name, enriched)
    if not current_baseline or req.meeting_type == 'discovery':
        current_baseline = sow
    return sow

@app.post('/scope-diff', response_model=ScopeDiffReport)
async def get_scope_diff(req: MeetingProcessRequest):
    global current_baseline
    if not current_baseline:
        raise HTTPException(status_code=400, detail='No baseline SOW found to compare against.')
    
    extracted = analyst.analyze(req.transcript_text)
    revised_reqs = []
    idx = 1
    for r in extracted:
        fe = await feasibility.check_feasibility(r)
        revised_reqs.append(Requirement(
            id=f'REQ-REV-{idx:03d}',
            title=r['title'],
            description=r['description'],
            type=fe['type'],
            category='Revised Item',
            estimated_hours=fe['hours'],
            reasoning=fe['reasoning'],
            source_quote=r['quote'],
            status='active'
        ))
        idx += 1
    
    diff = scope_differ.compare(current_baseline, revised_reqs)
    return diff

@app.post('/approve')
def approve_sow(req: ApprovalRequest):
    global current_baseline
    if not current_baseline:
        raise HTTPException(status_code=400, detail='No SOW available to approve.')
    current_baseline.is_approved = True
    current_baseline.approved_by = req.approved_by
    current_baseline.approval_timestamp = datetime.datetime.utcnow().isoformat()
    return {'status': 'approved', 'sow': current_baseline}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8003, reload=True)
