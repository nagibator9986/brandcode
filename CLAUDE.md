# UniConnect - Student-Teacher Communication App

## Project
BeeWare (Toga) mobile application for university internal communication.

## Run
```bash
cd uniconnect
pip install toga
python app.py
```

## Demo Accounts
- Admin: `admin` / `admin123`
- Teacher: `ivanov` / `teacher123`
- Student: `student1` / `student123`

## Architecture
- `config.py` - Colors, constants, configuration
- `database.py` - SQLite with schema + seed data
- `navigation.py` - Screen switching via window.content replacement
- `services/` - Business logic (auth, chat, announcements, schedule, users, admin)
- `widgets/` - Reusable UI components (card, top_bar, nav_bar, avatar, badge, etc.)
- `screens/` - All app screens organized by feature

## Conventions
- Screen pattern: `build_*_screen(nav, **kwargs)` returns `toga.Box`
- Layout: `outer(COLUMN) -> [top_bar, ScrollContainer(flex=1), nav_bar]`
- All colors from `config.COLORS`
- Services wrap DB queries; screens use services, never raw SQL
