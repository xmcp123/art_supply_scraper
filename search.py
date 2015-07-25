from macpherson import MacPhersonSearch,MacPhersonProductList
import argparse
import csv,os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Art Scraper')
    parser.add_argument('-nt', '--threads', help='Number of threads to load these with',default=4,type=int)
    parser.add_argument('-s', '--search', help='Your keyterm to search for',
                        default='markers')
    parser.add_argument('-max', '--max', help='Maximum number of results',
                        default=30)
    parser.add_argument('-o', '--output', help='Output csv file',
                        default='/tmp/out.csv')
    args = parser.parse_args()

    print "Searching for ",args.search
    ms = MacPhersonSearch(keyword = args.search, max_results = args.max)
    ms.search()
    print "Creating Product list"
    mp=MacPhersonProductList(ms,max_threads=args.threads)

    results = mp.product_list
    if os.path.exists(args.output):
        print "Removing old file ",args.output
        os.remove(args.output)
    print "Writing ",len(results), "to file",args.output

    with open(args.output, 'wb') as csvfile:

        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Parent Title","Title","Price","Location","Amount","Total","Percent of Total","URL"])
        for result in results:
            cur_row = []
            key_list = ['parent_title','title','price','location','amount','total','percent_of_total','url']
            for key in key_list:
                cur_row.append(result[key])
            writer.writerow(cur_row)