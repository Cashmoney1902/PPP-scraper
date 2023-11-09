from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc
import time
import pandas as pd

def scrape_players(sport):
    players_list = []
    try:
        driver.find_element(By.XPATH, f"//div[@class='name'][normalize-space()='{sport}']").click()
        time.sleep(0.1)

        stat_container = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "stat-container")))
        categories = driver.find_element(By.CSS_SELECTOR, ".stat-container").text.split('\n')

        for category in categories:
            try:
                driver.find_element(By.XPATH, f"//div[text()='{category}']").click()
                projectionsPP = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".projection")))

                for projections in projectionsPP:
                    names = projections.find_element(By.CLASS_NAME, "name").text
                    value = projections.find_element(By.CLASS_NAME, "presale-score").get_attribute('innerHTML')
                    proptype = projections.find_element(By.CLASS_NAME, "text").get_attribute('innerHTML')

                    player_data = {
                        'Name': names,
                        'Value': value,
                        'Prop': proptype.replace("<wbr>", "")
                    }
                    players_list.append(player_data)
            except NoSuchElementException:
                print(f"Category '{category}' not found for {sport}. Skipping...")
    except NoSuchElementException:
        print(f"{sport} section not found. Skipping...")
        return None  # Return None if sport not found

    return players_list

def scrape_sports(*sports):
    all_players = {}
    for sport in sports:
        players = scrape_players(sport)
        if players is not None:  # Only create CSV if players are found
            all_players[sport] = players
    return all_players

# ... (rest of your code remains the same)



options = uc.ChromeOptions()
prefs = {"profile.default_content_settings.geolocation": 2}
options.add_experimental_option("prefs", prefs)
options.add_argument("--deny-permission-prompts")
driver = uc.Chrome(options=options)

driver.get("https://app.prizepicks.com/")
time.sleep(0.1)

try:
    close_button = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "close")))
    close_button.click()
except NoSuchElementException:
    pass

sports_to_scrape = ['NBA']  # Add more sports here

all_players = scrape_sports(*sports_to_scrape)

for sport, players in all_players.items():

    df = pd.DataFrame(players)
    df.to_csv(f'{sport.lower()}_players.csv', index=False)
    print(f"{sport} Players:")
    print(df)
    print('\n')

driver.quit()
