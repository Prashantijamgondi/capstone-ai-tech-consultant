from typing import List
from agents.agent_team import ScopeOfWork, ScopeDiffReport, Requirement

class ScopeDiffer:
    def compare(self, baseline: ScopeOfWork, revised_reqs: List[Requirement]) -> ScopeDiffReport:
        baseline_titles = {r.title: r for r in baseline.requirements}
        revised_titles = {r.title: r for r in revised_reqs}

        added = []
        removed = []
        modified = []
        out_of_scope = []

        for title, r in revised_titles.items():
            if title not in baseline_titles:
                r.status = 'added'
                added.append(r)
                if 'ai' in title.lower() or 'blockchain' in title.lower() or 'custom crm' in title.lower():
                    out_of_scope.append(f'{title}: Beyond standard project baseline. Requires separate quotation.')

        for title, r in baseline_titles.items():
            if title not in revised_titles:
                r.status = 'removed'
                removed.append(r)

        revised_total_hours = sum(r.estimated_hours for r in revised_reqs)
        diff_hours = revised_total_hours - baseline.total_hours

        summary = (
            f'Scope comparison against approved baseline: {len(added)} added, {len(removed)} removed. '
            f'Net hours impact: {diff_hours:+d} hours.'
        )

        return ScopeDiffReport(
            project_id=baseline.project_title,
            baseline_hours=baseline.total_hours,
            revised_hours=revised_total_hours,
            hours_difference=diff_hours,
            added_requirements=added,
            removed_requirements=removed,
            modified_requirements=modified,
            out_of_scope_items=out_of_scope,
            summary=summary
        )

scope_differ = ScopeDiffer()
