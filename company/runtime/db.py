import sqlite3
from pathlib import Path

SCHEMA_VERSION=1

def connect(path):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(path)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA journal_mode=WAL')
    migrate(db)
    return db

def migrate(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS capabilities(id TEXT PRIMARY KEY, operation TEXT NOT NULL, account TEXT NOT NULL, status TEXT NOT NULL, scopes_json TEXT NOT NULL, last_test TEXT, expires_at TEXT, cost_minor INTEGER NOT NULL DEFAULT 0, currency TEXT, UNIQUE(operation,account));
    CREATE TABLE IF NOT EXISTS grants(id TEXT PRIMARY KEY, generation INTEGER NOT NULL, venture_id TEXT NOT NULL, commands_json TEXT NOT NULL, channel TEXT, destination TEXT, data_scopes_json TEXT NOT NULL, payee TEXT, currency TEXT, per_action_cap INTEGER, total_cap INTEGER, used_amount INTEGER NOT NULL DEFAULT 0, max_uses INTEGER, uses INTEGER NOT NULL DEFAULT 0, expires_at TEXT, revoked INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS budgets(venture_id TEXT NOT NULL, currency TEXT NOT NULL, cap_minor INTEGER NOT NULL, reserved_minor INTEGER NOT NULL DEFAULT 0, spent_minor INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(venture_id,currency));
    CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL, venture_id TEXT NOT NULL, command_type TEXT NOT NULL, amount_minor INTEGER NOT NULL DEFAULT 0, currency TEXT, state TEXT NOT NULL, grant_id TEXT, input_hash TEXT NOT NULL, provider_ref TEXT, result_json TEXT, simulated INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(grant_id) REFERENCES grants(id));
    CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL, type TEXT NOT NULL, aggregate_id TEXT NOT NULL, venture_id TEXT, payload_json TEXT NOT NULL, simulated INTEGER NOT NULL, evidence_ref TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY, claim TEXT NOT NULL, evidence_type TEXT NOT NULL, source TEXT NOT NULL, observed_at TEXT, expires_at TEXT, hash TEXT, restricted INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS obligations(id TEXT PRIMARY KEY, venture_id TEXT NOT NULL, order_id TEXT, description TEXT NOT NULL, due_at TEXT, amount_minor INTEGER, currency TEXT, status TEXT NOT NULL DEFAULT 'OPEN');
    CREATE TABLE IF NOT EXISTS ledger_entries(id TEXT PRIMARY KEY, kind TEXT NOT NULL, evidence_ref TEXT, reversal_of TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS ledger_lines(entry_id TEXT NOT NULL, account TEXT NOT NULL, currency TEXT NOT NULL, debit_minor INTEGER NOT NULL DEFAULT 0, credit_minor INTEGER NOT NULL DEFAULT 0, FOREIGN KEY(entry_id) REFERENCES ledger_entries(id));
    CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY, venture_id TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, state TEXT NOT NULL, qualified_contacts INTEGER NOT NULL DEFAULT 0, replies INTEGER NOT NULL DEFAULT 0, paid INTEGER NOT NULL DEFAULT 0, contribution_minor INTEGER, currency TEXT, end_at TEXT);
    CREATE TABLE IF NOT EXISTS cost_records(id TEXT PRIMARY KEY, venture_id TEXT NOT NULL, category TEXT NOT NULL, amount_minor INTEGER NOT NULL DEFAULT 0, currency TEXT, owner_minutes INTEGER NOT NULL DEFAULT 0, meta_work INTEGER NOT NULL DEFAULT 0);
    ''')
    defaults={'schema_version':str(SCHEMA_VERSION),'operation':'PAUSED_BY_OWNER','autonomy':'DRY_RUN','stop_generation':'1','live_enabled':'0'}
    for k,v in defaults.items(): db.execute('INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)',(k,v))
    db.commit()

def get_meta(db,key,default=None):
    r=db.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
    return r['value'] if r else default

def set_meta(db,key,value):
    db.execute('INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,str(value)))
