Use test-driven development when implementing features or behavior
changes in this repository.

The expected workflow is:

1. Create the smallest useful skeleton for the new behavior. Define
   the classes, functions, and methods that are expected to exist.
   Where behavior is not implemented yet, raise `NotImplementedError`.
2. Write unit tests for the desired behavior before implementing that
   behavior. These are the red tests. Run the relevant tests and
   verify that they fail for the expected reason.
3. Implement the behavior. This is the green phase. Keep the
   implementation focused on making the red tests pass, without
   adding speculative generality.
4. Run the relevant tests again and verify that they pass.
5. Refactor only after the tests are green, and rerun the relevant
   tests after refactoring.

Do not skip the red phase when implementing a feature unless Sumanth
explicitly says to do so for that specific change.

For very small bug fixes, a new test may be omitted when Sumanth says
that the test would not add enough value. Still make the behavior
change deliberately and run the relevant existing tests.

When running unit tests, follow `prompts/unittests.md`.
