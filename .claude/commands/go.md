# Go - Execute Next TDD Cycle

Find the next test in plan.md and implement it following TDD.

## Workflow

1. **Read plan.md** - Find the next unmarked test
2. **Red Phase** - Write a failing test
3. **Run tests** - Confirm it fails
4. **Green Phase** - Write minimum code to pass
5. **Run tests** - Confirm all pass
6. **Mark complete** - Update plan.md with [x]
7. **Consider refactoring** - If needed, enter refactor phase

## Rules

- ONE test at a time
- Minimum code to pass
- Run tests after each phase
- Mark progress in plan.md

## Output Format

After completing:
```
Completed: [test name]
Status: [Red -> Green -> Refactored (if applicable)]
Next: [next test in plan.md or "All tests complete"]
```
