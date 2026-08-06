# Zorathvael OS — Troubleshooting Guide

## Common Issues & Solutions

### Missing Environment Variables
If the application raises configuration errors, verify that your `.env` file is properly populated based on `.env.example`.

### Module Import Errors
Ensure that the `PYTHONPATH` includes the project root directory when executing scripts outside the root folder.
