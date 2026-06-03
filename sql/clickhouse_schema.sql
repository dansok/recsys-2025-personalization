CREATE DATABASE IF NOT EXISTS recsys2025;

CREATE TABLE IF NOT EXISTS recsys2025.product_events
(
    event_type LowCardinality(String),
    client_id UInt64,
    timestamp DateTime,
    sku UInt64,
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (event_type, client_id, timestamp, sku);

CREATE TABLE IF NOT EXISTS recsys2025.page_visits
(
    client_id UInt64,
    timestamp DateTime,
    url UInt64,
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (client_id, timestamp, url);

CREATE TABLE IF NOT EXISTS recsys2025.search_queries
(
    client_id UInt64,
    timestamp DateTime,
    query String,
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (client_id, timestamp);

CREATE TABLE IF NOT EXISTS recsys2025.product_properties
(
    sku UInt64,
    category UInt64,
    price UInt16,
    name String,
    ingested_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY sku;

CREATE TABLE IF NOT EXISTS recsys2025.user_features
(
    feature_set String,
    client_id UInt64,
    buy_count UInt32,
    add_to_cart_count UInt32,
    remove_from_cart_count UInt32,
    page_visit_count UInt32,
    search_count UInt32,
    unique_skus UInt32,
    unique_categories UInt32,
    avg_price_bucket Float32,
    days_since_last_buy Float32,
    generated_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (feature_set, client_id);

CREATE TABLE IF NOT EXISTS recsys2025.evaluation_runs
(
    run_id String,
    model_name String,
    feature_set String,
    task String,
    metric String,
    value Float64,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (run_id, model_name, task, metric);
