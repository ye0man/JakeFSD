# Example: API to SQLite to CSV

This example fetches posts from a public REST API, loads them into SQLite, and exports the result to a CSV file.

## Files

- `pipeline.yaml` — the JakeFSD pipeline manifest

## Run

From this directory:

```bash
jakefsd run pipeline.yaml
```

The pipeline will:
1. Fetch posts from `https://jsonplaceholder.typicode.com/posts`
2. Load them into `data/posts.db` table `posts`
3. Write `reports/posts.csv`

## Requires internet

This example calls a live public API. Make sure you are online.

## Preview a stage

```bash
jakefsd preview pipeline.yaml --stage source
```
