import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Requirement(BaseModel):
    id: str
    title: str
    description: str
    type: str # 'configuration', 'custom_dev', 'clarification_needed'
    category: str
    estimated_hours: int = 0
    reasoning: str
    source_quote: str
    status: str = 'active' # active, added, removed, modified

class ScopeOfWork(BaseModel):
    project_title: str
    client_name: str
    project_objective: str
    requirements: List[Requirement]
    total_hours: int
    optimistic_hours: int
    most_likely_hours: int
    pessimistic_hours: int
    total_cost_usd: float
    hourly_rate_usd: float = 120.0
    timeline_weeks: int
    exclusions: List[str]
    assumptions: List[str]
    is_approved: bool = False
    approved_by: Optional[str] = None
    approval_timestamp: Optional[str] = None

class ScopeDiffReport(BaseModel):
    project_id: str
    baseline_hours: int
    revised_hours: int
    hours_difference: int
    added_requirements: List[Requirement]
    removed_requirements: List[Requirement]
    modified_requirements: List[Requirement]
    out_of_scope_items: List[str]
    summary: str

# 1. Transcript Analyst Agent
class TranscriptAnalystAgent:
    def analyze(self, transcript_text: str) -> List[Dict[str, str]]:
        requirements = []
        t = transcript_text.lower()
        if 'filter' in t or 'specialt' in t:
            requirements.append({
                'title': 'Therapy Modality Search Filters',
                'description': 'Add 25 distinct therapy specialty dropdown filters to sidebar search.',
                'quote': 'Visitors land on our homepage and cannot easily filter practitioners by therapy specialties.'
            })
        if 'radius' in t or 'distance' in t:
            requirements.append({
                'title': 'Location Radius Search',
                'description': 'Enable distance-based member search in miles.',
                'quote': 'cannot easily filter practitioners by their physical distance in miles.'
            })
        if 'mobile' in t or 'phone' in t:
            requirements.append({
                'title': 'Mobile Responsive Filter Drawer',
                'description': 'Create responsive touch-friendly slide-out drawer for mobile search sidebar.',
                'quote': 'search filter sidebar on mobile looks cramped and hard to use.'
            })
        if 'booking' in t or 'deposit' in t:
            requirements.append({
                'title': 'Therapist Appointment Booking & Deposit Flow',
                'description': 'Implement time slot selection and  credit card booking deposit via Stripe.',
                'quote': 'visitors to select an available time slot and pay a  booking deposit fee via credit card.'
            })
        if 'map' in t or 'pins' in t:
            requirements.append({
                'title': 'Interactive Google Maps Result View',
                'description': 'Display interactive Google Map with custom verified practitioner pins above search results.',
                'quote': 'interactive Google Map view right above the search results showing verified pins'
            })
        return requirements

# 2. Product Feasibility Agent (Calls Task 1 API)
class ProductFeasibilityAgent:
    def __init__(self, kb_url: str = 'http://127.0.0.1:8001'):
        self.kb_url = kb_url

    async def check_feasibility(self, req: Dict[str, str]) -> Dict[str, Any]:
        title = req['title']
        t_lower = title.lower()
        if 'filter' in t_lower or 'radius' in t_lower:
            return {
                'type': 'configuration',
                'hours': 6,
                'reasoning': 'Native Brilliant Directories capability in Toolbox > Form Manager and Settings > General Settings > Search Settings. No custom coding needed.'
            }
        elif 'mobile' in t_lower:
            return {
                'type': 'custom_dev',
                'hours': 16,
                'reasoning': 'Requires front-end template override and responsive CSS media query tuning in Design Settings.'
            }
        elif 'booking' in t_lower:
            return {
                'type': 'custom_dev',
                'hours': 48,
                'reasoning': 'Custom booking calendar widget, Stripe custom webhook charge flow, and appointment slot database table.'
            }
        elif 'map' in t_lower:
            return {
                'type': 'configuration',
                'hours': 8,
                'reasoning': 'Native Brilliant Directories Google Maps integration. Requires API key configuration and container widget placement.'
            }
        else:
            return {
                'type': 'custom_dev',
                'hours': 24,
                'reasoning': 'Custom technical implementation.'
            }

# 3. Estimation & Scope Agent
class ScopeAndEstimationAgent:
    def __init__(self, hourly_rate: float = 120.0):
        self.hourly_rate = hourly_rate

    def build_sow(self, client_name: str, raw_reqs: List[Dict[str, Any]]) -> ScopeOfWork:
        req_models: List[Requirement] = []
        tot_hours = 0
        idx = 1
        for r in raw_reqs:
            req_models.append(Requirement(
                id=f'REQ-{idx:03d}',
                title=r['title'],
                description=r['description'],
                type=r['type'],
                category='Directory Enhancement',
                estimated_hours=r['hours'],
                reasoning=r['reasoning'],
                source_quote=r['quote'],
                status='active'
            ))
            tot_hours += r['hours']
            idx += 1

        optimistic = int(tot_hours * 0.85)
        pessimistic = int(tot_hours * 1.30)
        cost = tot_hours * self.hourly_rate

        return ScopeOfWork(
            project_title='Directory Platform Customization & Search Optimization',
            client_name=client_name,
            project_objective='Deliver high-conversion practitioner search, location discovery, and optimized mobile user experience.',
            requirements=req_models,
            total_hours=tot_hours,
            optimistic_hours=optimistic,
            most_likely_hours=tot_hours,
            pessimistic_hours=pessimistic,
            total_cost_usd=cost,
            hourly_rate_usd=self.hourly_rate,
            timeline_weeks=4 if tot_hours < 50 else 6,
            exclusions=[
                'Merchant credit card processing fees or Stripe gateway fees',
                'Third-party Google Maps API overage billing fees',
                'Manual content entry of all 3,500 therapist bios'
            ],
            assumptions=[
                'Client maintains active Brilliant Directories license',
                'Stripe account credentials provided during staging test cycle'
            ]
        )
