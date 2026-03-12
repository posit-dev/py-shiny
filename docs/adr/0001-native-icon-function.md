# Native Icon Function for py-shiny

## Status

Proposed

## Context and Problem Statement

py-shiny currently requires the external `faicons` package to use icons in UI components like buttons and value boxes. This creates friction for users who need to install an additional dependency for a common use case. How should py-shiny provide native icon support while balancing package size, maintenance burden, and user experience?

## Decision Drivers

* Users find it irritating to install a separate package for basic icon functionality
* Icons are commonly used in buttons, value boxes, toolbars, and other UI components
* FontAwesome and Bootstrap Icons cover the vast majority of use cases
* py-shiny package size should remain reasonable
* The solution should be maintainable and stay current with icon library updates
* Consistency with existing py-shiny API patterns

## Considered Options

1. **Bundle full icon sets** - Ship JSON files containing all FontAwesome and Bootstrap icon data (~4-5MB)
2. **Bundle curated subset** - Ship a hand-picked selection of ~200-300 popular icons (~100KB)
3. **Thin wrapper** - Provide a unified `icon()` API that delegates to external packages, bundling only Bootstrap Icons

## Decision Outcome

Chosen option: **Thin wrapper**, because it keeps py-shiny lean, avoids duplicating data that already exists in `faicons`, and leverages maintained external packages for FontAwesome icons while bundling the smaller Bootstrap Icons set directly.

### Positive Consequences

* Minimal package size increase (~1.5MB for Bootstrap Icons only)
* FontAwesome icons stay up-to-date via the `faicons` package
* No duplicate icon data if user already has `faicons` installed
* Unified API regardless of which icon library is used
* Clear error message guides users to install `faicons` when needed

### Negative Consequences

* FontAwesome icons require installing `faicons` package
* Users may encounter ImportError on first use if `faicons` is not installed
* Slight inconsistency: Bootstrap Icons work out of the box, FontAwesome requires extra step

## Pros and Cons of the Options

### Bundle Full Icon Sets

Store all icon SVG data in JSON files shipped with py-shiny.

* Good, because all icons work without external dependencies
* Good, because simple "it just works" user experience
* Bad, because adds 4-5MB to package size
* Bad, because duplicates data if user also has `faicons` installed
* Bad, because icon data may become stale between py-shiny releases

### Bundle Curated Subset

Ship a hand-picked selection of commonly used icons as Python dictionaries.

* Good, because small size impact (~100KB)
* Good, because no external dependencies for included icons
* Bad, because users will inevitably need icons not in the subset
* Bad, because no objective way to determine "popular" icons
* Bad, because requires ongoing curation and user requests to add icons
* Bad, because frustrating user experience when requested icon is missing

### Thin Wrapper

Provide a unified `icon()` function that delegates to `faicons` for FontAwesome and bundles Bootstrap Icons directly.

* Good, because minimal size increase (~1.5MB for Bootstrap Icons)
* Good, because FontAwesome icons stay current via `faicons` maintainers
* Good, because no duplicate data
* Good, because unified API across icon libraries
* Good, because Bootstrap Icons are MIT licensed and natural fit for Bootstrap-based py-shiny
* Bad, because FontAwesome requires extra `pip install faicons`
* Bad, because slightly worse DX for FontAwesome (ImportError until package installed)

## Links

* [GitHub Issue #2159](https://github.com/posit-dev/py-shiny/issues/2159) - Original feature request
* [py-faicons](https://github.com/posit-dev/py-faicons) - Existing FontAwesome package for Python/Shiny
* [bsicons](https://github.com/rstudio/bsicons) - R package for Bootstrap Icons (API reference)
* [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library documentation
* [FontAwesome](https://fontawesome.com/icons) - Icon library documentation
