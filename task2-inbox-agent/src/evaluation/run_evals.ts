import fs from 'fs';
import path from 'path';
import { emailClassifier } from '../email/classifier';
import { emailDrafter } from '../drafting/drafter';
import { feedbackManager } from '../feedback/streak_manager';

async function runEvals() {
  console.log('='.repeat(70));
  console.log('RUNNING TASK 2: INBOX AGENT EVALUATION SUITE (20 TEST CASES)');
  console.log('='.repeat(70));

  const emailsPath = path.join(__dirname, '../data/emails.json');
  const emails = JSON.parse(fs.readFileSync(emailsPath, 'utf-8'));
  const testCases = emails.slice(0, 20);

  let passedCount = 0;

  for (const tc of testCases) {
    const t0 = Date.now();
    const cl = emailClassifier.classify(tc.subject, tc.body);
    const draft = await emailDrafter.draftReply(tc.id, tc.sender, tc.subject, tc.body, 0, false);
    const latency = Date.now() - t0;

    const categoryCorrect = cl.category === tc.category;
    const hasReply = draft.suggestedReply.length > 50;
    const safetyEnforced = (tc.risk === 'high') ? draft.requiresHumanApproval === true : true;

    const passed = categoryCorrect && hasReply && safetyEnforced;
    if (passed) passedCount++;

    const statusStr = passed ? 'PASS' : 'FAIL';
    console.log('[' + tc.id + '] ' + statusStr + ' | Cat: ' + cl.category + ' | Risk: ' + draft.riskLevel + ' | Latency: ' + latency + 'ms');
  }

  console.log('-'.repeat(70));
  console.log('Testing 20-Consecutive Approval Autonomy Rule & Safeguards:');
  const cat = 'how_to';
  for (let i = 1; i <= 20; i++) {
    feedbackManager.recordFeedback({
      emailId: 'streak_test_' + i,
      category: cat,
      originalDraft: 'Exact standard reply.',
      finalSent: 'Exact standard reply.',
      action: 'approved',
      timestamp: new Date().toISOString()
    });
  }
  const stateAfter20 = feedbackManager.getState(cat);
  console.log('State after 20 unedited approvals: Consecutive=' + stateAfter20.consecutiveApprovals + ', AutonomyEligible=' + stateAfter20.isEligibleForAutonomy);

  feedbackManager.recordFeedback({
    emailId: 'streak_test_edit',
    category: cat,
    originalDraft: 'Exact standard reply.',
    finalSent: 'Edited human custom reply.',
    action: 'edited',
    reason: 'Added specific detail',
    timestamp: new Date().toISOString()
  });
  const stateAfterEdit = feedbackManager.getState(cat);
  console.log('State after human edit: Consecutive=' + stateAfterEdit.consecutiveApprovals + ', AutonomyEligible=' + stateAfterEdit.isEligibleForAutonomy);

  console.log('-'.repeat(70));
  const pct = ((passedCount / testCases.length) * 100).toFixed(1);
  console.log('Task 2 Evaluation Summary: ' + passedCount + '/' + testCases.length + ' passed (' + pct + '%)');
  console.log('='.repeat(70));
}

runEvals();
