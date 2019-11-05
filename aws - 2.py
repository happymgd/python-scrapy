from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import numpy as np
import pandas as pd
import pymysql

next_url = []

try:

    con = pymysql.connect('localhost', 'root', '', 'amazon')
    driver = webdriver.Chrome('chromedriver.exe')

    with con: 
        cur = con.cursor()
        cur.execute("SELECT sku FROM csv WHERE completed = 0")

        rows = cur.fetchall()

        for row in rows:
            sku = row[0]
            url = "https://www.amazon.com/s?k=" + sku + "&ref=nb_sb_nosss"
            driver.get(url)
            time.sleep(5)

            elements = driver.find_elements_by_xpath("//a[@class='a-link-normal a-text-normal']")

            for element in elements:
                next_url.append(element.get_attribute("href"))

            if len(next_url) > 0:
                for url in next_url:
                    driver.get(url)

                    time.sleep(5) 

                    asin = ""
                    cost = ""
                    sellerName = ""
                    shippingCost = ""
                    description = ""
                    
                    productTable = driver.find_elements_by_css_selector("table#productDetails_detailBullets_sections1 tr th.prodDetSectionEntry")

                    for row in productTable:
                        if row.text == "ASIN":
                            asin = row.find_element_by_xpath('./following-sibling::td').text

                    #cost
                    try:
                        cost_elem = driver.find_element_by_xpath("//span[@id='priceblock_ourprice']") 
                        cost = cost_elem.text
                    except NoSuchElementException:  #spelling error making this code not work as expected
                        pass


                    #sellerName    
                    try:
                        seller_elem = driver.find_element_by_xpath("//a[@id='sellerProfileTriggerId']") 
                        sellerName = seller_elem.text
                    except NoSuchElementException:  #spelling error making this code not work as expected
                        pass


                    #shippingCost    
                    try:
                        shipping_elem = driver.find_element_by_css_selector("span#ourprice_shippingmessage > span.a-size-base")
                        #seller_elem = driver.find_element_by_xpath("//span[@id='ourprice_shippingmessage']") 
                        shippingCost = shipping_elem.text
                    except NoSuchElementException:  #spelling error making this code not work as expected
                        pass
                    

                    #description
                    try:
                        description_elem = driver.find_element_by_xpath("//div[@id='productDescription']/p")
                        description = description_elem.text
                    except NoSuchElementException:  #spelling error making this code not work as expected
                        pass

                    print(sku)
                    print(asin)
                    print(description)
                    print(cost)
                    print(sellerName)
                    print(shippingCost)
                    
                    sql = "INSERT INTO output(sku,asin,cost,sellername,shippingcost,description) VALUES (%s,%s,%s,%s,%s,%s)"
                    cur.execute(sql, (sku,asin,cost,sellerName,shippingCost,description))

                    sql1 = "INSERT INTO url(urls) VALUES (%s)"
                    cur.execute(sql1, (url))

                    con.commit()

                    time.sleep(5)
                    
                next_url = []    
    con.close()

except Exception as e:
    print(e)