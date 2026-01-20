# Red Phase - Write a Failing Test

Write a failing test for the next item in plan.md.

## Instructions

1. Read plan.md to find the next unmarked test
2. Write ONE failing test that:
   - Has a descriptive name (e.g., shouldReturnEmptyListWhenNoItems)
   - Tests ONE specific behavior
   - Fails for the right reason (not due to syntax errors)
3. Run the test to confirm it fails
4. Do NOT write any production code yet

## Test Structure

```
[Test]
public void Should[Action]When[Condition]()
{
    // Arrange

    // Act

    // Assert
}
```

## Checklist
- [ ] Test has a meaningful name
- [ ] Test is focused on one behavior
- [ ] Test fails as expected
- [ ] No production code written
