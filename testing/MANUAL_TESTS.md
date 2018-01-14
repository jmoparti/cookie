# Manual testing

Despite the [automated test harness](AUTOMATED_TESTS.md), there are still some flavors of testing
that need to be done manually.

## General tips 

Use the following makefile targets from the automated test suite (see [its docs for details](AUTOMATED_TESTS.md)) to
repeatably setup guinea pigs for manual testing:

* `run_cookiecutter_with_input`
* `run_cookiecutter_wout_input`

## Testing Travis configs

Run the `test_travis_env` makefile target from the automated test suite (see [its docs for details](AUTOMATED_TESTS.md)).

This will lay down several projects under the `<repo>/testing/output/travis-*` directories, and you can use them as guinea pigs.

Take on of them that does a deploy to our internal repos and do the following general steps:

1. Create a repo named "sysops-boilerplate" in your personal EC github org
   * Create a 'develop' branch in that repo
1. Clone that repo to your local box and update the 'develop' branch with the project emitted by the cookiecutter
   * Copy over the files from the `<cookiecutter-repo>/testing/output/travis-*` directory you want to use as the basis for this
   * Use one that has the 'managed dependencies and py27 only' in its combo of settings
   * Update the VERSION file to contain a test version based on the current day's date
     * Format `YYYY.MM.DD.N`
       * YYYY - 4 digit year
       * MM - 2 digit month
       * DD - 2 digit day
       * N - ascending positive integer
     * For example `2017.09.26.1`
   * Commit all of this to the 'develop' branch in your local clone and push back to your ec github origin 
1. Go to EC Travis and activate this repo with travis
   * Mark it as 'does not build if no travis.yml'
   * Mark is as 'build on push'
   * Mark is as 'build on pull request'
   * Mark it to limit concurrency to 1 job at a time
1. Test the travis behavior for a pull request
   * Create a pull request in your boilerplate repo from its develop to master
   * Self merge it
   * Monitor the travis builds to make sure things happen according to plan
     * A standard build should succeed
     * No deploy should happen
1. Test the travis behavior for a 'tag created' event
   * Create a github release off of master branch in your boilerplate repo 
   * Self merge
   * Monitor the travis builds to make sure things happen according to plan
     * A standard build should succeed
     * A deploy should happen
   * On your local box, do a test install into a virtualenv with the version you used to build the deployed wheel
     * Example : `cd ~/tmp && virtualenv test-venv && source test-venv/bin/activate && pip install sysops-boilerplate==2017.09.26.1`
1. Clean up after yourself
   * Go to EC Travis and deactivate this repo with travis
