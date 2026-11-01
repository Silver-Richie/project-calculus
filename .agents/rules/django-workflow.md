# Django Development Rules

## Running Python & Django Commands
- The project environment is stored locally in `env/`.
- All Python commands must execute through `.\env\Scripts\python.exe` on Windows.
- Always run `.\env\Scripts\python.exe manage.py check` after modifying settings or models.

## Database & Models
- Run `.\env\Scripts\python.exe manage.py makemigrations` and `.\env\Scripts\python.exe manage.py migrate` whenever modifying models.
- Maintain backward compatibility in database migrations.

## Code Conventions
- Use descriptive view and route names.
- Keep business logic in appropriate modules/services, keeping views concise.
