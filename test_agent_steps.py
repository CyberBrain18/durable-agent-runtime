import agent


def show_progress(messages, steps):
    print(f"step finished: {len(steps)} tool call(s) so far, {len(messages)} messages")


result = agent.run_agent(
    "Do this one tool call at a time, never two at once. "
    "Step 1: get the current time. Step 2: calculate 23 * 47. Then tell me both.",
    on_step=show_progress,
)

print("answer:", result["answer"])