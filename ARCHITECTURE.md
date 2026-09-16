# Architecture decisions

## 1. Windows is the bridge

The first deployment assumes the enterprise work is primarily on desktop files and systems, while the Android device is the physical/mobile execution surface.

## 2. ARTEMIS is an execution adapter

NahaLabs owns jobs, business context, policy, auditing and reporting. ARTEMIS receives only the mobile task needed to execute a job.

## 3. Cloud-independent first

The prototype uses SQLite behind a small repository boundary. The intended production swap is Supabase/Postgres + object storage + Cloudflare Workers or a FastAPI service hosted on a free/low-cost platform.

## 4. Human approval boundary

The MVP does not automatically perform financial transactions, destructive actions, credential changes or irreversible business actions. Those will require explicit policy gates later.
