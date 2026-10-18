import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title='AITechConsultantUnifiedServer')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', response_class=HTMLResponse)
def index():
    with open('ui/index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.get('health')
def health():
    return {'status': 'healthy', 'deployed': True}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)
