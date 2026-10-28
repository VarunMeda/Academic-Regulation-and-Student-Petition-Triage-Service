import json, sqlite3, time, uuid
from pathlib import Path
class Store:
    def __init__(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(path,check_same_thread=False); self.db.execute("create table if not exists runs(id text primary key,status text,payload text,result text,correlation_id text,created real,updated real)"); self.db.execute("create table if not exists quarantine(id integer primary key,errors text,correlation_id text,created real)"); self.db.commit()
    def create(self,payload,cid):
        rid=str(uuid.uuid4()); now=time.time(); self.db.execute("insert into runs values(?,?,?,?,?,?,?)",(rid,"pending",json.dumps(payload),None,cid,now,now)); self.db.commit(); return rid
    def update(self,rid,status,result=None): self.db.execute("update runs set status=?,result=?,updated=? where id=?",(status,json.dumps(result) if result else None,time.time(),rid)); self.db.commit()
    def get(self,rid):
        r=self.db.execute("select id,status,correlation_id,created,updated,result from runs where id=?",(rid,)).fetchone();
        if not r:return None
        return {"run_id":r[0],"status":r[1],"correlation_id":r[2],"created_at":r[3],"updated_at":r[4],"result":json.loads(r[5]) if r[5] else None}
    def quarantine(self,errors,cid): self.db.execute("insert into quarantine(errors,correlation_id,created) values(?,?,?)",(json.dumps(errors),cid,time.time())); self.db.commit()

