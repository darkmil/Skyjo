# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import numpy as np


class InvalidCardIndex(Exception):
    pass

class CardAlreadyKnown(Exception):
    pass




initial_knowledge = 2
cards_per_player = 12
row_per_player = 4
column_per_player = cards_per_player // row_per_player


law = np.array([5, 10, 15] + [10]*12)
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
            player_list.append(Skyjo_player())
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
    
    def look_at_top_discard_card(self):
        top_card_value = self.__discard[-1]
        return top_card_value
    
    def __determine_starting_player(self):
        cards_value_list = []
        for player in self.player_list:
            cards_value = player.get_known_cards()[1]
            cards_value_list.append(cards_value)
        sorting_list = np.array([(k, np.sum(val), np.max(val)) for k, val in enumerate(cards_value_list)])
        starting_player_index = sorting_list[np.lexsort((sorting_list[:,2], sorting_list[:,1]))][-1, 0]
        self.player_list = np.roll(self.player_list, -starting_player_index)


class Skyjo_player():
    def __init__(self):
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
        return self.__cards[np.abs(self.__)]
    
    def play(self, startegy='std'):
        if startegy == 'std':
            top_discard_card_value
            
        
skyjo_instance = Skyjo_game(4)
for k in skyjo_instance.player_list:
    print(np.sum(k.get_known_cards()[1]))