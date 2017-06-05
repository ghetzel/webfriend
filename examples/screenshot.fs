#!/usr/bin/env webfriend

# navigate to Hacker News
go "https://news.ycombinator.com" -> $www

log "Page loaded in {www[timing][requestTime]}ns"

# log the result of loading the page
log "URL {www[url]}: Loaded with HTTP {www[status]}"

# take a screenshot of the current page
page::screenshot "hackernews.png"

# and, while we're at it, retrieve all the cookies that we have, too
loop $cookie in cookies::all {
    log "[{index}] {cookie[name]}:"

    loop $k, $v in $cookie {
        log "  {k:13s} {v}"
    }
}
