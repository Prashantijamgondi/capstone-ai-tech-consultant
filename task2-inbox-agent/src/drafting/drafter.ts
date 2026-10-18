import { knowledgeClient, KnowledgeResponse } from '../knowledge-client/client';
import { emailClassifier, EmailClassification } from '../email/classifier';

export interface EmailDraft {
  emailId: string;
  category: string;
  sender: string;
  subject: string;
  customerSummary: string;
  suggestedReply: string;
  sources: Array<{ title: string; url: string }>;
  riskLevel: string;
  urgency: string;
  requiresHumanApproval: boolean;
  canAutoSend: boolean;
  streakCount: number;
}

export class EmailDrafter {
  async draftReply(
    emailId: string,
    sender: string,
    subject: string,
    body: string,
    currentStreak: number = 0,
    isAutonomous: boolean = false
  ): Promise<EmailDraft> {
    const classification = emailClassifier.classify(subject, body);
    const kbResponse: KnowledgeResponse = await knowledgeClient.query(subject + ' ' + body);

    let customerSummary = 'Customer is inquiring about ' + subject.toLowerCase();
    let suggestedReply = '';
    const sources = kbResponse.sources.map(s => ({ title: s.title, url: s.url }));

    if (classification.category === 'refund_cancellation') {
      customerSummary = 'Customer is requesting an account cancellation or refund.';
      suggestedReply = 'Hi there,\n\nThank you for reaching out to us. We have received your request regarding account cancellation / refund.\n\nOur team has pulled up your billing record and forwarded this directly to our billing administrator for review according to our refund policies.\n\nWe will update you within 1 business day once the transaction status is confirmed.\n\nBest regards,\nCustomer Support Team';
    } else if (classification.category === 'complaint') {
      customerSummary = 'Customer submitted an urgent grievance or service complaint.';
      suggestedReply = 'Hi there,\n\nWe sincerely apologize for the frustration and inconvenience this issue has caused you. We take this very seriously.\n\nOur senior technical consultant is actively reviewing the logs and service status right now. We will follow up with you within the hour with concrete remediation steps.\n\nSincerely,\nTechnical Operations Team';
    } else if (classification.category === 'quote_request' || classification.category === 'project_request') {
      customerSummary = 'Customer is requesting a custom feature, integration, or commercial quote.';
      suggestedReply = 'Hi there,\n\nThank you for your interest in extending your directory platform!\n\nWe have logged your custom project requirements and our solutions architect is assessing feasibility against our standard settings and modules.\n\nWe will prepare a structured Scope of Work (SOW) and developer hours estimate for your review shortly.\n\nBest regards,\nSolutions Team';
    } else if (kbResponse.status === 'answered') {
      customerSummary = 'Customer is asking how to configure or use product settings.';
      suggestedReply = 'Hi there,\n\nThank you for reaching out! Here is how you can resolve this:\n\n' + kbResponse.answer + '\n\nPlease let us know if you have any questions or need further assistance.\n\nBest regards,\nCustomer Support Team';
    } else {
      customerSummary = 'Customer question requires specialized technical assistance.';
      suggestedReply = 'Hi there,\n\nThank you for contacting support. We have escalated your inquiry to our senior technical specialist to ensure you get the exact configuration steps.\n\nWe will follow up with you shortly.\n\nBest regards,\nCustomer Support Team';
    }

    const canAutoSend = isAutonomous && !classification.requiresHumanReview;

    return {
      emailId,
      category: classification.category,
      sender,
      subject,
      customerSummary,
      suggestedReply,
      sources,
      riskLevel: classification.risk,
      urgency: classification.urgency,
      requiresHumanApproval: !canAutoSend,
      canAutoSend,
      streakCount: currentStreak
    };
  }
}

export const emailDrafter = new EmailDrafter();
