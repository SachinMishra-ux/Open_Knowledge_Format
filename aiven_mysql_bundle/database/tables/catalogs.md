---
type: Database Table
title: 'Table: catalogs'
description: Auto-generated schema and relationships metadata for table catalogs.
resource: mysql+pymysql://***@mysql-34425d40-sachin19566-5236.g.aivencloud.com:16512/defaultdb/catalogs
tags:
- database
- table
- sql
timestamp: '2026-07-02T13:39:19.762285'
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
- name: season
  type: ENUM
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: year
  type: YEAR
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: description
  type: TEXT
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: cover_image_url
  type: TEXT
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: launched_at
  type: DATE
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
database_name: defaultdb
schema_name: default
---

# Table: catalogs

## Schema Information

| Column | Type | Primary Key? | Nullable? | Default | Foreign Key Reference |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INTEGER` | 🔑 Yes | No |  |  |
| `name` | `VARCHAR(200)` |  | No |  |  |
| `season` | `ENUM` |  | No |  |  |
| `year` | `YEAR` |  | No |  |  |
| `description` | `TEXT` |  | Yes |  |  |
| `cover_image_url` | `TEXT` |  | Yes |  |  |
| `launched_at` | `DATE` |  | Yes |  |  |