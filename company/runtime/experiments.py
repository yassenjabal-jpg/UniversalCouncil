class ConcurrencyConflict(RuntimeError):
    pass

def update_experiment(db, experiment_id, expected_version, **changes):
    allowed={'state','qualified_contacts','replies','paid','contribution_minor','currency','end_at'}
    if not changes or not set(changes).issubset(allowed):
        raise ValueError('invalid experiment update')
    cols=list(changes)
    sql='UPDATE experiments SET '+','.join(f'{k}=?' for k in cols)+', version=version+1 WHERE id=? AND version=?'
    with db:
        cur=db.execute(sql,[changes[k] for k in cols]+[experiment_id,expected_version])
        if cur.rowcount!=1:
            raise ConcurrencyConflict('optimistic concurrency conflict')
    return dict(db.execute('SELECT * FROM experiments WHERE id=?',(experiment_id,)).fetchone())
