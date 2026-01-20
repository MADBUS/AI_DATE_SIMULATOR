# Commit - Create a Git Commit

Create a commit following TDD commit discipline.

## Prerequisites
- ALL tests must be passing
- ALL compiler/linter warnings resolved

## Commit Types

### Behavioral Commit (feat/fix)
For changes that add or modify functionality:
```
feat: [description of new behavior]
fix: [description of bug fix]
```

### Structural Commit (refactor/style)
For changes that don't alter behavior:
```
refactor: [description of structural change]
style: [formatting, naming changes]
```

## Instructions

1. Run all tests - confirm passing
2. Check for warnings - resolve any issues
3. Stage changes with `git add`
4. Create commit with appropriate type prefix
5. Keep commits small and focused

## Commit Message Format
```
[type]: [short description]

[optional body with more details]

[optional footer]
```

## Checklist
- [ ] All tests passing
- [ ] No warnings
- [ ] Commit type matches change type (behavioral vs structural)
- [ ] Message is clear and concise
