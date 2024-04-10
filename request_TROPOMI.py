import requests
import os


# overriding requests.Session.rebuild_auth to mantain headers when redirected
class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    # Overrides from the library to keep headers when redirected to or from
    # the NASA auth host.

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and redirect_parsed.hostname != self.AUTH_HOST and original_parsed.hostname != self.AUTH_HOST:

                del headers['Authorization']

        return


start_date = '2023-08-02'  # yyyy-mm-dd
start_time = '00:00:00'  # hh:mm:ss

end_date = '2023-08-02'
end_time = '23:59:59'

min_lat = '40'
max_lat = '45'

min_lon = '-78'
max_lon = '-70'

folder = './TROPOMI_data'
if not os.path.exists(folder):
    os.mkdir(folder)

username = "tely136"
password = "!4cVkM!jfyg9"

session = SessionWithHeaderRedirection(username, password)

# Define your search criteria
collection_id = 'C2089270961-GES_DISC'
bounding_box = f'{min_lon},{min_lat},{max_lon},{max_lat}'  # Fill in with your bounding box coordinates
time_range = f'{start_date}T{start_time}Z,{end_date}T{end_time}Z'  # Fill in with your time interval

# CMR API endpoint for granule search
cmr_search_url = f'https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id={collection_id}&bounding_box={bounding_box}&temporal={time_range}'

# Make the API request
response = requests.get(cmr_search_url)
response.raise_for_status()  # Check for request errors

# Parse the response
granules = response.json()['feed']['entry']

# Extract and print download URLs
for granule in granules:
    # The specifics of this part might vary depending on the dataset and response structure
    urls = [link['href'] for link in granule['links'] if link.get('rel') == 'http://esipfed.org/ns/fedsearch/1.1/data#']
    for url in urls:

        filename = url[url.rfind('/') + 1:]
        if filename.endswith('.nc'):
            print(filename)

            try:
                # submit the request using the session
                response = session.get(url, stream=True)
                print(response.status_code)

                # raise an exception in case of http errors
                response.raise_for_status()

                date = filename.split('_')[8]
                date = date.split('T')[0]

                path = os.path.join(folder, date)
                if not os.path.exists(path):
                    os.mkdir(path)

                # save the file
                with open(os.path.join(path, filename), 'wb') as fd:

                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        fd.write(chunk)

            except requests.exceptions.HTTPError as e:

                # handle any errors here
                print(e)

