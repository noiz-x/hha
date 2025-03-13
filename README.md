# Project Name: HHA

## Description
HHA is a Django-based web application designed to manage events, demographics, and ministries for a Church body. This project aims to streamline event management, user registration, and provide a comprehensive platform for organizational activities.

## Features
- **Event Management**: Create, update, and manage events with detailed descriptions, speakers, and hashtags.
- **User Registration**: Allow users to register for events, with options for RSVP and payment uploads.
- **QR Code Generation**: Generate and validate QR codes for event registrations.
- **Admin Dashboard**: Admin functionalities to manage users, events, and view detailed reports.
- **Email Notifications**: Send email notifications for event confirmations and updates.

## Installation

1. Clone the repository:
  ```bash
  git clone https://github.com/noiz-x/hha.git
  ```
2. Navigate to the project directory:
  ```bash
  cd hha
  ```
3. Create a virtual environment:
  ```bash
  python3 -m venv venv
  ```
4. Activate the virtual environment:
  - On Windows:
    ```bash
    venv\Scripts\activate
    ```
  - On macOS/Linux:
    ```bash
    source venv/bin/activate
    ```
5. Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Usage

1. Apply the migrations:
  ```bash
  python manage.py migrate
  ```
2. Create a superuser:
  ```bash
  python manage.py createsuperuser
  ```
3. Run the development server:
  ```bash
  python manage.py runserver
  ```
4. Open your web browser and go to `http://127.0.0.1:8000/` to access the application.

## Contributing
1. Fork the repository.
2. Create a new branch:
  ```bash
  git checkout -b `feature-branch`
  ```
3. Make your changes and commit them:
  ```bash
  git commit -m "Description of your changes"
  ```
4. Push to the branch:
  ```bash
  git push origin `feature-branch`
  ```
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.


## Contact
For any inquiries or feedback, please contact https://www.linkedin.com/in/iamgeekspe/.
