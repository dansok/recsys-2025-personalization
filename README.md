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
docker compose up -d clickhouse mlflow
recsys schema apply
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
