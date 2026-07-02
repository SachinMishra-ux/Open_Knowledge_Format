---
type: Database Table
title: 'Table: catalog_products'
description: Auto-generated schema and relationships metadata for table catalog_products.
resource: mysql+pymysql://***@mysql-34425d40-sachin19566-5236.g.aivencloud.com:16512/defaultdb/catalog_products
tags:
- database
- table
- sql
timestamp: '2026-07-02T13:39:19.603633'
columns:
- name: catalog_id
  type: INTEGER
  nullable: false
  default: null
  primary_key: true
  foreign_key:
    table: catalogs
    column: id
- name: product_id
  type: INTEGER
  nullable: false
  default: null
  primary_key: true
  foreign_key:
    table: products
    column: id
database_name: defaultdb
schema_name: default
---

# Table: catalog_products

## Schema Information

| Column | Type | Primary Key? | Nullable? | Default | Foreign Key Reference |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `catalog_id` | `INTEGER` | 🔑 Yes | No |  | 🔗 references [catalogs](catalogs.md)(`id`) |
| `product_id` | `INTEGER` | 🔑 Yes | No |  | 🔗 references [products](products.md)(`id`) |

## Relationships

- Columns `(catalog_id)` reference [catalogs](catalogs.md) `(id)`
- Columns `(product_id)` reference [products](products.md) `(id)`