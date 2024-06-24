#!/usr/bin/env bash

uvicorn swift_api_graphql.app:app --port 8001 --reload
