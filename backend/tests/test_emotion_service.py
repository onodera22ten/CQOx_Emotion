from datetime import datetime, timedelta

from cqox.emotion import service, schemas


def sample_draft():
    now = datetime.utcnow() + timedelta(days=1)
    return schemas.EpisodeDraftCreate(
        scenario_type=schemas.ScenarioType.INTERVIEW,
        topic="転職理由",
        scheduled_at=now,
        location="online",
        pre_state=schemas.PreState(pre_anxiety=7, pre_crying_risk=6, pre_speech_block_risk=5),
        preparations_planned=schemas.PreparationPlan(
            journaling_10m=5,
            three_messages=7,
            breathing_4_7_8=3,
            roleplay_self_qa=0,
            safe_word_plan=0,
        ),
        preference_weights_raw=schemas.PreferenceWeightsRaw(relief=5, expression=4, relationship=1),
    )


def test_episode_lifecycle(db_session):
    draft = sample_draft()
    res = service.create_episode_draft(db_session, user_id=1, draft=draft)
    assert res.episode_id == 1

    episodes = service.list_episodes(db_session, user_id=1)
    assert len(episodes) == 1
    assert episodes[0].topic == "転職理由"

    outcome_payload = schemas.OutcomeCreate(
        stress_during=5,
        stress_after=3,
        crying_level=2,
        speech_block_level=1,
        expression_score=7,
        relationship_impact=1,
        partner_reaction=schemas.PartnerReaction.POSITIVE,
        days_after_reflection=2,
        would_repeat_preparation=8,
        reflection_short="十分な準備ができた",
    )
    outcome = service.record_outcome(db_session, user_id=1, episode_id=1, outcome=outcome_payload)
    assert outcome.expression_score == 7

    timeline = service.get_timeline_points(db_session, user_id=1)
    assert len(timeline.points) == 1
    assert timeline.points[0].episode_id == 1


def test_preference_profile(db_session):
    profile = service.get_preference_profile(db_session, user_id=1)
    assert profile.weight_relief > 0

    updated = service.update_preference_profile(
        db_session,
        user_id=1,
        payload=schemas.PreferenceProfileCreate(weight_relief=0.6, weight_expression=0.3, weight_relationship=0.1),
    )
    assert abs(updated.weight_relief - 0.6) < 1e-6
