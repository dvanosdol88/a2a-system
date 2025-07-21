# User Acceptance Testing

The following criteria must be satisfied to pass UAT:

- The end-to-end test script exits with status `0` within 10 seconds.
- The AI Connector processes tasks from the Redis stream and writes completed
  results back to `a2a_stream_results`.
- The result field must exactly mirror the submitted task with no prefix.
