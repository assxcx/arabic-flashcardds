#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lebanese Arabic Spaced Repition Flash Cards
Created on Fri Sep 26 19:15:37 2025

@author: Joseph
"""
import csv
import random
import datetime
from typing import List, Dict


# Load flashcards from file
def load_flashcards(filename: str) -> List[Dict]:
    flashcards = []
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                flashcards.append({
                    'arabic': row[0],
                    'transliteration': row[1],
                    'translation': row[2],
                    'last_reviewed': row[3] if len(row) > 3 else str(datetime.date.today()),
                    'interval': int(row[4]) if len(row) > 4 else 1,
                    'ease_factor': float(row[5]) if len(row) > 5 else 2.5,
                    'repetition': int(row[6]) if len(row) > 6 else 0
                })
    except FileNotFoundError:
        print(f"⚠️ File not found: {filename}")
    return flashcards

# Save updated flashcards
def save_flashcards(filename: str, flashcards: List[Dict]):
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Arabic', 'Transliteration', 'Translation', 'Last Reviewed', 'Interval', 'Ease Factor', 'Repetition'])
        for card in flashcards:
            writer.writerow([
                card['arabic'], card['transliteration'], card['translation'],
                card['last_reviewed'], card['interval'], card['ease_factor'],
                card['repetition']
            ])

# Log failed cards for trouble list
def log_failed_card(card: Dict, errors_file='errors.csv'):
    with open(errors_file, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            card['arabic'], card['transliteration'], card['translation'],
            str(datetime.date.today())
        ])

# Save progress summary
def save_progress_report(total, correct, incorrect, report_file='progress_report.csv'):
    with open(report_file, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            str(datetime.date.today()), total, correct, incorrect,
            f"{round((correct / total) * 100, 1) if total else 0}%"
        ])

# Spaced repetition update
def update_flashcard(card: Dict, grade: int):
    if grade >= 3:
        if card['repetition'] == 0:
            card['interval'] = 1
        elif card['repetition'] == 1:
            card['interval'] = 6
        else:
            card['interval'] = int(card['interval'] * card['ease_factor'])
        card['repetition'] += 1
    else:
        card['repetition'] = 0
        card['interval'] = 1

    card['ease_factor'] += (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    card['ease_factor'] = max(1.3, card['ease_factor'])
    card['last_reviewed'] = str(datetime.date.today())

# Get cards due today
def get_due_flashcards(flashcards: List[Dict]) -> List[Dict]:
    today = datetime.date.today()
    return [card for card in flashcards if (today - datetime.date.fromisoformat(card['last_reviewed'])).days >= card['interval']]

# Review session (can be normal or trouble mode)
def review_flashcards(flashcards: List[Dict], User, is_trouble_mode=False, seed=0, num_of_words =10):
    random.seed(seed)
    if is_trouble_mode:
        print("⚠️ Trouble Words Mode: Reviewing only missed cards.")
        due_cards = flashcards
    else:
        due_cards = get_due_flashcards(flashcards)
        if not due_cards:
            print("🎉 No cards to review today!")
            return

    random.shuffle(due_cards)
    due_cards = due_cards[:num_of_words]

    total = 0
    correct = 0
    incorrect = 0
    
    for card in due_cards:
        print("\n🧠 Arabic:", card['arabic'])
        input("Transliteration? (press Enter to continue)...")
        print("💬 Transliteration:", card['transliteration'])

        answer = input("What is the English translation? ").strip()
        print(f"✅ Correct: {card['translation']}")
        print(f"📝 Your Answer: {answer}")

        while True:
            try:
                grade = int(input("Rate recall (0=forgot, 4=perfect): "))
                if 0 <= grade <= 4:
                    break
                else:
                    print("Enter a number between 0 and 4.")
            except ValueError:
                print("Enter a valid number.")

        if not is_trouble_mode:
            update_flashcard(card, grade)

        total += 1
        if grade >= 3:
            correct += 1
        else:
            incorrect += 1
            if not is_trouble_mode:
                log_failed_card(card, f'{User}_errors.csv')

        if not is_trouble_mode:
            print(f"📅 Next review in {card['interval']} days.")
            
        done = ''
        while not done in ['Y', 'N']:
            print("Input Y or N to continue")
            done = input("Do you wish to continue?").upper()
        if done == 'N':
            while not done in [1,2]:
                done = int(input("new words (1) or exit (2)?"))
            if done ==1:
                break
            return 0
        
    new_session = ''
    while not new_session in ['N','Y']:
        print("Input Y or N to continue")
        new_session = input("Continue with the same batch words?")
    

    if new_session.upper() == 'N':
        choice = 0 
        while not choice in [1,2]:
            print("Enter 1 or 2 to proceed:")
            choice = int(input('Option 1) Shuffle new words\nOption 2) Change number of words in batch (will also pick new words)'))
        if choice == 1:
            seed+=1
            review_flashcards(flashcards, User, is_trouble_mode, seed, num_of_words)
        elif choice == 2:
            seed+=1
            num_of_words = int(input("Input number of words in batch: "))
            review_flashcards(flashcards, User, is_trouble_mode, seed, num_of_words)
    else:
        review_flashcards(flashcards, User, is_trouble_mode, seed, num_of_words)

            
    # Show and save progress stats
    print("\n📊 Session Summary")
    print(f"Total Reviewed: {total}")
    print(f"✅ Correct: {correct}")
    print(f"❌ Missed: {incorrect}")
    if total > 0:
        percent = round((correct / total) * 100, 1)
        print(f"🎯 Accuracy: {percent}%")
        save_progress_report(total, correct, incorrect, f'{User}_progress_report.csv' )

# Main menu
def main(User):
    seed = random.randint(-1e10,1e10)
    flashcards_file = f'flashcards_{User}.csv'
    print(flashcards_file)
    flashcards = load_flashcards(flashcards_file)

    print("\n🕌 Arabic Spaced Repetition Trainer")

    while True:
        print("\n📋 Choose a mode:")
        print("1. Review due cards (SRS)")
        print("2. Review trouble words")
        print("3. Quit")
        choice = 0
        while not choice in [1,2,3]:
            try:
                choice = int(input("Enter choice (1/2/3): "))
            except ValueError:
                print("Please enter a valid number.")
                continue
        num_of_words = -1
        while num_of_words < 1:
            try:
                num_of_words = int(input("How many words do you wish to review? "))
            except ValueError:
                print("Please enter a valid number.")
                continue
        if choice == 1:
            review_flashcards(flashcards, User, num_of_words=num_of_words,seed=seed)
            save_flashcards(flashcards_file, flashcards)
        elif choice == 2:
            errors = load_flashcards(f'{User}_errors.csv')
            if not errors:
                print("✅ No trouble words logged yet!")
            else:
                review_flashcards(errors, User, is_trouble_mode=True,num_of_words=num_of_words, seed=seed)
        elif choice == 3:
            print("👋 Goodbye! Keep practicing!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    User = ''
    while User != 'BELLA' and User != 'JOE':
        User = input("Bella or Joe?").upper()
    main(User)

