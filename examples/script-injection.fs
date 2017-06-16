#!/usr/bin/env webfriend

# navigate to Hacker News
go "https://news.ycombinator.com"

# set a list of patterns for text to extract from the page
# this is used by the injected script below
$terms = [
    '/(\d+) points/',
]

# inject and execute this JavaScript. Scripts are wrapped in a dynamically-generated
# function that lives on the "window" object.  Values returned from the injected script
# will be converted to native types and be accessible as the command's return value
#
# Everything between the 'begin' and 'end' keywords will be passed to the browser.
#
javascript begin
    if(this.terms) {
        // we're going to start walking from the <body> tag down
        var bodyTag = document.getElementsByTagName('body')[0];
        var walker = document.createTreeWalker(bodyTag, NodeFilter.SHOW_TEXT, null, false);
        var patterns = [];

        // parse incoming terms into patterns or exact string matches
        for(var i = 0; i < this.terms.length; i++) {
            var term = this.terms[i];

            if(term.length > 2 && term.indexOf('/') == 0 && term.lastIndexOf('/') > 0) {
                var rx = term.slice(1, term.lastIndexOf('/'));
                var opts = term.slice(term.lastIndexOf('/') + 1);

                patterns.push(new RegExp(rx, opts));
            } else {
                patterns.push(term);
            }
        }

        var results = [];

        // iterate through all text nodes on the page
        while(node = walker.nextNode()) {
            // for each pattern...
            for(var i = 0; i < patterns.length; i++) {
                var pattern = patterns[i];

                if(pattern instanceof RegExp) {
                    // if it's a regular expression, apply it
                    var match = node.nodeValue.match(pattern);

                    if(match) {
                        if(match.length > 1) {
                            // if groups were used, add each result
                            match = match.slice(1);

                            for(var j = 0; j < match.length; j++) {
                                results.push(parseInt(match[j]));
                            }
                        } else {
                            // otherwise, use the whole match
                            results.push(match[0]);
                        }

                        break;
                    }
                } else if(node.nodeValue == pattern) {
                    // otherwise, exact matches only
                    results.push(node.nodeValue);
                    break;
                }
            }
        }

        // return results
        return results;
    } else {
        throw 'Must provide a list of terms in the $terms variable.';
    }
end -> $matches

# show the result of the script execution
log $matches
