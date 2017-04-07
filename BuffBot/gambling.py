import random
from discord.ext import commands
import discord
import database
from coins import Coin
import time

class Gamble:
    def __init__(self, bot):
        self.bot = bot  # The bot object.
        self.database = database.Database(self.bot)  # database object -> used to update and get coin amount
        self.blackjack_players = []
        self.blackjack_game_status = 0
        self.deck = []
        self.coins = Coin(bot)
        self.dealerCards = []

    @commands.group(name="newgame", pass_context=True)
    async def newgame(self,ctx) :
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid newgame command passed...')



    @newgame.command(name="blackjack", pass_context=True)
    async def new_blackjack_game(self):
        if self.blackjack_game_status != 0:
            self.bot.say("A game is already in place.. wait until it is finished.")
            return None,

        self.deck = self.generateCards()
        self.blackjack_game_status = 1
        await self.bot.say("A blackjack table have now opened.. "
                           "please do ``` !joingame blackjack <bet> ``` to join the table.")


    @commands.group(name="joingame", pass_context=True, )
    async def joingame(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid joingame command passed...')

    @joingame.command(name ="test")
    async def test(self):
        print("test")

    @joingame.command(name = "blackjack", pass_context=True)
    async def join_blackjack_game(self, ctx, bet):
        user = ctx.message.author
        if self.blackjack_game_status != 1 :
            await self.bot.say("No table is open for the moment..")
            return None

        if float(bet) <= 0 and not self.coins.check_balance(bet):
            await self.bot.say("{}, please make sure your bet is higher than 0 and you've enough coins.".format(user.mention))
            return None

        self.database.remove_coins(userid=user.id, coins=float(bet), mention=user.mention)

        self.blackjack_players.append({
            "user" : user, "cards": [self.drawCard(), self.drawCard()], "bet" : float(bet), "status" : 0
        })

        await self.bot.say("{}, you've joined the table.. please wait for a host to start the round".format(user.mention))

    @commands.group(name="rungame", pass_context=True)
    async def rungame(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid rungame command passed...')

    @rungame.command(name ="blackjack", pass_context= True)
    async def start_blackjack_table(self, ctx):


        self.blackjack_game_status = 3;
        self.dealerCards = [self.drawCard(), self.drawCard()]
        output = "Welcome to the blackjack room!!! \n"
        output += "Dealers card shown to you fellows is {}\n".format(self.dealerCards[0].getStringSymbol() + self.dealerCards[0].getStringValue())
        output += "====================================================\n"
        for player in self.blackjack_players:
            output += "{} has these cards: {}. That's a total score of {}\n"\
                .format(player['user'].mention, player['cards'][0].getStringSymbol() +  player['cards'][0].getStringValue()
                        + " " +  player['cards'][1].getStringSymbol() + player['cards'][1].getStringValue(), self.blackjack_calculate_card_values(player['cards']))
            pass

        await self.bot.say(output)
        pass

    @commands.group(name="bj", pass_context=True)
    async def bj (self, ctx) :
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid rungame command passed...')

    @bj.command(name = "hit", pass_context=True)
    async def blackjack_hit(self, ctx):
        player = self.player_in_blackjack_table(ctx.message.author)
        if player == None:
            await self.bot.say("{}, you're currently not in a game..".format(ctx.message.author.mention))
            return None

        if player['status'] != 0 :
            await self.bot.say("{}, you're standing..".format(ctx.message.author.mention))
            return None

        player['cards'].append(self.drawCard())
        output = "{}, you're selected draw.. \n".format(ctx.message.author.mention)
        output += "{}, you've not these cards: {}. That's a total score of {}\n" \
            .format(player['user'].mention, player['cards'][0].getStringSymbol() + player['cards'][0].getStringValue()
                    + " " + player['cards'][1].getStringSymbol() + player['cards'][1].getStringValue(),
                    self.blackjack_calculate_card_values(player['cards']))
        await self.bot.say(output)

    @bj.command(name="stand", pass_context=True)
    async def blackjack_hit(self, ctx):
        player = self.player_in_blackjack_table(ctx.message.author)
        if player == None:
            await self.bot.say("{}, you're currently not in a game..".format(ctx.message.author.mention))
            return None

        if player['status'] != 0:
            await self.bot.say("{}, you're standing..".format(ctx.message.author.mention))
            return None
        pass


    def player_in_blackjack_table(self, user):
        for player in self.blackjack_players :
            if player['user'] == user: return player
        return None

    def blackjack_calculate_card_values(self, cards:list):
        score = 0
        for card in cards :
            temp_score = score + card.getCardValue()
            if temp_score > 21 :
                if card.getCardValue() == 11 :
                    temp_score -= 10;
                else :
                    for c_temp in cards :
                        if c_temp.getCardValue() == 21 :
                            temp_score -= 10
                            if temp_score <= 21 : break

            score = temp_score

        return score

    def drawCard (self) :
        if not len(self.deck) > 0 :
            self.deck = self.generateCards()
        return self.deck.pop()


    def generateCards(self):
        '''
        Generate cards and then shuffle them
        @return shuffled deck
        '''
        cards = []  # The veriable that holds all the cards
        deck = 5  # How many deck that is created

        # create deck(s)
        for y in range(0, deck):
            symbol = 0  # deligere symbol
            value = 0  # Deligere value

            # Generate a deck of cards
            for x in range(0, 4):
                for i in range(0, 13):
                    obj = Card(symbol, value)
                    cards.append(obj)
                    value += 1
                symbol += 1
                value = 0

        # Shuffle the decks and return it
        return random.sample(cards, len(cards))


class Card:
    def __init__(self, symbol, value):
        '''
        Symbol er da hvilken type kort det er. 
        Value er da hvilken verdi kortet har
        '''
        self.symbol = symbol
        self.value = value

    def __repr__(self):
        return repr((self.symbol, self.value))

        # Return value of the card

    def getValue(self):
        return self.value

    # Return the symbolValue
    def getSymbol(self):
        return self.symbol

    def getCardValue(self):
        if self.value < 9 : return self.value + 2
        elif self.value >= 9 and self.value != 12: return 10
        else: return 11

    # Set the value over to string for reading
    def getStringValue(self):
        value = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
        return value[self.value]

    # set the symbol value over to string for reading
    def getStringSymbol(self):
        symbol_name = ['♠', '♣', '♥', '♦']
        return symbol_name[self.symbol]


def setup(bot):
    bot.add_cog(Gamble(bot))
