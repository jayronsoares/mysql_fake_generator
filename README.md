# MySQL Fake Data Generator

## Description

A Python tool to generate realistic fake data for MySQL databases. It creates SQL insert statements based on your table schema and allows you to download these statements for easy database population.

## Features

- Generates realistic fake data using the [Faker](https://faker.readthedocs.io/) library.
- Customizable row count (up to 30,000 rows).
- Downloadable SQL insert statements.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mysql-fake-data-generator.git
   cd mysql-fake-data-generator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**
   ```bash
   streamlit run app.py
   ```

2. **Configure MySQL connection:**
   - Enter your database credentials in the Streamlit sidebar.
   - Select the table and specify the number of rows.

3. **Generate and download data:**
   - Click "Generate Fake Data" to create the data.
   - Download the SQL insert statements by clicking "Download data as SQL."

## Requirements

- Python 3.x
- `streamlit`
- `mysql-connector-python`
- `pandas`
- `Faker`

## Contributing

Feel free to contribute by opening issues or submitting pull requests.

## License

MIT License. See [LICENSE](LICENSE) for details.
