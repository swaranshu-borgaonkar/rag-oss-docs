# tbcontracts-mcp Package Overview

tbcontracts-mcp is an MCP (Model Context Protocol) server that enables token budget management across multi-agent LLM systems by wrapping the token-budget-contracts library.

## Core Functionality

The package solves a specific problem in multi-agent orchestration: uneven token consumption. When multiple agents (planner, researcher, writer, critic) operate simultaneously, high-priority agents may exhaust their budget while lower-priority ones remain idle. This tool addresses that by determining in real time how remaining budget should be reallocated based on agent priorities and current spending.

## Available Tools

register_agent: Establish an agent with priority weight and initial token allocation.
record_spend: Log token consumption; triggers automatic reallocation if budget is exceeded.
get_remaining_budget: Query an individual agent's current status.
request_reallocation: Execute priority-weighted budget borrowing logic and return a concrete reallocation plan.
get_budget_snapshot: Retrieve full system state as structured JSON.

All tools use strict input schemas and return structured JSON responses rather than free text, enabling programmatic parsing by orchestrators.

## Installation & Requirements

Install via: pip install tbcontracts-mcp
Requires Python 3.10+. The package pulls in token-budget-contracts>=0.3.0 and opentelemetry-api.

## Observability

Spend tracking emits through two channels: OpenTelemetry spans from the underlying library (enable via TBCONTRACTS_MCP_OTEL=1) and gen_ai.client.token.usage counters following emerging OTel semantic conventions.

## Scope Clarification

This tool handles allocation decisions only, it does not perform cross-provider cost tracking, network-level rate limiting, or serve as an observability dashboard itself.
