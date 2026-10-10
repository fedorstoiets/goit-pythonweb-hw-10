$ErrorActionPreference = "Stop"

Write-Host "=== HW10 quick verification ==="

Write-Host "`n1. Docker services"
docker compose ps

Write-Host "`n2. Root endpoint"
Invoke-RestMethod http://127.0.0.1:8000/

Write-Host "`n3. Health endpoint"
Invoke-RestMethod http://127.0.0.1:8000/health

Write-Host "`n4. Alembic current"
docker compose exec app alembic current

Write-Host "`n5. Swagger URL"
Write-Host "http://127.0.0.1:8000/docs"

Write-Host "`n6. Mailpit URL"
Write-Host "http://127.0.0.1:8025"

Write-Host "`nQuick verification complete."
