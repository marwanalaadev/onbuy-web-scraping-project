import requests
from lxml import html
import re
from pymongo import MongoClient
import logging

# Initialize an empty list to store links
links = []

# Create a session object for making HTTP requests
session_obj = requests.Session()  

# Define user-agent headers for HTTP requests
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36d'}

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to save document to MongoDB
def save_mongodb(document):
    try:
        # MongoDB configuration
        MONGO_URI = 'mongodb://localhost:27017/'
        DATABASE_NAME = "onbuy"
        PRODUCTS_COLLECTION_NAME = "onbuy"
        
        # Connect to MongoDB and select database and collection
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        products_collection = db[PRODUCTS_COLLECTION_NAME]
        
        # Check if the product exists in the collection
        existing_product = products_collection.find_one({"url": document["url"]})
        
        # If the product exists, update it; otherwise, insert a new document
        if existing_product: 
            products_collection.update_one({"url": document["url"]}, {"$set": document})
            logger.info(f"Product '{document['title']}' updated successfully.")
        else:
            products_collection.insert_one(document)
            logger.info(f"Product '{document['title']}' inserted successfully.")
    except Exception as e:
        logger.error(f"Error occurred while saving to MongoDB: {str(e)}")

# Function to send a POST request
def send_post(req_url, session_obj, headers, params):
    counter = 0
    while counter < 10:
        try:
            response = session_obj.get(req_url, headers=headers, params=params)
            if response.status_code == 200:
                logger.info(response.url + '  ::  ' + str(response.status_code))
                return response
            else:
                counter += 1
                logger.warning('The request has been blocked!\nTry counter is: ' + str(counter) + ' : ' + response.url)
        except Exception as e:
            counter += 1
            logger.error(f'Error occurred while sending POST request: {str(e)}')
    return None

# Function to send a GET request
def send_request(req_url, session_obj, headers):
    counter = 0
    while counter < 10:
        try:
            response = session_obj.get(req_url, headers=headers)
            if response.status_code == 200:
                logger.info(str(response.status_code) + '  ::  ' + response.url)
                return response
            else:
                counter += 1
                logger.warning('The request has been blocked!\nTry counter is: ' + str(counter) + ' : ' + response.url)
        except Exception as e:
            counter += 1
            logger.error(f'Error occurred while sending GET request: {str(e)}')
    return None

# Function to get categories from a URL
def get_categories(url):
    response = send_request(url, session_obj, headers)
    page = html.fromstring(response.content)
    main_categories = page.xpath('//h2[@class="sub-heading"]/a/@href')
    for main_category in main_categories:
        response = send_request(main_category, session_obj, headers)
        page = html.fromstring(response.content)
        sub_categories = page.xpath('//h5/a/@href')
        for sub_category in sub_categories:
            if sub_category in links:
                logger.info('Skipping already processed category')
            else:
                links.append(sub_category)
    return links

# Function to parse HTML response
def parse_html(html_response):
    page = html.fromstring(html_response.content)
    if page.xpath('//h1/text()'):
        title = page.xpath('//h1/text()')[0]
    else:
        title = 'null'
    if page.xpath('//meta[@property="og:image"]/@content'):
        image = page.xpath('//meta[@property="og:image"]/@content')[0]
    else:
        image = 'null'
    if page.xpath('//div[@data-price]/@data-price'):
        price = page.xpath('//div[@data-price]/@data-price')[0]
    else:
        price = 'null'
    try:
        barcode = re.findall('gtin13":\["(.*?)"', html_response.text)[0]
    except:
        barcode = 'null'
    dicto = {
        'title': title,
        'price': price,
        'barcode': barcode,
        'image': image,
        'url': html_response.url,
    }
    return dicto

# Main execution
if __name__ == "__main__":
    try:
        # Get categories from the specified URL
        links = get_categories('https://www.onbuy.com/gb/categories/')
        logger.info(f"Total categories found: {len(links)}")

        # Iterate over the links and process them
        for idx, link in enumerate(links, start=1):
            try:
                logger.info(f"Processing line {idx}: {link.strip()}")
                response = send_request(link.strip(), session_obj, headers)
                page = html.fromstring(response.content)
                count = page.xpath('//p[@id="current-search-results"]/text()')
                products_count = int(re.findall('(\d+)', count[0])[0])
                for x in range(60, products_count, 60):
                    params = {
                        'offset': x,
                        'search_type': 'category',
                        'base_url': link,
                        'master_category_id': re.findall('\~c(\d+)', link)[0],
                    }
                    post_response = send_post('https://www.onbuy.com/gb/ajax/search-results.html', session_obj,headers, params=params)
                    page = html.fromstring(post_response.json()['results'].strip())
                    products = page.xpath('//div[@data-product-link]/@data-product-link')
                    for product in products:
                        response = send_request(product, session_obj, headers)
                        my_dict = parse_html(response)
                        save_mongodb(my_dict)
            except Exception as e:
                logger.error(f"Error occurred while processing category: {str(e)}")
                logger.error(f"Url: {str(link)}")
    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}")
