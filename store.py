import json
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
QUEUE = "jobs"
PROCESSING = "processing"

def run_key(run_id):
    return f"run:{run_id}"

def save_run(run):
    r.set(run_key(run["id"]), json.dumps(run))

def get_run(run_id):
    data = r.get(run_key(run_id))
    if data is None:
        return None
    return json.loads(data)

def enqueue(run_id):
    r.lpush(QUEUE, run_id)
    
def dequeue():
     return r.blmove(QUEUE, PROCESSING, 0, "RIGHT", "LEFT")

def ack(run_id):
    r.lrem(PROCESSING, 1, run_id)
    
def recover():
    count = 0
    while True:
        run_id = r.lmove(PROCESSING, QUEUE, "RIGHT", "RIGHT")
        if run_id is None:
            break
        count += 1
    return count

def checkpoint_key(run_id):
    return f"checkpoint: {run_id}"

def save_checkpoint(run_id, messages, steps):
    data = {"messages": messages, "steps": steps}
    r.set(checkpoint_key(run_id), json.dumps(data))

def get_checkpoint(run_id):
    data = r.get(checkpoint_key(run_id))
    if data is None:
        return None
    return json.loads(data)

def delete_checkpoint(run_id):
    r.delete(checkpoint_key(run_id))