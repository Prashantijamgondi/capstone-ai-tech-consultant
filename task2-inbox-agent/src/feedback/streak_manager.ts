import fs from 'fs';
import path from 'path';

export interface FeedbackEvent {
  emailId: string;
  category: string;
  originalDraft: string;
  finalSent: string;
  action: 'approved' | 'edited' | 'rejected';
  reason?: string;
  timestamp: string;
}

export interface CategoryAutonomyState {
  category: string;
  consecutiveApprovals: number;
  isEligibleForAutonomy: boolean;
  totalProcessed: number;
  totalEdits: number;
}

export class FeedbackManager {
  private storePath: string;
  private state: Record<string, CategoryAutonomyState> = {};
  private history: FeedbackEvent[] = [];

  constructor(storePath: string = path.join(__dirname, '../../feedback_store.json')) {
    this.storePath = storePath;
    this.load();
  }

  private load() {
    try {
      if (fs.existsSync(this.storePath)) {
        const raw = JSON.parse(fs.readFileSync(this.storePath, 'utf-8'));
        this.state = raw.state || {};
        this.history = raw.history || [];
      }
    } catch {
      this.state = {};
      this.history = [];
    }
  }

  private save() {
    try {
      fs.writeFileSync(this.storePath, JSON.stringify({ state: this.state, history: this.history }, null, 2));
    } catch (err) {
      console.error('Failed to save feedback store', err);
    }
  }

  getState(category: string): CategoryAutonomyState {
    if (!this.state[category]) {
      this.state[category] = {
        category,
        consecutiveApprovals: 0,
        isEligibleForAutonomy: false,
        totalProcessed: 0,
        totalEdits: 0
      };
    }
    return this.state[category];
  }

  recordFeedback(event: FeedbackEvent): CategoryAutonomyState {
    const s = this.getState(event.category);
    s.totalProcessed += 1;
    this.history.push(event);

    // Exact match or whitespace-only difference counts as unedited
    const isUnchanged = event.originalDraft.trim() === event.finalSent.trim();

    // High risk categories (refunds, complaints, custom enterprise quotes) NEVER auto-send
    const highRiskCategories = ['refund_cancellation', 'complaint', 'project_request'];
    const isSafeCategory = !highRiskCategories.includes(event.category);

    if (event.action === 'approved' && isUnchanged) {
      s.consecutiveApprovals += 1;
      if (s.consecutiveApprovals >= 20 && isSafeCategory) {
        s.isEligibleForAutonomy = true;
      }
    } else {
      // Human edited or rejected -> RESET streak immediately!
      s.consecutiveApprovals = 0;
      s.isEligibleForAutonomy = false;
      s.totalEdits += 1;
    }

    this.save();
    return s;
  }

  getHistory(): FeedbackEvent[] {
    return this.history;
  }

  getAllStates(): Record<string, CategoryAutonomyState> {
    return this.state;
  }
}

export const feedbackManager = new FeedbackManager();