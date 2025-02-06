# Elasticsearch

## Introduction

Many system design problems will involve some aspect of search and retrieval: I've got a lot of "things" and I want to be able to find the right one(s). While most database systems are pretty good at this (e.g. Postgres with a full-text index is sufficient for many problems!), at a certain scale or level of sophistication you'll want to bring out a purpose-built system. And usually this involves a lot of similar requirements like sorting, filtering, ranking, faceting, etc. Enter one of the most well-known search engines: **Elasticsearch**.

From an interview perspective, this deep dive will tackle two different angles to understanding Elasticsearch:

1. First, you'll learn how to _use_ Elasticsearch. This will give you a powerful tool for your arsenal. Rarely are you going to find a search and retrieval question which is too complex for Elasticsearch. If you're interviewing for a startup or interviewing at a product architecture-style interview, knowing Elasticsearch will help. You can skip this section if you've used it before!
2. Secondly, you'll learn how Elasticsearch _works_ under the hood. As an incredible piece of distributed systems engineering, Elasticsearch brings together a lot of different concepts which can be used even outside search and retrieval problems. And some gnarly interviewers (I'm not the only one, I promise!) might ask you to pretend Elasticsearch doesn't exist and explain some of the top-level concepts yourself. This is more common for infra- heavy roles, particularly at cloud companies.

Elasticsearch is an enormous project built over more than a decade so there's a ton of features and functionality that we won't cover here, but we'll try to cover important bits in as we dig all the way in to this project. Off we go.