# How to build and test

## Building

A cookiecutter doesn't need to be "built" so much as pulled and applied by running an instance of the cookiecutter command line tool.

See the [usage doc](USAGE.md) for more details.

## Testing

Some of the testing has been automated, but much of it is still manual. 

Please see [the README for how to test the project](testing/README.md) for more details.

# Tracking issues

* The GitHub issues in this repo are used for tracking development sub-tasks
  and not for "customer" facing bug reports/feature requests.
* Instead, please make a JIRA issue (either "bug" or "new feature" type) in
  the "SI" JIRA project.
* Then drop a line into the ``#si`` slack channel requesting someone take a look
  at your issue.
* As time permits, someone from the SI Team will take a look and get back to you with
  feedback.  This **is not** a promise that work will instantly be done on it.
* If you want your bug fixed or your new feature then you have one of two options:
  * Lobby the product owner of the SI team for inclusion of this work into the product
    owner's agenda for sprint work.
  * Work up a candidate implementation yourself and submit a pull request against the
    ``develop`` branch of the repo, then lobby the product owner for SI team bandwidth
    to review your pull request.

# Pull requests

1. Your pull request should be based on the scope of a JIRA issue that you've
   already created (see above in "Tracking issues").
1. You should already have discussed your reason for the pull request with
   the SI team before creating it.
  * This is to avoid you wasting time working on a pull request when someone
    else might already be doing it, or when your proposal doesn't fit the
    goals of the project.
1. Your pull request must have a relevant "SI" project JIRA issue in its title.
1. Your pull request's description field  must show proof that you ran the full test suites somehow outside of Travis
   * This is because most of it cannot be run in the context of a travis build.
   * See the included instructions at the start of this doc about using Vagrant or the Spetsnaz OpenStack cluster to
     host your dev/test sandbox VMs.
1. Your pull request must pass all travis tests
1. You should drop a line in the ``#si`` slack channel reference your pull request and requesting a review.
