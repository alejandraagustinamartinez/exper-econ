from otree.api import *
import random

doc = """
A simple Tullock game 
"""

class C(BaseConstants):
    NAME_IN_URL = 'contest'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5
    ENDOWMENT = 20
    COST_PER_TICKET = {1: 1, 2: 2}
    PRIZE = 20


class Subsession(BaseSubsession):
    is_paid = models.BooleanField()

    def setup(self):
        self.is_paid = (self.round_number == 1)
        self.group_randomly()
        for group in self.get_groups():
            group.setup()


class Group(BaseGroup):
    def setup(self):
        for player in self.get_players():
            player.setup()


    def determine_outcomes(self):
        tickets = []
        for player in self.get_players():
            for i in range(player.tickets_purchased):
                tickets.append(player.id_in_group)
        if not tickets:
            for player in self.get_players():
                tickets.append(player.id_in_group)
        winner_id = random.choice(tickets)
        for player in self.get_players():
            player.is_winner = (player.id_in_group == winner_id)
            player.earnings = (player.endowment - player.cost_per_ticket*player.tickets_purchased
                               + player.is_winner*C.PRIZE)
            if self.subsession.is_paid:
                player.payoff = player.earnings
        #print(tickets)

class Player(BasePlayer):
    endowment = models.IntegerField()
    cost_per_ticket = models.IntegerField()
    tickets_purchased = models.IntegerField()
    is_winner = models.BooleanField()
    earnings = models.IntegerField()

    def setup(self):
        self.endowment = C.ENDOWMENT
        self.cost_per_ticket = C.COST_PER_TICKET[self.id_in_group]


def creating_session(subsession):
    subsession.setup()


# PAGES
class Intro(Page):

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class SetupRound(WaitPage):
    pass


class Decision(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return ['tickets_purchased']


class Waitfordecision(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        for group in subsession.get_groups():
            group.determine_outcomes()


class Results(Page):
    pass


class Endblock(Page):

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Intro,
                 SetupRound,
                 Decision,
                 Waitfordecision,
                 Results,
                 Endblock]
