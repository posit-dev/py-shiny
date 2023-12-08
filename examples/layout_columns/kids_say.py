import numpy as np
from htmltools import TagList

from shiny import ui

kid_phrases = [
    "Why is the sky blue?",
    "I want ice cream for breakfast!",
    "Can I have a pet dinosaur?",
    "I have imaginary friends!",
    "Let's build a treehouse!",
    "Why do bees buzz?",
    "I can do a cartwheel!",
    "Can we have a giant pillow fight?",
    "What if I could fly like a bird?",
    "I love playing in mud!",
    "Let's have a picnic on the moon!",
    "Can we have a sleepover every day?",
    "Why do I have to go to bed so early?",
    "One day, I'll be a superhero!",
    "I want to learn magic tricks!",
    "Can I paint the walls with glitter?",
    "Let's have a dance party in the living room!",
    "I wish I could talk to animals!",
    "What if the clouds were made of cotton candy?",
    "I want to be a dinosaur when I grow up!",
    "Can I have chocolate for dinner?",
    "What if toys came to life when we're not looking?",
    "I want to explore the deep ocean like a mermaid!",
    "Can we have a pet elephant?",
]

hipster_names = [
    "Hazel",
    "Felix",
    "Luna",
    "Jasper",
    "Olive",
    "Atticus",
    "Clementine",
    "August",
    "Ivy",
    "Ezra",
    "Wren",
    "Arlo",
    "Juniper",
    "Finn",
    "Aurora",
    "Milo",
    "Harper",
    "Theo",
    "Poppy",
    "Otto",
    "Willow",
    "Silas",
    "Maisie",
    "Oscar",
]


def random_cards(n=1):
    base_classes = [
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
        "light",
        "dark",
    ]
    classes = [f"bg-{c}-subtle text-{c}-emphasis" for c in base_classes]

    # Randomly sample, with replacement, from kid_phrases, hipster_name and classes
    # to create an array of cards
    phrases = np.random.choice(kid_phrases, n)
    names = np.random.choice(hipster_names, n)
    classes = np.random.choice(classes, n)

    return [
        ui.card(
            ui.h5(f"{names[i]} says", class_="card-title"),
            phrases[i],
            class_=classes[i],
        )
        for i in range(n)
    ]


def random_card():
    return random_cards(1)[0]
