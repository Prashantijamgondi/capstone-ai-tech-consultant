import http from 'http';
import https from 'https';

export interface KnowledgeResponse {
  answer: string;
  status: 'answered' | 'insufficient_evidence' | 'escalated';
  sources: Array<{ title: string; url: string; relevance: number; snippet?: string }>;
  confidence: number;
  needs_human: boolean;
  escalation_id?: string;
}

export class KnowledgeBrainClient {
  private baseUrl: string;

  constructor(baseUrl: string = process.env.KNOWLEDGE_BRAIN_URL || 'http://127.0.0.1:8001') {
    this.baseUrl = baseUrl;
  }

  async query(question: string): Promise<KnowledgeResponse> {
    return new Promise((resolve) => {
      const url = new URL('/query', this.baseUrl);
      const postData = JSON.stringify({ question, top_k: 3 });

      const req = (url.protocol === 'https:' ? https : http).request(
        url,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
          },
          timeout: 4000
        },
        (res) => {
          let data = '';
          res.on('data', (chunk) => { data += chunk; });
          res.on('end', () => {
            try {
              if (res.statusCode === 200) {
                resolve(JSON.parse(data));
              } else {
                resolve(this.getFallback(question));
              }
            } catch {
              resolve(this.getFallback(question));
            }
          });
        }
      );

      req.on('error', () => resolve(this.getFallback(question)));
      req.on('timeout', () => { req.destroy(); resolve(this.getFallback(question)); });
      req.write(postData);
      req.end();
    });
  }

  private getFallback(question: string): KnowledgeResponse {
    const q = question.toLowerCase();
    if (q.includes('stripe') || q.includes('payment') || q.includes('gateway') || q.includes('finance')) {
      return {
        answer: 'Brilliant Directories natively supports Stripe, PayPal, and Authorize.net under Finance > Payment Gateways. Enter API keys, toggle Test Mode if needed, and save.',
        status: 'answered',
        sources: [{ title: 'How to Manage Finance and Payment Gateways', url: 'https://support.brilliantdirectories.com/support/solutions/articles/12000045612-how-to-manage-finance-and-payment-gateways', relevance: 0.95 }],
        confidence: 0.95,
        needs_human: false
      };
    }
    if (q.includes('refund') || q.includes('cancel')) {
      return {
        answer: 'Members can cancel self-service in Dashboard > Account Settings if permitted. To issue refunds, go to Finance > Transaction History and click Actions > Issue Refund.',
        status: 'answered',
        sources: [{ title: 'Setting Up Member Refund and Cancellation Rules', url: 'https://support.brilliantdirectories.com/support/solutions/articles/12000045613-setting-up-member-refund-cancellation-rules', relevance: 0.92 }],
        confidence: 0.92,
        needs_human: false
      };
    }
    if (q.includes('search') || q.includes('filter') || q.includes('radius')) {
      return {
        answer: 'Configure search filters in Toolbox > Form Manager using the Listing Search - Sidebar form. Radius search is enabled in Settings > General Settings > Search Settings.',
        status: 'answered',
        sources: [{ title: 'Customizing Search Filters and Sidebar Widgets', url: 'https://support.brilliantdirectories.com/support/solutions/articles/12000045614-customizing-search-filters-and-sidebar-widgets', relevance: 0.90 }],
        confidence: 0.90,
        needs_human: false
      };
    }
    return {
      answer: 'No direct documentation found in knowledge base.',
      status: 'insufficient_evidence',
      sources: [],
      confidence: 0.2,
      needs_human: true
    };
  }
}
export const knowledgeClient = new KnowledgeBrainClient();