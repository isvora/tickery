import pickle

import jsonpickle


# Load data from json file
def load_data():
    # List of TickerData objects
    ticker_data_list = []

    # Load the content from data.json
    with open('data.json', 'rb') as fp:
        json_list = pickle.load(fp)

    # Loop through the content and use jsonpickle to create objects
    for ticker_data in json_list:
        ticker_data_list.append(jsonpickle.decode(ticker_data))

    # Return the list of TickerData objects
    return ticker_data_list


class Analyser:

    @staticmethod
    def main():
        print("Analysing data...")

        ticker_data_list = load_data()


if __name__ == "__main__":
    Analyser.main()
