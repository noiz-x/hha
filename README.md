# HHA

HHA is a Django-based web application designed to manage events, demographics, and ministries for a Church body. It streamlines event management and user registration while providing a comprehensive platform for organizational activities.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **Event Management:**  
  Create, update, and manage events with detailed descriptions, speakers, and hashtags.

- **User Registration:**  
  Allow users to register for events with options for RSVP and payment uploads.

- **QR Code Generation:**  
  Generate and validate QR codes for event registrations.

- **Admin Dashboard:**  
  Admin functionalities to manage users, events, and view detailed reports.

- **Email Notifications:**  
  Send email notifications for event confirmations and updates.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/noiz-x/hha.git
cd hha
```

### Create and Activate a Virtual Environment

- **On Windows:**
  ```bash
  python3 -m venv venv
  venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root directory with the following environment variables. Replace placeholder values with your actual configuration:

```dotenv
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
```

---

## Usage

1. **Apply Migrations:**

   ```bash
   python manage.py migrate
   ```

2. **Create a Superuser:**

   ```bash
   python manage.py createsuperuser
   ```

3. **Collect Static Files:**

   ```bash
   python manage.py collectstatic
   ```

4. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

5. **Access the Application:**  
   Open your web browser and navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository.**
2. **Create a New Branch:**

   ```bash
   git checkout -b feature-branch
   ```

3. **Make Your Changes and Commit Them:**

   ```bash
   git commit -m "Description of your changes"
   ```

4. **Push to Your Branch:**

   ```bash
   git push origin feature-branch
   ```

5. **Open a Pull Request.**

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For inquiries or feedback, please reach out via [LinkedIn](https://www.linkedin.com/in/iamgeekspe/).