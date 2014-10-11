#-*- coding: utf-8 -*-


def generate_marketcap_json(output_dir):
    """
    Get marketcap values from coinmarketcap.com and output to a JSON file.
    :param output_dir: Output directory to write serialized JSON in filesystem.
    """
    try:
        # Get full web page from Coinmarketcap.com index.
        session = requests.Session()
        link = 'http://coinmarketcap.com/'
        req = session.get(link)

        # Create BeautifulSoup object with web response.
        soup = BeautifulSoup(req.text)

        # Ordered dictionary object to store data to be JSON serialized.
        marketcap_dict = OrderedDict()
        marketcap_dict['timestamp'] = datetime.now().strftime(
                                        '%a %b %d %Y, %H:%M:%S')
        marketcap_dict['currencies'] = []

        # Regex expression to search for patterns in web page.
        anything = re.compile('^.*$')
        name_regex = re.compile('^.*\\bcurrency-name\\b.*$')
        marketcap_regex = re.compile('^.*\\bmarket-cap\\b.*$')
        price_regex = re.compile('^.*\\bprice\\b.*$')
        positive_change_regex = re.compile('^.*\\bpositive_change\\b.*$')
        negative_change_regex = re.compile('^.*\\bnegative_change\\b.*$')

        # Find HTML <tr> tags for each currency.
        table = soup.findAll('tr', {'id': anything})

        # Find the top 5 (five) currencies with the highest marketcap
        # and obtain their values
        for item in table[:5]:
            currency = []

            # Get the currency name
            names = item.findAll('td', {'class': name_regex})
            for name in names:
                currency.append(name.find('a').contents[0].strip())

            # Get the marketcap value
            marketcaps = item.findAll('td', {'class': marketcap_regex})
            for marketcap in marketcaps:
                currency.append(marketcap.contents[0].strip())

            # Get the price value
            prices = item.findAll('a', {'class': price_regex})
            for price in prices:
                currency.append(price.contents[0].strip())

            # Get the change percentage and sign
            changes = item.findAll('td', {'class': positive_change_regex})

            if changes:
                for change in changes:
                    currency.append(change.contents[0].strip())
                    currency.append('positive')
            else:
                changes = item.findAll('td', {'class': negative_change_regex})
                for change in changes:
                    currency.append(change.contents[0].strip())
                    currency.append('negative')

            marketcap_dict['currencies'].append(currency)

        # Generate JSON file from ordered dictionary
        json_path = output_dir + 'marketcap.json'
        print 'Generating ' + json_path + ' file...'
        write_json_file(marketcap_dict, json_path)
