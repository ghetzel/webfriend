#!/usr/bin/env webfriend

# navigate to Hacker News
go "https://news.ycombinator.com"

# take a screenshot of the current page
page::screenshot "hackernews.png"

# and, while we're at it, retrieve all the cookies that we have too
cookies::all -> $cookies
