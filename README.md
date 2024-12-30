 ## BBC News Scraper

This project is a Python-based web scraping tool designed to fetch news data from BBC News. It first scrapes the headline links from the main BBC News page and then retrieves detailed information from the latest articles.

**Features**

*   **Data Collected**:
    
    *   Article Title
        
    *   Date of Upload
        
    *   Publisher
        
    *   Publisher Role (in BBC)
        
    *   Description
        
*   **Technologies Used**:
    
    *   fake_useragent: To avoid detection by websites.
        
    *   requests_html: For rendering JavaScript and making HTTP requests.
        
    *   bs4 (BeautifulSoup): For parsing HTML and extracting data.
        
    *   json: For handling JSON responses.
        
    *   sqlite3: For storing scraped data in a SQLite database.
        
    *   pandas: For data manipulation and exporting.
        
    *   logging: For tracking the progress and debugging.
        
*   **Output Formats**:
    
    *   CSV
        
    *   Excel
        
    *   JSON
        
    *   SQLite3 database
        
*   **Logging**:A logger file is created at the end of the process to help track the scraping progress and identify any issues.
    

**Installation**

1.  Clone the repository:  git clone [https://github.com/Abdullah-Shaheer/news_headlines-scraper.git](https://github.com/Abdullah-Shaheer/news_headlines-scraper.git)
    
2.  Install the required dependencies:  pip install -r requirements.txt
    

**Usage**

1.  Run the script:  python main.py
    
2.  The script will:
    
    *   Scrape headline links from the BBC News main page.
        
    *   Navigate through each link to fetch detailed article data.
        
    *   Save the data in multiple formats (CSV, Excel, JSON, SQLite).
        
3.  Check the log file (scraper.log) to review the scraping progress or debug any issues.
    

**Output**

*   **Data Formats**:
    
    *   articles.csv
        
    *   articles.xlsx
        
    *   articles.json
        
    *   articles.db (SQLite)
        
*   **Log File**:
    
    *   scraper.log
        

**Prerequisites**

*   Python 3.8 or higher
    
*   Internet connection
    
----------------------

**Author**->  
Developed by  ([https://github.com/Abdullah-Shaheer](https://github.com/Abdullah-Shaheer)). 
Feel free to reach out for any questions or collaboration.
