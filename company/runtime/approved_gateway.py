import json
from .policy import (
    authorize, reserve, consume, release,
    reserve_use, consume_use, release_use,
    create_grant as _create_grant, h,
)
from .states import ActionState

class GatewayError(ValueError):
    pass

class ApprovedGateway:
    """Single sanctioned Stage 0 execution entrypoint.

    Direct provider calls and direct Kernel.execute are not live-approved.
    """

    def __init__(self, db):
        self.db = db

    def create_grant(self, grant_id, venture_id, commands, **kwargs):
        for field in ("per_action_cap", "total_cap", "max_uses"):
            value = kwargs.get(field)
            if value is not None and int(value) < 0:
                raise GatewayError(f"{field} cannot be negative")
        _create_grant(self.db, grant_id, venture_id, commands, **kwargs)

    def execute(self, *, action_id, idempotency_key, venture_id, command_type,
                operation, account, adapter, grant_id, destination=None,
                amount_minor=0, currency=None, data_scope=None, simulated=True,
                payload=None):
        amount_minor = int(amount_minor)
        if amount_minor < 0:
            raise GatewayError("action amount cannot be negative")

        existing = self.db.execute(
            "SELECT * FROM actions WHERE idempotency_key=?", (idempotency_key,)
        ).fetchone()
        if existing:
            return dict(existing)

        authorize(
            self.db,
            grant_id=grant_id,
            venture_id=venture_id,
            command_type=command_type,
            operation=operation,
            account=account,
            destination=destination,
            amount_minor=amount_minor,
            currency=currency,
            data_scope=data_scope,
            simulated=simulated,
        )

        financial = bool(amount_minor and currency)
        if financial:
            reserve(self.db, grant_id, venture_id, currency, amount_minor)
        else:
            reserve_use(self.db, grant_id)

        try:
            with self.db:
                self.db.execute(
                    """INSERT INTO actions
                    (id,idempotency_key,venture_id,command_type,amount_minor,currency,
                     state,grant_id,input_hash,simulated)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        action_id, idempotency_key, venture_id, command_type,
                        amount_minor, currency, ActionState.RUNNING.value,
                        grant_id, h(payload or {}), int(simulated),
                    ),
                )

            result = adapter.dispatch(payload or {})
            if result.get("unknown_after_accept"):
                with self.db:
                    self.db.execute(
                        "UPDATE actions SET state=?,provider_ref=?,result_json=? WHERE id=?",
                        (
                            ActionState.UNKNOWN_OUTCOME.value,
                            result.get("provider_ref"),
                            json.dumps(result, sort_keys=True),
                            action_id,
                        ),
                    )
                return dict(self.db.execute(
                    "SELECT * FROM actions WHERE id=?", (action_id,)
                ).fetchone())

            if not result.get("postcondition", False):
                raise RuntimeError("postcondition not verified")

            if financial:
                consume(self.db, grant_id, venture_id, currency, amount_minor)
            else:
                consume_use(self.db, grant_id)

            with self.db:
                self.db.execute(
                    "UPDATE actions SET state=?,provider_ref=?,result_json=? WHERE id=?",
                    (
                        ActionState.SUCCEEDED.value,
                        result.get("provider_ref"),
                        json.dumps(result, sort_keys=True),
                        action_id,
                    ),
                )
            return dict(self.db.execute(
                "SELECT * FROM actions WHERE id=?", (action_id,)
            ).fetchone())
        except Exception:
            if financial:
                release(self.db, grant_id, venture_id, currency, amount_minor)
            else:
                release_use(self.db, grant_id)
            with self.db:
                self.db.execute(
                    "UPDATE actions SET state=? WHERE id=?",
                    (ActionState.FAILED.value, action_id),
                )
            raise

    def reconcile(self, action_id, outcome, *, provider_ref=None, evidence_ref=None):
        row = self.db.execute(
            "SELECT * FROM actions WHERE id=?", (action_id,)
        ).fetchone()
        if not row or row["state"] != ActionState.UNKNOWN_OUTCOME.value:
            raise GatewayError("action is not awaiting reconciliation")

        allowed = {
            ActionState.SUCCEEDED.value,
            ActionState.FAILED.value,
            ActionState.CANCELLED.value,
        }
        if outcome not in allowed:
            raise GatewayError("invalid reconciliation outcome")

        financial = bool(row["amount_minor"] and row["currency"])
        if outcome == ActionState.SUCCEEDED.value:
            if financial:
                consume(
                    self.db, row["grant_id"], row["venture_id"],
                    row["currency"], row["amount_minor"]
                )
            else:
                consume_use(self.db, row["grant_id"])
        else:
            if financial:
                release(
                    self.db, row["grant_id"], row["venture_id"],
                    row["currency"], row["amount_minor"]
                )
            else:
                release_use(self.db, row["grant_id"])

        result = {
            "reconciled": True,
            "outcome": outcome,
            "evidence_ref": evidence_ref,
        }
        with self.db:
            self.db.execute(
                """UPDATE actions
                SET state=?, provider_ref=COALESCE(?,provider_ref), result_json=?
                WHERE id=?""",
                (
                    outcome, provider_ref,
                    json.dumps(result, sort_keys=True), action_id
                ),
            )
        return dict(self.db.execute(
            "SELECT * FROM actions WHERE id=?", (action_id,)
        ).fetchone())
