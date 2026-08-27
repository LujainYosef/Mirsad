# SECURITY_RULES.md

## Security Rules

- Never expose secrets, credentials, API keys, tokens, private keys, or sensitive configuration values.
- Never hard-code secrets in source code.
- Always use environment variables or an approved secret-management system for secrets.
- Never generate insecure SQL or code vulnerable to SQL injection.
- Always use parameterized queries or safe ORM/database APIs.
- Always validate and sanitize user input at appropriate trust boundaries.
- Never trust client-side validation alone; validate security-sensitive input on the server.
- Never store passwords in plain text.
- Always use strong, industry-standard password hashing for stored passwords.
- Never log passwords, tokens, API keys, session identifiers, or other sensitive secrets.
- Never reveal stack traces, internal paths, database details, or implementation-sensitive errors to end users.
- Return safe, user-facing error messages while keeping detailed diagnostics in protected server-side logs.
- Apply least-privilege access to users, services, databases, files, and APIs.
- Never grant broader permissions than required for a task.
- Always authenticate and authorize security-sensitive operations.
- Never rely on obscurity as the primary security control.
- Use secure defaults for authentication, authorization, sessions, storage, and network communication.
- Protect sensitive data both in transit and at rest where appropriate.
- Never disable security controls merely to make development or testing easier.
- Validate uploaded files, including type, size, content, and storage location, before processing them.
- Prevent path traversal, command injection, XSS, CSRF, SSRF, and other common injection or request-forgery vulnerabilities.
- Do not construct shell commands from untrusted input without strict validation and safe APIs.
- Keep dependencies and frameworks updated and avoid known-vulnerable components.
- Do not expose unnecessary services, ports, endpoints, debug modes, or administrative functionality.
- Fail securely when authentication, authorization, validation, or security checks cannot be completed.
- Treat security findings as high priority and document their impact, likelihood, and remediation.
