CREATE TABLE inventory.suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE KEY (name, type)
);

CREATE INDEX idx_created_at ON suppliers (created_at);

CREATE INDEX idx_updated_at ON suppliers (updated_at);

CREATE INDEX suppliers_type_IDX USING BTREE ON suppliers (`type`);
