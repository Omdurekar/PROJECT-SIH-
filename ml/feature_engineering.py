import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "budget",
    "expenditure",
    "planned_duration_days",
    "time_elapsed_days",
    "completion_percentage",
    "total_milestones",
    "completed_milestones",
    "delayed_milestones",
    "pending_milestones",
    "risk_score",
    "schedule_variance_days",
    "budget_variance",
    "time_elapsed_pct",
    "progress_variance",
    "milestone_delay_ratio",
    "milestone_completion_ratio",
    "expenditure_pct",
    "remaining_duration_days"
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derives domain-specific features for project delay classification.
    """
    data = df.copy()

    # Time Elapsed Percentage
    planned_dur = np.maximum(1.0, data["planned_duration_days"].values)
    data["time_elapsed_pct"] = (data["time_elapsed_days"].values / planned_dur) * 100.0

    # Schedule Variance (Days remaining or overdue)
    data["schedule_variance_days"] = data["planned_duration_days"].values - data["time_elapsed_days"].values

    # Budget Variance
    data["budget_variance"] = data["budget"].values - data["expenditure"].values

    # Progress Variance = Actual Completion % - Expected Progress %
    data["progress_variance"] = data["completion_percentage"].values - data["time_elapsed_pct"].values

    # Milestone Ratios
    total_m = np.maximum(1.0, data["total_milestones"].values)
    data["milestone_delay_ratio"] = data["delayed_milestones"].values / total_m
    data["milestone_completion_ratio"] = data["completed_milestones"].values / total_m

    # Expenditure Percentage
    budget_safe = np.maximum(0.01, data["budget"].values)
    data["expenditure_pct"] = (data["expenditure"].values / budget_safe) * 100.0

    # Remaining Duration
    data["remaining_duration_days"] = np.maximum(0.0, data["planned_duration_days"].values - data["time_elapsed_days"].values)

    return data
