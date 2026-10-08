MARKET_DISCOVERY_MODES={"SEGMENT_FIRST","PAIN_FIRST"}

MARKET_PULL_WEIGHTS={
    "pain_frequency":12,
    "existing_spend":12,
    "urgency":10,
    "workaround_burden":8,
    "buyer_clarity":8,
    "reachability":10,
    "free_ai_resistance":8,
    "repeatability":6,
    "margin_potential":6,
    "evidence_diversity":6,
    "purchasing_capacity":8,
    "local_price_fit":6,
}

class MarketRealityError(ValueError):
    pass

def _require(record, fields, label):
    missing=set(fields)-set(record)
    if missing:
        raise MarketRealityError(f"{label} missing: {sorted(missing)}")

def validate_market_reality(record):
    _require(record, {
        "discovery_mode","geography","demography","social_occupational",
        "purchasing_capacity","buying_behavior","evidence_scope"
    }, "market reality")

    if record["discovery_mode"] not in MARKET_DISCOVERY_MODES:
        raise MarketRealityError("invalid market discovery mode")

    geography=record["geography"]
    _require(geography, {"country","precision_basis"}, "geography")
    if not str(geography["country"]).strip():
        raise MarketRealityError("country is required")
    if not str(geography["precision_basis"]).strip():
        raise MarketRealityError("geographic precision requires a behavioral basis")

    demography=record["demography"]
    _require(demography, {"age_min","age_max","life_stage"}, "demography")
    age_min=int(demography["age_min"])
    age_max=int(demography["age_max"])
    if age_min<0 or age_max<age_min:
        raise MarketRealityError("invalid age range")
    if not str(demography["life_stage"]).strip():
        raise MarketRealityError("age requires life stage")

    social=record["social_occupational"]
    _require(social, {"segment","user","buyer","payer"}, "social/occupational")
    for field in ("segment","user","buyer","payer"):
        if not str(social[field]).strip():
            raise MarketRealityError(f"{field} cannot be empty")

    money=record["purchasing_capacity"]
    _require(money, {
        "currency","capacity_evidence","discretionary_budget_evidence",
        "existing_spend_evidence","willingness_to_pay_evidence",
        "price_floor_minor","price_ceiling_minor","payment_methods"
    }, "purchasing capacity")
    low=int(money["price_floor_minor"])
    high=int(money["price_ceiling_minor"])
    if low<0 or high<low:
        raise MarketRealityError("invalid segment price band")
    if not money["capacity_evidence"]:
        raise MarketRealityError("purchasing capacity requires segment evidence")
    if not money["payment_methods"]:
        raise MarketRealityError("at least one plausible payment method is required")

    behavior=record["buying_behavior"]
    _require(behavior, {
        "discovery_channels","first_touch_channels","conversation_channels",
        "trust_constraints","payment_behavior","reachability_status"
    }, "buying behavior")
    for field in ("discovery_channels","first_touch_channels","conversation_channels"):
        if not behavior[field]:
            raise MarketRealityError(f"{field} cannot be empty")
    if behavior["reachability_status"] not in {
        "AVAILABLE","CAN_BUILD","CAN_CONNECT","HUMAN_REQUIRED","CAPABILITY_GAP","NOT_FEASIBLE"
    }:
        raise MarketRealityError("invalid reachability status")

    evidence=record["evidence_scope"]
    _require(evidence, {
        "local_sources","geography_matches_target","segment_matches_target",
        "foreign_evidence_role"
    }, "evidence scope")
    if not evidence["local_sources"]:
        raise MarketRealityError("local or target-market evidence is required")
    if evidence["geography_matches_target"] is not True:
        raise MarketRealityError("geography evidence does not match target")
    if evidence["segment_matches_target"] is not True:
        raise MarketRealityError("segment evidence does not match target")
    if evidence["foreign_evidence_role"] not in {"NONE","SECONDARY_CONTEXT"}:
        raise MarketRealityError("foreign evidence may only be secondary context")

    return True

def market_pull_score(ratings):
    missing=set(MARKET_PULL_WEIGHTS)-set(ratings)
    if missing:
        raise MarketRealityError(f"market pull ratings missing: {sorted(missing)}")
    total=0.0
    for key,weight in MARKET_PULL_WEIGHTS.items():
        value=float(ratings[key])
        if value<0 or value>10:
            raise MarketRealityError(f"{key} rating must be 0..10")
        total += (value/10.0)*weight
    return round(total,2)

def classify_market_pull(score):
    score=float(score)
    if score<0 or score>100:
        raise MarketRealityError("market pull score must be 0..100")
    if score<60:
        return "REJECT"
    if score<75:
        return "DISCOVERY"
    if score<85:
        return "VALIDATION_CANDIDATE"
    return "PRIORITY_CANDIDATE"

def validate_project_candidate(market_record, ratings, project):
    validate_market_reality(market_record)
    _require(project, {"name","problem","price_minor","currency"}, "project candidate")
    if not str(project["problem"]).strip():
        raise MarketRealityError("project requires an observed problem")

    money=market_record["purchasing_capacity"]
    if project["currency"] != money["currency"]:
        raise MarketRealityError("project currency must match market price-band currency")

    price=int(project["price_minor"])
    if price<0:
        raise MarketRealityError("project price cannot be negative")
    if price>int(money["price_ceiling_minor"]):
        raise MarketRealityError("project price exceeds evidence-supported segment capacity")

    score=market_pull_score(ratings)
    state=classify_market_pull(score)
    if state=="REJECT":
        raise MarketRealityError("market pull too weak for a venture candidate")
    return {"score":score,"state":state}
