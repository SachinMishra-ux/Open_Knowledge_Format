---
type: Database Table
title: 'Table: products'
description: Auto-generated schema and relationships metadata for table products.
resource: mysql+pymysql://***@mysql-34425d40-sachin19566-5236.g.aivencloud.com:16512/defaultdb/products
tags:
- database
- table
- sql
timestamp: '2026-07-02T13:39:20.011690'
columns:
- name: id
  type: INTEGER
  nullable: false
  default: null
  primary_key: true
  foreign_key: null
- name: name
  type: VARCHAR(200)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: brand
  type: VARCHAR(100)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: category
  type: VARCHAR(80)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: subcategory
  type: VARCHAR(80)
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: price
  type: DECIMAL(10, 2)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: discount_pct
  type: TINYINT
  nullable: true
  default: '''0'''
  primary_key: false
  foreign_key: null
- name: stock
  type: INTEGER
  nullable: true
  default: '''0'''
  primary_key: false
  foreign_key: null
- name: color
  type: VARCHAR(50)
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: size_range
  type: VARCHAR(80)
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: image_url
  type: TEXT
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: description
  type: TEXT
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: created_at
  type: DATETIME
  nullable: true
  default: CURRENT_TIMESTAMP
  primary_key: false
  foreign_key: null
database_name: defaultdb
schema_name: default
---

# Table: products

## Schema Information

| Column | Type | Primary Key? | Nullable? | Default | Foreign Key Reference |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INTEGER` | 🔑 Yes | No |  |  |
| `name` | `VARCHAR(200)` |  | No |  |  |
| `brand` | `VARCHAR(100)` |  | No |  |  |
| `category` | `VARCHAR(80)` |  | No |  |  |
| `subcategory` | `VARCHAR(80)` |  | Yes |  |  |
| `price` | `DECIMAL(10, 2)` |  | No |  |  |
| `discount_pct` | `TINYINT` |  | Yes | `'0'` |  |
| `stock` | `INTEGER` |  | Yes | `'0'` |  |
| `color` | `VARCHAR(50)` |  | Yes |  |  |
| `size_range` | `VARCHAR(80)` |  | Yes |  |  |
| `image_url` | `TEXT` |  | Yes |  |  |
| `description` | `TEXT` |  | Yes |  |  |
| `created_at` | `DATETIME` |  | Yes | `CURRENT_TIMESTAMP` |  |