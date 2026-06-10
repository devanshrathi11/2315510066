# Stage 1

## REST API Design

For the core actions, here is the API contract:

### 1. Fetch User Notifications
**Endpoint:** `GET /api/v1/notifications`
**Headers:** `{"Authorization": "Bearer <token>"}`

**Response (200 OK):**
{
  "notifications": [
    {
      "id": "uuid",
      "type": "event",
      "message": "Campus fest tomorrow",
      "isRead": false,
      "createdAt": "2026-06-10T10:00:00Z"
    }
  ]
}

### 2. Mark Notification as Read
**Endpoint:** `PATCH /api/v1/notifications/{id}/read`
**Headers:** `{"Authorization": "Bearer <token>", "Content-Type": "application/json"}`

**Request:**
{
  "isRead": true
}

**Response (200 OK):**
{
  "success": true
}

## Real-time Mechanism
For real-time updates, WebSockets are definitely the way to go. Once a student logs in, the client opens a persistent WebSocket connection. When an event fires (like a placement result), the server just pushes the payload down the socket. This way, the UI updates instantly and we don't have to hammer the database with polling requests.

# Stage 2

## Database Choice
I'd pick PostgreSQL for this. Notifications have a pretty strict, predictable structure, and a relational DB gives us those solid ACID guarantees to make sure read/write states are accurate. 

## Schema Design
**Table: notifications**
- `id` (UUID, Primary Key)
- `student_id` (Integer, Indexed for fast lookups)
- `type` (Enum: Placement, Event, Result)
- `message` (Text)
- `is_read` (Boolean, Default: false)
- `created_at` (Timestamp, Indexed for sorting)

## Scaling Solutions
When we start hitting millions of rows, reads will definitely slow down. To fix that:
1. **Partitioning:** We can partition the table by month so the DB only scans smaller chunks of data at a time.
2. **Archiving:** Move old, unneeded notifications (like anything over 6 months old) to cold storage or an S3 bucket.
3. **Read Replicas:** Route all the heavy `GET` requests to a read-only replica database to take the load off our primary write DB.

## Queries
**Fetch unread:**
SELECT id, type, message, created_at FROM notifications WHERE student_id = 123 AND is_read = false;

**Update read state:**
UPDATE notifications SET is_read = true WHERE id = 'uuid';

# Stage 3

## Query Analysis
The query technically works, but it's doing a full table scan, which is why it's so slow. It's checking all 5 million rows to find matches for that specific student. Also, doing a `SELECT *` is pulling down unneeded data, which wastes memory and network bandwidth. The computation cost is basically O(N).

## Indexing Advice
The other developer's advice to index *every* column is a pretty bad idea. Sure, reads might get faster, but every time we insert a new notification, the DB has to update multiple index trees. It'll tank our write performance and eat up a ton of disk space. We should only index columns we actually use in WHERE, JOIN, or ORDER BY clauses (like `student_id` and `created_at`).

## Target Query
SELECT DISTINCT student_id 
FROM notifications 
WHERE notification_type = 'Placement' 
AND created_at >= NOW() - INTERVAL '7 days';

# Stage 4

## High Load Performance Solutions
Hitting the database every single time a page loads will definitely overwhelm the system. Here is how I'd fix it:

1. **Add a Redis Cache:** We can store a user's recent unread notifications in Redis. When they load the page, the API grabs it from memory in milliseconds. We only hit the actual DB if there's a cache miss.
*The tradeoff:* Cache invalidation is tricky. We have to make sure the cache updates immediately when a new notification arrives, otherwise users will see stale data.

2. **Pagination and Limits:**
We shouldn't fetch all notifications at once anyway. We should just fetch the top 10 or 20 using `LIMIT 10 OFFSET 0`. 
*The tradeoff:* Users have to explicitly click "load more" or scroll down to trigger the next fetch.

# Stage 5

## Implementation Shortcomings
Doing this synchronously in a giant loop is a recipe for disaster. If the `send_email` API times out or fails on the 200th student, the loop crashes, and the remaining 49,800 students get nothing. Plus, waiting for external APIs to respond one by one will take forever. Email sending and DB saves shouldn't be coupled together like this.

## Redesign Strategy
The best way to fix this is to decouple the email sending from the database inserts using a message broker (like RabbitMQ or AWS SQS). The main function should just dump jobs into a queue and return instantly. Then, independent background workers can pick up those jobs, update the DB, and try sending the email. If the email fails, the worker just puts it back in a retry queue.

## Revised Pseudocode
function notify_all(student_ids, message):
    # Just push to the queue, don't wait for emails to send
    for student_id in student_ids:
        job = { "student_id": student_id, "message": message }
        message_broker.publish("notification_queue", job)

function worker_process_job(job):
    # Background worker handles the heavy lifting
    save_to_db(job.student_id, job.message)
    push_to_app(job.student_id, job.message)
    
    try:
        send_email(job.student_id, job.message)
    except EmailFailure:
        # If email fails, try again later without breaking the app
        message_broker.publish("retry_queue", job)