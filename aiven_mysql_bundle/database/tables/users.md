---
type: Database Table
title: 'Table: users'
description: Auto-generated schema and relationships metadata for table users.
resource: mysql+pymysql://***@mysql-34425d40-sachin19566-5236.g.aivencloud.com:16512/defaultdb/users
tags:
- database
- table
- sql
timestamp: '2026-07-02T13:39:20.125090'
columns:
- name: id
  type: INTEGER
  nullable: false
  default: null
  primary_key: true
  foreign_key: null
- name: name
  type: VARCHAR(120)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: email
  type: VARCHAR(200)
  nullable: false
  default: null
  primary_key: false
  foreign_key: null
- name: phone
  type: VARCHAR(20)
  nullable: true
  default: null
  primary_key: false
  foreign_key: null
- name: loyalty_tier
  type: ENUM
  nullable: true
  default: '''Bronze'''
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

# Table: users

## Schema Information

| Column | Type | Primary Key? | Nullable? | Default | Foreign Key Reference |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INTEGER` | 🔑 Yes | No |  |  |
| `name` | `VARCHAR(120)` |  | No |  |  |
| `email` | `VARCHAR(200)` |  | No |  |  |
| `phone` | `VARCHAR(20)` |  | Yes |  |  |
| `loyalty_tier` | `ENUM` |  | Yes | `'Bronze'` |  |
| `created_at` | `DATETIME` |  | Yes | `CURRENT_TIMESTAMP` |  |