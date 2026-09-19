import random

class Strategy:
    """Base Strategy Class."""
    def __init__(self, name):
        self.name = name

    def move(self, my_history, opponent_history):
        raise NotImplementedError("Each strategy must implement its own move() method.")


# =====================================================================
# NICE STRATEGIES (Cooperative-First / Non-Exploitative)
# =====================================================================

class TitForTat(Strategy):
    """
    Rank 1 (Anatol Rapoport)
    Tournament Winner
    Simple and iconic: Cooperates on the first move, then copies opponent's previous move.
    """
    def __init__(self):
        super().__init__("Tit for Tat")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        return opponent_history[-1]


class Champion(Strategy):
    """
    Rank 2 (Danny C. Champion)
    2nd Place
    Complex multi-phase strategy:
    - Cooperates for the first 10 rounds.
    - If opponent defects in first 25 rounds, retaliates probabilistically based on defection rate.
    - After round 25, if opponent's total defections exceed 40%, defects permanently.
    - Otherwise, mirrors opponent's move with a slight bias toward forgiveness.
    """
    def __init__(self):
        super().__init__("Champion")

    def move(self, my_history, opponent_history):
        n = len(my_history)
        if n < 10:
            return 'C'
        
        d_count = opponent_history.count('D')
        d_rate = d_count / n

        # Phase 1: Early game retaliation (Rounds 10-25)
        if n < 25:
            if opponent_history[-1] == 'D':
                return 'D'
            if d_count > 0 and random.random() < (d_rate * 1.5):
                return 'D'
            return 'C'

        # Phase 2: Late game strict cut-off (Round > 25)
        if d_rate > 0.40:
            return 'D'
        
        # Default behavior: TFT with 5% chance of unprovoked forgiveness
        if opponent_history[-1] == 'D':
            return 'C' if random.random() < 0.05 else 'D'
        return 'C'


class Borufsen(Strategy):
    """
    Rank 3 (Otto Borufsen)
    3rd Place
    Calculates cumulative defect ratio across entire match length.
    If opponent's lifetime defection rate exceeds 25%, it locks into retaliatory defection.
    """
    def __init__(self):
        super().__init__("Borufsen")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        
        d_ratio = opponent_history.count('D') / len(opponent_history)
        if d_ratio > 0.25:
            return 'D'
        return 'C'


class Cave(Strategy):
    """
    Rank 4 (Rob Cave)
    4th Place
    Forgiving retaliator: Defects if opponent defected in ANY of the last 2 rounds.
    """
    def __init__(self):
        super().__init__("Cave")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        
        # Check last two turns for defections
        if opponent_history[-1] == 'D' or (len(opponent_history) >= 2 and opponent_history[-2] == 'D'):
            return 'D'
        return 'C'


class WmAdams(Strategy):
    """
    Rank 5 (William Adams)
    5th Place
    Uses a 5-round sliding window memory. Retaliates with 'D' if the opponent
    has defected 2 or more times within the last 5 turns.
    """
    def __init__(self):
        super().__init__("WmAdams")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        
        recent_window = opponent_history[-5:]
        if recent_window.count('D') >= 2:
            return 'D'
        return 'C'


class Graaskamp(Strategy):
    """
    Rank 6 (Jim Graaskamp & Ken Katzen)
    6th Place
    Plays Tit-for-Tat standardly, but inserts dynamic periodic probing defections
    at rounds 50, 100, and 150 to check if opponent is an unretaliating bot (e.g. AlwaysCooperate).
    If opponent fails to punish defections within 5 turns, it switches to Always Defect.
    """
    def __init__(self):
        super().__init__("Graaskamp")
        self.exploiting = False

    def move(self, my_history, opponent_history):
        n = len(my_history)
        if not opponent_history:
            self.exploiting = False  # Reset state on match start
            return 'C'

        # Check if probe succeeded without retaliation
        if n in [55, 105, 155] and 'D' in my_history[-5:]:
            if 'D' not in opponent_history[-5:]:
                self.exploiting = True

        if self.exploiting:
            return 'D'

        # Trigger probe defections
        if n in [50, 100, 150]:
            return 'D'

        return opponent_history[-1]


class Kluepfel(Strategy):
    """
    Rank 10 (Charles Kluepfel)
    10th Place
    Plays Tit-for-Tat, but adds a 3% random noise defect element to test opponent stability.
    """
    def __init__(self):
        super().__init__("Kluepfel")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        if random.random() < 0.03:
            return 'D'
        return opponent_history[-1]


class RichardHufford(Strategy):
    """
    Rank 16 (Richard Hufford)
    16th Place
    Early-phase Tit-for-Two-Tats (forgiving), late-phase standard Tit-for-Tat (strict).
    - Rounds 1-20: Requires 2 consecutive defections to retaliate.
    - Rounds 21+: Retaliates immediately after 1 defection.
    """
    def __init__(self):
        super().__init__("Richard Hufford")

    def move(self, my_history, opponent_history):
        n = len(opponent_history)
        if n < 2:
            return 'C'
            
        if n < 20:
            return 'D' if opponent_history[-1] == 'D' and opponent_history[-2] == 'D' else 'C'
            
        return opponent_history[-1]


class Yamachi(Strategy):
    """
    Rank 17 (Brian Yamauchi)
    17th Place
    Looks at a 3-round sliding memory window.
    Defects only if opponent defected at least twice in the past 3 turns.
    """
    def __init__(self):
        super().__init__("Yamachi")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        return 'D' if opponent_history[-3:].count('D') >= 2 else 'C'


class Elem(Strategy):
    """
    Rank N/A (Modern library baseline - Did not exist in the 2nd tournament)
    Plays Tit-for-Tat, but continuously monitors opponent's cooperation rate.
    If the opponent proves to be highly cooperative (>85% C after 10 turns),
    it takes a calculated 5% gamble to defect unprovoked for extra payoff.
    """
    def __init__(self):
        super().__init__("Elem")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        
        n = len(opponent_history)
        if n > 10:
            c_rate = opponent_history.count('C') / n
            if c_rate > 0.85 and random.random() < 0.05:
                return 'D'
                
        return opponent_history[-1]


# =====================================================================
# NOT NICE STRATEGIES (Probing / Exploitative / Mean)
# =====================================================================

class Tranquilizer(Strategy):
    """
    Rank 27 (Submitted as Craig Feathers)
    27th Place
    - Baseline: Plays Tit-for-Tat.
    - Sneaks in dynamic defections with probability p = n / 200.
    - If opponent retaliates after a Tranquilizer defection, apologizes ('C') to reset trust.
    """
    def __init__(self):
        super().__init__("Tranquilizer")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
            
        n = len(my_history)
        
        # If opponent defected on the previous round:
        if opponent_history[-1] == 'D':
            # Apologize ONLY if we defected two turns ago (triggering their response)
            if len(my_history) >= 2 and my_history[-2] == 'D':
                return 'C'
            # Otherwise, retaliate like Tit-for-Tat
            return 'D'
            
        # If opponent cooperated, test sneaky defection after round 10
        if n >= 10:
            p_defect = min(0.25, n / 200.0)
            if random.random() < p_defect:
                return 'D'
                
        return 'C'


class Joss(Strategy):
    """
    Rank 28 (Grofman's adaptation of Joss logic)
    28th Place
    Sneaky variant of Tit-for-Tat:
    Mirrors opponent's moves, but when opponent cooperates, there is a 10% chance
    Joss will sneak in an unprovoked defection to gain an advantage.
    """
    def __init__(self):
        super().__init__("Joss")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'C'
        if opponent_history[-1] == 'C':
            return 'D' if random.random() < 0.10 else 'C'
        return 'D'


class RevisedDowning(Strategy):
    """
    Rank 40 (Leslie Downing)
    40th Place
    Mathematical expected-value maximizer:
    Estimates conditional probabilities:
    - a: Probability opponent cooperates given Downing cooperates.
    - b: Probability opponent cooperates given Downing defects.
    Defects on turn 1 to initialize b. Updates probabilities after each round 
    and chooses the move (C or D) that yields higher long-term expected payoff.
    """
    def __init__(self):
        super().__init__("Revised Downing")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'D'  # Initial move to test 'b'
        
        c_after_c = 0
        c_after_d = 0
        total_c = 0
        total_d = 0

        for i in range(len(my_history) - 1):
            if my_history[i] == 'C':
                total_c += 1
                if opponent_history[i+1] == 'C':
                    c_after_c += 1
            else:
                total_d += 1
                if opponent_history[i+1] == 'C':
                    c_after_d += 1

        alpha = (c_after_c / total_c) if total_c > 0 else 0.5
        beta = (c_after_d / total_d) if total_d > 0 else 0.5

        # Payoffs: R=3 (Reward), S=0 (Sucker), T=5 (Temptation), P=1 (Punishment)
        expected_payoff_C = alpha * 3 + (1 - alpha) * 0
        expected_payoff_D = beta * 5 + (1 - beta) * 1

        return 'C' if expected_payoff_C > expected_payoff_D else 'D'


class Tester(Strategy):
    """
    Rank 46 (David Gladstein)
    46th Place
    Defects on move 1. If opponent retaliates on move 2, plays Tit-for-Tat.
    If opponent does NOT retaliate, alternates C, D, C, D to exploit opponent.
    """
    def __init__(self):
        super().__init__("Tester")

    def move(self, my_history, opponent_history):
        n = len(my_history)
        if n == 0:
            return 'D'
        if n == 1:
            return 'C'
        if opponent_history[0] == 'D' or opponent_history[1] == 'D':
            return opponent_history[-1]
        return 'D' if n % 2 == 0 else 'C'


class RandomStrategy(Strategy):
    """
    Rank 62 (The uniform baseline)
    62nd Place
    Chooses randomly between C and D with 50/50 probability each round.
    """
    def __init__(self):
        super().__init__("Random (50/50)")

    def move(self, my_history, opponent_history):
        return 'C' if random.random() < 0.5 else 'D'


class Tester2nd(Strategy):
    """
    Rank N/A (Modern benchmark variant - Did not exist in the 2nd tournament)
    Probing strategy: Immediately defects on round 1.
    If opponent retaliates with D, switches to standard Tit-for-Tat to cooperate.
    If opponent does not retaliate, continues defecting to exploit them.
    """
    def __init__(self):
        super().__init__("Tester 2nd")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'D'
        # If opponent ever retaliated, fall back to TFT
        if 'D' in opponent_history:
            return opponent_history[-1]
        # Otherwise keep defecting
        return 'D'


class DynamicTFT(Strategy):
    """
    Rank N/A (Modern library baseline - Did not exist in the 2nd tournament)
    Adjusts threshold dynamically: Starts mean (D) or nice (C) based on opponent's overall
    aggression level. Retaliates faster as opponent's defection percentage rises.
    """
    def __init__(self):
        super().__init__("Dynamic TFT")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'D'
        
        d_rate = opponent_history.count('D') / len(opponent_history)
        if random.random() < d_rate:
            return 'D'
        return opponent_history[-1]


class Tester3(Strategy):
    """
    Rank N/A (Modern benchmark variant - Did not exist in the 2nd tournament)
    Starts with 'D' on turn 1. If opponent cooperates on turn 1, defects again on turn 2.
    If opponent retaliates on turn 2, apologizes on turn 3 and plays Tit-for-Tat thereafter.
    """
    def __init__(self):
        super().__init__("Tester 3")

    def move(self, my_history, opponent_history):
        n = len(my_history)
        if n == 0:
            return 'D'
        if n == 1:
            return 'D' if opponent_history[0] == 'C' else 'C'
        if 'D' in opponent_history:
            return opponent_history[-1]
        return 'D'


class SuspiciousTitForTat(Strategy):
    """
    Rank N/A (Theoretical baseline - Did not exist in the 2nd tournament)
    Identical to Tit-for-Tat in every way except it strikes first with 'D' on turn 1.
    """
    def __init__(self):
        super().__init__("Suspicious Tit for Tat")

    def move(self, my_history, opponent_history):
        if not opponent_history:
            return 'D'
        return opponent_history[-1]


class AlwaysDefect(Strategy):
    """
    Rank N/A (Theoretical baseline - Did not exist in the 2nd tournament)
    Unconditionally defects on every single round.
    """
    def __init__(self):
        super().__init__("Always Defect")

    def move(self, my_history, opponent_history):
        return 'D'
