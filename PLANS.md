# Issue #7: Draws and No Contests

## Milestone 1: Scrape and normalize outcomes
- Update the stats spider to follow fight detail links from event rows instead of green result badges.
- Add `fight_outcome` to the scraped stats item and derive it from the normalized red/blue result markers.
- Extend scraper tests to cover decisive, draw, and no-contest event rows and result normalization cases.

## Milestone 2: Preserve all bouts in processed outputs
- Extract the notebook cleaning pipeline into testable Python code.
- Keep `data/stats/stats_processed.csv` as the decisive-only winner/loser view.
- Add `data/stats/stats_processed_all_bouts.csv` as the full processed all-bouts dataset with `red/blue` columns and `fight_outcome`.
- Keep the merged scorecards dataset on the all-bouts raw stats path and carry `fight_outcome` into the merged CSV.

## Milestone 3: Regenerate datasets and validate
- Rescrape UFC Stats through the latest event available at implementation time.
- Rebuild processed and merged datasets from the refreshed raw stats export.
- Run targeted tests first, then the best available validation stack: lint-like checks if available, type-aware checks if available, pytest, and regeneration verification.
