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

    df = pd.read_csv('10222019.csv')
    sku = df['sku.1']

    con = pymysql.connect('localhost', 'root', '', 'amazon')

    with con: 
        cur = con.cursor()
        sqlSelect  = "SELECT * FROM output ORDER BY id DESC LIMIT 1"
        cur.execute(sqlSelect)
        rows = cur.fetchall()
        
    for s in sku:
        #if rows and rows[0][1] != s: continue
        
        url = "https://www.amazon.com/s?k=" + s + "&ref=nb_sb_nosss"

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

                print(s)
                print(asin)
                print(description)
                print(cost)
                print(sellerName)
                print(shippingCost)
                
                sql_dup  = "SELECT * FROM output WHERE sku LIKE '" + str(s) + "' AND asin LIKE '" + str(asin) + "' ORDER BY id DESC"
                print(sql_dup)
                cur.execute(sql_dup)
                rows_dup = cur.fetchall()
                if rows_dup:
                    sql_update = "UPDATE output SET sku='" + str(s) + "' WHERE asin='" + str(asin) + "'"
                    print(sql_update)
                    cur.execute(sql_update)
                else:        
                    sql_insert = "INSERT INTO output(sku,asin,cost,sellername,shippingcost,description) VALUES (%s,%s,%s,%s,%s,%s)"
                    cur.execute(sql_insert, (s,asin,cost,sellerName,shippingCost,description))
                    con.commit()

                time.sleep(5)

            next_url = []

    con.close()

except Exception as e:
    print(e)