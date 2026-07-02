---
type: Database Table
title: 'Table: orders'
description: Auto-generated schema and relationships metadata for table orders.
resource: mysql+pymysql://***@mysql-34425d40-sachin19566-5236.g.aivencloud.com:16512/defaultdb/orders
tags:
- database
- table
- sql
timestamp: '2026-07-02T13:39:19.900807'
columns:
- name: id
  type: INTEGER
  nullable: false
  default: null
  primary_key: true
  foreign_key: null
- name: user_id
  type: INTEGER
  nullable: false
  default: null
  primary_key: false
  foreign_key:
    table: users
    column: id
- name: product_id
  type: INTEGER
  nullable: false
  default: null
  primary_key: false
  foreign_key:
    table: products
    column: id
- name: quantity
  type: TINYINT
  nullable: false
  default: '''1'''
  primary_key: false
  foreign_key: null
- name: total_price
  type: DECIMAL(10, 2)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: status
  type: ENUM
  nullable: true
  default: '''Pending'''
  primary_key: false
  foreign_key: null
- name: order_date
  type: DATETIME
  nullable: true
  default: CURRENT_TIMESTAMP
  primary_key: false
  foreign_key: null
database_name: defaultdb
schema_name: default
---

# Table: orders

## Schema Information

| Column | Type | Primary Key? | Nullable? | Default | Foreign Key Reference |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INTEGER` | 🔑 Yes | No |  |  |
| `user_id` | `INTEGER` |  | No |  | 🔗 references [users](users.md)(`id`) |
| `product_id` | `INTEGER` |  | No |  | 🔗 references [products](products.md)(`id`) |
| `quantity` | `TINYINT` |  | No | `'1'` |  |
| `total_price` | `DECIMAL(10, 2)` |  | No |  |  |
| `status` | `ENUM` |  | Yes | `'Pending'` |  |
| `order_date` | `DATETIME` |  | Yes | `CURRENT_TIMESTAMP` |  |

## Relationships

- Columns `(user_id)` reference [users](users.md) `(id)`
- Columns `(product_id)` reference [products](products.md) `(id)`