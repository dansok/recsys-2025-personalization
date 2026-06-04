# RecSys 2025 Behavioral Personalization

This project uses the Synerise RecSys Challenge 2025 dataset to build a production-style behavioral personalization system. The thesis is different from ESCI: instead of judged query-product relevance, this dataset contains user behavior over time and supports preference learning, propensity prediction, churn modeling, and personalized ranking.

## Why This Dataset

RecSys 2025 includes six months of real online-retailer behavior:

- `product_buy`
- `add_to_cart`
- `remove_from_cart`
- `page_visit`
- `search_query`
- product attributes: category, price bucket, quantized name embedding

The official challenge asks competitors to create Universal Behavioral Profiles: dense user representations used across churn, category propensity, product propensity, and hidden tasks.

Sources:

- [Dataset page](https://recsys.synerise.com/data-set)
- [Challenge repository](https://github.com/Synerise/recsys2025)

## Project Direction

The first MVP will compare:

- popularity baseline
- user category/price preference baseline
- co-occurrence recommender
- from-scratch matrix factorization / BPR
- LightGBM propensity ranker
- optional neural user profile model

Model implementations live under `src/recsys_personalization/models/`. The intent is to implement core recommenders from scratch, keep them importable and testable as library code, and benchmark them through shared training/evaluation harnesses.

```text
src/recsys_personalization/models/
  popularity.py
  item_nearest_neighbors.py
  matrix_factorization.py
  bayesian_personalized_ranking.py
  alternating_least_squares.py
  factorization_machine.py
  lightgbm_ranker.py

src/recsys_personalization/training/
  train_popularity.py
  train_item_nearest_neighbors.py
  train_matrix_factorization.py
  train_bayesian_personalized_ranking.py
  train_alternating_least_squares.py
  train_factorization_machine.py
  train_lightgbm_ranker.py

src/recsys_personalization/evaluation/
  ranking.py
  benchmark.py
```

Metrics:

- MAP@K
- Recall@K
- AUROC for churn/propensity tasks
- novelty/diversity where appropriate
- training time and inference latency

## Local Setup

```bash
make install
cp .env.example .env
make start
.venv/bin/recsys schema apply
```

MLflow UI: [http://localhost:5002](http://localhost:5002)

ClickHouse UI: [http://localhost:8124/play?theme=dark](http://localhost:8124/play?theme=dark)

ClickHouse HTTP API: [http://localhost:8124](http://localhost:8124)

`make start` starts the local Docker services, waits for MLflow and ClickHouse, prints the UI URLs, and opens both browser tabs on macOS. Use `OPEN_UI=0 make start` if you want to start services without opening browser tabs. Use `make open-uis` to reopen the local UI tabs later.

### ClickHouse UI Queries

The ClickHouse browser UI may default to a database other than `recsys2025`, so prefer fully qualified table names:

```sql
SHOW TABLES FROM recsys2025;
```

```sql
SELECT
    name,
    total_rows,
    formatReadableSize(total_bytes) AS size
FROM system.tables
WHERE database = 'recsys2025'
ORDER BY total_bytes DESC;
```

```sql
SELECT
    event_type,
    count() AS events,
    uniqExact(client_id) AS users,
    uniqExact(sku) AS products,
    min(timestamp) AS first_seen,
    max(timestamp) AS last_seen
FROM recsys2025.product_events
GROUP BY event_type
ORDER BY events DESC;
```

```sql
SELECT
    category,
    count() AS products,
    min(price) AS min_price_bucket,
    max(price) AS max_price_bucket,
    avg(price) AS avg_price_bucket
FROM recsys2025.product_properties
GROUP BY category
ORDER BY products DESC
LIMIT 25;
```

```sql
SELECT
    client_id,
    count() AS searches,
    anyLast(query) AS latest_query
FROM recsys2025.search_queries
GROUP BY client_id
ORDER BY searches DESC
LIMIT 25;
```

```sql
SELECT
    feature_set,
    count() AS users,
    avg(buy_count) AS avg_buys,
    avg(search_count) AS avg_searches,
    avg(unique_categories) AS avg_categories
FROM recsys2025.user_features
GROUP BY feature_set
ORDER BY users DESC;
```

Download the preprocessed challenge dataset:

```bash
recsys download --destination data/raw/recsys2025
```

The official page lists the preprocessed download at about 1.3 GB and recommends using it with the challenge code. The downloaded archive is `challenge_dataset.tar.gz`.

## Personalized Demo

Run a local frontend that lets you assume a validation-set user role and rank products according to that user's inferred behavior profile:

```bash
uvicorn recsys_personalization.api:app --reload --port 8010
```

Open [http://localhost:8010](http://localhost:8010).

The dataset anonymizes product names and search queries as numeric-token strings, so the UI supports filters such as `category:3398`, `sku:52586`, or numeric query tokens. Results are personalized by category affinity, price affinity, recent query-token overlap, and prior product interactions.
