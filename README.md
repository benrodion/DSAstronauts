# DSAstronauts

## 🚀 Project Overview
**DSAstronauts** is a collaborative Flask web application built for managing group trips and shared expenses. Developed as part of a university project for the *Data Structures & Algorithms* course, the platform allows users to:
- Create and manage user groups
- Track and settle group expenses

## 🧱 Features
- Group creation and user management
- Trip planning interface
- Shared transaction recording
- Simple expense balancing using Splitwise-like logic
- SQLite database integration via SQLAlchemy

## ⚙️ Tech Stack
- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML/CSS (Jinja templates), Bootstrap
- **Database**: SQLite
- **Testing**: Pytest
- **Version Control**: Git + GitHub

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- `pip` package manager

### Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/DSAstronauts.git
   cd DSAstronauts


2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
 
On macOS/Linux:

 ```bash
export FLASK_APP=app
flask run
 ```
On Windows (Command Prompt):

 ```bash
set FLASK_APP=app
flask run
 ```

> ⚠️ **Note:** Make sure you are in the **root directory** of the project (where `requirements.txt` is located), not inside the `app/` folder.
> If you still encounter issues, you can manually initialize modules by running:

```bash
python -m app.database
python -m app.forms
python -m app.helpers
```


## 🔍 Project Structure

```

DSAstronauts/
├── app/               # Main Flask app code
│   ├── routes.py      # URL routing and logic
│   ├── database.py    # DB models and setup
│   ├── splitwise.py   # Expense-splitting logic
│   ├── forms.py       # WTForms definitions
│   ├── helpers.py     # Utility functions
│   ├── templates/     # HTML templates (Jinja2)
│   └── static/        # CSS/JS and assets
├── tests/             # Unit and integration tests
├── requirements.txt   # Python dependencies
├── README.md          # Project overview
├── LICENSE            # MIT License
└── .github/           # GitHub Actions or config

```


## 🧪 Testing

To run the test suite:

```bash
pytest
```

## 🤝 Contributing

* Use feature branches based on tasks/issues
* Create pull requests to merge changes into `main`
* Ensure tests pass before submitting a PR
* Follow project guidelines in `.github/` for CI/CD



