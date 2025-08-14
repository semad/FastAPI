# Database Model Unit Tests

This directory contains comprehensive unit tests for all database models in the FastAPI application. Each model has its own test file that covers CRUD operations, validation, relationships, and edge cases.

## Test Coverage

### Models Tested

| Model | Test File | Status | Coverage |
|-------|-----------|---------|----------|
| **User** | `test_user.py` | ✅ Complete | CRUD, validation, relationships |
| **Book** | `test_book.py` | ✅ Complete | CRUD, validation, relationships |
| **Post** | `test_post.py` | ✅ Complete | CRUD, validation, relationships |
| **Tier** | `test_tier.py` | ✅ Complete | CRUD, validation, relationships |
| **RateLimit** | `test_rate_limit.py` | ✅ Complete | CRUD, validation, relationships |

### Test Categories

Each model test file includes the following test categories:

#### 1. **Write Operations (Create)**
- ✅ Successful creation with valid data
- ✅ Creation with minimal required data
- ✅ Creation with optional fields
- ✅ Duplicate constraint validation
- ✅ Foreign key constraint validation
- ✅ Data type validation

#### 2. **Read Operations (Retrieve)**
- ✅ Retrieval by primary key (ID)
- ✅ Retrieval by unique fields (UUID, name, etc.)
- ✅ Retrieval of non-existent records
- ✅ Bulk retrieval (get_multi)
- ✅ Filtered retrieval by relationships

#### 3. **Update Operations**
- ✅ Successful updates with complete data
- ✅ Partial updates (only specific fields)
- ✅ Update validation and constraints
- ✅ Timestamp updates verification

#### 4. **Delete Operations**
- ✅ Successful hard deletion
- ✅ Soft deletion (where applicable)
- ✅ Deletion of non-existent records
- ✅ Cascade behavior testing

#### 5. **Validation & Constraints**
- ✅ Required field validation
- ✅ Data type validation
- ✅ Length constraints
- ✅ Unique constraints
- ✅ Foreign key constraints

#### 6. **Relationships**
- ✅ Foreign key relationships
- ✅ Cascade behavior
- ✅ Relationship integrity
- ✅ Cross-model queries

## Running Tests

### Prerequisites

1. **Install test dependencies:**
   ```bash
   pip install pytest pytest-asyncio pytest-cov faker
   ```

2. **Database setup:**
   - Ensure PostgreSQL is running
   - Database connection configured in `conftest.py`
   - Test database accessible

### Test Execution

#### Run All Tests
```bash
# Run all model tests
python tests/run_all_tests.py

# Run with verbose output
python tests/run_all_tests.py --verbose

# Run with coverage report
python tests/run_all_tests.py --coverage
```

#### Run Specific Model Tests
```bash
# Test specific models
python tests/run_all_tests.py --models user,book

# List available models
python tests/run_all_tests.py --list-models
```

#### Run Individual Test Files
```bash
# Test specific model
pytest tests/test_user.py -v

# Test with coverage
pytest tests/test_user.py --cov=src/app/models/user --cov-report=term-missing
```

#### Run with pytest directly
```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_user.py::TestWriteUser -v

# Run specific test method
pytest tests/test_user.py::TestWriteUser::test_create_user_success -v
```

## Test Structure

### Fixtures
Each test file includes reusable fixtures:
- `sample_*_data`: Sample data for model creation
- `sample_*_read`: Sample read objects for testing
- `sample_*`: Sample related objects (e.g., `sample_user` for post tests)

### Test Classes
Tests are organized into logical classes:
- `TestWrite*`: Creation operations
- `TestRead*`: Retrieval operations  
- `TestUpdate*`: Update operations
- `TestDelete*`: Deletion operations
- `Test*Validation`: Validation and constraints
- `Test*Relationships`: Relationship testing

### Async Testing
All tests use `pytest-asyncio` for async database operations:
- Database sessions are async
- CRUD operations are awaited
- Proper cleanup and rollback

## Test Data

### Faker Integration
Tests use the `faker` library to generate realistic test data:
- Names, emails, usernames
- Text content, URLs
- Random numbers and dates
- Consistent data across test runs

### Sample Data Patterns
```python
@pytest.fixture
def sample_user_data():
    return {
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }
```

## Database Testing

### Test Database
- Uses separate test database instance
- Async SQLAlchemy sessions
- Automatic cleanup between tests
- Transaction rollback for isolation

### CRUD Testing
Tests verify both:
- Model object creation/retrieval
- Database persistence
- Constraint enforcement
- Relationship integrity

## Coverage Reports

### Generate Coverage
```bash
# HTML coverage report
pytest --cov=src/app/models --cov-report=html

# Terminal coverage report
pytest --cov=src/app/models --cov-report=term-missing
```

### Coverage Targets
- **Model Coverage**: 100% for all models
- **CRUD Operations**: 100% for all operations
- **Validation**: 100% for all constraints
- **Relationships**: 100% for all foreign keys

## Best Practices

### Test Isolation
- Each test is independent
- Database state is reset between tests
- No shared state between test methods

### Assertion Patterns
```python
# Verify object creation
assert created_object is not None
assert created_object.field == expected_value

# Verify database persistence
db_object = await crud.get(db=async_db, id=created_object.id)
assert db_object is not None
assert db_object["field"] == expected_value
```

### Error Testing
```python
# Test expected exceptions
with pytest.raises(IntegrityError):
    await crud.create(db=async_db, object=invalid_object)
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL is running
   - Verify connection settings in `conftest.py`
   - Ensure test database exists

2. **Import Errors**
   - Check Python path includes `src/`
   - Verify all dependencies are installed
   - Check for circular imports

3. **Test Failures**
   - Review database constraints
   - Check model validation rules
   - Verify CRUD operation implementations

### Debug Mode
```bash
# Run with debug output
pytest tests/ -v -s --tb=long

# Run single test with debug
pytest tests/test_user.py::TestWriteUser::test_create_user_success -v -s
```

## Contributing

### Adding New Tests
1. Follow existing test patterns
2. Use descriptive test names
3. Include comprehensive assertions
4. Test both success and failure cases
5. Add fixtures for reusable data

### Test Naming Convention
- Test classes: `Test{Operation}{Model}` (e.g., `TestWriteUser`)
- Test methods: `test_{operation}_{scenario}` (e.g., `test_create_user_success`)
- Fixtures: `sample_{model}_{type}` (e.g., `sample_user_data`)

### Running Tests Before Committing
```bash
# Quick test run
python tests/run_all_tests.py

# Full test suite with coverage
python tests/run_all_tests.py --coverage --verbose
```

## Performance

### Test Execution Time
- **Individual model tests**: 2-5 seconds
- **Full test suite**: 10-20 seconds
- **With coverage**: 15-30 seconds

### Optimization Tips
- Use `pytest-xdist` for parallel execution
- Minimize database operations in fixtures
- Use appropriate test scopes
- Clean up resources promptly

## Continuous Integration

### CI/CD Integration
Tests are designed to run in CI/CD pipelines:
- No external dependencies
- Deterministic results
- Fast execution
- Clear failure reporting

### Pre-commit Hooks
Consider adding pre-commit hooks to run tests:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: run-tests
        name: Run Model Tests
        entry: python tests/run_all_tests.py
        language: system
        pass_filenames: false
```

---

For questions or issues with the tests, please refer to the main project documentation or create an issue in the project repository.

