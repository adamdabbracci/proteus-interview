## Description

When I clone a project and then update tasks in the cloned copy, the changes also show up in the original project. This is causing real confusion on our team because we use a "Sprint Template" project that we clone at the start of each quarter, then update tasks as we work through them. But the template itself keeps getting modified even though we're only touching the clone.

## Steps to Reproduce

1. Start the server (`python run.py`)
2. Create a project called "Sprint Template":
   ```bash
   curl -X POST http://localhost:5000/api/projects \
     -H "Content-Type: application/json" \
     -d '{"name": "Sprint Template", "description": "Reusable quarterly template"}'
   ```
3. Add a couple of tasks to it:
   ```bash
   curl -X POST http://localhost:5000/api/projects/<project_id>/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Set up CI pipeline", "assignee": "alice", "labels": ["infra"]}'

   curl -X POST http://localhost:5000/api/projects/<project_id>/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Write integration tests", "assignee": "bob", "labels": ["testing"]}'
   ```
4. Clone it as "Q1 Sprint":
   ```bash
   curl -X POST http://localhost:5000/api/projects/<project_id>/clone \
     -H "Content-Type: application/json" \
     -d '{"name": "Q1 Sprint"}'
   ```
5. In "Q1 Sprint", mark the "Set up CI pipeline" task as done:
   ```bash
   curl -X PATCH http://localhost:5000/api/projects/<clone_id>/tasks/<task_id> \
     -H "Content-Type: application/json" \
     -d '{"status": "done"}'
   ```
6. Go back and view "Sprint Template":
   ```bash
   curl http://localhost:5000/api/projects/<project_id>
   ```

## Expected Behavior

The "Set up CI pipeline" task in "Sprint Template" should still show `status: "todo"` since I only changed it in "Q1 Sprint".

## Actual Behavior

The "Set up CI pipeline" task in "Sprint Template" shows `status: "done"` -- even though I never touched it directly. It's as if the clone and the original are linked somehow.

## Additional Notes

- Interestingly, adding a **new** task to the cloned project does NOT add it to the original (that part works fine)
- The problem only happens when you **modify** an existing task that was carried over from the original
- This happens 100% of the time -- it's not intermittent
- We noticed it because our Sprint Template kept getting "used up" after each quarter and we had to recreate it from scratch
