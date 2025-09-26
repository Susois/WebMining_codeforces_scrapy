FROM python:3.9-slim

# Set the working directory
WORKDIR /codeforces-scrapy

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the port for the dashboard
EXPOSE 8050

# Command to run the Scrapy spider
CMD ["sh", "scripts/run_spider.sh"]