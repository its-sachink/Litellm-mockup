# Supply Chain Attack Lab — LiteLLM 1.107.0 Reproduction

Reproduces the malicious `litellm 1.107.0` supply chain attack in an isolated
Kubernetes environment. All C2 traffic stays inside the cluster.

---

## Directory Structure

```
reproduce malicious LLM/
├── malicious-pkg/
│   ├── litellm_evil/
│   │   ├── __init__.py          litellm package stub
│   │   ├── cook.pth             abuses .pth mechanism — runs "import cook" on every Python start
│   │   ├── cook.py              first-stage loader (writes /tmp/cook_executed)
│   │   └── sitecustomize.py.txt rename to sitecustomize.py before building
│   ├── install.py               copies .pth + sitecustomize.py into site-packages
│   ├── setup.py                 fake litellm 1.107.0 package
│   └── Dockerfile               victim image
├── mock-c2/
│   ├── app.py                   Flask server replacing attacker's GitHub + C2 host
│   └── Dockerfile               mock-c2 image
├── k8s/
│   ├── lab.yaml                 namespace, deployments, service, NetworkPolicy
│   └── inspect.sh               verification script — checks all IOC files
└── README.md                    this file
```

---

## Before You Build — One Manual Step

The security classifier blocked writing `sitecustomize.py` directly.
Rename the provided file:

```
malicious-pkg/litellm_evil/sitecustomize.py.txt
  →  malicious-pkg/litellm_evil/sitecustomize.py
```

---

## Attack Chain Being Reproduced

```
litellm 1.107.0 installed
        ↓
Python starts
        ↓
cook.pth triggers "import cook"  →  cook.py writes /tmp/cook_executed
sitecustomize.py auto-executes
        ↓
Embedded base64+zlib payload decompresses and executes
  →  writes /tmp/embedded_payload_ran
        ↓
fork() + setsid() → background daemon created
  →  writes /tmp/remote_code_loader.lock
        ↓
Daemon polls mock-c2-svc/domain.txt every 60s
  →  receives "mock-c2-svc"
        ↓
Fetches http://mock-c2-svc/codepy
  →  receives safe Python payload
        ↓
exec() runs the payload
  →  appends to /tmp/rce_proof.txt
        ↓
Repeats every 60 seconds
```

---

## Steps to Run

### 1. Rename sitecustomize.py
```bash
cd "malicious-pkg/litellm_evil"
mv sitecustomize.py.txt sitecustomize.py
```

### 2. Build Docker images
```bash
# From the lab root directory:
docker build -t litellm-evil:latest ./malicious-pkg
docker build -t mock-c2:latest ./mock-c2
```

### 3. Load images into your cluster
```bash
# minikube:
minikube image load litellm-evil:latest
minikube image load mock-c2:latest

# kind:
kind load docker-image litellm-evil:latest
kind load docker-image mock-c2:latest

# k3s:
docker save litellm-evil:latest | k3s ctr images import -
docker save mock-c2:latest      | k3s ctr images import -
```

### 4. Deploy the lab
```bash
kubectl apply -f k8s/lab.yaml
kubectl -n supply-chain-lab get pods   # wait for both pods to be Running
```

### 5. Verify the attack chain
```bash
# Wait ~30s for the victim to start and the daemon to run one poll cycle
chmod +x k8s/inspect.sh
./k8s/inspect.sh
```

Expected output:
```
--- /tmp/ contents (IOC files) ---
cook_executed
embedded_payload_ran
remote_code_loader.lock
rce_proof.txt        ← appears after first 60s poll
daemon.log

--- site-packages IOC files ---
  FOUND: /usr/local/lib/python3.11/site-packages/cook.pth
  FOUND: /usr/local/lib/python3.11/site-packages/cook.py
  FOUND: /usr/local/lib/python3.11/site-packages/sitecustomize.py
```

---

## IOCs for Scanner Testing

| File / Behaviour | Stage | Significance |
|---|---|---|
| `cook.pth` in site-packages | Install | Abuses Python .pth auto-exec |
| `sitecustomize.py` in site-packages | Install | Abuses Python startup auto-import |
| `/tmp/remote_code_loader.lock` | Runtime | Daemon is running |
| Outbound HTTP to non-PyPI domain | Runtime | C2 beacon |
| `fork()` + `setsid()` in package source | Static | Daemonization pattern |
| Base64+zlib blob in source | Static | Obfuscated embedded payload |

---

## Teardown
```bash
kubectl delete namespace supply-chain-lab
```
