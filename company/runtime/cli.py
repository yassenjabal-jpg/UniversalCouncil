import argparse, json
from .db import connect

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--db',required=True)
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status')
    a=p.parse_args(argv)
    db=connect(a.db)
    if a.cmd=='status':
        rows=db.execute('SELECT key,value FROM meta ORDER BY key').fetchall()
        print(json.dumps({r['key']:r['value'] for r in rows},indent=2))

if __name__=='__main__': main()
