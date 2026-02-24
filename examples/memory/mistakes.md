---
summary: "Common mistakes and lessons learned"
updated: 2026-02-24
tags: [mistakes, lessons]
---

# Mistakes Log

## worker-memory-leak
**Date**: 2026-02-24
**Context**: API v2 content service staging deployment

### What Happened
Worker threads processing large file uploads were not releasing memory after completion. Memory usage grew from 200MB to 2GB over 24 hours, causing OOM crashes.

### Root Cause
Node.js worker threads don't automatically garbage collect when:
1. Parent thread holds references to worker objects
2. Large buffers are passed via `postMessage()` without transfer
3. Worker isn't explicitly terminated

### Solution
```javascript
// Before (leaky)
const worker = new Worker('./processor.js');
worker.postMessage({ buffer: largeBuffer });

// After (fixed)
const worker = new Worker('./processor.js');
worker.postMessage({ buffer: largeBuffer }, [largeBuffer.buffer]); // Transfer ownership
worker.on('message', (result) => {
  worker.terminate(); // Explicit cleanup
  worker = null;
});
```

### Lesson
Always:
- Transfer ArrayBuffer ownership when passing to workers
- Explicitly terminate workers after use
- Monitor memory usage in staging before production
- Set up memory leak detection in CI

### Related
- [Daily log: 2026-02-24](daily/2026-02-24.md)
- [Project: API v2](projects/api-v2.md)

---

## cors-config-mismatch
**Date**: 2026-02-24
**Context**: API v2 staging deployment

### What Happened
Frontend couldn't make requests to staging API - all requests blocked by CORS policy.

### Root Cause
Staging environment CORS config only allowed `localhost:3000`, but frontend staging runs on `staging.example.com`.

### Solution
Updated CORS config to use environment-specific allowed origins:
```javascript
const allowedOrigins = {
  development: ['http://localhost:3000'],
  staging: ['https://staging.example.com'],
  production: ['https://example.com']
};
```

### Lesson
- Always test with actual staging URLs, not localhost
- Use environment-specific configs for CORS
- Add CORS config validation to deployment checklist

---

## Template for New Entries

```markdown
## short-identifier
**Date**: YYYY-MM-DD
**Context**: Brief context

### What Happened
Description of the mistake

### Root Cause
Why it happened

### Solution
How it was fixed (with code if relevant)

### Lesson
What to do differently next time

### Related
- [Link to related files]
```
