import json

import agent

result = agent.run_agent("What time is it, and what's 23 * 47?")
print(json.dumps(result["messages"], indent=2))