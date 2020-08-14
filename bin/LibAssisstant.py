from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import getpass
import time
import sched


def establish_connection(url, key_class, end_time=60, executable_path=r'E:\Outpost\Packages\geckodriver.exe'):
    # for initial connection
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options, executable_path=executable_path)
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, end_time).until(ec.presence_of_element_located((By.CLASS_NAME, key_class)))
        finally:
            return driver
    except Exception as e:
        print(e)
        return 0


def wait_response(driver, wait_class, method='class', end_time=60):
    if method == 'class':
        method = By.CLASS_NAME
    elif method == 'name':
        method = By.NAME
    elif method == 'id':
        method = By.ID
    elif method == 'lktext':
        method = By.LINK_TEXT
    try:
        WebDriverWait(driver, end_time).until(ec.presence_of_element_located((method, wait_class)))
    except Exception as e:
        print(e)


def seat_reservation(Config, passwd, end_time=60):
    # login
    driver = establish_connection(Config['url'], 'account_login', end_time)
    if driver != 0:
        driver.find_element_by_name('username').send_keys(Config['username'])
        driver.find_element_by_name('pwd').send_keys(passwd)
        driver.find_element_by_class_name('account_login').click()
    else:
        print('Error: connection failed!')
        exit()

    # function confirm page
    wait_response(driver, 'col-sm-12')  # main form
    function_select_buttons = driver.find_elements_by_css_selector('.col-sm-12 a')  # add seat reservation
    function_select_buttons[1].click()  # add reservation application

    # wait_response(driver, 'rplace', method='name')
    # driver.find_element_by_id('rplace-0').click()       # library selector
    # time.sleep(1)
    # driver.find_element_by_id('service-1').click()
    # time.sleep(1)
    # driver.find_element_by_id('submit').click()
    driver.get(Config['seat_service_page'])  # redirect to seat reserve page

    floor_selector = Select(driver.find_element_by_id('tab-select'))  # floor selector
    floor_selector.select_by_value('xingqing' + str(Config['floor']) + 'floor')
    time.sleep(2)
    position_link = driver.find_element_by_id(Config['position'])  # position select
    ActionChains(driver).move_to_element(position_link).click(position_link).perform()
    wait_response(driver, 'btlist', method='id')  # wait for seats list

    # select seat
    for seat in Config['seat_list']:
        seat_link = driver.find_element_by_partial_link_text(str(seat))
        if seat_link.get_attribute('disabled'):
            # unavailable
            continue
        else:
            # select
            seat_link.click()
            break


def read_conf(path='./Config.conf'):
    conf_file = open(path)
    lines = conf_file.readlines()
    Config = {}
    for line in lines:
        if '#' in line:
            continue
        else:
            line = line.strip('\n').split(' ')
            if len(line[1:]) == 1:
                Config[line[0]] = line[1]
            else:
                Config[line[0]] = line[1:]
    Config['address'] = Config['address'].split(':')
    Config['floor'] = Config['address'][0]
    Config['position'] = Config['address'][1]
    Config['seat_list'] = Config['address'][2].split(',')
    Config['runtime'] = Config['runtime'].split(':')
    return Config


if __name__ == '__main__':
    # ---------- config ---------- #
    Config = read_conf('./Config.conf')
    passwd = getpass.getpass('passwd: ')
    end_time = 60

    start_time = time.localtime(time.time())
    exec_time = list(start_time)
    exec_time[2] += 1
    exec_time[3] = int(Config['runtime'][0])
    exec_time[4] = int(Config['runtime'][1])
    exec_time = time.mktime(tuple(exec_time))

    # info confirm
    print('will reserve {}th floor {} {} for you at {}'.format(Config['floor'], Config['position'], Config['seat_list'], time.asctime(time.localtime(exec_time))))
    print('please keep this window open...')

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enterabs(exec_time, 1, seat_reservation, argument=(Config, passwd))
    scheduler.run()


