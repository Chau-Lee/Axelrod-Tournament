import random
import pandas as pd
from tabulate import tabulate
import os

from strategies import (
    # 10 Top "Nice" Strategies
    TitForTat,
    Champion,
    Elem,
    Cave,
    Graaskamp,
    WmAdams,
    Borufsen,
    Kluepfel,
    RichardHufford,
    Yamachi,
    # 10 Top "Not Nice" (Probing / Mean) Strategies
    Tester2nd,
    DynamicTFT,
    Tranquilizer,
    Joss,
    Tester3,
    RevisedDowning,
    Tester,
    SuspiciousTitForTat,
    AlwaysDefect,
    RandomStrategy
)

PAYOFFS = {
    ('C', 'C'): (3.0, 3.0),
    ('C', 'D'): (0.0, 5.0),
    ('D', 'C'): (5.0, 0.0),
    ('D', 'D'): (1.0, 1.0),
}

ROUNDS_PER_MATCH = 100


def apply_noise(move, noise_level):
    if noise_level > 0 and random.random() < noise_level:
        return 'D' if move == 'C' else 'C'
    return move


def play_match(p1, p2, rounds=ROUNDS_PER_MATCH, noise=0.0):
    hist1, hist2 = [], []
    total_score1, total_score2 = 0.0, 0.0

    for _ in range(rounds):
        m1_intended = p1.move(hist1, hist2)
        m2_intended = p2.move(hist2, hist1)

        m1_actual = apply_noise(m1_intended, noise)
        m2_actual = apply_noise(m2_intended, noise)

        hist1.append(m1_actual)
        hist2.append(m2_actual)

        pts1, pts2 = PAYOFFS[(m1_actual, m2_actual)]
        total_score1 += pts1
        total_score2 += pts2

    return total_score1, total_score2


def run_tournament(strategies_list, rounds=ROUNDS_PER_MATCH, noise=0.0):
    strategy_names = [s.name for s in strategies_list]
    
    # Map strategies to short abbreviations for matrix headers
    abbr_map = {
        'Tit for Tat': 'TFT',
        'Champion': 'CH',
        'Elem': 'EL',
        'Cave': 'CA',
        'Graaskamp': 'GR',
        'WmAdams': 'WA',
        'Borufsen': 'BO',
        'Kluepfel': 'KL',
        'Richard Hufford': 'RH',
        'Yamachi': 'YA',
        'Tester 2nd': 'T2',
        'Dynamic TFT': 'DT',
        'Tranquilizer': 'TR',
        'Joss': 'JO',
        'Tester 3': 'T3',
        'Revised Downing': 'RD',
        'Tester': 'TE',
        'Suspicious Tit for Tat': 'ST',
        'Always Defect': 'AD',
        'Random (50/50)': 'RN'
    }
    
    abbr_names = [abbr_map.get(name, name[:2].upper()) for name in strategy_names]
    
    matrix = {abbr: {opp_abbr: 0.0 for opp_abbr in abbr_names} for abbr in abbr_names}
    num_strategies = len(strategies_list)

    for i in range(num_strategies):
        for j in range(i, num_strategies):
            s1 = strategies_list[i]
            s2 = strategies_list[j]
            a1 = abbr_names[i]
            a2 = abbr_names[j]

            score1, score2 = play_match(s1, s2, rounds=rounds, noise=noise)

            if i == j:
                matrix[a1][a2] = round(score1, 1)
            else:
                matrix[a1][a2] = round(score1, 1)
                matrix[a2][a1] = round(score2, 1)

    df = pd.DataFrame(matrix).T

    # 1. Mean Cumulative Score across all opponents
    df['Mean'] = df.mean(axis=1).round(1)
    
    # 2. Rank Point (Overall position based on mean score)
    df['Rank Point'] = df['Mean'].rank(ascending=False, method='min').astype(int)
    
    # 3. No. of Wins (Count of head-to-head match victories against opponents)
    wins = []
    for row_name in df.index:
        win_count = 0
        for col_name in abbr_names:
            if row_name != col_name:
                if df.loc[row_name, col_name] > df.loc[col_name, row_name]:
                    win_count += 1
        wins.append(win_count)
    df['No. of Wins'] = wins

    # 4. Rank Wins (Rank position based purely on head-to-head win counts)
    df['Rank Wins'] = df['No. of Wins'].rank(ascending=False, method='average')

    # Sort table by Rank Point
    df = df.sort_values(by='Rank Point', ascending=True)
    
    cols_order = abbr_names + ['Mean', 'Rank Point', 'No. of Wins', 'Rank Wins']
    df = df[cols_order]
    
    return df


if __name__ == "__main__":
    while True:
        try:
            user_noise = float(input("Enter noise percentage (0 to 100): "))
            if 0 <= user_noise <= 100:
                noise_decimal = user_noise / 100.0
                break
            print("Please enter a number between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    participants = [
        # Top 10 Nice
        TitForTat(), Champion(), Elem(), Cave(), Graaskamp(),
        WmAdams(), Borufsen(), Kluepfel(), RichardHufford(), Yamachi(),
        # Top 10 Not Nice
        Tester2nd(), DynamicTFT(), Tranquilizer(), Joss(), Tester3(),
        RevisedDowning(), Tester(), SuspiciousTitForTat(), AlwaysDefect(), RandomStrategy()
    ]

    print(f"\nRunning Tournament with 20 Strategies...")
    print(f"Rounds: {ROUNDS_PER_MATCH} | Noise: {user_noise}%\n")

    results_df = run_tournament(participants, rounds=ROUNDS_PER_MATCH, noise=noise_decimal)

    # Append results to CSV
    csv_filename = "tournament_results.csv"
    file_exists = os.path.isfile(csv_filename)
    results_df.to_csv(csv_filename, mode='a', header=not file_exists)
    print(f"Results appended to '{csv_filename}'.\n")

    # Display table matching the Axelrod journal format
    print("================================================ TOURNAMENT STANDINGS ================================================")
    table_formatted = results_df.reset_index().rename(columns={'index': 'Prog.'})
    print(tabulate(table_formatted, headers='keys', tablefmt='github', showindex=False))