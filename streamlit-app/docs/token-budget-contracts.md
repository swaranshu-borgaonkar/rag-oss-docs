# Token Budget Contracts - Full Description

## Overview

Token Budget Contracts (tbcontracts) is a Python library for priority-weighted, confidence-gated token budget governance in multi-agent LLM systems. It solves a critical problem: in systems with multiple AI agents, budget allocation is typically static, causing important agents to starve while less critical ones hoard unused resources.

## Core Problem & Solution

The library addresses inefficient token spending in multi-agent setups. Rather than hardcoding flat caps per agent, tbcontracts enables dynamic budget reallocation, allowing unused capacity to flow from lower-priority or idle agents to those currently needing it, in real time. It prevents budget from flowing uphill (from important to less important agents) and maintains minimum reserves for donor agents.

## Key Features

Priority-Weighted Allocation: Agents receive priority levels that determine budget borrowing hierarchy.

Confidence-Gated Spending: Once an agent reports a high-confidence result, further spending on that agent is automatically blocked, so you're not paying for retrieval the model didn't need.

Real-Time Reallocation: When an agent runs low, the system identifies donors starting with the lowest-priority, most-idle candidates, pulling only the shortfall needed.

Flexible Token Counting: Includes a built-in estimator or accepts exact usage data from LLM providers.

## Installation

pip install token-budget-contracts
For accurate tokenization: pip install "token-budget-contracts[accurate-tokenizer]"

## Basic Usage Example

from tbcontracts import BudgetManager
manager = BudgetManager()
manager.register_agent("researcher", priority=3, max_tokens=4000)
manager.register_agent("critic", priority=1, max_tokens=2000)

## Technical Details

Python Support: 3.9-3.12. License: MIT. Status: Alpha (v0.1.1). Author: Swaranshu Borgaonkar.

## Patent & Licensing

The implementation reflects governance methods described in U.S. Provisional Patent Application No. 64/081,925, filed June 3, 2026.
