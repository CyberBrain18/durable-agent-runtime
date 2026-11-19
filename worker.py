from datetime import datetime, timezone
import store
from agent import run_agent
import time
SIMULATED_DELAY = 15   # TEMP: seconds to pause, so we can test crashes. Set to 0 to disable.
def now():
    return datetime.now(timezone.utc).isoformat()

def process(run_id):
    run = store.get_run(run_id)
    if run is None:
        print(f"[worker] run {run_id} not found, skipping")
        return
    
    if run["status"] in ("completed", "failed"):
        print(f"[worker] run {run_id} already finished, skipping")
        return
    
    checkpoint = store.get_checkpoint(run_id)
    if checkpoint is None:
        print(f"[worker] starting {run_id} fresh")
        messages, steps = None, None
    else:
        print(f"[worker] resuming {run_id} after {len(checkpoint['steps'])} tool call(s)") 
        messages, steps = checkpoint["messages"], checkpoint["steps"]
    
    run["status"] = "running"
    store.save_run(run)
    
    def save_progress(messages, steps):
        store.save_checkpoint(run_id, messages, steps)
        run["steps"] = steps
        store.save_run(run)
        print(f"[worker] checkpoint saved: {len(steps)} tool call(s) so far")    # NEW
        time.sleep(SIMULATED_DELAY) 

    try:
        result = run_agent(
            run["question"],
            messages=messages,
            steps=steps,
            on_step=save_progress,
        )
        run["answer"] = result["answer"]
        run["steps"] = result["steps"]
        run["status"] = "completed"
    except Exception as e:
        run["status"] = "failed"
        run["error"] = str(e)
        print(f"[worker] {run_id} failed: {e}") 
    
    run["finished_at"] = now()
    store.save_run(run)
    store.delete_checkpoint(run_id)                
    print(f"[worker] {run_id} -> {run['status']}")
    
def main():
    recovered = store.recover()
    print(f"[worker] recovered {recovered} unfinished job(s)")
    print("[worker] waiting for jobs...")
    while True:
        run_id = store.dequeue()
        process(run_id)
        store.ack(run_id)

if __name__ == "__main__":
    main()
        
