import requests
from bs4 import BeautifulSoup
import csv
import asyncio


# function for getting whole data about a product
def getProductDetail(product):
    detail = requests.get(product["ProductURL"])
    soup = BeautifulSoup(detail.content, "html.parser")

    # print(product)
    try:
        Description = soup.select_one("#title #productTitle").text.strip()

    except AttributeError:
        Description = "N/A"

    try:
        ASIN = soup.select_one("th:contains('ASIN') + td").text.strip()
        if ASIN:
            print("asin exist")
        else:
            ASIN = soup.select_one(".detail-bullet-list ul span:-soup-contains('ASIN') + span").text.strip()

    except AttributeError:
        ASIN = "N/A"

    try:
        th = soup.css.select("#productDetails_techSpec_section_1 th")
        td = soup.css.select("#productDetails_techSpec_section_1 td")

        ProductDescription = []
        for i in range(len(th)):
            ProductDescription.append({str(th[i].text.strip()): str(td[i].text.strip())[1:]})
    except AttributeError:
        ProductDescription = "N/A"

    try:
        Manufacturer = soup.select_one("th:contains('Manufacturer') + td").text.strip()[1:]
    except AttributeError:
        Manufacturer = "N/A"
    
    product["product_description"] = {
        "Description": Description,
        "ASIN" : ASIN,
        "ProductDescription" : ProductDescription,
        "Manufacturer": Manufacturer
    }

    # print(product)

# ---------------------------------------------------------------------------------------------
    # for scraping the products 
def scrape_theDetail(url, products):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # print(soup)
    for product in soup.select(".s-asin"):
        # product_url = "https://www.amazon.in" + str(product.get("href"))
        product_uri = product.select_one(".a-link-normal").get("href")
        product_url = "https://www.amazon.in"+str(product_uri)
        product_name = product.select_one(".a-text-normal").text.strip()

        try:
            product_price = product.select_one(".a-price .a-offscreen").text.strip()
        except AttributeError:
            product_price = "N/A"

        try:
            product_rating = product.select_one(".a-icon-alt").text.strip()
        except AttributeError:
            product_rating = "N/A"

        try:
            num_reviews = product.select_one(".a-size-base").text.strip()
        except AttributeError:
            num_reviews = "N/A"

        product = {
            "ProductURL": product_url,
            "ProductName": product_name,
            "ProductPrice": product_price,
            "Rating": product_rating,
            "NumberofReviews": num_reviews,
        }

        # getProductDetail(product)

        products.append(product)


# ---------------------------------------------------------------------------------------------
def main():
    url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
    pages = 20
    products = []

    for pageNo in range(1, pages+1):
        newurl = "https://www.amazon.in/s?k=bags&"+str(pageNo)+"&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"+str(pageNo)
        scrape_theDetail(newurl, products)
    
    # traversing on each producct to get further data using the url
    for i in products:
        getProductDetail(i)

    # Save the data to a CSV file
    with open("amazon_products.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ProductURL", "ProductName", "ProductPrice", "Rating", "NumberofReviews", "product_description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

    print("Data scraped and saved to 'amazon_products.csv'.")


main()