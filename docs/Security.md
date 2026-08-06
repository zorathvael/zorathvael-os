# Zorathvael OS — Security Documentation

Security is a primary pillar of Zorathvael OS. All API credentials and sensitive configurations are strictly externalized into environment variables and excluded from version control via `.gitignore`. Input validation is strictly enforced across all workflow steps to prevent injection vulnerabilities. Secret logging is disabled by default to protect user data privacy.
