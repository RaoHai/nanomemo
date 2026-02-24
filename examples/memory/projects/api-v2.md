---
summary: "API v2 - Complete redesign with GraphQL, microservices, improved performance"
created: 2026-01-10
updated: 2026-02-24
status: in-progress
tags: [project, backend, api]
related: [people/alice.md, infra/production.md]
---

# API v2 Redesign

## Overview
Complete redesign of the API layer to improve performance, maintainability, and developer experience. Moving from REST to GraphQL with microservices architecture.

## Status
In progress - 60% complete, on track for Q2 2026 launch

## Goals
- Reduce average response time from 200ms to <50ms
- Improve type safety with GraphQL schema
- Enable independent service deployment
- Better error handling and observability

## Key Decisions
- **GraphQL over REST**: Better client flexibility, reduced over-fetching
- **TypeScript throughout**: Type safety from schema to implementation
- **Event-driven architecture**: Services communicate via message queue
- **Incremental rollout**: Shadow traffic testing before full migration

## Technical Details
- **Stack**: Node.js, TypeScript, Apollo Server, PostgreSQL, Redis, RabbitMQ
- **Architecture**: API Gateway → GraphQL → Microservices → Databases
- **Key Files**:
  - `services/gateway/` - API gateway and GraphQL schema
  - `services/auth/` - Authentication service
  - `services/users/` - User management service
  - `services/content/` - Content delivery service

## Progress
- [x] Architecture design and RFC
- [x] GraphQL schema definition
- [x] Authentication service migration
- [x] User service migration
- [ ] Content service migration (in progress)
- [ ] Shadow traffic testing
- [ ] Performance benchmarking
- [ ] Full production rollout

## Blockers
- Content service migration blocked on database schema changes (ETA: 2026-03-01)
- Need infrastructure team approval for additional Redis instances

## Next Steps
1. Complete content service migration
2. Set up shadow traffic testing environment
3. Run load tests and optimize bottlenecks
4. Prepare rollback plan
5. Schedule gradual rollout starting with 5% traffic

## Notes
- Alice Chen is the technical lead
- Weekly sync meetings on Mondays at 2pm
- Performance targets based on user research showing 50ms threshold for "instant" feel
- Monitoring dashboard: https://grafana.internal/api-v2
