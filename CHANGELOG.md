# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-11

First public release: the **catalogue** stage of ChatCloset.

### Added

- FastAPI application serving a JSON API under `/api` and the static storefront under `/` from a single process.
- `GET /api/products` with optional `category` (`men`, `women`, `kids`), `min_price` and `max_price` filters,
  validated by Pydantic (`422` on invalid input) and documented at `/docs`.
- MongoDB access through an injectable `get_db` dependency, configured by `MONGO_URI` / `MONGO_DB`
  (local MongoDB or Atlas).
- Deterministic demo catalogue of 120 products (40 per category), seeded automatically into an empty database.
- 120 real product photos (WebP, generated once with the OpenAI Image API), with an offline SVG fallback.
- `scripts/generate_product_images.py`: a resumable photo generator with dry-run, a cost estimate and confirmation.
- Vanilla JS storefront: category tabs, price-range filter, responsive grid, HTML-escaped rendering.
- API tests against an in-memory MongoDB (mongomock).
- Documentation: README, High-Level Design, Low-Level Design.
- Apache-2.0 license.

[Unreleased]: https://github.com/OWNER/chatcloset/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/OWNER/chatcloset/releases/tag/v1.0.0
