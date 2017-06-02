#!/usr/bin/env webfriend

# navigate to Hacker News
go "https://news.ycombinator.com"

# log the result of loading the page
log "URL {result[url]}: Loaded with HTTP {result[status]}"

# take a screenshot of the current page
page::screenshot "hackernews.png"

# and, while we're at it, retrieve all the cookies that we have, too
for $cookie in cookies::all {
    log "[{index}] {cookie[name]}:"

    for $k, $v in $cookie {
        log "  {k:13s} {v}"
    }
}
