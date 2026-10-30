import os, time, uuid
from locust import HttpUser, between, task

class PetitionUser(HttpUser):
    wait_time=between(0.2,1.0)
    complete_run_slo_ms=int(os.getenv("COMPLETE_RUN_SLO_MS","10000"))

    @task
    def submit_and_poll(self):
        payload={"category":"attendance","description":"Documented medical attendance shortfall","attendance_percentage":72,"prescribed_minimum":80,"medical_documented":True,"condonation_requested":True}
        key="locust-"+uuid.uuid4().hex
        started=time.perf_counter()
        with self.client.post("/api/petitions",json=payload,headers={"Idempotency-Key":key},name="submit petition",catch_response=True) as response:
            if response.status_code != 202: response.failure(f"submit status {response.status_code}"); return
            run_id=response.json()["run_id"]
        while time.perf_counter()-started < self.complete_run_slo_ms/1000:
            status=self.client.get(f"/api/runs/{run_id}",name="poll status")
            if status.status_code != 200: break
            if status.json()["status"] in {"completed","escalated","failed"}:
                self.client.get(f"/api/runs/{run_id}/result",name="get result")
                return
            time.sleep(0.1)
