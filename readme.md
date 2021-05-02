# Cornell ClassRoster Discord Bot

The ClassRoster bot is a convenient Discord bot which pulls information from [Cornell Class Roster](https://classes.cornell.edu), [CUReviews](https://cureviews.org), and RateMyProfessors and returns relevant data when queried about a particular class.

## Adding the Bot

Click [here](https://discord.com/api/oauth2/authorize?client_id=800019561239674890&permissions=8&scope=bot) to add the bot to your server.

## Commands and Getting Started

The bot is very simple. There is only one command, `c!get`. It takes in two arguments:

`DEP`: the department acronym. Click on [this link](https://classes.cornell.edu) for a full listing of department acronyms.

`NUM`: the course number. 

### Examples

`c!get CS 2110` will return results for the class known as CS 2110 - Objected Oriented Programming and Data Structures.

`c!get MMMMM 1111` will return an error message, because no such class exists at Cornell.

![sample output](https://i.imgur.com/e7nLQRy.png)
