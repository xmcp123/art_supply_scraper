Basic Usage

python search.py --search 'search_query' --max 200 --threads 10 -o /tmp/output.csv

Arguments:
 -s / --search - Your search query
 -nt / --threads - The number of threads to use downloading project pages. Please keep this number at 10 or less
 -o / --output - The CSV file we will output to. Keep in mind this file will be removed if it already exists
 -m / --max - The total number of results we will load before exiting.
