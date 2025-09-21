# NFL Team Builder

NFL Team Builder is a Django web application that allows football fans to create, manage, and experiment with custom NFL teams and rosters. Users can build teams, assign players to roster spots, and explore different lineup combinations.

## Features

- User authentication (sign up, login, logout)
- Create, view, edit, and delete fantasy teams
- Assign NFL players to roster spots (QB, RB, WR, TE, K, DEF, FLEX, BENCH)
- Search and filter NFL players by name, position, or team
- Only team owners can edit or delete their teams
- Responsive, accessible, and modern UI with a forest green theme

## Tech Stack

- Python 3 & Django 5
- PostgreSQL (default, can be changed in `settings.py`)
- HTML5, CSS3 (custom styles)
- JavaScript (optional, for enhancements)
- [NFL API Data](https://rapidapi.com/) (for player stats, if enabled)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd cat-collector-lec
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the database:**
   - Update `DATABASES` in `catcollector/settings.py` if needed.

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Load NFL players:**
   ```bash
   python manage.py load_players
   ```

6. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Visit the app:**
   - Open [http://localhost:8000/](http://localhost:8000/) in your browser.

## Usage

- Sign up for an account.
- Create a new team and assign players to roster spots.
- Edit or delete your teams as needed.
- Browse all teams and player stats.

## Accessibility & Best Practices

- All images have descriptive `alt` text.
- Buttons and links are consistently styled.
- Navigation is accessible from all pages.
- Edit/delete options are only visible to the team owner.
- Forms are pre-filled for editing.

## License

This project is for educational purposes. See LICENSE for details.

---
