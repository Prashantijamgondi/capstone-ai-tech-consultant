import express, { Request, Response } from 'express';
import fs from 'fs';
import path from 'path';
import { emailClassifier } from './email/classifier';
import { emailDrafter } from './drafting/drafter';
import { feedbackManager } from './feedback/streak_manager';

const app = express();
const PORT = process.env.INBOX_AGENT_PORT || 8002;

app.use(express.json());

// Enable CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

const emailsPath = path.join(__dirname, 'data/emails.json');
let emails: any[] = [];
try {
  emails = JSON.parse(fs.readFileSync(emailsPath, 'utf-8'));
} catch {
  emails = [];
}

app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'Task 2: Inbox Agent (TypeScript)',
    emailsLoaded: emails.length,
    activeCategories: Object.keys(feedbackManager.getAllStates()).length
  });
});

app.get('/emails', (req: Request, res: Response) => {
  res.json(emails);
});

app.post('/draft', async (req: Request, res: Response) => {
  try {
    const { emailId, sender, subject, body } = req.body;
    const cat = emailClassifier.classify(subject, body).category;
    const state = feedbackManager.getState(cat);
    
    const draft = await emailDrafter.draftReply(
      emailId || 'custom_email',
      sender || 'customer@example.com',
      subject,
      body,
      state.consecutiveApprovals,
      state.isEligibleForAutonomy
    );
    res.json(draft);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/feedback', (req: Request, res: Response) => {
  try {
    const { emailId, category, originalDraft, finalSent, action, reason } = req.body;
    const updatedState = feedbackManager.recordFeedback({
      emailId,
      category,
      originalDraft,
      finalSent,
      action,
      reason,
      timestamp: new Date().toISOString()
    });
    res.json({ success: true, updatedState });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/autonomy-status', (req: Request, res: Response) => {
  res.json({
    states: feedbackManager.getAllStates(),
    totalHistory: feedbackManager.getHistory().length
  });
});

app.listen(PORT, () => {
  console.log([Task 2] Inbox Agent Express Server running on port );
});