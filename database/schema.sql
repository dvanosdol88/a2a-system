-- A2A System Database Schema
-- Supports PostgreSQL and SQLite

-- Tasks table to replace tasks.json
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task TEXT NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_to VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    completed_at TIMESTAMP,
    metadata JSONB
);

-- API Keys table for authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    permissions JSONB
);

-- Request logs for monitoring and rate limiting
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id),
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_code INTEGER,
    response_time_ms INTEGER
);

-- System metrics for monitoring
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created ON tasks(created);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_request_logs_timestamp ON request_logs(timestamp);
CREATE INDEX idx_request_logs_api_key ON request_logs(api_key_id);
CREATE INDEX idx_system_metrics_name_timestamp ON system_metrics(metric_name, timestamp);