from app.ara import ARA

ara = ARA()

print("\n===== STATUS =====")
print(ara.status())

print("\n===== PROCESS =====")
response = ara.process("Open Chrome")

print(response)