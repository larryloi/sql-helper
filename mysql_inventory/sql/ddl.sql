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




CREATE TABLE my_orders (
    id BIGINT AUTO_INCREMENT NOT NULL,
    order_id VARCHAR(36) NOT NULL,
    supplier_id INT NOT NULL,
    item_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    qty INT NOT NULL,
    net_price INT NOT NULL,
    tax_rate FLOAT NOT NULL,
    issued_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    spec VARCHAR(1024) NULL,
    created_at DATETIME NULL,
    updated_at DATETIME NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE INDEX IDX_my_orders_issued_at ON my_orders (issued_at);
CREATE UNIQUE INDEX IDX_my_orders_order_id ON my_orders (order_id);
CREATE INDEX IDX_my_orders_completed_at ON my_orders (completed_at);
CREATE INDEX IDX_my_orders_created_at ON my_orders (created_at);
CREATE INDEX IDX_my_orders_updated_at ON my_orders (updated_at);