---
type: NoSQL Collection
title: 'Collection: UPI collection'
description: Auto-generated schema for collection UPI collection via schema inference.
resource: mongodb+srv://***@upicluster.trdgo4v.mongodb.net/?appName=UPICluster/upi_db/UPI
  collection
tags:
- mongodb
- nosql
- collection
timestamp: '2026-07-02T17:43:05.938078'
database_name: upi_db
collection_name: UPI collection
sample_size_used: 10
fields:
- name: _id
  types:
  - ObjectId
- name: transaction_id
  types:
  - str
- name: timestamp
  types:
  - str
- name: sender_bank
  types:
  - str
- name: receiver_bank
  types:
  - str
- name: amount
  types:
  - float
- name: status
  types:
  - str
- name: city
  types:
  - str
- name: state
  types:
  - str
---

# Collection: UPI collection

This collection contains JSON documents in the 'upi_db' MongoDB database.

## Inferred Schema (Sampled 10 documents)

| Field Path | Inferred Type(s) | Notes |
| :--- | :--- | :--- |
| `_id` | `ObjectId` | Primary Key (usually ObjectId) |
| `amount` | `float` |  |
| `city` | `str` |  |
| `receiver_bank` | `str` |  |
| `sender_bank` | `str` |  |
| `state` | `str` |  |
| `status` | `str` |  |
| `timestamp` | `str` |  |
| `transaction_id` | `str` |  |