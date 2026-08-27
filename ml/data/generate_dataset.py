import os
import random
import pandas as pd
import numpy as np

def generate_project_dataset(num_samples: int = 1200, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)

    departments = [
        "Ministry of Road Transport & Highways",
        "Ministry of Railways",
        "Ministry of Power",
        "Ministry of Urban Development",
        "Ministry of Health & Family Welfare",
        "Ministry of Electronics & IT",
        "Ministry of Water Resources"
    ]

    project_types = [
        "Infrastructure",
        "Transportation",
        "Energy & Power",
        "Urban Infrastructure",
        "Healthcare Facility",
        "Digital Governance",
        "Water & Sanitation"
    ]

    locations = [
        "Delhi NCR", "Mumbai", "Bengaluru", "Hyderabad", "Chennai",
        "Kolkata", "Ahmedabad", "Pune", "Jaipur", "Lucknow", "Patna", "Guwahati"
    ]

    data = []

    for i in range(1, num_samples + 1):
        project_id = f"PRJ-{1000 + i}"
        dept = random.choice(departments)
        proj_type = random.choice(project_types)
        loc = random.choice(locations)

        budget = round(random.uniform(10.0, 3500.0), 2)  # Crores INR
        planned_duration = random.randint(180, 1800)  # Days

        # Time elapsed ratio (0.1 to 1.2)
        elapsed_ratio = random.uniform(0.1, 1.2)
        time_elapsed = int(planned_duration * elapsed_ratio)

        # Base completion efficiency (some projects are fast, some slow)
        efficiency_factor = np.random.normal(loc=0.85, scale=0.25)
        efficiency_factor = max(0.1, min(1.3, efficiency_factor))

        expected_completion = min(100.0, (time_elapsed / planned_duration) * 100.0)
        completion_pct = round(max(0.0, min(100.0, expected_completion * efficiency_factor)), 2)

        # Expenditure
        expenditure_pct = max(0.05, min(1.2, (completion_pct / 100.0) * random.uniform(0.8, 1.3)))
        expenditure = round(budget * expenditure_pct, 2)

        # Milestones
        total_milestones = random.randint(5, 40)
        completed_milestones = int(total_milestones * (completion_pct / 100.0))
        remaining_milestones = total_milestones - completed_milestones

        # Delayed milestones out of remaining/total
        milestone_delay_prob = max(0.0, min(0.9, (expected_completion - completion_pct) / 100.0 + random.uniform(0.0, 0.2)))
        delayed_milestones = int(remaining_milestones * milestone_delay_prob)
        pending_milestones = max(0, remaining_milestones - delayed_milestones)

        # Risk indicator score (0 to 10)
        risk_score = round(max(0.0, min(10.0, (100.0 - completion_pct) * 0.05 + delayed_milestones * 0.4 + random.uniform(0, 2))), 2)

        # Calculate progress variance: actual progress - expected progress
        progress_variance = completion_pct - expected_completion

        # Determine Delay Category (Ground Truth logic for synthetic data generation)
        if progress_variance < -25 or (time_elapsed > planned_duration and completion_pct < 80) or delayed_milestones > (total_milestones * 0.35):
            delay_level = "HIGH"
        elif progress_variance < -10 or delayed_milestones > (total_milestones * 0.15) or risk_score > 5.5:
            delay_level = "MEDIUM"
        else:
            delay_level = "LOW"

        data.append({
            "project_id": project_id,
            "project_name": f"{proj_type} Project - {loc} #{i}",
            "department": dept,
            "project_type": proj_type,
            "location": loc,
            "budget": budget,
            "expenditure": expenditure,
            "planned_duration_days": planned_duration,
            "time_elapsed_days": time_elapsed,
            "completion_percentage": completion_pct,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "delayed_milestones": delayed_milestones,
            "pending_milestones": pending_milestones,
            "risk_score": risk_score,
            "delay_level": delay_level
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    os.makedirs("ml/data", exist_ok=True)
    df = generate_project_dataset(1500)
    output_path = "ml/data/projects_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset generated with {len(df)} samples saved to {output_path}")
