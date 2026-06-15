# Deadlock API (v0.1.0)


## API Clients

We have auto generated and updated clients for many languages. You can find them here: [https://github.com/deadlock-api/openapi-clients](https://github.com/deadlock-api/openapi-clients)

## Support the Deadlock API

Whether you're building your own database, developing data science projects, or enhancing your website with game and player analytics, the Deadlock API has the data you need.

Your sponsorship helps keep this resource open, free and future-proof for everyone. By supporting the Deadlock API, you will enable continued development, new features and reliable access for developers, analysts and streamers worldwide.

Help us continue to provide the data you need - sponsor the Deadlock API today!

**-> You can Sponsor the Deadlock API on [Patreon](https://www.patreon.com/c/user?u=68961896) or [GitHub](https://github.com/sponsors/raimannma)**

## Disclaimer
_deadlock-api.com is not endorsed by Valve and does not reflect the views or opinions of Valve or anyone officially involved in producing or managing Valve properties. Valve and all associated properties are trademarks or registered trademarks of Valve Corporation_
        

---

## [GET] /v1/analytics/ability-order-stats
**Summary:** Ability Order Stats

**Tags:** Analytics

**Description:**
Retrieves statistics for the ability order of a hero.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `hero_id` | `query` | Yes | `integer` | See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_ability_upgrades` | `query` | No | `integer / null` | Filter players based on their minimum number of ability upgrades over the whole match. |
| `max_ability_upgrades` | `query` | No | `integer / null` | Filter players based on their maximum number of ability upgrades over the whole match. |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for an ability order to be included in the response. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |
| `include_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to include (only players who have purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `exclude_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to exclude (only players who have not purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |

### Responses
- **200**: Ability Order Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch ability order stats

---

## [GET] /v1/analytics/badge-distribution
**Summary:** Badge Distribution

**Tags:** Analytics

**Description:**
This endpoint returns the player badge distribution.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `is_high_skill_range_parties` | `query` | No | `boolean / null` | Filter matches based on whether they are in the high skill range. |
| `is_low_pri_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the low priority pool. |
| `is_new_player_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the new player pool. |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |

### Responses
- **200**: Badge Distribution
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch badge distribution

---

## [GET] /v1/analytics/build-item-stats
**Summary:** Build Item Stats

**Tags:** Analytics

**Description:**
Retrieves item statistics from hero builds.

Results are cached for **1 hour** based on the unique combination of query parameters provided. Subsequent identical requests within this timeframe will receive the cached response.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `hero_id` | `query` | No | `integer / null` | Filter builds based on the hero ID. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_last_updated_unix_timestamp` | `query` | No | `integer / null` | Filter builds based on their last updated time (Unix timestamp). **Default:** 30 days ago. |
| `max_last_updated_unix_timestamp` | `query` | No | `integer / null` | Filter builds based on their last updated time (Unix timestamp). |

### Responses
- **200**: Build Item Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch build item stats

---

## [GET] /v1/analytics/game-stats
**Summary:** Game Stats

**Tags:** Analytics

**Description:**
Retrieves aggregate game-level statistics.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `bucket` | `query` | No | `string` | Bucket allows you to group the stats by a specific field. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> Only works for `game_modes` with badge data (e.g. `normal`, not `street_brawl`). |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> Only works for `game_modes` with badge data (e.g. `normal`, not `street_brawl`). |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |

### Responses
- **200**: Game Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch game stats

---

## [GET] /v1/analytics/hero-ban-stats
**Summary:** Hero Ban Stats

**Tags:** Analytics

**Description:**
Retrieves ban statistics for each hero based on historical match data from demo analysis.

Only matches with successfully extracted ban data are included. Matches where ban extraction failed (empty `banned_hero_ids`) are excluded entirely.

Results are cached for **1 hour** based on the combination of query parameters provided.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `bucket` | `query` | No | `string` | Bucket allows you to group the stats by a specific field. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. **Minimum:** March 1, 2026. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |

### Responses
- **200**: Hero Ban Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero ban stats

---

## [GET] /v1/analytics/hero-build-stats/{hero_id}
**Summary:** Hero Build Stats

**Tags:** Analytics

**Description:**
Retrieves performance statistics for hero builds based on historical match data from demo analysis.

Only includes builds that exist in the hero builds database.

The `hero_build_id` is the first build the player had selected when the game started. It does not reflect any build changes made during the match.

Results are cached for **1 hour** based on the combination of query parameters provided.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `hero_id` | `path` | Yes | `integer` | The hero ID to fetch build stats for. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. **Minimum:** March 1, 2026. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `hero_build_id` | `query` | No | `integer / null` | Filter results for a specific hero build. |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for a build to be included in the response. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Build Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero build stats

---

## [GET] /v1/analytics/hero-comb-stats
**Summary:** Hero Comb Stats

**Tags:** Analytics

**Description:**
Retrieves overall statistics for each hero combination.

Results are cached for **1 hour**. The cache key is determined by the specific combination of filter parameters used in the query. Subsequent requests using the exact same filters within this timeframe will receive the cached response.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `include_hero_ids` | `query` | No | `array / null` | Comma separated list of hero ids to include. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `exclude_hero_ids` | `query` | No | `array / null` | Comma separated list of hero ids to exclude. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `include_enemy_hero_ids` | `query` | No | `array / null` | Comma separated list of enemy hero ids to include. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `exclude_enemy_hero_ids` | `query` | No | `array / null` | Comma separated list of enemy hero ids to exclude. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for a hero combination to be included in the response. |
| `max_matches` | `query` | No | `integer / null` | The maximum number of matches played for a hero combination to be included in the response. |
| `comb_size` | `query` | No | `integer / null` | The combination size to return. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Comb Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero comb stats

---

## [GET] /v1/analytics/hero-counter-stats
**Summary:** Hero Counter Stats

**Tags:** Analytics

**Description:**
Retrieves hero-versus-hero matchup statistics based on historical match data.

This endpoint analyzes completed matches to calculate how often a specific hero (`hero_id`) wins against an enemy hero (`enemy_hero_id`) and the total number of times they have faced each other under the specified filter conditions.

Results are cached for **1 hour** based on the combination of query parameters provided. Subsequent identical requests within this timeframe will receive the cached response.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_enemy_networth` | `query` | No | `integer / null` | Filter enemy players based on their net worth. |
| `max_enemy_networth` | `query` | No | `integer / null` | Filter enemy players based on their net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `same_lane_filter` | `query` | No | `boolean / null` | When `true`, only considers matchups where both `hero_id` and `enemy_hero_id` were assigned to the same lane (e.g., both Mid Lane). When `false`, considers all matchups regardless of assigned lane. |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for a hero combination to be included in the response. |
| `max_matches` | `query` | No | `integer / null` | The maximum number of matches played for a hero combination to be included in the response. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Counter Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero counter stats

---

## [GET] /v1/analytics/hero-stats
**Summary:** Hero Stats

**Tags:** Analytics

**Description:**
Retrieves performance statistics for each hero based on historical match data.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `bucket` | `query` | No | `string` | Bucket allows you to group the stats by a specific field. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `min_hero_matches` | `query` | No | `integer / null` | Filter players based on the number of matches they have played with a specific hero within the filtered time range. |
| `max_hero_matches` | `query` | No | `integer / null` | Filter players based on the number of matches they have played with a specific hero within the filtered time range. |
| `min_hero_matches_total` | `query` | No | `integer / null` | Filter players based on the number of matches they have played with a specific hero in their entire history. |
| `max_hero_matches_total` | `query` | No | `integer / null` | Filter players based on the number of matches they have played with a specific hero in their entire history. |
| `include_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to include (only players who have purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `exclude_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to exclude (only players who have not purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero stats

---

## [GET] /v1/analytics/hero-synergy-stats
**Summary:** Hero Synergy Stats

**Tags:** Analytics

**Description:**
Retrieves hero pair synergy statistics based on historical match data.

This endpoint analyzes completed matches to calculate how often a specific pair of heroes (`hero_id1` and `hero_id2`) won when playing *together on the same team*, and the total number of times they have played together under the specified filter conditions.

Results are cached for **1 hour** based on the combination of query parameters provided. Subsequent identical requests within this timeframe will receive the cached response.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `same_lane_filter` | `query` | No | `boolean / null` | When `true`, only considers matchups where both `hero_id1` and `hero_id2` were assigned to the same lane (e.g., both Mid Lane). When `false`, considers all matchups regardless of assigned lane. |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for a hero combination to be included in the response. |
| `max_matches` | `query` | No | `integer / null` | The maximum number of matches played for a hero combination to be included in the response. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Synergy Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero synergy stats

---

## [GET] /v1/analytics/item-flow-stats
**Summary:** Item Flow Stats

**Tags:** Analytics

**Description:**
Retrieves item build-flow statistics: per-phase item win/pick rates and the transitions between them.

Items are grouped into columns by the in-match phase they were bought in (controlled by
`phase_interval_s` and `phase_count`). The response contains `nodes` (items aggregated within a phase)
and `edges` (transitions between an item and items in the next phase). A locked build path can be
supplied via `locked_item_ids` / `locked_columns` to restrict the population to players who bought
those items in the given stage columns.

Each node also carries `adjusted_win_rate`: the item's win rate standardized to the stage's
net-worth-at-buy distribution. Because players who are already ahead have more souls and buy items
sooner, raw win rate is heavily confounded by wealth; the adjusted figure re-weights each item's win
rate across net-worth buckets to the stage-wide distribution, isolating the item's contribution from
the buyer's lead. It is still observational, not a controlled/causal estimate. `reached_per_column`
gives the distinct baseline games that bought any upgrade in each column, so consumers can show how
survivorship-selected (e.g. long-game-only) a late stage is.

Results are cached for **1 hour** based on the unique combination of query parameters provided.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `phase_interval_s` | `query` | No | `integer / null` | Deprecated/unused. `normal` mode uses fixed phase boundaries (0-9m, 9-20m, 20-30m, 30m+) aligned to the stats time-series; `street_brawl` columns are rounds. |
| `phase_count` | `query` | No | `integer / null` | Number of columns for `street_brawl` (rounds). Ignored for `normal`, which has fixed time phases. **Default:** 4. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches for a node or edge to be included in the response. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |
| `include_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to include (only players who have purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `exclude_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to exclude (only players who have not purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `locked_item_ids` | `query` | No | `array / null` | Comma separated list of item ids forming a "locked" build path. Pairs positionally with `locked_columns`: the i-th item must have been bought in the i-th `locked_columns` stage. See more: <https://api.deadlock-api.com/v1/assets/items> |
| `locked_columns` | `query` | No | `array / null` | Comma separated 0-based stage column indices for each `locked_item_ids` entry (time phase for `normal`, round for `street_brawl`). Must have the same length as `locked_item_ids`. |

### Responses
- **200**: Item Flow Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch item flow stats

---

## [GET] /v1/analytics/item-permutation-stats
**Summary:** Item Permutation Stats

**Tags:** Analytics

**Description:**
Retrieves item permutation statistics based on historical match data.

Results are cached for **1 hour** based on the unique combination of query parameters provided. Subsequent identical requests within this timeframe will receive the cached response.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `item_ids` | `query` | No | `array / null` | Comma separated list of item ids. See more: <https://api.deadlock-api.com/v1/assets/items> |
| `comb_size` | `query` | No | `integer / null` | The combination size to return. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `hero_id` | `query` | No | `integer / null` | Filter matches based on the hero ID. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Item Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch item stats

---

## [GET] /v1/analytics/item-stats
**Summary:** Item Stats

**Tags:** Analytics

**Description:**
Retrieves item statistics based on historical match data.

Results are cached for **1 hour** based on the unique combination of query parameters provided. Subsequent identical requests within this timeframe will receive the cached response.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `bucket` | `query` | No | `string` | Bucket allows you to group the stats by a specific field. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `hero_id` | `query` | No | `integer / null` | Filter matches based on the hero ID. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `enemy_hero_ids` | `query` | No | `string / null` | Filter to matches where one or more of these heroes were on the opposing team. Comma separated. When set, returns "what items beat hero(es) X?" stats. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `enemy_hero_ids_all_match` | `query` | No | `boolean / null` | When `true`, requires *all* of the specified `enemy_hero_ids` to be on the same enemy team. When `false` (default), matches if *any* of the specified hero(es) are on the enemy team. Ignored when `enemy_hero_ids` is unset. |
| `min_enemy_networth` | `query` | No | `integer / null` | Filter the specified enemy hero(es) by their final net worth. Ignored when `enemy_hero_ids` is unset. |
| `max_enemy_networth` | `query` | No | `integer / null` | Filter the specified enemy hero(es) by their final net worth. Ignored when `enemy_hero_ids` is unset. |
| `same_lane_filter` | `query` | No | `boolean / null` | When `true`, only counts buyers in the same `assigned_lane` as one of the specified enemy heroes. Ignored when `enemy_hero_ids` is unset. **Default:** `false`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `include_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to include. See more: <https://api.deadlock-api.com/v1/assets/items> |
| `exclude_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to exclude. See more: <https://api.deadlock-api.com/v1/assets/items> |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for an item to be included in the response. |
| `max_matches` | `query` | No | `integer / null` | The maximum number of matches played for a hero combination to be included in the response. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |
| `min_bought_at_s` | `query` | No | `integer / null` | Filter items bought after this game time (seconds). |
| `max_bought_at_s` | `query` | No | `integer / null` | Filter items bought before this game time (seconds). |

### Responses
- **200**: Item Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch item stats

---

## [GET] /v1/analytics/kill-death-stats
**Summary:** Kill Death Stats

**Tags:** Analytics

**Description:**
This endpoint returns the kill-death statistics across a 128x128 pixel raster.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `team` | `query` | No | `integer / null` | Filter by team number. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `account_ids` | `query` | No | `array / null` | Filter matches by account IDs of players that participated in the match. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `is_high_skill_range_parties` | `query` | No | `boolean / null` | Filter matches based on whether they are in the high skill range. |
| `is_low_pri_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the low priority pool. |
| `is_new_player_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the new player pool. |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_kills_per_raster` | `query` | No | `integer / null` | Filter Raster cells based on minimum kills. |
| `max_kills_per_raster` | `query` | No | `integer / null` | Filter Raster cells based on maximum kills. |
| `min_deaths_per_raster` | `query` | No | `integer / null` | Filter Raster cells based on minimum deaths. |
| `max_deaths_per_raster` | `query` | No | `integer / null` | Filter Raster cells based on maximum deaths. |
| `min_game_time_s` | `query` | No | `integer / null` | Filter kills based on their game time. |
| `max_game_time_s` | `query` | No | `integer / null` | Filter kills based on their game time. |

### Responses
- **200**: Kill Death Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch kill death stats

---

## [GET] /v1/analytics/player-performance-curve
**Summary:** Player Performance Curve

**Tags:** Analytics

**Description:**
Retrieves player performance statistics (net worth, kills, deaths, assists) over time throughout matches.

Results are cached for **1 hour** based on the unique combination of query parameters provided.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `resolution` | `query` | No | `integer / null` | Resolution for relative game times in percent (0-100). **Default:** 10 (buckets of 10%). Set to **0** to use absolute game time (seconds). |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `include_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to include (only players who have purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `exclude_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to exclude (only players who have not purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Player Performance Curve
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch player performance curve

---

## [GET] /v1/analytics/player-stats/metrics
**Summary:** Player Stats Metrics

**Tags:** Analytics

**Description:**
Returns comprehensive statistical analysis of player performance.

Results are cached for **1 hour** based on the unique combination of query parameters provided. Subsequent identical requests within this timeframe will receive the cached response.

> Note: Quantiles are calculated using the [DDSketch](https://www.vldb.org/pvldb/vol12/p2195-masson.pdf) algorithm, so they are not exact but have a maximum relative error of 0.01.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_matches` | `query` | No | `integer / null` | The maximum number of matches to analyze. |
| `include_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to include (only players who have purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `exclude_item_ids` | `query` | No | `array / null` | Comma separated list of item ids to exclude (only players who have not purchased these items). See more: <https://api.deadlock-api.com/v1/assets/items> |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch player stats metrics

---

## [GET] /v1/analytics/scoreboards/heroes
**Summary:** Hero Scoreboard

**Tags:** Analytics

**Description:**
This endpoint returns the hero scoreboard.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `sort_by` | `query` | Yes | `string` | The field to sort by. |
| `sort_direction` | `query` | No | `string` | The direction to sort heroes in. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_matches` | `query` | No | `integer / null` | Filter by min number of matches played. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `account_id` | `query` | No | `integer / null` | Filter for matches with a specific player account ID. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Hero Scoreboard
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero scoreboard

---

## [GET] /v1/analytics/scoreboards/players
**Summary:** Player Scoreboard

**Tags:** Analytics

**Description:**
This endpoint returns the player scoreboard.

### Rate Limits:
> The rate limits below are **shared across all analytics endpoints**.

| Type | Limit |
| ---- | ----- |
| IP | 200req/min |
| Key | 400req/min |
| Global | 2000req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `sort_by` | `query` | Yes | `string` | The field to sort by. |
| `sort_direction` | `query` | No | `string` | The direction to sort players in. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `hero_id` | `query` | No | `integer / null` | Filter matches based on the hero ID. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_matches` | `query` | No | `integer / null` | The minimum number of matches played for a player to be included in the scoreboard. |
| `max_matches` | `query` | No | `integer / null` | The maximum number of matches played for a hero combination to be included in the response. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `start` | `query` | No | `integer / null` | The offset to start fetching players from. |
| `limit` | `query` | No | `integer / null` | The maximum number of players to fetch. |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: Player Scoreboard
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch player scoreboard

---

## [GET] /v1/assets/accolades
**Summary:** List Accolades

**Tags:** Accolades

**Description:**
Returns the per-accolade metadata used by the game client, parsed from the patch's KV3 source files.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/accolades/by-name/{name}
**Summary:** Get Accolade By Name

**Tags:** Accolades

**Description:**
Returns a single accolade by `class_name` or `tracked_stat_name` (case-insensitive).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `name` | `path` | Yes | `string` | Accolade `class_name` (e.g. `kills`) or `tracked_stat_name` |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown accolade name or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/accolades/{accolade_id}
**Summary:** Get Accolade

**Tags:** Accolades

**Description:**
Returns a single accolade by id.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `accolade_id` | `path` | Yes | `integer` | Accolade id (`m_unAccoladeID`) |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown accolade id or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/build-tags
**Summary:** List Build Tags

**Tags:** Build Tags

**Description:**
Returns the build tag taxonomy used by the game client, derived from per-version localization keys.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/build-tags/by-name/{name}
**Summary:** Get Build Tag By Name

**Tags:** Build Tags

**Description:**
Returns a single build tag by `class_name` (case-insensitive).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `name` | `path` | Yes | `string` | Build tag `class_name` (e.g. `citadel_build_tag_weapon`) |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown build tag name or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/build-tags/{build_tag_id}
**Summary:** Get Build Tag

**Tags:** Build Tags

**Description:**
Returns a single build tag by id.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `build_tag_id` | `path` | Yes | `integer` | Build tag id (murmurhash2 of `class_name`) |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown build tag id or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/client-versions
**Summary:** List Client Versions

**Tags:** Client Versions

**Description:**
Returns all known Deadlock client/game versions for which versioned assets are available, sorted ascending (oldest first).

### Responses
- **200**: 
- **500**: Failed to load source assets

---

## [GET] /v1/assets/colors
**Summary:** List Colors

**Tags:** Colors

**Description:**
Panorama color palette (`@define <name>: #RRGGBB[AA];` declarations from `citadel_base_styles.css`), keyed by `snake_case` name.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/fonts
**Summary:** Fonts Index

**Tags:** Assets Bucket

**Description:**
Nested file-tree of all hosted fonts, mapping each name to its public CDN URL.

### Responses
- **200**: 
- **500**: Failed to load source assets

---

## [GET] /v1/assets/generic-data
**Summary:** Get Generic Data

**Tags:** Generic Data

**Description:**
Returns the game-wide generic configuration (street brawl, lane info, glitch settings, damage flash, item draft, etc.) parsed from the patch's `generic_data.vdata` KV3 source file.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/heroes
**Summary:** List Heroes

**Tags:** Heroes

**Description:**
Returns the per-hero metadata used by the game client, parsed from the patch's KV3 source files.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |
| `only_active` | `query` | No | `boolean / null` | When true, hides heroes that aren't player-selectable or are disabled / in-development. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/heroes/by-name/{name}
**Summary:** Get Hero By Name

**Tags:** Heroes

**Description:**
Returns a single hero by `class_name` or display `name`. Matches the bare value as well as the `hero_`-prefixed form.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `name` | `path` | Yes | `string` | Hero class name (e.g. `hero_atlas`) or short name (e.g. `atlas`) |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown hero name or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/heroes/{hero_id}
**Summary:** Get Hero

**Tags:** Heroes

**Description:**
Returns a single hero by id.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `hero_id` | `path` | Yes | `integer` | Hero id (`m_HeroID`) |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown hero id or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/icons
**Summary:** Icons Index

**Tags:** Assets Bucket

**Description:**
Nested file-tree of all hosted icons, mapping each name to its public CDN URL.

### Responses
- **200**: 
- **500**: Failed to load source assets

---

## [GET] /v1/assets/images
**Summary:** Images Index

**Tags:** Assets Bucket

**Description:**
Nested file-tree of all hosted images, mapping each name to its public CDN URL.

### Responses
- **200**: 
- **500**: Failed to load source assets

---

## [GET] /v1/assets/items
**Summary:** List Items

**Tags:** Items

**Description:**
Returns the full per-patch item list — abilities, weapons, and upgrades.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/items/by-hero-id/{id}
**Summary:** List Items By Hero

**Tags:** Items

**Description:**
Hero-bound abilities, excluding the generic movement abilities.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `id` | `path` | Yes | `integer` | Hero id (`m_HeroID`). |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 

---

## [GET] /v1/assets/items/by-slot-type/{slot_type}
**Summary:** List Items By Slot Type

**Tags:** Items

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `slot_type` | `path` | Yes | `ItemSlotType` | Slot type: `weapon`, `spirit`, or `vitality`. |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 

---

## [GET] /v1/assets/items/by-type/{type}
**Summary:** List Items By Type

**Tags:** Items

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `type` | `path` | Yes | `ItemType` | Item type: `ability`, `weapon`, or `upgrade`. |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 

---

## [GET] /v1/assets/items/{id_or_class_name}
**Summary:** Get Item

**Tags:** Items

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `id_or_class_name` | `path` | Yes | `string` | Numeric `id` or string `class_name`. |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown item id/class_name or client_version

---

## [GET] /v1/assets/loot-tables
**Summary:** List Loot Tables

**Tags:** Loot Tables

**Description:**
Returns the per-table loot definitions used by the game client, parsed from the patch's KV3 source files. Keyed by table `class_name`.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/map
**Summary:** Map

**Tags:** Map

**Description:**
Map metadata for a client version: the minimap radius, image-layer CDN URLs, the relative positions of every objective/tower marker, and the three zip-line lane cubic splines. Defaults to the latest known client version.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/misc-entities
**Summary:** List Misc Entities

**Tags:** Misc Entities

**Description:**
Returns the per-misc-entity metadata used by the game client, parsed from the patch's KV3 source files.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/misc-entities/{id_or_classname}
**Summary:** Get Misc Entity

**Tags:** Misc Entities

**Description:**
Returns a single misc entity by numeric id or by `class_name` (case-insensitive).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `id_or_classname` | `path` | Yes | `string` | Misc entity id (`murmurhash2(class_name)`) or `class_name` |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown misc entity id/class_name or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/npc-units
**Summary:** List NPC Units

**Tags:** NPC Units

**Description:**
Returns the per-NPC-unit metadata used by the game client, parsed from the patch's KV3 source files.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/npc-units/{id_or_classname}
**Summary:** Get NPC Unit

**Tags:** NPC Units

**Description:**
Returns a single NPC unit by numeric id or by `class_name` (case-insensitive).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `id_or_classname` | `path` | Yes | `string` | NPC unit id (`murmurhash2(class_name)`) or `class_name` |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown NPC unit id/class_name or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/ranks
**Summary:** List Ranks

**Tags:** Ranks

**Description:**
Returns the 12 player ranks (tier, localized name, badge image URLs, hex color).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/ranks/{tier}
**Summary:** Get Rank

**Tags:** Ranks

**Description:**
Returns a single rank by tier index.

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `tier` | `path` | Yes | `integer` | Rank tier (0-11) |
| `language` | `query` | No | `` | Language code. Defaults to `english`. |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Unknown tier or client_version
- **500**: Failed to load source assets

---

## [GET] /v1/assets/sounds
**Summary:** Sounds Index

**Tags:** Assets Bucket

**Description:**
Nested file-tree of all hosted sounds, mapping each name to its public CDN URL.

### Responses
- **200**: 
- **500**: Failed to load source assets

---

## [GET] /v1/assets/steam-info
**Summary:** Get Steam Info

**Tags:** Steam Info

**Description:**
Returns the `steam.inf` manifest published with the patch (client/server version, app IDs, source revision, build timestamp).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `client_version` | `query` | No | `integer / null` | Client/game version (e.g. `6518`). Defaults to the latest known version. |

### Responses
- **200**: 
- **404**: Requested client_version is not available
- **500**: Failed to load source assets

---

## [GET] /v1/assets/steam-info/all
**Summary:** Get All Steam Infos

**Tags:** Steam Info

**Description:**
Returns the `steam.inf` manifest for every known patch as a single array, newest version first. Replaces the legacy `/v1/steam-info/all` endpoint.

### Responses
- **200**: 
- **500**: Failed to load source assets

---

## [GET] /v1/builds
**Summary:** Search

**Tags:** Builds

**Description:**
Search for builds based on various criteria.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `min_unix_timestamp` | `query` | No | `integer` | Filter builds based on their `last_updated` time (Unix timestamp). |
| `max_unix_timestamp` | `query` | No | `integer` | Filter builds based on their `last_updated` time (Unix timestamp). |
| `min_published_unix_timestamp` | `query` | No | `integer` | Filter builds based on their published time (Unix timestamp). |
| `max_published_unix_timestamp` | `query` | No | `integer` | Filter builds based on their published time (Unix timestamp). |
| `sort_by` | `query` | No | `string` | The field to sort the builds by. |
| `start` | `query` | No | `integer` | The index of the first build to return. |
| `limit` | `query` | No | `integer` | The maximum number of builds to return. |
| `sort_direction` | `query` | No | `string` | The direction to sort the builds in. |
| `search_name` | `query` | No | `string` | Search for builds with a name containing this string. |
| `search_description` | `query` | No | `string` | Search for builds with a description containing this string. |
| `only_latest` | `query` | No | `boolean` | Only return the latest version of each build. |
| `language` | `query` | No | `integer` | Filter builds by language. |
| `build_language` | `query` | No | `string` | Filter builds by language. |
| `build_id` | `query` | No | `integer` | Filter builds by ID. |
| `version` | `query` | No | `integer` | Filter builds by version. |
| `hero_id` | `query` | No | `integer` | Filter builds by hero ID. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `tag` | `query` | No | `integer` | Filter builds by tag. |
| `rollup_category` | `query` | No | `integer` | Filter builds by rollup category. |
| `author_id` | `query` | No | `integer` | The author's `SteamID3` |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Internal server error

---

## [GET] /v1/commands/resolve
**Summary:** Resolve Command

**Tags:** Commands

**Description:**
Resolves a command and returns the resolved command.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 60req/60s |
| Key | - |
| Global | 300req/60s |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `region` | `query` | No | `string` | The players region |
| `account_id` | `query` | Yes | `integer` | The players `SteamID3` |
| `template` | `query` | No | `string` | The command template to resolve |
| `hero_name` | `query` | No | `string / null` | Hero name to check for hero specific stats |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.

---

## [GET] /v1/commands/variables/available
**Summary:** Available Variables

**Tags:** Commands

**Description:**
Returns a list of available variables that can be used in the command endpoint.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.

---

## [GET] /v1/commands/variables/resolve
**Summary:** Resolve Variables

**Tags:** Commands

**Description:**
Resolves variables and returns a map of variable name to resolved value.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 60req/min |
| Key | - |
| Global | 300req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `region` | `query` | No | `string` |  |
| `account_id` | `query` | Yes | `integer` |  |
| `variables` | `query` | No | `string` | Variables to resolve, separated by commas. |
| `hero_name` | `query` | No | `string / null` | Hero name to check for hero specific stats |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.

---

## [GET] /v1/commands/widgets/versions
**Summary:** Widget Versions

**Tags:** Commands

**Description:**
Returns a map of str->int of widget versions.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.

---

## [GET] /v1/graphql
**Summary:** GraphQL Playground

**Tags:** GraphQL

**Description:**
Interactive GraphiQL playground for exploring the GraphQL API.

Open this endpoint in a browser to access the playground. Send GraphQL queries via `POST /v1/graphql` with a JSON body of the form `{ "query": "...", "variables": {...} }`.

### Rate Limits (POST):
| Type | Limit |
| ---- | ----- |
| IP | 10req/min |
| Key | 10req/10s |
| Global | 100req/min |

### Responses
- **200**: GraphiQL playground UI

---

## [GET] /v1/info
**Summary:** API Info

**Tags:** Info

**Description:**
Returns information about the API.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **500**: 

---

## [GET] /v1/info/health
**Summary:** Health Check

**Tags:** Info

**Description:**
Checks the health of the services.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **500**: 

---

## [GET] /v1/leaderboard/{region}
**Summary:** Leaderboard

**Tags:** Leaderboard

**Description:**
Returns the leaderboard.

### Note:

Valve updates the leaderboard once per hour.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `region` | `path` | Yes | `string` | The region to fetch the leaderboard for. |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **500**: Fetching or parsing the leaderboard failed

---

## [GET] /v1/leaderboard/{region}/raw
**Summary:** Leaderboard as Protobuf

**Tags:** Leaderboard

**Description:**
Returns the leaderboard, serialized as protobuf message.

You have to decode the protobuf message.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Message:
- CMsgClientToGcGetLeaderboardResponse

### Note:

Valve updates the leaderboard once per hour.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `region` | `path` | Yes | `string` | The region to fetch the leaderboard for. |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **500**: Fetching the leaderboard failed

---

## [GET] /v1/leaderboard/{region}/{hero_id}
**Summary:** Hero Leaderboard

**Tags:** Leaderboard

**Description:**
Returns the leaderboard for a specific hero.

### Note:

Valve updates the leaderboard once per hour.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `region` | `path` | Yes | `string` | The region to fetch the leaderboard for. |
| `hero_id` | `path` | Yes | `integer` | The hero ID to fetch the leaderboard for. See more: <https://api.deadlock-api.com/v1/assets/heroes> |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **500**: Fetching or parsing the hero leaderboard failed

---

## [GET] /v1/leaderboard/{region}/{hero_id}/raw
**Summary:** Hero Leaderboard as Protobuf

**Tags:** Leaderboard

**Description:**
Returns the leaderboard for a specific hero, serialized as protobuf message.

You have to decode the protobuf message.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Message:
- CMsgClientToGcGetLeaderboardResponse

### Note:

Valve updates the leaderboard once per hour.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `region` | `path` | Yes | `string` | The region to fetch the leaderboard for. |
| `hero_id` | `path` | Yes | `integer` | The hero ID to fetch the leaderboard for. See more: <https://api.deadlock-api.com/v1/assets/heroes> |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **500**: Fetching the hero leaderboard failed

---

## [GET] /v1/matches/active
**Summary:** Active

**Tags:** Matches

**Description:**
Returns active matches that are currently being played.

Fetched from the watch tab in game, which is limited to the **top 200 matches**.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `query` | No | `integer / null` | The account ID to filter active matches by (`SteamID3`) |
| `account_ids` | `query` | No | `array / null` | Comma separated list of account ids to include |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **500**: Fetching or parsing active matches failed

---

## [GET] /v1/matches/active/raw
**Summary:** Active as Protobuf

**Tags:** Matches

**Description:**
Returns active matches that are currently being played, serialized as protobuf message.

Fetched from the watch tab in game, which is limited to the **top 200 matches**.

You have to decode the protobuf message.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Message:
- CMsgClientToGcGetActiveMatchesResponse

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **500**: Fetching active matches failed

---

## [POST] /v1/matches/custom/create
**Summary:** Create Match

**Tags:** Custom Matches

**Description:**
This endpoint creates a custom match using a bot account.

**Process:**
1. A party is created with your provided settings.
2. The system waits for the party code to be generated.
3. The party code is returned in the response.
4. The bot switches to spectator mode.
5. The bot marks itself as ready.
6. You and other players join, ready up, and start the match.

**Callbacks:**
If a callback URL is provided, POST requests will be sent to it:
- **settings:** When lobby settings change, a POST is sent to `{callback_url}/settings` with the `CsoCitadelParty` protobuf message as JSON.
- **match start:** When the match starts, a POST is sent to `{callback_url}` with the match ID.

_Protobuf definitions: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)_

**Note:**
The bot will leave the match 15 minutes after creation, regardless of match state.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/h |
| Key | 100req/30min |
| Global | 1000req/h |

### Responses
- **200**: Successfully fetched custom match id.
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Creating custom match failed

---

## [POST] /v1/matches/custom/{lobby_id}/leave
**Summary:** Leave Lobby

**Tags:** Custom Matches

**Description:**
This endpoint makes the bot leave the custom match lobby early.
By default the bot leaves automatically after 15 minutes, but this endpoint allows you to trigger it sooner.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/h |
| Key | 100req/30min |
| Global | 1000req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `lobby_id` | `path` | Yes | `string` |  |

### Responses
- **200**: Successfully left the lobby.
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Leaving lobby failed

---

## [POST] /v1/matches/custom/{lobby_id}/ready
**Summary:** Ready Up

**Tags:** Custom Matches

**Description:**
This endpoint allows you to ready up for a custom match.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/h |
| Key | 100req/30min |
| Global | 1000req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `lobby_id` | `path` | Yes | `string` |  |

### Responses
- **200**: Successfully ready up.
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Ready up failed

---

## [POST] /v1/matches/custom/{lobby_id}/start
**Summary:** Start Match

**Tags:** Custom Matches

**Description:**
This endpoint starts a custom match.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/h |
| Key | 100req/30min |
| Global | 1000req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `lobby_id` | `path` | Yes | `string` |  |

### Responses
- **200**: Successfully started the match.
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Starting match failed

---

## [POST] /v1/matches/custom/{lobby_id}/unready
**Summary:** Unready

**Tags:** Custom Matches

**Description:**
This endpoint allows you to unready for a custom match.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/h |
| Key | 100req/30min |
| Global | 1000req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `lobby_id` | `path` | Yes | `string` |  |

### Responses
- **200**: Successfully unready.
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Unready failed

---

## [GET] /v1/matches/custom/{party_id}/match-id
**Summary:** Get Match ID

**Tags:** Custom Matches

**Description:**
This endpoint allows you to get the match id of a custom match.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `party_id` | `path` | Yes | `integer` |  |

### Responses
- **200**: Successfully fetched custom match id.
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Fetch Custom Match ID failed

---

## [GET] /v1/matches/live/urls
**Summary:** Live Broadcast URLs

**Tags:** Matches

**Description:**
Returns a list of all currently available live broadcast URLs.

These can be used in any demofile broadcast parser:
- [Demofile-Net](https://github.com/saul/demofile-net)
- [Haste](https://github.com/blukai/haste/)

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **500**: Fetching live URLs failed

---

## [POST] /v1/matches/live/urls
**Summary:** Ingest Live Broadcast URLs

**Tags:** Matches

**Description:**
Submit one or more live broadcast URLs so they show up in the `GET /live/urls` listing.

Each submitted URL is stored for 15 minutes; re-submit periodically to keep a match listed
while it is still live. Existing entries for the same `match_id` are overwritten.

These URLs can be used in any demofile broadcast parser:
- [Demofile-Net](https://github.com/saul/demofile-net)
- [Haste](https://github.com/blukai/haste/)

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Ingesting live URLs failed

---

## [GET] /v1/matches/metadata
**Summary:** Bulk Metadata

**Tags:** Matches

**Description:**
This endpoints lets you fetch multiple match metadata at once. The response is a JSON array of match metadata.

When player info is included, each player object contains a `hero_build_id` field (if available) from demo analysis.

> **Note:** The `hero_build_id` represents the first build the player had selected when the game started. It does not reflect any build changes made during the match.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/min |
| Key | 10req/10s |
| Global | 100req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `include_info` | `query` | No | `boolean` | Include match info in the response. |
| `include_more_info` | `query` | No | `boolean` | Include more match info in the response. |
| `include_objectives` | `query` | No | `boolean` | Include objectives in the response. |
| `include_mid_boss` | `query` | No | `boolean` | Include midboss in the response. |
| `include_player_info` | `query` | No | `boolean` | Include player info in the response. |
| `include_player_kda` | `query` | No | `boolean` | Include only K/D/A fields (`kills`, `deaths`, `assists`) for players. |
| `include_player_items` | `query` | No | `boolean` | Include player items in the response. |
| `include_player_stats` | `query` | No | `boolean` | Include player stats in the response. |
| `include_player_final_stats` | `query` | No | `boolean` | Include only the final per-player stats (last sample of every `stats.*` time-series) as a single `final_stats` object. Far cheaper than `include_player_stats`, which returns the whole array per field. |
| `include_player_death_details` | `query` | No | `boolean` | Include player death details in the response. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. Omit or pass empty string for no filter. |
| `match_mode` | `query` | No | `string / null` | Filter matches based on the match mode. Valid values: `unranked`, `private_lobby`, `coop_bot`, `ranked`, `server_test`, `tutorial`, `hero_labs`. **Default:** `ranked,unranked`. |
| `match_ids` | `query` | No | `array / null` | Comma separated list of match ids, limited by `limit` |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `is_high_skill_range_parties` | `query` | No | `boolean / null` | Filter matches based on whether they are in the high skill range. |
| `is_low_pri_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the low priority pool. |
| `is_new_player_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the new player pool. |
| `account_ids` | `query` | No | `array / null` | Filter matches by account IDs of players that participated in the match. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `item_filter_hero_id` | `query` | No | `integer / null` | Hero ID to scope item filters to. Required when using `include_item_ids` or `exclude_item_ids`. |
| `include_item_ids` | `query` | No | `string / null` | Comma separated list of item ids to include. Requires `item_filter_hero_id`. Returns matches where a player on the specified hero has ALL of these items. |
| `exclude_item_ids` | `query` | No | `string / null` | Comma separated list of item ids to exclude. Requires `item_filter_hero_id`. Returns matches where a player on the specified hero has NONE of these items. |
| `extra_match_columns` | `query` | No | `string / null` | Comma separated list of extra match-level columns to include in the response. Each column is aggregated with `any(...)`. Only alphanumeric characters, underscores, and dots (for nested field access) are allowed. Example: `objectives_mask_team0,team_score`. |
| `extra_player_columns` | `query` | No | `string / null` | Comma separated list of extra player-level columns to include in the response. Each column is added inside the player tuple. Only alphanumeric characters, underscores, and dots (for nested field access) are allowed. Example: `stats.player_damage,stats.player_healing`. Implicitly enables player fields. |
| `order_by` | `query` | No | `string` | The field to order the results by. |
| `order_direction` | `query` | No | `string` | The direction to order the results by. |
| `limit` | `query` | No | `integer` | The maximum number of matches to return. |
| `format` | `query` | No | `` | The response format. Valid values: `json` (a JSON array), `ndjson` (newline-delimited JSON objects). |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded

---

## [GET] /v1/matches/recently-fetched
**Summary:** Recently Fetched

**Tags:** Matches

**Description:**
This endpoint returns a list of match ids that have been fetched within the last 10 minutes.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: Recently fetched match info
- **500**: Failed to fetch recently fetched matches

---

## [POST] /v1/matches/salts
**Summary:** Match Salts Ingest

**Tags:** Internal

**Description:**
You can use this endpoint to help us collecting data.

The endpoint accepts a list of MatchSalts objects, which contain the following fields:

- `match_id`: The match ID
- `cluster_id`: The cluster ID
- `metadata_salt`: The metadata salt
- `replay_salt`: The replay salt
- `username`: The username of the person who submitted the match

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **400**: Provided parameters are invalid or the salt check failed.
- **429**: Rate limit exceeded
- **500**: Ingest failed

---

## [GET] /v1/matches/{match_id}/live/url
**Summary:** Live Broadcast URL

**Tags:** Matches

**Description:**
This endpoints spectates a match and returns the live URL to be used in any demofile broadcast parser.

Example Parsers:
- [Demofile-Net](https://github.com/saul/demofile-net)
- [Haste](https://github.com/blukai/haste/)

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 2req/h |
| Key | 5req/m, 100req/h |
| Global | 5req/10s, 500req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `match_id` | `path` | Yes | `integer` | The match ID |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Spectating match failed

---

## [GET] /v1/matches/{match_id}/metadata
**Summary:** Metadata

**Tags:** Matches

**Description:**
This endpoint returns the match metadata for the given `match_id` parsed into JSON.

Each player object is enriched with a `hero_build_id` field (if available) from demo analysis.

> **Note:** The `hero_build_id` represents the first build the player had selected when the game started. It does not reflect any build changes made during the match.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Messages:
- CMsgMatchMetaData
- CMsgMatchMetaDataContents

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | From Cache: 100req/s<br>From S3: 100req/10s<br>From Steam: 3req/h |
| Key | From Cache: 100req/s<br>From S3: 100req/s<br>From Steam: 300req/h |
| Global | From Cache: 100req/s<br>From S3: 700req/s<br>From Steam: 1500req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `match_id` | `path` | Yes | `integer` | The match ID |
| `is_custom` | `query` | No | `boolean / null` |  |
| `disable_steam` | `query` | No | `boolean / null` | If `true`, skip the Steam fallback when the metadata is not available in S3 and return an error instead. |

### Responses
- **200**: Match metadata, see protobuf type: CMsgMatchMetaDataContents
- **400**: Provided parameters are invalid.
- **404**: Match metadata not found
- **429**: Rate limit exceeded
- **500**: Fetching or parsing match metadata failed

---

## [GET] /v1/matches/{match_id}/metadata/raw
**Summary:** Metadata as Protobuf

**Tags:** Matches

**Description:**
This endpoints returns the raw .meta.bz2 file for the given `match_id`.

You have to decompress it and decode the protobuf message.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Messages:
- CMsgMatchMetaData
- CMsgMatchMetaDataContents

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | From Cache: 100req/s<br>From S3: 100req/10s<br>From Steam: 3req/h |
| Key | From Cache: 100req/s<br>From S3: 100req/s<br>From Steam: 300req/h |
| Global | From Cache: 100req/s<br>From S3: 700req/s<br>From Steam: 1500req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `match_id` | `path` | Yes | `integer` | The match ID |
| `is_custom` | `query` | No | `boolean / null` |  |
| `disable_steam` | `query` | No | `boolean / null` | If `true`, skip the Steam fallback when the metadata is not available in S3 and return an error instead. |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **404**: Match metadata not found
- **429**: Rate limit exceeded
- **500**: Fetching match metadata failed

---

## [GET] /v1/matches/{match_id}/salts
**Summary:** Salts

**Tags:** Matches

**Description:**
This endpoints returns salts that can be used to fetch metadata and demofile for a match.

**Note:** We currently fetch many matches without salts, so for these matches we do not have salts stored.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | From DB: 100req/s<br>From Steam: 10req/30mins |
| Key | From DB: -<br>From Steam: 10req/min |
| Global | From DB: -<br>From Steam: 10req/10s |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `match_id` | `path` | Yes | `integer` | The match ID |
| `disable_steam` | `query` | No | `boolean / null` | If `true`, skip the Steam fallback when the salts are not available in Clickhouse and return an error instead. |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded
- **500**: Fetching match salts failed

---

## [GET] /v1/patches
**Summary:** Notes

**Tags:** Patches

**Description:**
**Deprecated:** Use `/v2/patches` instead, which returns a unified feed combining the Forum changelog and the Steam news feed.

Returns the parsed result of the RSS Feed from the official Forum.

RSS-Feed: https://forums.playdeadlock.com/forums/changelog.10/index.rss

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **500**: Fetching or parsing the RSS-Feed failed

---

## [GET] /v1/patches/big-days
**Summary:** Big Days

**Tags:** Patches

**Description:**
Returns a list of dates where Deadlock's "big" patch days were, usually bi-weekly.
The exact date is the time when the announcement forum post was published.

This list is manually maintained, and so new patch dates may be delayed by a few hours.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 

---

## [GET] /v1/players/hero-stats
**Summary:** Hero Stats

**Tags:** Players

**Description:**
This endpoint returns statistics for each hero played by a given player account.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_ids` | `query` | Yes | `array` | Comma separated list of account ids, Account IDs are in `SteamID3` format. |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `hero_ids` | `query` | No | `string / null` | Filter matches based on the hero IDs. See more: <https://api.deadlock-api.com/v1/assets/heroes> |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `max_networth` | `query` | No | `integer / null` | Filter players based on their final net worth. |
| `min_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `max_average_badge` | `query` | No | `integer / null` | Filter matches based on the average badge level (tier = first digits, subtier = last digit) of *both* teams involved. See more: <https://api.deadlock-api.com/v1/assets/ranks> |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |

### Responses
- **200**: Hero Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero stats

---

## [GET] /v1/players/mmr
**Summary:** Batch MMR

**Tags:** MMR

**Description:**
Batch Player MMR

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_ids` | `query` | Yes | `array` | Comma separated list of account ids, Account IDs are in `SteamID3` format. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |

### Responses
- **200**: MMR
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch mmr

---

## [GET] /v1/players/mmr/distribution
**Summary:** MMR Distribution

**Tags:** MMR

**Description:**
Player MMR Distribution

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `is_high_skill_range_parties` | `query` | No | `boolean / null` | Filter matches based on whether they are in the high skill range. |
| `is_low_pri_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the low priority pool. |
| `is_new_player_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the new player pool. |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |

### Responses
- **200**: MMR
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch mmr

---

## [GET] /v1/players/mmr/distribution/{hero_id}
**Summary:** Hero MMR Distribution

**Tags:** MMR

**Description:**
Player Hero MMR Distribution

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). **Default:** 30 days ago. |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `is_high_skill_range_parties` | `query` | No | `boolean / null` | Filter matches based on whether they are in the high skill range. |
| `is_low_pri_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the low priority pool. |
| `is_new_player_pool` | `query` | No | `boolean / null` | Filter matches based on whether they are in the new player pool. |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `hero_id` | `path` | Yes | `integer` | The hero ID to fetch the MMR history for. See more: <https://api.deadlock-api.com/v1/assets/heroes> |

### Responses
- **200**: Hero MMR
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero mmr

---

## [GET] /v1/players/mmr/{hero_id}
**Summary:** Batch Hero MMR

**Tags:** MMR

**Description:**
Batch Player Hero MMR

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_ids` | `query` | Yes | `array` | Comma separated list of account ids, Account IDs are in `SteamID3` format. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `hero_id` | `path` | Yes | `integer` | The hero ID to fetch the MMR history for. See more: <https://api.deadlock-api.com/v1/assets/heroes> |

### Responses
- **200**: Hero MMR
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero mmr

---

## [GET] /v1/players/rank-predict/image
**Summary:** Rank Predict Avg Image

**Tags:** Players

**Description:**
Returns the average predicted rank badge image (binary) for a comma-separated list of account IDs. Use `?format=webp` for WebP and `?size=small` for the small badge (defaults to large).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_ids` | `query` | Yes | `array` | Comma-separated list of account IDs (max 12). |
| `format` | `query` | No | `string` | Image format. Defaults to `png`. Supported: `png`, `webp`. |
| `size` | `query` | No | `string` | Image size. Defaults to `large`. Supported: `large`, `small`. |

### Responses
- **200**: Average predicted rank badge image
- **400**: Invalid or missing account IDs
- **403**: One of the users is protected
- **404**: No image available for the predicted rank
- **422**: Not enough recent ranked matches for one or more accounts
- **429**: Rate limit exceeded
- **500**: Prediction failed
- **503**: Rank prediction model not loaded

---

## [GET] /v1/players/steam
**Summary:** Batch Steam Profile

**Tags:** Steam

**Description:**
This endpoint returns Steam profiles of players.

Pass `refresh=true` to force a live refresh of the listed accounts from the
Steam Web API (`GetPlayerSummaries` + `GetFriendList`) before returning. The
refreshed rows are persisted to the `steam_profiles` table and returned in the
response with `last_updated` set to the current time. Refresh requests are
rate limited and capped at 100 account ids per call to stay inside the
shared Steam Web API key budget.

See: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetPlayerSummaries_(v0002)

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s (read path), 3req/min + 15req/h (refresh) |
| Key | - (read path), 10req/min + 60req/h (refresh) |
| Global | - (read path), 30req/min + 200req/h (refresh) |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_ids` | `query` | Yes | `array` | Comma separated list of account ids, Account IDs are in `SteamID3` format. |
| `refresh` | `query` | No | `boolean` | Refresh the listed profiles from the Steam Web API before returning. |

### Responses
- **200**: Steam Profiles
- **400**: Provided parameters are invalid.
- **404**: No Steam profile found.
- **429**: Rate limit exceeded (only enforced when refresh=true).
- **500**: Failed to fetch steam profiles.
- **502**: Steam Web API call failed (only when refresh=true).

---

## [GET] /v1/players/steam-search
**Summary:** Steam Profile Search

**Tags:** Steam

**Description:**
This endpoint lets you search for Steam profiles by account_id or personaname.

See: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetPlayerSummaries_(v0002)

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `search_query` | `query` | Yes | `string` | Search query for Steam profiles. |
| `limit` | `query` | No | `integer / null` | Maximum number of profiles to return. |
| `min_matches_played_last_30d` | `query` | No | `integer / null` | Only return profiles that have played at least this many matches in the last 30 days. Defaults to 5 to filter out inactive/empty profiles and keep search responsive. |
| `min_last_team_avg_badge` | `query` | No | `integer / null` | Only return profiles whose `last_team_avg_badge` is at least this value. Defaults to 0 (no filter). Profiles with no recorded badge are stored as 0 and are excluded when this is set above 0. |
| `matches_played_weight` | `query` | No | `number / null` | Weight applied to `log1p(matches_played_last_30d)` when reranking candidates. The final score per profile is `jaro_winkler(personaname_lc, query) + weight * log1p(matches_played)`. Set to 0 to rank purely by string similarity; raise it to bias toward active/popular players. |

### Responses
- **200**: Steam Profile Search
- **400**: Provided parameters are invalid.
- **404**: No Steam profiles found.
- **500**: Failed to fetch steam profiles.

---

## [GET] /v1/players/{account_id}/account-stats
**Summary:** Account Stats

**Tags:** Players

**Description:**
This endpoint returns the player account stats for the given `account_id`.

!THIS IS A PATREON ONLY ENDPOINT!

You have to be friend with one of the bots to use this endpoint.
On first use this endpoint will return an error with a list of invite links to add the bot as friend.
From then on you can use this endpoint.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Messages:
- CMsgClientToGcGetAccountStats
- CMsgAccountStats

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 5req/min |
| Key | 20req/min & 800req/h |
| Global | 200req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **403**: Account is not a Patreon subscriber or not prioritized.
- **429**: Rate limit exceeded
- **500**: Fetching account stats failed

---

## [GET] /v1/players/{account_id}/card
**Summary:** Card

**Tags:** Players

**Description:**
This endpoint returns the player card for the given `account_id`.

!THIS IS A PATREON ONLY ENDPOINT!

You have to be friend with one of the bots to use this endpoint.
On first use this endpoint will return an error with a list of invite links to add the bot as friend.
From then on you can use this endpoint.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Messages:
- CMsgClientToGcGetProfileCard
- CMsgCitadelProfileCard

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 5req/min |
| Key | 20req/min & 800req/h |
| Global | 200req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **403**: Account is not a Patreon subscriber or not prioritized.
- **429**: Rate limit exceeded
- **500**: Fetching card failed

---

## [GET] /v1/players/{account_id}/enemy-stats
**Summary:** Enemy Stats

**Tags:** Players

**Description:**
This endpoint returns the enemy stats.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `min_matches_played` | `query` | No | `integer / null` | Filter based on the number of matches played. |
| `max_matches_played` | `query` | No | `integer / null` | Filter based on the number of matches played. |

### Responses
- **200**: Enemy Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch enemy stats

---

## [GET] /v1/players/{account_id}/match-history
**Summary:** Match History

**Tags:** Players

**Description:**
This endpoint returns the player match history for the given `account_id`.

If the account is friends with one of our bots, the match history is a combination of the data from **Steam** and **ClickHouse**, so you always get the most up-to-date data and full history.
If the account is not friends with a bot, only the stored match history from **ClickHouse** is returned.

Protobuf definitions can be found here: [https://github.com/SteamDatabase/Protobufs](https://github.com/SteamDatabase/Protobufs)

Relevant Protobuf Messages:
- CMsgClientToGcGetMatchHistory
- CMsgClientToGcGetMatchHistoryResponse

### Rate Limits (only applies to bot friends):
| Type | Limit |
| ---- | ----- |
| IP | 100req/s<br>Bot-Friend: 10req/h<br>With `force_refetch=true`: 1req/h |
| Key | -<br>Bot-Friend: 300req/h<br>With `force_refetch=true`: 5req/h |
| Global | -<br>Bot-Friend: 1500req/h<br>With `force_refetch=true`: 10req/h |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |
| `force_refetch` | `query` | No | `boolean` | Refetch the match history from Steam, even if it is already cached in `ClickHouse`. Only use this if you are sure that the data in `ClickHouse` is outdated. Enabling this flag results in a strict rate limit. |

### Responses
- **200**: 
- **400**: Provided parameters are invalid.
- **429**: Rate limit exceeded. Returns stored match history from ClickHouse as a fallback. When `force_refetch=true`, returns an error instead.
- **500**: Fetching player match history failed

---

## [GET] /v1/players/{account_id}/mate-stats
**Summary:** Mate Stats

**Tags:** Players

**Description:**
This endpoint returns the mate stats.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |
| `game_mode` | `query` | No | `` | Filter matches based on their game mode. Valid values: `normal`, `street_brawl`. **Default:** `normal`. |
| `min_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `max_unix_timestamp` | `query` | No | `integer / null` | Filter matches based on their start time (Unix timestamp). |
| `min_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `max_duration_s` | `query` | No | `integer / null` | Filter matches based on their duration in seconds (up to 7000s). |
| `min_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `max_match_id` | `query` | No | `integer / null` | Filter matches based on their ID. |
| `min_matches_played` | `query` | No | `integer / null` | Filter based on the number of matches played. |
| `max_matches_played` | `query` | No | `integer / null` | Filter based on the number of matches played. |
| `same_party` | `query` | No | `boolean` | Filter based on whether the mates were on the same party. Two players are considered to be in the same party if they were on the same team and are Steam friends as of the match start time (per the `steam_profiles` friends list). |

### Responses
- **200**: Mate Stats
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch mate stats

---

## [GET] /v1/players/{account_id}/mmr-history
**Summary:** MMR History

**Tags:** MMR

**Description:**
Player MMR History

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |

### Responses
- **200**: MMR History
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch mmr history

---

## [GET] /v1/players/{account_id}/mmr-history/{hero_id}
**Summary:** Hero MMR History

**Tags:** MMR

**Description:**
Player Hero MMR History

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |
| `hero_id` | `path` | Yes | `integer` | The hero ID to fetch the MMR history for. See more: <https://api.deadlock-api.com/v1/assets/heroes> |

### Responses
- **200**: Hero MMR History
- **400**: Provided parameters are invalid.
- **500**: Failed to fetch hero mmr history

---

## [GET] /v1/players/{account_id}/rank-predict
**Summary:** Rank Predict

**Tags:** Players

**Description:**
Predicts a player's current rank badge from their last 30 ranked/unranked matches.
Requires at least 30 eligible matches (Ranked or Unranked, Normal game mode) with valid badge data.

> **This is an ML prediction and may be inaccurate.** The model has no access to the player's
> actual hidden MMR — it infers rank from match context signals only.

### Model Accuracy (5-fold cross-validation)

| Metric | Value |
|--------|-------|
| R²     | 0.949 |
| MAE    | 1.08 sub-ranks |
| RMSE   | 1.89 sub-ranks |
| Within ±1 sub-rank | 77.6% |
| Within ±3 sub-rank | 93.9% |
| Within ±5 sub-rank | 97.7% |
| Within ±6 sub-rank | 98.6% |
| Within ±10 sub-rank | 99.6% |

Accuracy by tier:

| Tier range | n | MAE |
|------------|---|-----|
| Low (1-4)  | 404 | 3.68 sub-ranks |
| Mid (5-7)  | 777 | 2.91 sub-ranks |
| High (8-11)| 25,556 | 0.98 sub-ranks |

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |

### Responses
- **200**: 
- **400**: Invalid account ID
- **403**: User is protected or endpoint unavailable
- **422**: Not enough recent ranked matches (need 30)
- **429**: Rate limit exceeded
- **500**: Prediction failed
- **503**: Rank prediction model not loaded

---

## [GET] /v1/players/{account_id}/rank-predict/image
**Summary:** Rank Predict Image

**Tags:** Players

**Description:**
Returns the predicted rank badge image directly (binary), not a URL. Use `?format=webp` for WebP and `?size=small` for the small badge (defaults to large).

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `account_id` | `path` | Yes | `integer` | The players `SteamID3` |
| `format` | `query` | No | `string` | Image format. Defaults to `png`. Supported: `png`, `webp`. |
| `size` | `query` | No | `string` | Image size. Defaults to `large`. Supported: `large`, `small`. |

### Responses
- **200**: Predicted rank badge image
- **400**: Invalid account ID
- **403**: User is protected or endpoint unavailable
- **404**: No image available for the predicted rank
- **422**: Not enough recent ranked matches (need 30)
- **429**: Rate limit exceeded
- **500**: Prediction failed
- **503**: Rank prediction model not loaded

---

## [GET] /v1/servers
**Summary:** List Game Servers

**Tags:** Servers

**Description:**
Returns all currently active game servers.

### Responses
- **200**: 

---

## [POST] /v1/servers/metrics
**Summary:** Game Server Metric Ingest

**Tags:** Servers

**Description:**
Ingests a single metric event reported by a game server. The schema is intentionally
flexible: `metric_value` carries the primary numeric measurement and `metadata` holds
arbitrary key/value context that varies per game mode or metric. Optional `map` and
`game_mode_version` let callers segment leaderboards per map or per ruleset revision.
Requires a valid game server secret as a Bearer token.

### Responses
- **202**: Metric accepted for ingestion.
- **400**: Invalid request body.
- **401**: Invalid or missing game server secret.

---

## [POST] /v1/servers/status
**Summary:** Game Server Status

**Tags:** Servers

**Description:**
Reports the current status of a game server.
Game servers must call this endpoint at least once every 30 seconds to remain active.
Requires a valid game server secret as a Bearer token.

### Responses
- **200**: 
- **400**: Invalid request body.
- **401**: Invalid or missing game server secret.

---

## [GET] /v1/servers/steam
**Summary:** List Steam Game Servers

**Tags:** Servers

**Description:**
Returns the list of Deadlock game servers registered with the Steam master server
(`IGameServersService/GetServerList`), filtered to Deadlock's appid.

### Responses
- **200**: 
- **500**: Fetching the Steam server list failed.

---

## [GET] /v1/sql
**Summary:** Query

**Tags:** SQL

**Description:**
Executes a SQL query on the database.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 2req/min, 20req/hr |
| Key | 10req/min |
| Global | 30req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `query` | `query` | Yes | `string` | The SQL query to execute. It must follow the Clickhouse SQL syntax. |
| `format` | `query` | No | `` | The response format. Valid values: `json` (a JSON array), `ndjson` (newline-delimited JSON objects). |

### Responses
- **200**: 
- **500**: 

---

## [GET] /v1/sql/tables
**Summary:** List Tables

**Tags:** SQL

**Description:**
Lists all tables in the database.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/min |
| Key | - |
| Global | 60req/min |

### Responses
- **200**: 
- **500**: 

---

## [GET] /v1/sql/tables/{table}/schema
**Summary:** Table Schema

**Tags:** SQL

**Description:**
Returns the schema of a table.

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 10req/min |
| Key | - |
| Global | 60req/min |

### Parameters
| Name | In | Required | Type | Description |
| ---- | -- | -------- | ---- | ----------- |
| `table` | `path` | Yes | `string` | The name of the table to fetch the schema for. |

### Responses
- **200**: 
- **500**: 

---

## [GET] /v2/patches
**Summary:** Notes

**Tags:** Patches

**Description:**
Returns a unified feed combining patch notes from the official Forum changelog and the Steam news feed.

Each entry is tagged with a `source` field (`forum` or `steam`).

- Forum RSS: https://forums.playdeadlock.com/forums/changelog.10/index.rss
- Steam News RSS: https://store.steampowered.com/feeds/news/app/1422450/

### Rate Limits:
| Type | Limit |
| ---- | ----- |
| IP | 100req/s |
| Key | - |
| Global | - |

### Responses
- **200**: 
- **500**: Fetching or parsing one of the RSS feeds failed

---

