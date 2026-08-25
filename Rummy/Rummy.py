import random

# ------------------ CARD + DECK + TABLE ------------------
suits = ['♥', '♦', '♣', '♠']
ranks =['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
#ranks = ['10', 'J', 'Q', 'K', 'A'] #enable for testing

rank_order = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14
} #used for sorting hand

deck_size = len(ranks)*len(suits) #used for ending game

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in suits for r in ranks]
        random.shuffle(self.cards)

    def draw(self):
        global deck_size
        global countdown_start
        if deck_size > 0:
            deck_size -= 1
            if deck_size == 0:
                print("\n-- Deck is Empty --")
                countdown_start = True
            return self.cards.pop()
        else:
            return None

class Table:
    def __init__(self):
        self.melds = []
    
    def add_meld(self, player, meld):
        sort_cards(meld)
        player.add_points(get_points(meld))
        self.melds.append(meld)
    
    def add_indiv(self, player, card):
        global meld_index
        mesh_meld = []
        mesh_meld = self.melds[meld_index].copy()
        mesh_meld.append(card)
        player.add_points(get_points(mesh_meld) - get_points(self.melds[meld_index]))
        self.melds[meld_index].append(card)
        sort_cards(self.melds[meld_index])
        meld_index=0

    def __repr__(self):
        string = "Table Melds:"
        for i in range(len(self.melds)):
            string += "\n"+str(i)+": "+str(self.melds[i])
        return string

# ------------------ PLAYER ------------------

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.points = 0

    def draw_card(self, deck):
        card = deck.draw()
        if card:
            self.hand.append(card)
            return card
        elif card == None:
            return None

    def discard(self, index):
        global game_going
        if len(self.hand) == 1:
            game_going = False
        return self.hand.pop(index)

    def show_hand(self):
        sort_cards(self.hand)
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}")
    
    def add_points(self, amount):
        self.points += amount
    
    def turn(self, player, deck, discard_pile):
        if playerlist[player][0] == "Human":
            player_turn(player, deck, discard_pile)
        elif playerlist[player][0] == "Bot":
            ai_turn(player, deck, discard_pile)

# ------------------ GAME LOGIC ------------------
def sort_cards(cards):
    cards.sort(key=lambda card: (rank_order[card.rank], card.suit))

def can_form_meld_with_card(hand, new_cards = [], checking = False, check_set = False, check_run = False):
    global combination
    global playng_on_table
    combination = []
    temp_hand = hand + new_cards

    # Try all combinations of 3+ cards with selected
    if (checking):
        for i in range(len(temp_hand)):
            for j in range(i + 1, len(temp_hand)):
                for k in range(j + 1, len(temp_hand)):
                    combo = [temp_hand[i], temp_hand[j], temp_hand[k]]

                    if new_cards[0] not in combo:
                        continue

                    if is_valid_meld(combo):
                        if playing_on_table:
                            combination.append(temp_hand[i])
                            combination.append(temp_hand[j])
                            combination.append(temp_hand[k])
                        return True
                    elif check_set and is_valid_set(combo):
                        if playing_on_table:
                            combination.append(temp_hand[i])
                            combination.append(temp_hand[j])
                            combination.append(temp_hand[k])
                        return True
                    elif check_run and is_valid_run(combo):
                        if playing_on_table:
                            combination.append(temp_hand[i])
                            combination.append(temp_hand[j])
                            combination.append(temp_hand[k])
                        return True

    #Try all combinations of 3+ cards
    elif (not checking):
        for i in range(len(temp_hand)):
            for j in range(i + 1, len(temp_hand)):
                for k in range(j + 1, len(temp_hand)):
                    combo = [temp_hand[i], temp_hand[j], temp_hand[k]]
                    if is_valid_meld(combo):
                        return True
                    elif check_set and is_valid_set(combo):
                        return True
                    elif check_run and is_valid_run(combo):
                        return True
    return False

def can_play_on_table(hand, table, selected_cards = [], checking = False):
    if not checking:
        for meld in table:
            for card in hand:
                if is_valid_set(meld):
                    if can_form_meld_with_card(meld, [card], True, True, False):
                        #print("hey")
                        return True
                elif is_valid_run(meld):
                    if can_form_meld_with_card(meld, [card], True, False, True):
                        #print("hey2")
                        return True
        return False
    else:
        mesh_meld = []
        for meld in table:
            if is_valid_set(meld):
                if can_form_meld_with_card(meld, [selected_cards[0]], True, True, False):
                    #print("hi")
                    return True
            elif is_valid_run(meld):
                if can_form_meld_with_card(meld, [selected_cards[0]], True, False, True):
                    #print("hi2")
                    return True
        for meld in table:
            if is_valid_run(meld):
                for card in hand:
                    if can_form_meld_with_card(meld, [card], True, False, True):
                        mesh_meld = meld.copy()
                        mesh_meld.append(card)
                        if can_form_meld_with_card(mesh_meld, selected_cards, True, False, True):
                            #print("hello")
                            return True
    return False

def is_valid_set(cards):
    if len(cards) < 3:
        return False

    ranks = [card.rank for card in cards]
    suits = [card.suit for card in cards]

    return len(set(ranks)) == 1 and len(set(suits)) == len(cards)

def is_valid_run(cards):
    if len(cards) < 3:
        return False

    # Same suit
    suits = [card.suit for card in cards]
    if len(set(suits)) != 1:
        return False

    # Sort by rank
    values = sorted([rank_order[card.rank] for card in cards])
    #Check Ace 2 3
    if (values[-1] == 14 and values[1] == 3 and values[0] == 2):
        for i in range(len(values) - 2):
            if values[i] + 1 != values[i + 1]:
                return False
        return True
    # Check consecutive
    for i in range(len(values) - 1):
        if values[i] + 1 != values[i + 1]:
            return False

    return True

def is_valid_meld(cards):
    return is_valid_set(cards) or is_valid_run(cards)

def draw_from_discard(player, discard_pile, index):
    drawn_cards = discard_pile[index:]
    del discard_pile[index:]
    player.hand.extend(drawn_cards)
    return drawn_cards

def play_meld(player, selected_cards, indices):
    # Validate meld
    if not is_valid_meld(selected_cards):
        return 2

    # Remove cards ONLY after validation
    meld = []
    for i in indices:
        meld.append(player.hand.pop(i))
    return meld

def play_table(player, selected_cards, indices):
    global meld_index

    mesh_meld = table.melds[meld_index].copy()
    for card in selected_cards:
        mesh_meld.append(card)
    
    try:
        if not is_valid_meld(mesh_meld):
            return None
    except IndexError:
        return None
    
    cards = []
    for i in indices:
        cards.append(player.hand.pop(i))
    return cards

def get_points(meld):
    points = 0
    ranks = []
    for card in meld:
        ranks.append(card.rank)
    for rank in ranks:
        if rank in ("2", "3", "4", "5", "6", "7", "8", "9"):
            points += 5
        elif rank in ("10", "J", "Q", "K"):
            points += 10
        elif rank == "A":
            if ranks[0] == "A":
                    if ranks[1] == "A":
                        points +=15
            elif "K" in ranks:
                points+=10
            elif "2" in ranks:
                points +=5
    return points
                
def player_turn(player, deck, discard_pile):
    print("\n---", playerlist[player][1] + "'S TURN ---")
    global countdown
    global countdown_start
    global game_going
    global meld_index
    if countdown_start:
        countdown -=1
        if countdown == 0:
            game_going = False
    selected_card = None
    drawn_cards = []

    # ---- DRAW PHASE LOOP ----
    while True:
        print("\nDiscard pile:")
        for i, card in enumerate(discard_pile):
            print(f"{i}: {card}")

        print("\nYour hand:")
        player.show_hand()

        choice = input("Draw from (d)eck or (p)ile? ")

        if choice == 'd':
            # Draw from deck
            card = player.draw_card(deck)
            if card != None:
                print(f"You drew: {card}")
                break  # done with draw phase
            else:
                print("❌ Deck is Empty")
                continue

        elif choice == 'p':
            index = int(input("Choose which card to draw down to (0 = bottom, last index= top): "))

            if index < 0 or index >= len(discard_pile):
                print("❌ Invalid index. Try again.")
                continue

            selected_cards = discard_pile[index:]

            # Top card case → optional meld
            if index == len(discard_pile) - 1:
                # Take top card
                player.hand.append(discard_pile.pop())
                print(f"You took down to: {selected_cards[0]}")
                break  # done with draw phase

            else:
                # Non-top card → must be playable
                if can_form_meld_with_card(player.hand, selected_cards, True) or (can_play_on_table(player.hand, table.melds, selected_cards, True) and player.points != 0):
                    # Take all cards from chosen down to top
                    selected_card = discard_pile[index]
                    drawn_cards = discard_pile[index:]
                    del discard_pile[index:]
                    player.hand.extend(drawn_cards)

                    print("\nYou picked up:")
                    for card in drawn_cards:
                        print(card)
                    break  # done with draw phase
                else:
                    print("❌ You are not able to play this. Try again.")
                    continue  # return to start of draw phase

        else:
            print("❌ Invalid choice. Try again.")
            continue

    # -------- PLAY MELDS --------
    while can_form_meld_with_card(player.hand):
        print("\nYour hand:")
        player.show_hand()
        choice = input("Do you want to play a meld? (y/n): ")

        if choice != 'y':
            if selected_card == None or selected_card not in player.hand or (can_play_on_table(player.hand, table.melds, [selected_card], True) and player.points != 0):
                break
            print("❌ You must play a meld using the selected discard card!")
            continue
        
        indices = input("Enter card indices (space separated): ")
        indices = list(map(int, indices.split()))
        indices.sort(reverse = True)

        selected_cards = []
        for i in indices:
            selected_cards.append(player.hand[i])
        
        # Enforce required card rule
        if selected_card and selected_card not in selected_cards and selected_card in player.hand :
            print("❌ You must use the selected card from discard in your meld!")
            continue

        meld = play_meld(player, selected_cards, indices)

        if meld and meld != 2:
            print("✅ You played:", meld)
            table.add_meld(player, meld)
        elif meld == 2:
            print("❌ Invalid meld! Must be a set or run.")

    #----------- PLAY CARDS ON TABLE ---------
    while can_play_on_table(player.hand, table.melds) and player.points != 0:
        print("\n")
        print(table)
        print("\nYour hand:")
        player.show_hand()

        choice = input("Do you want to play a card on the table? (y/n): ")
        if choice != 'y':
            if selected_card == None or selected_card not in player.hand:
                break
            print("❌ You must play the selected discard card!")
            continue

        print("\n")
        print(table)
        print("\nYour hand:")
        player.show_hand()
        try:
            indices = input("Which card/cards do you want to play: ")
            indices = list(map(int, indices.split()))
            indices.sort(reverse=True)
        except ValueError:
                print("❌ Invalid choice. Try again.")
                continue
        selected_cards = []
        try:
            for i in indices:
                selected_cards.append(player.hand[i])
        except IndexError:
            print("❌ Please select a number in the provided indices.")
            continue

        if selected_card and selected_card not in selected_cards and selected_card in player.hand :
            print("❌ You must use the selected card from the discard pile.")
            continue
        
        try:
            meld_index = int(input("Which meld do you want to add to: "))
        except ValueError:
                    print("❌ Invalid choice. Try again.")
                    continue
        
        
        cards = play_table(player, selected_cards, indices)
        if cards:
            for card in cards:
                print("✅ You played:", card)
                table.add_indiv(player, card)
        elif cards == False:
            break
        else:
            print("❌ Invalid meld! Must form a set or run.")


    # -------- DISCARD ---------
    have_discarded = False
    while (not have_discarded and len(player.hand) != 0):
        print("\nYour hand before discard:")
        player.show_hand()

        try:
            discard_index = int(input("Choose index to discard: "))
            if (discard_index <= (len(player.hand)-1) and discard_index>=0):
                have_discarded = True
                card = player.discard(discard_index)
                discard_pile.append(card)
                print("Discarded:", card)
            else:
                print("❌ Invalid choice. Try again.")
        except ValueError:
            print("❌ Invalid choice. Try again.")

def ai_turn(player, deck, discard_pile):
    print("\n--- ", playerlist[player][1]+ "'S TURN ---")
    global combination
    global countdown
    global countdown_start
    global game_going
    global meld_index
    global playing_on_table
    if countdown_start:
        countdown -=1
        if countdown == 0:
            game_going = False
    selected_card = None
    drawn_cards = []

    #define choices for drawing
    choices = ['d', 'p']
    pile_choices = []
    pile_choices.append(len(discard_pile) - 1) #Always allow top card
    for i in range(len(discard_pile)):
        selected_cards = discard_pile[i:]
        if can_form_meld_with_card(player.hand, selected_cards, True) or can_play_on_table(player.hand, table.melds, selected_cards, True):
            pile_choices.append(i)
    if len(deck.cards) == 0:
        choices.remove('d')
    
    # ---- DRAW PHASE LOOP ----
    while True:
        choice = random.choice(choices)  # Randomly choose to draw from deck or pile

        if choice == 'd':
            # Draw from deck
            card = player.draw_card(deck)
            print(f"{player.name} drew a card from the deck.")
            break # done with draw phase

        elif choice == 'p':
            index = random.choice(pile_choices)

            selected_cards = discard_pile[index:]

            # Top card case → optional meld
            if index == len(discard_pile) - 1:
                # Take top card
                player.hand.append(discard_pile.pop())
                print(f"{player.name} took down to: {selected_cards[0]}")
                break  # done with draw phase

            else:
                # Take all cards from chosen down to top
                selected_card = discard_pile[index]
                drawn_cards = discard_pile[index:]
                del discard_pile[index:]
                player.hand.extend(drawn_cards)

                print(f"{player.name} picked up:")
                for card in drawn_cards:
                    print(card)
                break  # done with draw phase

    # -------- PLAY MELDS --------

    while can_form_meld_with_card(player.hand):
        no_included = False

        yes_or_no = ['y']
        #yes_or_no = [] #used for testing
        if selected_card == None or selected_card not in player.hand or (can_play_on_table(player.hand, table.melds, [selected_card], True)and player.points != 0):
            yes_or_no.append('n')  # Allow 'n' if no required card
            no_included = True


        choice = random.choice(yes_or_no)  # Randomly choose to play a meld or not
        if choice != 'y':
            break
        meld_choices = []
        for i in range(len(player.hand)):
            for j in range(i + 1, len(player.hand)):
                for k in range(j + 1, len(player.hand)):
                    combo = [player.hand[i], player.hand[j], player.hand[k]]
                    if is_valid_meld(combo) and no_included:
                        meld_choices.append((combo, [i, j, k]))
                    elif is_valid_meld(combo) and not no_included and selected_card in combo:
                        meld_choices.append((combo, [i, j, k]))
        meld, indices = random.choice(meld_choices)  # Randomly select a meld from the available choices

        selected_cards = meld
        indices.sort(reverse=True)

        meld = play_meld(player, selected_cards, indices)

        if meld and meld != 2:
            sort_cards(meld)
            print(f"{player.name} played:", meld)
            table.add_meld(player, meld)

    #----------- PLAY CARDS ON TABLE ---------
    while can_play_on_table(player.hand, table.melds) and player.points != 0:
        no_included = False
        yes_or_no = ['y']
        if selected_card == None or selected_card not in player.hand:
            yes_or_no.append('n')  # Allow 'n' if no required card
            no_included = True
        choice = random.choice(yes_or_no)  #choose to play a meld or not
        if choice != 'y':
            break
        check_others = False
        combination = []
        playing_on_table = True
        playable_cards = []
        for i in range(len(player.hand)):
            for meld in table.melds:
                meld_index = table.melds.index(meld)
                if can_form_meld_with_card(meld, [player.hand[i]], True) and no_included:
                    combination = [player.hand[i]]
                    playable_cards.append([combination, [i, meld_index]])
                elif can_form_meld_with_card(meld, [player.hand[i]], True) and not no_included and selected_card == player.hand[i]:
                    for card in table.melds[meld_index]:
                        try:
                            combination.remove(card)
                        except ValueError:
                            pass
                        check_others = True
                    playable_cards.append([combination, [i, meld_index]])

        choice_cards = random.choice(playable_cards)

        meld_index = choice_cards[1][1]

        index_of_other = None
        if check_others:
            if choice_cards[0].index(selected_card) != 0:
                index_of_other = 0
            elif choice_cards[0].index(selected_card) != 1 and len(choice_cards[0]) > 1:
                index_of_other = 1
            else:
                check_others = False

        if check_others:
            indices = [choice_cards[1][0], player.hand.index(choice_cards[0][index_of_other])]
        else:
            indices = [choice_cards[1][0]]

        cards = play_table(player, combination, indices)
        if cards:
            for card in cards:
                print(player.name + " played:", card, "on", table.melds[meld_index])
                table.add_indiv(player, card)
        playing_on_table = False

    # -------- DISCARD ---------
    if len(player.hand) > 0:
        choice = random.randint(0, len(player.hand)-1)
        card = player.discard(choice)
        discard_pile.append(card)
        print(player.name + " discarded:", card)


# ------------------ GAME SETUP ------------------
deck = Deck() #instantiate deck
table = Table() #instantiate table
discard_pile = [] #instantiate discard_pile

meld_index = 0 #used for playing cards on table

combination = [] #used for playing cards on table

playing_on_table = False #used for playing cards on table

players = {"DEV":"Human", "AI": "Bot"} #players provided to the game in this form (temporary)

playerlist = {}
# create players in playerlist in the form player object, [player type ("Bot" or "Human"), player name str]
for playername in players:
    player = Player(playername)
    playerlist.update({player: [players[playername], playername]})
    for _ in range(7):
        player.draw_card(deck)


# Start discard pile with 1 card
discard_pile.append(deck.draw())

# used for ending game at the right time
countdown = len(players)
countdown_start = False
game_going = True

# ------------------ GAME LOOP ------------------

while game_going:
    for player in playerlist:
        player.turn(player, deck, discard_pile)
        if game_going == False:
            break

# ------------------ END GAME ------------------
print("\n------ Game Over ------")
print(table)
print("Final Scores:")
for player in playerlist:
    for card in player.hand:
        if card.rank == "A":
            player.add_points(-15)
        else:
            player.add_points(-get_points([card]))
    print("\n"+player.name + "'s Score: "+ str(player.points)+"\n"+player.name+"'s Hand:"+str(player.hand))
