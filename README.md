# Private Chat App

Private Chat App is a  Python project that provides a private chat solution in the local network without Internet. This repository contains the server and also User entry point.
[![Download App](https://img.shields.io)](https://github.com/Jubayer-Hossain-JB/Private_Chat-App/blob/main/dist/Private%20Chat%20App.exe)
## Features
- Socket-based chat backend
- Web interface
- Desktop GUI client
- Uploads directory for handling user files

## Repository layout
- web.py —  web server
- soket.py — chat server
- window.py — GUI to run
- web/ — web assets (User entry point)
- resources/ — application resources
- uploads/ — directory for user uploads

## Prerequisites
- Python 3.8+ recommended
- Virtual environment recommended


## File uploads & storage
- Uploaded files are stored in `uploads/`. Ensure this directory is writable by the process.
- Sanitize and validate uploads before use if you plan to deploy publicly.


## Contributing
- Open issues or PRs on the repo.
- When contributing, include tests or manual reproduction steps for bugs.

## License
The project includes a LICENSE file. Check it for the full license text.
