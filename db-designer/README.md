# db-designer Project

## Overview
The `db-designer` project is a database design tool that follows the Model-View-Controller (MVC) architectural pattern. It allows users to create and manage database schemas visually.

## Directory Structure
```
db-designer
├── controllers
│   ├── __init__.py
│   └── main_controller.py
├── models
│   ├── __init__.py
│   └── database_model.py
├── views
│   ├── __init__.py
│   └── main_window.py
├── main.py
├── requirements.txt
└── README.md
```

## Requirements
This project requires Python 3.10 or higher and PySide6 version 6.10 or higher. You can install the required dependencies using the following command:

```
pip install -r requirements.txt
```

## Usage
To run the application, execute the `main.py` file. This will initialize the application, set up the main window, and start the event loop.

```
python main.py
```

## Contributing
Contributions to the `db-designer` project are welcome. Please feel free to submit issues or pull requests for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.