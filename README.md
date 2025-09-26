# Codeforces Scrapy Project

This project is designed to scrape data from the Codeforces problem set and store it in MongoDB. The scraped data will be analyzed for content and structure, and a knowledge graph will be built to visualize relationships between problems, contests, and tags. Additionally, a dashboard will be created to provide an interactive interface for exploring the data.

## Project Structure

- **scrapy.cfg**: Configuration file for Scrapy, specifying project settings and spider locations.
- **requirements.txt**: Lists the required Python packages for the project, including Scrapy, MongoDB drivers, and data analysis libraries.
- **Dockerfile**: Instructions to build a Docker image for the project, ensuring consistent environment setup.
- **.env**: Stores environment variables, such as MongoDB connection details.
- **README.md**: Documentation for the project, including setup instructions and an overview.
- **tests/**: Contains unit tests for spiders and pipelines to ensure functionality.
- **notebooks/**: Jupyter notebook for data analysis and visualization of crawled data.
- **codeforces_scrapy/**: Main package containing all the code for scraping, processing, analyzing, and visualizing data.

## Setup Instructions

1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/Susois/WebMining_codeforces_scrapy
   cd codeforces-scrapy
   ```

2. **Create a Virtual Environment**: 
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**: 
   On Linux / macOS:
   ```bash
   source venv/bin/activate
   ```
   On Windows (PowerShell):
   ```bash
   venv\Scripts\activate
   ```

4. **Install Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Spider**: 
   To scrape and push data into MongoDB (requires .env configured with Mongo connection):
   ```bash
   scrapy crawl codeforces_spider -s LOG_LEVEL=INFO
   ```

   To scrape and save data into a JSON file:
   ```bash
   scrapy crawl codeforces_spider -s LOG_LEVEL=INFO -o output.json
   ```

## Contributing


## License
