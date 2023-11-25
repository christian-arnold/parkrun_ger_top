from urllib.request import Request, urlopen
import os
import pandas as pd
import re
class PageReader:
    def __init__(self, date:str):
        '''
        Parameters:
            date: date in the form 25/11/2023
        '''
        self.date = date

        
    def get_url_dict(self, url = 'https://www.parkrun.com.de/results/firstfinishers/'):
        '''
        Get the urls of all result pages.
        '''
        content = self.get_page_content(url)
        urls = self.extract_results_urls(content)

        return urls

    def extract_results_urls(self,input_string):
        # Define the pattern to match URLs
        pattern = re.compile(r'<a href="https://www\.parkrun\.com\.de/([^/]+)/results">([^<]+)</a>')

        # Find all matches in the input string
        matches = pattern.findall(input_string)

        # Create a dictionary from the matches
        result_dict = {name.lower(): f'https://www.parkrun.com.de/{slug}/results' for slug, name in matches}

        return result_dict

    def get_top_result_list(self, max_results = 20):
        '''build a list containing all results and return the top'''
        all_results = []
        for name, url in self.get_url_dict().items():
            print(f'Doing {name}')
            results = self.process_url(name, url)
            all_results.append(results)

        all_results = pd.concat(all_results)
        #sort the results
        all_results.sort_values('Zeit', inplace = True)
        return all_results[:max_results] if len(all_results) > max_results else all_results
    
    def get_page_content(self, url):
        contentfile = 'page_content.txt'

        if True: #not os.path.exists(contentfile):
            req = Request(
                url=url,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
            )
            webpage = urlopen(req).read().decode('utf-8')

            f= open(contentfile, 'w')
            f.write(webpage)
            f.close()

        else:
            f = open(contentfile, 'r')
            webpage = f.read()
            f.close()
        
        return webpage

    def get_result_table_from_html(self, webpage_content):
        t = pd.read_html(webpage_content)

        #drop the club column and then the nan
        d = t[0].drop('Verein', axis = 1)
        d = d.dropna()

        #get the women
        f = d[d['Geschlecht'].str.contains('Weiblich')]
        f['Zeit'] = list(f['Zeit'].apply(pr.extract_time))
        f = f[f['Zeit'].str.len() == 5]
        
        f['Zeit'] = pd.to_datetime(f['Zeit'],format= '%M:%S' ).dt.time
        
        return f[:10] if len(f)>10 else f

    def process_url(self, name, url):
        '''Process the url for one parkrun'''
        content = self.get_page_content(url)
        table = self.get_result_table_from_html(content)
        table['parkrun'] = [name]*len(table)

        return table
        
    def extract_time(self, input_string):
        # Define a regular expression pattern to match time in the format HH:MM or H:MM
        time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})')

        # Find all matches in the input string
        matches = time_pattern.findall(input_string)

        # Return the first match (if any)
        return matches[0] if matches else None

        

if __name__ == '__main__':
    url = 'https://www.parkrun.com.de/oberwald/results/latestresults/'

    pr = PageReader('25/11/2023')
    tr = pr.get_top_result_list()
    
    
