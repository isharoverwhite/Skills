# AMC Query Skill Context

## Directory Overview
This directory contains an AI Agent Skill focused on Amazon Marketing Cloud (AMC), specifically for Sponsored Ads (Vietnam). It acts as a knowledge base providing essential guidelines, SQL dialect rules (Apache Calcite), date range mechanics, and a collection of pre-defined SQL queries to accurately extract and analyze AMC data.

## Key Files
- `AMC_QUERY_SKILL.md`: The primary instruction set and reference document for this skill. It contains:
  - **AMC SQL Rules:** Critical limitations and required substitutions in AMC (e.g., avoiding `DATE()`, avoiding `SELECT *`, correctly aggregating `advertiser_id_internal`).
  - **Date Range Guide:** Vital instructions explaining that date filtering in AMC is handled via the UI Settings tab, NOT via SQL `WHERE` clauses.
  - **Skill Definitions:** A catalog of specific SQL skills (Skills 1-6) with pre-written queries for tasks like sales analysis, top ASINs, CTR/CVR performance, and add-to-cart analysis.
  - **Reference Tables:** A quick reference for available AMC tables (e.g., `amazon_attributed_events_by_conversion_time`) and their confirmed column names.

## Usage
AI agents operating within this directory must prioritize the instructions and constraints outlined in `AMC_QUERY_SKILL.md` when generating or reviewing SQL queries for Amazon Marketing Cloud.

**Crucial Agent Directives:**
- **Stateless Time:** NEVER use SQL-level date filtering (like `WHERE event_date = ...`). The SQL must be stateless regarding time. If a user asks for data from a specific timeframe, provide the stateless SQL and explicitly instruct the user to set the date range via the Query Editor UI Settings tab.
- **Dialect Strictness:** Strictly adhere to the SQL dialect limitations mentioned. Any violation will result in parse errors in AMC.
- **Column Validation:** Utilize the provided reference tables to ensure that only confirmed and properly aggregated columns are used in `SELECT` statements.