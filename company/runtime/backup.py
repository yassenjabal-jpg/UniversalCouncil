import shutil, sqlite3
from pathlib import Path
from .db import connect,set_meta

def backup(db, dest):
    dest=Path(dest); dest.parent.mkdir(parents=True,exist_ok=True)
    out=sqlite3.connect(dest)
    with out: db.backup(out)
    out.close(); return dest

def restore_paused(src,dest):
    shutil.copy2(src,dest)
    db=connect(dest)
    with db:
        set_meta(db,'operation','PAUSED_BY_OWNER')
        set_meta(db,'live_enabled','0')
        current=int(db.execute("SELECT value FROM meta WHERE key='stop_generation'").fetchone()[0])
        set_meta(db,'stop_generation',current+1)
        db.execute('UPDATE grants SET revoked=1')
    return db
