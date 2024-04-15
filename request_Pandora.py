import requests
import datetime


start_date = datetime.date(2020, 1, 1)
end_date = datetime.date(2020, 1, 31)

current_day = start_date
filenames = []
while current_day <= end_date:

    date_str = datetime.datetime.strftime(current_day, '%Y%m%d')
    filenames.append(f'Pandora135s1_ManhattanNY-CCNY_{date_str}_L2Fit_fnvh3c15d20200411p1-8.txt')
    current_day = current_day + datetime.timedelta(days=1)

base_url = 'https://data.pandonia-global-network.org/ManhattanNY-CCNY/Pandora135s1/L2Fit/'

site = 'CCNY'
savepath = f'C:/Users/Thomas Ely/OneDrive - The City College of New York/Pandora Data/{site}/'

for name in filenames:
    file_url = f"{base_url}{name}"

    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()

        with open(savepath+name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"Downloaded '{name}'")
