# Zorathvael OS — Deployment Guide

Zorathvael OS is engineered for flexible deployment across edge devices, desktops, and cloud servers. 

For server deployment, the system runs on a standard Python 3.12 environment with containerization support via Docker. Production deployments require setting secure environment variables through secret management systems rather than plain text `.env` files. Continuous deployment is handled via GitHub Actions upon merging to the main branch.
