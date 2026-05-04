# ADR 0001: Cold Start Mitigation for Azure Students

## Status
Implemented

## Context
The project uses Azure App Service on the "Azure Students" (Free/F1) plan. This plan does not support the "Always On" feature, leading to "Cold Starts" where the backend container is idled after 20 minutes of inactivity. This causes the first request to take 30-60 seconds to respond, often leading to frontend timeouts or poor user experience.

## Decision
We will implement a dual-layer mitigation strategy:
1.  **Frontend Pre-warming**: The React frontend will fire a non-blocking `GET /api/health` request upon the initial load of the landing page. This triggers the Azure container startup process while the user is still reading the landing page content.
2.  **SSE Heartbeat**: To prevent the Azure Load Balancer from closing long-running analysis connections (SSE), the backend will send a `: keep-alive` comment every 15 seconds.

## Consequences
- **Pros**: Improved perceived performance for users; reduced "Connection Lost" errors during long analyses; zero additional cost.
- **Cons**: Slightly increased traffic to the backend; does not completely eliminate cold start if the user goes directly to a deep link.
