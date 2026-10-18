export type EmailCategory = 
  | 'how_to'
  | 'troubleshooting'
  | 'project_request'
  | 'refund_cancellation'
  | 'complaint'
  | 'quote_request'
  | 'follow_up';

export interface EmailClassification {
  category: EmailCategory;
  confidence: number;
  risk: 'low' | 'medium' | 'high';
  urgency: 'low' | 'normal' | 'urgent';
  requiresHumanReview: boolean;
}

export class EmailClassifier {
  classify(subject: string, body: string): EmailClassification {
    const s = subject.toLowerCase();
    const b = body.toLowerCase();
    const text = s + ' ' + b;

    // 1. Follow-up intent
    if (s.startsWith('following up') || s.startsWith('status of') || s.startsWith('any updates') || s.startsWith('second follow-up')) {
      return {
        category: 'follow_up',
        confidence: 0.94,
        risk: text.includes('refund') ? 'high' : 'low',
        urgency: 'normal',
        requiresHumanReview: text.includes('refund')
      };
    }

    // 2. Cancellation and Refund requests
    if (text.includes('refund') || s.includes('cancel subscription') || s.includes('cancel trial') || text.includes('double charge') || text.includes('disputed charge') || text.includes('overcharged')) {
      return {
        category: 'refund_cancellation',
        confidence: 0.95,
        risk: 'high',
        urgency: text.includes('immediate') || text.includes('audit') ? 'urgent' : 'normal',
        requiresHumanReview: true
      };
    }

    // 3. Genuine Complaints & Outages
    if (text.includes('unacceptable') || text.includes('site down') || text.includes('lost thousands') || s.includes('broke custom layout') || s.includes('billing error') || s.includes('complaint')) {
      return {
        category: 'complaint',
        confidence: 0.92,
        risk: 'high',
        urgency: 'urgent',
        requiresHumanReview: true
      };
    }

    // 4. Commercial Quotes
    if (s.startsWith('quote for') || s.startsWith('cost to') || s.startsWith('estimate for') || s.startsWith('cost for')) {
      return {
        category: 'quote_request',
        confidence: 0.92,
        risk: 'medium',
        urgency: 'normal',
        requiresHumanReview: true
      };
    }

    // 5. Custom Project Requests
    if (s.startsWith('need custom') || s.startsWith('mobile app') || s.startsWith('enterprise sso') || s.startsWith('custom marketplace') || s.startsWith('ai chat widget') || s.startsWith('custom lead')) {
      return {
        category: 'project_request',
        confidence: 0.93,
        risk: 'high',
        urgency: 'normal',
        requiresHumanReview: true
      };
    }

    // 6. Troubleshooting technical glitches
    if (s.includes('failing') || s.includes('not returning') || s.includes('going to spam') || s.includes('not rendering') || s.includes('webhook failure') || s.includes('greyed out') || s.includes('not linking') || s.includes('missing recent') || s.includes('warning') || s.includes('error')) {
      return {
        category: 'troubleshooting',
        confidence: 0.90,
        risk: 'medium',
        urgency: 'normal',
        requiresHumanReview: false
      };
    }

    // 7. Standard How-To
    return {
      category: 'how_to',
      confidence: 0.92,
      risk: 'low',
      urgency: 'normal',
      requiresHumanReview: false
    };
  }
}

export const emailClassifier = new EmailClassifier();
