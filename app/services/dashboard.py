from sqlalchemy.orm import Session
from app.models.schemas import DashboardOverview, ProjectResponse
from app.database import projects as db_projects
from app.models.orm import Project

def get_dashboard_overview_service(db: Session) -> DashboardOverview:
    stats = db_projects.get_project_stats(db)

    # Get High Priority projects (HIGH delay level or risk score >= 7.0)
    high_priority_query = db.query(Project).filter(
        (Project.delay_level == "HIGH") | (Project.risk_score >= 7.0)
    ).order_by(Project.risk_score.desc(), Project.completion_percentage.asc()).limit(10).all()

    high_priority_projects = [ProjectResponse.model_validate(p) for p in high_priority_query]

    # Department summary breakdown
    all_projects = db.query(Project).all()
    dept_summary = {}
    for p in all_projects:
        dept = p.department
        if dept not in dept_summary:
            dept_summary[dept] = {
                "total_projects": 0,
                "total_budget": 0.0,
                "high_delay_count": 0
            }
        dept_summary[dept]["total_projects"] += 1
        dept_summary[dept]["total_budget"] += p.budget
        if p.delay_level == "HIGH":
            dept_summary[dept]["high_delay_count"] += 1

    return DashboardOverview(
        total_projects=stats["total_projects"],
        delay_distribution=stats["delay_distribution"],
        total_budget=stats["total_budget"],
        utilized_budget=stats["utilized_budget"],
        avg_completion_percentage=stats["avg_completion_percentage"],
        high_priority_projects=high_priority_projects,
        department_summary=dept_summary
    )
