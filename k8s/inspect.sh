#!/usr/bin/env bash
# inspect.sh — run after deploying lab.yaml to verify the attack chain executed
NS="supply-chain-lab"
VICTIM=$(kubectl get pod -n $NS -l app=victim -o jsonpath='{.items[0].metadata.name}')

echo "=== Victim pod: $VICTIM ==="
echo ""

echo "--- /tmp/ contents (IOC files) ---"
kubectl exec -n $NS $VICTIM -- ls -la /tmp/

echo ""
echo "--- cook_executed (Step 1: .pth auto-exec) ---"
kubectl exec -n $NS $VICTIM -- cat /tmp/cook_executed 2>/dev/null || echo "NOT FOUND"

echo ""
echo "--- embedded_payload_ran (Step 2: base64+zlib embedded payload) ---"
kubectl exec -n $NS $VICTIM -- cat /tmp/embedded_payload_ran 2>/dev/null || echo "NOT FOUND"

echo ""
echo "--- remote_code_loader.lock (Step 3: daemon running) ---"
kubectl exec -n $NS $VICTIM -- cat /tmp/remote_code_loader.lock 2>/dev/null || echo "NOT FOUND"

echo ""
echo "--- rce_proof.txt (Step 4: remote payload executed) ---"
kubectl exec -n $NS $VICTIM -- cat /tmp/rce_proof.txt 2>/dev/null || echo "NOT FOUND (wait 60s for first poll)"

echo ""
echo "--- daemon.log (C2 polling activity) ---"
kubectl exec -n $NS $VICTIM -- cat /tmp/daemon.log 2>/dev/null || echo "NOT FOUND"

echo ""
echo "--- Running processes (daemon PID) ---"
kubectl exec -n $NS $VICTIM -- ps aux

echo ""
echo "--- site-packages IOC files ---"
kubectl exec -n $NS $VICTIM -- python -c \
  "import site, os; sp=site.getsitepackages()[0]; \
   iocs=['cook.pth','cook.py','sitecustomize.py']; \
   [print(f'  FOUND: {sp}/{f}') if os.path.exists(f'{sp}/{f}') else print(f'  missing: {f}') for f in iocs]"
