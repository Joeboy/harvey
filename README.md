# Harvey

This is a simple script I wrote to make submitting timesheets to harvest a bit
less painful. It's designed around my personal needs and preferences, you
might need to do a bit of work to make it work for you. Or just use it as a
reference for whatever you need to do. You're a developer, aren't you?

# Setup

* You'll need to be set up with an account at harvestapp.com.
* Get a personal access token from https://id.getharvest.com/developers
* rename settings.py.dist to settings.py
* Edit settings.py with your personal access token and other details

# Usage

Make a timesheet text file that looks something like this:

~~~~
Mon 2 March 2020-03-02
.5 SCOPE-13506: Make the broken thing not be broken anymore
5 SCOPE-13512: Break some more things
2.5 SCOPE-13003: Make some things different, but still broken


Tuesday 3 March 2020-03-03
.5 SCOPE-9801: Make tests fail
6.5 SCOPE-13003: Make tests pass; cause catastrophic errors in production instead
1 SCOPE-13004: Port application to Commodore Basic

...etc...
~~~~

Save it as eg. "work202003.txt" (it doesn't really matter what you call it)

To check it looks OK without submitting anything:

~~~~
python3 harvey.py --file ~/reckon/wfp/timesheets/work202003.txt
~~~~

If everything looks OK, submit it to harvest:

~~~~
python3 harvey.py --file ~/reckon/wfp/timesheets/work202003.txt --submit
~~~~

All being well, your timesheet entries should have been magically transferred to harvestapp.com

Haven't tried it in python 2, I suspect it'll work but will submit timesheets
in an arbitrary order. Just use python 3, it's 2020 (or if it isn't, it's
almost certainly no earlier).
