CREATE TABLE IF NOT EXISTS services (
    id VARCHAR(256),
    name VARCHAR(256),
    type VARCHAR(256),
    api_version VARCHAR(8),
    description VARCHAR(1024),
    url VARCHAR(512),
    contact_url VARCHAR(512),
    service_version VARCHAR(8),
    environment VARCHAR(16),
    organization VARCHAR(256),
    organization_url VARCHAR(512),
    organization_logo VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (id)
);

--Email for maintainer of service
CREATE TABLE hosts (
    service_id VARCHAR(256),
    email VARCHAR(256)
);

--Services that have been registered have individual service keys that are used for self-maintenance
--These service keys are used at PUT and DELETE /services endpoints
CREATE TABLE service_keys (
    service_id VARCHAR(64),
    service_key VARCHAR(128)
);

CREATE UNIQUE INDEX unique_service ON service_keys (service_id);

--Api key used in "Authorization" header at POST /services endpoint
CREATE TABLE api_keys (
    api_key VARCHAR(64),
    comment VARCHAR(256)
);

--Admin key used to poll /update/services endpoint
CREATE TABLE admin_keys (
    admin_key VARCHAR(64),
    comment VARCHAR(256)
);
