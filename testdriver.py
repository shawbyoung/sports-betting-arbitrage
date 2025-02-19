from driver import driver

class testdriver(driver):
    def __init__(self):
        super().__init__('testdriver')

    def get_page(self, page_link):
        try:
            self.driver.get(page_link)
        except Exception as e:
            self._log(f'Hit exception in visit page, {e}')