import json, sqlite3, time, uuid
from pathlib import Path
class Store:
    def __init__(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(path,check_same_thread=False); self.db.execute("create table if not exists runs(id text primary key,status text,payload text,result text,correlation_id text,created real,updated real,idempotency_key text unique)"); self.db.execute("create table if not exists quarantine(id integer primary key,errors text,correlation_id text,created real)"); self.db.execute("create table if not exists feedback(id integer primary key,run_id text,category text,useful integer,citations_correct integer,comments text,created real)"); self.db.commit()
        try: self.db.execute("alter table runs add column idempotency_key text"); self.db.execute("create unique index if not exists idx_runs_idempotency on runs(idempotency_key)"); self.db.commit()
        except sqlite3.OperationalError: pass
    def create(self,payload,cid,idempotency_key=None):
        if idempotency_key:
            existing=self.db.execute("select id from runs where idempotency_key=?",(idempotency_key,)).fetchone()
            if existing: return existing[0], True
        rid=str(uuid.uuid4()); now=time.time(); self.db.execute("insert into runs values(?,?,?,?,?,?,?,?)",(rid,"pending",json.dumps(payload),None,cid,now,now,idempotency_key)); self.db.commit(); return rid, False
    def update(self,rid,status,result=None): self.db.execute("update runs set status=?,result=?,updated=? where id=?",(status,json.dumps(result) if result is not None else None,time.time(),rid)); self.db.commit()
    def payload(self,rid):
        row=self.db.execute("select payload from runs where id=?",(rid,)).fetchone(); return json.loads(row[0]) if row else None
    def get(self,rid):
        r=self.db.execute("select id,status,correlation_id,created,updated,result from runs where id=?",(rid,)).fetchone();
        if not r:return None
        return {"run_id":r[0],"status":r[1],"correlation_id":r[2],"created_at":r[3],"updated_at":r[4],"result":json.loads(r[5]) if r[5] else None}
    def quarantine(self,errors,cid): self.db.execute("insert into quarantine(errors,correlation_id,created) values(?,?,?)",(json.dumps(errors),cid,time.time())); self.db.commit()
    def feedback(self, item):
        self.db.execute("insert into feedback(run_id,category,useful,citations_correct,comments,created) values(?,?,?,?,?,?)",(item["run_id"],item["category"],int(item["useful"]),int(item["citations_correct"]),item.get("comments"),time.time())); self.db.commit()

