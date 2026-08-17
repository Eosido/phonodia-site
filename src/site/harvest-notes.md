# Harvest notes — phonodiavocalensemble.com

Date: 2026-08-13. Tool: WebFetch only (no bash/curl), as instructed.

## The blocking constraint: query strings are stripped in transit

This is the single most important finding, and it invalidates the pagination plan in the brief.

**Every query string is discarded before the request reaches WordPress.** `per_page`, `page`,
`_fields`, `slug`, `offset`, `orderby` and `include` all have no effect. Evidence:

| Request | Expected | Actual |
|---|---|---|
| `/wp/v2/pages?per_page=3&page=1&_fields=id,slug,link` | 3 items, 3 fields | worked once, then stopped |
| `/wp/v2/pages?per_page=15&page=1` vs `?per_page=15&page=2` | different items | **byte-identical responses** |
| `/wp/v2/pages?_fields=id&per_page=40&orderby=id&order=asc` | up to 40 ids, ascending | 3 items, date-descending |
| `/wp/v2/pages?slug=store&_fields=id,slug` | 1 object, 2 fields | same default 3 objects, all fields |
| `/wp-json/?_fields=name,description,...` | only requested keys | full root object, truncated before `routes` |

On top of that, the fetch layer **truncates the response body** at roughly the size of three
full page objects, so even the default `per_page=10` listing only ever yields ~3 items.

Consequences:
- Pages cannot be paginated. Only ~3 of 30 page objects are reachable from the collection.
- Page IDs cannot be looked up by slug, so path-addressed `/wp/v2/pages/<id>` (which *does* work)
  could only be used for the 5 IDs discovered incidentally.
- `X-WP-Total` / `X-WP-TotalPages` headers are not exposed by WebFetch, so exact totals are unknown.

### Workarounds used
1. **XML sitemaps** (`/wp-sitemap.xml` and its children) — path-only, small, complete. These gave
   the full URL inventory for pages, posts, products and all five js_* custom post types.
2. **Path-addressed REST** — `/wp/v2/pages/<id>` returns a complete, verbatim object.
3. **WooCommerce Store API** — `wc/store/v1/products` is public, path-only, and returned the whole
   9-product catalogue. (The brief said not to attempt `wc/v3`, which needs auth; `wc/store/v1` is a
   different, unauthenticated namespace.)
4. **Rendered-page fetches** — WebFetch's markdown conversion preserves `<img>` URLs, so the live
   HTML was used to recover image placement.

## A second caution: the summariser fabricates

The model behind WebFetch invented data on the first attempt — it returned a `pages` response
containing keys that do not exist in the WP REST schema (`featured_products`, `products[]`, `price`,
`date_published`). Every subsequent prompt therefore included an explicit instruction to copy
character-for-character and to invent nothing. All JSON saved here comes from responses that
survived that constraint. Treat any figure not present in these files as unverified.

## Endpoint status

| Endpoint | Result |
|---|---|
| `/wp-json/` | 200, captured (truncated before `routes`) |
| `/wp-json/wp/v2/types` | 200, complete |
| `/wp-json/wp/v2/pages` | 200, truncated to 3 of ~30 |
| `/wp-json/wp/v2/pages/2940` | 200, complete and verbatim |
| `/wp-json/wp/v2/posts` | 200, truncated to 1 of 2 |
| `/wp-json/wp/v2/media` | 200, truncated to 5 |
| `/wp-json/wp/v2/product` | registered (`rest_base: product`) but listing truncates |
| `/wp-json/wc/store/v1/products` | 200, complete — all 9 |
| `/wp-json/wp/v2/menu-items` | **401** |
| `/wp-json/wp/v2/menus` | **401** (same as menu-items) |
| `/wp-json/wp/v2/settings` | **401** |
| `/wp-json/wp/v2/js_events` | **404** |
| `/wp-json/wp/v2/js_artist` | **404** |
| `/wp-json/wp/v2/js_videos` | **404** |
| `/wp-json/wp/v2/js_photo_albums` | **404** |
| `/wp-json/wp/v2/js_albums` | **404** |
| `/feed/` | returned gzip binary, unreadable by the fetch layer |

## Incidental findings

- There is a **fifth** theme custom post type, `js_albums`, not named in the brief.
- The front page's own markup links to **`phonodia.com`** (`/el/events/`, `/el/about/`) and loads its
  hero video from `phonodia.com` / `cdn.phonodia.com` — a different domain from the one harvested.
- Site is on Bluehost/Newfold with Jetpack Boost, Wordfence, WPBakery (`vc_*` shortcodes),
  Slider Revolution, AIOSEO, Polylang and WooCommerce (Vivacom Smart payment gateway).
- REST namespace list includes `mcp` and `wp-abilities/v1`.
- Front-page and members content is built with WPBakery shortcodes that are *not* expanded in
  `content.rendered` — the raw `[vc_row]…` shortcodes appear literally, so grids of events, members
  and media resolve only in the browser.
