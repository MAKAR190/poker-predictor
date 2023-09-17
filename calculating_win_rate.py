import itertools
import random

# Define the ranks and suits
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Define rank values (numerical values for each rank)
rank_values = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 11,  # Updated for Jack
    'Q': 12,
    'K': 13,
    'A': 14  # Ace has the highest value
}
    # Create a dictionary to map full ranks to abbreviated ranks
rank_abbreviations = {
        'Two': '2',
        'Three': '3',
        'Four': '4',
        'Five': '5',
        'Six': '6',
        'Seven': '7',
        'Eight': '8',
        'Nine': '9',
        'Ten': '10',
        'Jack': 'J',
        'Queen': 'Q',
        'King': 'K',
        'Ace': 'A'
    }
# Generate a full deck of cards
deck = [(rank, suit) for rank in ranks for suit in suits]

def evaluate_hand(cards):
    # Define poker hand rankings
    poker_hands = [
        "High Card", "One Pair", "Two Pairs", "Three of a Kind",
        "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
    ]



    # Define rank values (numerical values for each rank)
    rank_values = {
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        'J': 11,
        'Q': 12,
        'K': 13,
        'A': 14  # Ace has the highest value
    }

    # Convert full ranks to abbreviated ranks
    cards = [(rank_abbreviations[card[0]], card[1]) for card in cards]

    def rank_hand(hand):
        return sorted(hand, key=lambda x: rank_values[x[0]])

    def is_straight(hand):
        return all(rank_values[hand[i][0]] == rank_values[hand[i - 1][0]] + 1 for i in range(1, len(hand)))

    def is_flush(hand):
        return all(card[1] == hand[0][1] for card in hand)

    def count_ranks(hand):
        rank_count = {}
        for card in hand:
            rank = card[0]
            if rank in rank_count:
                rank_count[rank] += 1
            else:
                rank_count[rank] = 1
        return rank_count

    def is_four_of_a_kind(hand):
        rank_count = count_ranks(hand)
        return any(count == 4 for count in rank_count.values())

    def is_full_house(hand):
        rank_count = count_ranks(hand)
        return any(count == 3 for count in rank_count.values()) and any(count == 2 for count in rank_count.values())

    def is_three_of_a_kind(hand):
        rank_count = count_ranks(hand)
        return any(count == 3 for count in rank_count.values())

    def is_two_pair(hand):
        rank_count = count_ranks(hand)
        return list(rank_count.values()).count(2) == 4

    def is_one_pair(hand):
        rank_count = count_ranks(hand)
        return list(rank_count.values()).count(2) == 2

    def evaluate_straight_flush(hand):
        if is_straight(hand) and is_flush(hand):
            return poker_hands.index("Straight Flush")
        return -1

    def evaluate_four_of_a_kind(hand):
        if is_four_of_a_kind(hand):
            return poker_hands.index("Four of a Kind")
        return -1

    def evaluate_full_house(hand):
        if is_full_house(hand):
            return poker_hands.index("Full House")
        return -1

    def evaluate_flush(hand):
        if is_flush(hand):
            return poker_hands.index("Flush")
        return -1

    def evaluate_straight(hand):
        if is_straight(hand):
            return poker_hands.index("Straight")
        return -1

    def evaluate_three_of_a_kind(hand):
        if is_three_of_a_kind(hand):
            return poker_hands.index("Three of a Kind")
        return -1

    def evaluate_two_pair(hand):
        if is_two_pair(hand):
            return poker_hands.index("Two Pairs")
        return -1

    def evaluate_one_pair(hand):
        if is_one_pair(hand):
            return poker_hands.index("One Pair")
        return -1

    def evaluate_high_card(hand):
        return poker_hands.index("High Card")

    # Evaluate the poker hand
    hand = rank_hand(cards)
    if evaluate_straight_flush(hand) >= 0:
        return poker_hands[evaluate_straight_flush(hand)]
    if evaluate_four_of_a_kind(hand) >= 0:
        return poker_hands[evaluate_four_of_a_kind(hand)]
    if evaluate_full_house(hand) >= 0:
        return poker_hands[evaluate_full_house(hand)]
    if evaluate_flush(hand) >= 0:
        return poker_hands[evaluate_flush(hand)]
    if evaluate_straight(hand) >= 0:
        return poker_hands[evaluate_straight(hand)]
    if evaluate_three_of_a_kind(hand) >= 0:
        return poker_hands[evaluate_three_of_a_kind(hand)]
    if evaluate_two_pair(hand) >= 0:
        return poker_hands[evaluate_two_pair(hand)]
    if evaluate_one_pair(hand) >= 0:
        return poker_hands[evaluate_one_pair(hand)]
    return poker_hands[evaluate_high_card(hand)]

def calculate_win_rate(my_cards, table_cards, num_simulations=10000):
    # Remove the cards you already have from the deck
    remaining_deck = [card for card in deck if card not in my_cards and card not in table_cards]

    # Define the rules for winning (simplified)
    def evaluate_strength(cards):
    # For simplicity, we assume the highest card wins
     max_rank = max(rank_values.get(card[0], 0) for card in cards)  # Use 0 as the default value for missing ranks
     return rank_values.get(max_rank, max_rank)


    # Convert table card ranks to abbreviated ranks
    table_cards = [(rank_abbreviations.get(card[0], card[0]), card[1]) for card in table_cards]

    # Simulate many poker hands and calculate the win rate
    hands_won = 0

    for _ in range(num_simulations):
        # Shuffle the remaining deck
        random.shuffle(remaining_deck)

        # Deal two additional cards for your hand (assuming a total of 7 cards)
        my_full_hand = my_cards + remaining_deck[:2]

        # Generate all possible combinations of 5 cards from the 7 cards
        all_combinations = itertools.combinations(my_full_hand, 5)

        # Evaluate the strength of each combination
        best_strength = 0
        for combo in all_combinations:
            combo_strength = evaluate_strength(list(combo))
            if combo_strength > best_strength:
                best_strength = combo_strength

        # Evaluate the strength of the table hand
        table_strength = evaluate_strength(table_cards)

        # Compare your hand with the table hand
        if best_strength > table_strength:
            hands_won += 1

    # Calculate your win rate
    win_rate = (hands_won / num_simulations) * 100
    return win_rate

