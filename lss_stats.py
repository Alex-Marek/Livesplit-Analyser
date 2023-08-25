from livesplit_analyser_2 import *

def main():
    splits_file = Splits_File()
    with open("6aa1.lss", 'r') as file:
        data = file.read()
    xml_data = BeautifulSoup(data,'xml')
    splits_file.load_whole_file(xml_data)
    splits_file.print_splits_summary()

    


if __name__ == "__main__":
    main()
