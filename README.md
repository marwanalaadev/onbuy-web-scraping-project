# Web Scraping Project

This project is a web scraping tool built with Python for extracting product data from a onbuy website and storing it in a MongoDB database.

## Features

- Scrapes product data from a website.
- Stores the data in a MongoDB database.
- Configurable user-agent headers for HTTP requests.
- Logging functionality to track scraping progress and errors.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/web-scraping-project.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the scraper, make sure to configure the following codes in `main.py`:

```python
# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = "onbuy"
PRODUCTS_COLLECTION_NAME = "onbuy"


## Usage

To use the web scraper, follow these steps:

1. Configure MongoDB connection details in `main.py`.
2. Run the main script:

    ```bash
    python main.py
    ```

3. Monitor the logs (`app.log`) for status updates and errors.


## Error Handling

The scraper handles network errors, HTTP errors, and other exceptions gracefully. Check the logs (`app.log`) for details on any encountered errors.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please contact Marwan Alaa at marwan.alaa.dev@gmail.com".
