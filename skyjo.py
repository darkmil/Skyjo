# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import matplotlib.pyplot as plt
import numpy as np

from tqdm import trange, tqdm
from weakref import ref


class InvalidCardIndex(Exception):
    pass

class CardAlreadyKnown(Exception):
    pass

class InvalidStartegy(Exception):
    pass


initial_knowledge = 2
cards_per_player = 12
row_per_player = 4
column_per_player = cards_per_player // row_per_player

value_threshold_discard = 4
value_threshold_replace = 4


law = np.array([5, 10, 15] + [10]*12)
expected_value = np.sum(law * (np.arange(15)-2) / 150)
law_cs = np.cumsum(law)
law_s = np.sum(law)

probability_law = law_cs/law_s


class Skyjo_game():
    def __init__(self, n_player=4):
        self.__deck = self.__gen_deck()
        self.player_list = self.__gen_players(n_player)
        self.__determine_starting_player()
        self.__discard = []
        self.__discard_top_card()
        
    def __gen_deck(self):
        deck = [-2]*5 + [-1]*10 + [0]*15
        for k in range(1, 13):
            deck += [k]*10
        deck = np.random.permutation(deck)
        return list(deck)
    
    def __gen_players(self, n_player):
        player_list = []
        for k in range(n_player):
            player_list.append(Skyjo_player(self))
        for k in range(12):
            for player in player_list:
                player._take_card(self.card_from_deck())
        for player in player_list:
           player._cards_to_array() 
        return player_list
    
    def __discard_top_card(self):
        self.__discard.append(self.__deck.pop())
    
    def card_from_deck(self):
        top_card = self.__deck.pop()
        return top_card
    
    def card_from_discard(self):
        top_card = self.__discard.pop()
        return top_card
    
    def card_to_discard(self, card):
        self.__discard.append(card)
    
    def look_at_top_discard_card(self):
        top_card_value = self.__discard[-1]
        return top_card_value

    def look_at_top_deck_card(self):
        top_card_value = self.__deck[-1]
        return top_card_value
    
    def __determine_starting_player(self):
        cards_value_list = []
        for player in self.player_list:
            cards_value = player.get_known_cards()[1]
            cards_value_list.append(cards_value)
        sorting_list = np.array([(k, np.sum(val), np.max(val)) for k, val in enumerate(cards_value_list)])
        starting_player_index = sorting_list[np.lexsort((sorting_list[:,2], sorting_list[:,1]))][-1, 0]
        self.player_list = np.roll(self.player_list, -starting_player_index)
    
    def play_next_move(self):
        pass

class Skyjo_player():
    def __init__(self, game = None):
        self.__ref_game = ref(game)
        self.__cards = []
        self.__startegy = None
        self.__unknown_cards = np.ones(12, dtype=np.int8)
        for k in range(initial_knowledge):
            self.look_at_random_card()
        
    def _take_card(self, card):
        self.__cards.append(card)
        
    def _cards_to_array(self):
        self.__cards = np.array(self.__cards)
        
    def look_at_card(self, index_card):
        if cards_per_player <= index_card or index_card < 0:
            raise InvalidCardIndex("The index of the card must be positive or equal to 0 and smaller than {}".format(cards_per_player-1))
        elif not self.__unknown_cards[index_card]:
            raise CardAlreadyKnown("This card is already known")
        self.__unknown_cards[index_card] = 0
        
    def look_at_random_card(self):
        self.look_at_card(self.__select_uk_card_at_random())
        
    def __select_uk_card_at_random(self):
        index_selected_card = np.random.randint(np.sum(self.__unknown_cards))
        indices_non_zero = np.nonzero(self.__unknown_cards)[0]
        index_selected_card = indices_non_zero[index_selected_card]
        return index_selected_card
    
    def get_known_cards(self):
        position_known_cards = np.abs(self.__unknown_cards - 1)
        indices_known_cards = np.nonzero(position_known_cards)[0]
        return indices_known_cards, self.__cards[indices_known_cards]
    
    def get_known_score(self):
        _, known_cards = self.get_known_cards()
        return np.sum(known_cards)
    
    def _get_score(self):
        return np.sum(self.__cards)
    
    def replace_card(self, position, card):
        game = self.__ref_game()
        game.card_to_discard(self.__cards[position])
        self.__cards[position] = card
        self.__unknown_cards[position] = 0
        
    def play(self, startegy='lowest'):
        game = self.__ref_game()
        top_discard_card_value = game.look_at_top_discard_card()
        known_cards_positions, known_cards_values = self.get_known_cards()
        if startegy == 'lowest':
            no_of_kc = self.get_number_of_known_cards()
            if no_of_kc == cards_per_player - 1:
                scores_estimated = []
                for player in game.player_list:
                    player_known_score = player.get_known_score()
                    player_number_of_ukc = cards_per_player - player.get_number_of_known_cards()
                    score_estimated = player_known_score + player_number_of_ukc * expected_value
                    scores_estimated.append(score_estimated)
                print(scores_estimated)
            else:
                if top_discard_card_value <= value_threshold_discard:
                    if np.max(known_cards_values) > top_discard_card_value:
                        position_known_card = known_cards_positions[np.argmax(known_cards_values)]
                        top_discard_card = game.card_from_discard()
                        self.replace_card(position_known_card, top_discard_card)
                    else:
                        top_discard_card = game.card_from_discard()
                        position_uk_card = self.__select_uk_card_at_random()
                        self.replace_card(position_uk_card, top_discard_card)
                else:
                    top_deck_card = game.card_from_deck()
                    if top_deck_card <= value_threshold_replace:
                        if np.max(known_cards_values) > top_deck_card:
                            position_known_card = known_cards_positions[np.argmax(known_cards_values)]
                            self.replace_card(position_known_card, top_deck_card)
                        else:
                            position_uk_card = self.__select_uk_card_at_random()
                            self.replace_card(position_uk_card, top_deck_card)
                    else:
                        self.look_at_random_card()
        else:
            raise InvalidStartegy("The strategy selected doesn't exist.")

    def get_number_of_known_cards(self):
        return np.abs(12 - np.sum(self.__unknown_cards))

number_of_player = 4

# for k in skyjo_instance.player_list:
#     print(np.sum(k.get_known_cards()[1]))


# skyjo_instance = Skyjo_game(number_of_player)


scores = []
for k in trange(10000):
    skyjo_instance = Skyjo_game(number_of_player)
    pkc_list = [np.array([])] * 4
    kc_list = [np.array([])] * 4
    nk_cards = []
    while not 12 in nk_cards:
        for k in skyjo_instance.player_list:
            k.play()
            positions_k_cards, k_cards = k.get_known_cards()
            pkc_list.append(positions_k_cards)
            kc_list.append(k_cards)
            nk_cards.append(k.get_number_of_known_cards())
            # print(skyjo_instance.player_list[0].get_known_score())

    
    inter_scores = []
    for k in skyjo_instance.player_list:
        inter_scores.append(k._get_score())
    scores.append(inter_scores)
scores = np.array(scores)
