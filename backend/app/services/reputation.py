from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import models


def recalc_creator_stats(db: Session, creator_id: int) -> None:
    creator = db.query(models.Creator).filter(models.Creator.id == creator_id).first()
    if not creator:
        return

    sessions = (
        db.query(models.Session)
        .filter(models.Session.creator_id == creator_id, models.Session.failed.is_(False))
        .all()
    )

    if not sessions:
        creator.players_passed = 0
        creator.avg_score = 0.0
        creator.reputation = 0.0
        creator.rating = 0.0
        db.commit()
        return

    unique_players = {s.player_name for s in sessions}
    players_passed = len(unique_players)

    scores = []
    for s in sessions:
        if s.total_questions > 0:
            score10 = (s.correct_count / s.total_questions) * 10.0
            scores.append(score10)

    avg_score = sum(scores) / len(scores) if scores else 0.0

    base_rep = players_passed // 10
    bonus = 0.0
    if avg_score >= 7.0:
        bonus += 0.5

    week_ago = datetime.utcnow() - timedelta(days=7)
    active_recent = [s for s in sessions if s.started_at >= week_ago]
    if len(active_recent) >= 5:
        bonus += 0.5

    reputation = float(base_rep) + bonus

    creator.players_passed = players_passed
    creator.avg_score = round(avg_score, 2)
    creator.reputation = round(reputation, 2)
    creator.rating = creator.reputation

    db.commit()
