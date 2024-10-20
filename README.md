# Flask Blog Microservices

This project is a Flask-based blog application that has been refactored into a microservices architecture.

## Automated Setup

We've provided a setup script to automate the process of creating virtual environments and installing dependencies for all components of the application.

1. Make sure you have Python 3.7+ installed on your system.

2. Clone the repository:
   ```
   git clone <repository-url>
   cd flask_blog
   ```

3. Run the setup script:
   ```
   python setup.py
   ```

   This script will create virtual environments and install all necessary dependencies for the main application and each microservice.

## Running the Application Locally

After running the setup script, follow these steps to run the application:

1. Initialize the databases:
   In the main flask_blog directory, run:
   ```
   python init_db.py  # For the main database
   python init_users_db.py  # For the users database
   python init_comments_db.py  # For the comments database
   ```

2. Start each service in a separate terminal window:

   Open 5 new terminal windows, navigate to the flask_blog directory in each, and run the following commands (one in each terminal):

   ```
   # Terminal 1
   cd services/db_service
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   python db_service.py

   # Terminal 2
   cd services/post_service
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   python post_service.py

   # Terminal 3
   cd services/auth_service
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   python auth_service.py

   # Terminal 4
   cd services/template_service
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   python template_service.py

   # Terminal 5
   cd services/comment_service
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   python comment_service.py
   ```

3. Start the main application:
   Open a new terminal window, navigate to the flask_blog directory, and run:
   ```
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   python app.py
   ```

4. Access the application:
   Open a web browser and navigate to `http://localhost:5000` to access the blog application.

## Testing the Application

1. Register a new user:
   - Click on "Register" and create a new account.

2. Log in:
   - Use your newly created credentials to log in.

3. Create a new blog post:
   - Click on "New Post" and create your first blog entry.

4. View, edit, and delete posts:
   - Navigate through your posts, try editing and deleting them.

5. Add comments:
   - Try adding comments to your posts.

6. Test pagination:
   - Create multiple posts and comments to test the pagination feature.

7. Check error handling:
   - Try accessing non-existent posts or performing unauthorized actions to test error handling.

## Troubleshooting

- If the setup script fails, make sure you have Python 3.7+ installed and that you're in the correct directory.
- If any service fails to start, ensure you're in the correct directory and the virtual environment is activated.
- Verify that the database initialization scripts have run successfully.
- If you encounter any "address already in use" errors, make sure no other applications are using the required ports (5000-5005).

## Environment Variables

By default, the application uses predefined local URLs for services. If you need to modify these, you can set the following environment variables:

- `SECRET_KEY`: Secret key for the main application (default: "your secret key")
- `POST_SERVICE_URL`: URL for the post service (default: "http://localhost:5002")
- `AUTH_SERVICE_URL`: URL for the auth service (default: "http://localhost:5003")
- `TEMPLATE_SERVICE_URL`: URL for the template service (default: "http://localhost:5004")
- `COMMENT_SERVICE_URL`: URL for the comment service (default: "http://localhost:5005")

## Next Steps

After successfully testing the application locally, you can proceed to deploy it on a virtual machine or a cloud platform of your choice.
