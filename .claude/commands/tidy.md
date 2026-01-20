# Tidy First - Structural Changes Only

Make structural improvements without changing behavior.

## What is Tidy First?

Separate structural changes from behavioral changes:
- **Structural**: Renaming, extracting, moving, formatting
- **Behavioral**: Adding features, fixing bugs, changing logic

## Instructions

1. Ensure all tests pass BEFORE starting
2. Identify ONE structural improvement
3. Make the change
4. Run tests - they MUST still pass
5. Commit with `refactor:` or `style:` prefix
6. Repeat if more tidying needed

## Tidy Patterns

- **Guard Clauses**: Replace nested conditionals with early returns
- **Extract Helper**: Pull out reusable logic
- **Cohesion Order**: Group related code together
- **Reading Order**: Arrange code in logical reading order
- **Explaining Variables**: Name complex expressions
- **Remove Dead Code**: Delete unused code

## Rules

- NEVER change behavior during tidy
- ALWAYS run tests after each change
- COMMIT structural changes separately
- ONE change at a time

## Checklist
- [ ] Tests passing before tidy
- [ ] Made structural change only
- [ ] Tests still passing after
- [ ] Committed separately from behavioral changes
