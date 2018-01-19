#!/usr/bin/env webfriend

# navigate to Your Website's login form
go "https://yoursite.example.abc/login"

# type "username123" into the <input> tag with name="username"
field 'input[name="username"]' {
    value: 'username123',
}

# type "secret" into the <input> tag with name="password"
field 'input[name="password"]' {
    value: 'password',
}

# click the "Login" button
click 'input[type="submit"]'

# wait for the page load to complete
wait_for_load

# try to select an element on the page that will only exist
# if the login was successful.
#
# This will either succeed or emit an error and fail.
#
select 'something'
