Urban Airship API Utilities
===========================

Currently just provides a simple ``ua`` command line tool with a single sub-command:

.::

        ua get-tokens $APP_KEY $UA_SECRET

You can also set your secret as an environment variable:

.::

        UA_SECRET=... ua get-tokens $APP_KEY

And control the filename:

.::

       UA_SECRET=... ua get-tokens $APP_KEY -o some-new-file.json
       UA_SECRET=... ua get-tokens $APP_KEY -o - | gzip > yet-another-file.json.gz


Installing
++++++++++

In a virtualenv in safest (if you have virtualenv installed):

.::

        virtualenv ua-api-utils
        cd ua-api-utils
        . bin/activate
        pip install ua-api-utils

Or in your ``$HOME`` directory if you have your user-site in your ``$PATH``:

.::

        pip install --user ua-api-utils

And of course, there's always sudo to install it globally:

.::

        sudo pip install ua-api-utils

