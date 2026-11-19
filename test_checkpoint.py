import store

# 1. save a fake checkpoint
store.save_checkpoint("test-1", [{"role": "user", "content": "hi"}], [])

# 2. read it back
print("after save:", store.get_checkpoint("test-1"))

# 3. delete it and read again
store.delete_checkpoint("test-1")
print("after delete:", store.get_checkpoint("test-1"))