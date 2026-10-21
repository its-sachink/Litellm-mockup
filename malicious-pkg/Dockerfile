FROM python:3.11-slim

WORKDIR /pkg
COPY litellm_evil/ /pkg/litellm_evil/
COPY setup.py install.py /pkg/

# Install the fake package
RUN pip install --no-index /pkg

# Manually place cook.pth, cook.py, sitecustomize.py into site-packages
# (mirrors what the real malicious wheel does)
RUN python /pkg/install.py

# Verify the files are in place
RUN python -c "import site; import os; sp=site.getsitepackages()[0]; \
    print('site-packages:', sp); \
    print('files:', [f for f in os.listdir(sp) if f in ('cook.pth','cook.py','sitecustomize.py')])"

# Keep the container alive so we can exec into it
CMD ["python", "-c", "import time; print('victim container running'); time.sleep(86400)"]
