# pythonwebcrawler
A program that acceses a set list of websites and extracts data (emails and phone numbers) from them

- input file must be csv and must contain sites without the "https://www." part (accepted formate are example.com or another-example.com. Forbidden ones look like https://www.apple.com or www.samsung.com)
- after having a valid input file all you have to do is to run the program. It will stop when it finishes the entire list of websites
- after the program has stopped processing all the sites, there will be 2 new files called data and alldata
- data contains only valid data (phone numbers & email) while alldata will contain all data that could potentially be a valid one (potential phone numbers & emails)
- keep in mind that the program is still in progress and it will sometime put wrong data in the data file