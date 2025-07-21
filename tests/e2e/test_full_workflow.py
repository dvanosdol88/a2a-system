import time
import redis

# 1. Start the AI Connector (if not already running)
#    (Assume it's already running on localhost:6379)

# 2. Send a test task
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
task_id = r.xadd('a2a_stream', {'task': 'end-to-end test'})

# 3. Poll the results stream
start = time.time()
while time.time() - start < 10:
    entries = r.xreadgroup(
        'ai_group',
        'e2e_consumer',
        {'a2a_stream_results': '>'},
        count=1,
        block=1000,
    )
    if entries:
        for _, messages in entries:
            for _, data in messages:
                assert data['result'] == 'end-to-end test'
                assert data['status'] == 'completed'
                raise SystemExit(0)
raise AssertionError("E2E result not received in time")
