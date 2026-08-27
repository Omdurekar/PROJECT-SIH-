import datetime
from typing import Dict, Any

def calculate_days_difference(date_str_1: str, date_str_2: str) -> int:
    """
    Calculates absolute or directional days difference between two YYYY-MM-DD strings.
    """
    try:
        d1 = datetime.datetime.strptime(date_str_1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(date_str_2, "%Y-%m-%d")
        return (d2 - d1).days
    except ValueError:
        return 0

def derive_project_metrics(
    budget: float,
    expenditure: float,
    planned_duration: int,
    time_elapsed: int,
    completion_pct: float,
    total_milestones: int,
    completed_milestones: int,
    delayed_milestones: int,
    risk_score: float
) -> Dict[str, float]:
    planned_dur_safe = max(1.0, float(planned_duration))
    time_elapsed_pct = (float(time_elapsed) / planned_dur_safe) * 100.0
    schedule_variance_days = float(planned_duration) - float(time_elapsed)
    budget_variance = float(budget) - float(expenditure)
    progress_variance = float(completion_pct) - time_elapsed_pct

    total_m_safe = max(1.0, float(total_milestones))
    milestone_delay_ratio = float(delayed_milestones) / total_m_safe
    milestone_completion_ratio = float(completed_milestones) / total_m_safe

    budget_safe = max(0.01, float(budget))
    expenditure_pct = (float(expenditure) / budget_safe) * 100.0
    remaining_duration_days = max(0.0, float(planned_duration) - float(time_elapsed))

    return {
        "schedule_variance_days": round(schedule_variance_days, 2),
        "budget_variance": round(budget_variance, 2),
        "time_elapsed_pct": round(time_elapsed_pct, 2),
        "progress_variance": round(progress_variance, 2),
        "milestone_delay_ratio": round(milestone_delay_ratio, 4),
        "milestone_completion_ratio": round(milestone_completion_ratio, 4),
        "expenditure_pct": round(expenditure_pct, 2),
        "remaining_duration_days": round(remaining_duration_days, 2)
    }
