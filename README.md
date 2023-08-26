# Box Inventory Management System

This project allows you to manage a store's inventory of cuboid boxes.

## Getting Started

- Please make sure that you have:
 - Python 3.9 installed (https://www.python.org/downloads/)
 - Refer to env.example file to setup your environment variables in .env file

1. Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/box-inventory.git
cd box-inventory
```

2. Create a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

3. Install the project dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file based on .env.example and update the values:
```bash
cp .env.example .env
# Update the values in .env with your configuration
```

## Running the Project

1. Apply database migrations:
```bash
python manage.py migrate
```

2. 
```bash
python manage.py runserver
```

3. Access the project in your browser at http://127.0.0.1:8000/

4. Create a super user to assign users' staff permission for them to access staff scope APIs
```bash
python manage.py createsuperuser
```

5. After signing up:
    - Verify your account from a link sent to your email.
    - Use the access token received in the response of the verification link as a **Authorization: Bearer _your-access-token_** for API requests.
    - You can login again to verify your account or to get access token again in case the token is expired or lost(**note: you need to verify your account to get access token**)

6. All non permitted actions are handled with proper http status code. Also, Default conditions of area, volume and other limit are implemented.

## API Endpoints
- **signup:** POST **/auth/signup/**
Name  | Type
----- | -----
username  | string
email  | string
password  | string

- **login:** POST **/auth/login/**
Name  | Type
----- | -----
email  | string
password  | string

- **Add Box:** POST **/inventory/boxes/** (Permissions: Must be staff )
Name  | Type
----- | -----
length  | integer
breadth  | integer
height  | integer

- **Update Box:** PATCH **/inventory/boxes/<box_id>/** (Permissions: must be staff)
Name  | Type
----- | -----
length  | integer (optional)
breadth  | integer (optional)
height  | integer (optional)

- **List All Boxes:** GET **/inventory/boxes/** (Permissions: Any User, Filters Applicable)
- **List User's Boxes:** GET **/inventory/boxes/myboxes/** (Permissions: Must be staff, Filters Applicable)
- **Retrieve Box:** GET **/inventory/boxes/<box_id>/** (Permissions: Authenticated user)
- **Delete Box:** DELETE **/inventory/boxes/<box_id>/** (Permissions: Authenticated user)


