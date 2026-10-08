ALLOWED_FOUNDER_VERDICTS={"SUPPORT","OPPOSE","KILL","PIVOT","TEST_NOW"}
NO_REPLY_STATES={
    "INSUFFICIENT_EVIDENCE",
    "DELIVERY_FAILURE",
    "CHANNEL_FAILURE",
    "CONTACT_FAILURE",
    "TIMING_FAILURE",
    "OFFER_FAILURE",
    "NOT_INTERESTED",
}
HR_RECOMMENDATIONS={
    "KEEP",
    "IMPROVEMENT_TRIAL",
    "MERGE",
    "REMOVE_WITHOUT_REPLACEMENT",
    "REPLACE",
    "FIRE_RECOMMENDATION",
}

class GovernanceControlError(ValueError):
    pass

def validate_founder_position(position):
    required={
        "verdict",
        "confidence_0_100",
        "next_10_hours_yes_no",
        "own_money_yes_no",
        "single_strongest_reason",
        "one_evidence_that_changes_view",
        "cost_of_delay",
    }
    missing=required-set(position)
    if missing:
        raise GovernanceControlError(f"missing founder-position fields: {sorted(missing)}")
    if position["verdict"] not in ALLOWED_FOUNDER_VERDICTS:
        raise GovernanceControlError("zero-revenue mode forbids neutral/undefined verdict")
    confidence=int(position["confidence_0_100"])
    if confidence<0 or confidence>100:
        raise GovernanceControlError("confidence must be 0..100")
    for field in ("next_10_hours_yes_no","own_money_yes_no"):
        if position[field] not in {"YES","NO"}:
            raise GovernanceControlError(f"{field} must be YES or NO")
    for field in ("single_strongest_reason","one_evidence_that_changes_view","cost_of_delay"):
        if not str(position[field]).strip():
            raise GovernanceControlError(f"{field} cannot be empty")
    return True

def validate_pass_with_conditions(condition):
    required={"metric","deadline","threshold","default_failure_action"}
    missing=required-set(condition)
    if missing:
        raise GovernanceControlError(f"PASS-WITH-CONDITIONS missing: {sorted(missing)}")
    if condition["default_failure_action"] not in {"KILL","PIVOT","REJECT","HOLD"}:
        raise GovernanceControlError("condition requires explicit default failure action")
    return True

def validate_distribution_gate(record):
    required={
        "buyer",
        "decision_maker",
        "where_buyer_spends_attention",
        "first_touch_channel",
        "conversation_channel",
        "formal_document_channel",
        "normal_response_window",
        "fallback_channel",
        "local_market_evidence",
        "channel_capability_status",
    }
    missing=required-set(record)
    if missing:
        raise GovernanceControlError(f"distribution gate missing: {sorted(missing)}")
    if not record["local_market_evidence"]:
        raise GovernanceControlError("local market evidence is required")
    if record["channel_capability_status"] not in {
        "AVAILABLE","CAN_BUILD","CAN_CONNECT","HUMAN_REQUIRED","NOT_FEASIBLE","CAPABILITY_GAP"
    }:
        raise GovernanceControlError("invalid channel capability status")
    return True

def diagnose_no_reply(*, delivery_confirmed, channel_supported, contact_supported, timing_supported, offer_supported):
    if not delivery_confirmed:
        return "DELIVERY_FAILURE"
    if not channel_supported:
        return "CHANNEL_FAILURE"
    if not contact_supported:
        return "CONTACT_FAILURE"
    if not timing_supported:
        return "TIMING_FAILURE"
    if not offer_supported:
        return "OFFER_FAILURE"
    return "INSUFFICIENT_EVIDENCE"

def validate_hr_recommendation(record):
    required={"role","recommendation","evidence","unique_value_assessment","replacement_or_merge_plan","review_trigger"}
    missing=required-set(record)
    if missing:
        raise GovernanceControlError(f"HR recommendation missing: {sorted(missing)}")
    if record["recommendation"] not in HR_RECOMMENDATIONS:
        raise GovernanceControlError("invalid HR recommendation")
    if record["recommendation"]=="REPLACE" and not record["replacement_or_merge_plan"]:
        raise GovernanceControlError("REPLACE requires a replacement plan")
    if not record["evidence"]:
        raise GovernanceControlError("HR recommendation requires evidence")
    return True

def validate_hr_self_review(reviewer_role):
    if reviewer_role=="HR & Capability Director":
        raise GovernanceControlError("HR self-evaluation is forbidden")
    return True

def complaint_route(subject_role):
    if subject_role=="HR & Capability Director":
        return "Owner"
    return "HR & Capability Director"
