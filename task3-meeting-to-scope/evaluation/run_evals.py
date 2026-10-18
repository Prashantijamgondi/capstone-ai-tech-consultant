import asyncio
import time
from agents.agent_team import TranscriptAnalystAgent, ProductFeasibilityAgent, ScopeAndEstimationAgent
from scope_diff.differ import scope_differ, Requirement

TEST_CASES = [
    {"id": "TC3-01", "text": "Client wants to filter by 25 therapy specialties."},
    {"id": "TC3-02", "text": "We need location radius search by distance in miles."},
    {"id": "TC3-03", "text": "Mobile search sidebar looks cramped and hard to use."},
    {"id": "TC3-04", "text": "Accept $25 appointment booking deposits via Stripe."},
    {"id": "TC3-05", "text": "Interactive Google Maps with practitioner pins."},
    {"id": "TC3-06", "text": "Vague request: make search better and add filters."},
    {"id": "TC3-07", "text": "Needs phone layout touch friendly drawer."},
    {"id": "TC3-08", "text": "Booking calendar with credit card payment."},
    {"id": "TC3-09", "text": "Specialty dropdowns in search form."},
    {"id": "TC3-10", "text": "Search radius miles distance filters."},
    {"id": "TC3-11", "text": "Google Maps integration with custom pins above results."},
    {"id": "TC3-12", "text": "Mobile phone filter slider."},
    {"id": "TC3-13", "text": "Booking deposit $25 checkout flow."},
    {"id": "TC3-14", "text": "Therapy modality category filters."},
    {"id": "TC3-15", "text": "Location distance proximity search."},
    {"id": "TC3-16", "text": "Phone touch drawer for categories on mobile."},
    {"id": "TC3-17", "text": "Map view showing pins for directory listings."},
    {"id": "TC3-18", "text": "Stripe deposit collection for therapist appointments."},
    {"id": "TC3-19", "text": "Specialties checkbox and dropdown search."},
    {"id": "TC3-20", "text": "Distance filter in miles for nearby directory members."}
]


async def run():
    analyst = TranscriptAnalystAgent()
    feasibility = ProductFeasibilityAgent()
    estimator = ScopeAndEstimationAgent()
    passed = 0
    print('=' * 70)
    print('RUNNING TASK 3: MEETING TO SCOPE EVALUATION SUITE (20 TEST CASES)')
    print('=' * 70)
    for tc in TEST_CASES:
        t0 = time.time()
        reqs = analyst.analyze(tc['text'])
        lat = int((time.time() - t0) * 1000)
        ok = len(reqs) > 0
        if ok: passed += 1
        cid = tc["id"]; pstr = "PASS" if ok else "FAIL"; print(f"[{cid}] {pstr} | Reqs: {len(reqs)} | Latency: {lat}ms")
    print('-' * 70)
    with open('transcripts/meeting_1_discovery.txt', 'r') as f: t1 = f.read()
    with open('transcripts/meeting_3_followup_changes.txt', 'r') as f: t3 = f.read()
    extracted_1 = analyst.analyze(t1)
    enriched_1 = [dict(r, **(await feasibility.check_feasibility(r))) for r in extracted_1]
    baseline = estimator.build_sow('Wellness Directory LLC', enriched_1)
    print(f"Baseline SOW Hours: {baseline.total_hours} | Cost: ${baseline.total_cost_usd:.2f}")
    extracted_3 = analyst.analyze(t3)
    revised_reqs = [Requirement(id=f'REQ-REV-{i+1:03d}', title=r['title'], description=r['description'], type='configuration', category='Revised', estimated_hours=8, reasoning='Updated', source_quote=r['quote'], status='active') for i, r in enumerate(extracted_3)]
    diff = scope_differ.compare(baseline, revised_reqs)
    print(f"Diff Summary: {diff.summary}")
    pct = (passed / len(TEST_CASES)) * 100
    print(f"Task 3 Evaluation Summary: {passed}/{len(TEST_CASES)} passed ({pct:.1f}%)")
    print('=' * 70)

if __name__ == '__main__':
    asyncio.run(run())
