from app.schemas.client import ClientCreate
import json

# Test 1: Bezpośrednia walidacja Pydantic
print("=== Test 1: Bezpośrednia walidacja Pydantic ===")
try:
    client = ClientCreate(
        archetype="A" * 101,
        tags=["test"],
        notes="Test walidacji"
    )
    print(f"Utworzono klienta: {client}")
except Exception as e:
    print(f"Błąd walidacji: {e}")

# Test 2: Walidacja z JSON (jak FastAPI)
print("\n=== Test 2: Walidacja z JSON (jak FastAPI) ===")
json_data = {
    "archetype": "A" * 101,
    "tags": ["test"],
    "notes": "Test walidacji"
}

try:
    client = ClientCreate(**json_data)
    print(f"Utworzono klienta z JSON: {client}")
except Exception as e:
    print(f"Błąd walidacji z JSON: {e}")

# Test 3: model_dump
print("\n=== Test 3: model_dump ===")
try:
    client = ClientCreate(
        archetype="A" * 50,  # Poprawna długość
        tags=["test"],
        notes="Test walidacji"
    )
    print(f"model_dump(): {client.model_dump()}")
except Exception as e:
    print(f"Błąd: {e}")