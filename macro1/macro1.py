from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash
from google.cloud import firestore
import random
from operator import itemgetter
import json


macro1 = Blueprint('macro1', __name__, template_folder='templates')

client = firestore.Client()


POLICY_NAMES = {
    'A': 'Increase Infrastructure Spending',
    'B': 'Lower Interest Rates',
    'C': 'Promote Exports',
    'D': 'Raise Interest Rates',
    'E': 'Tax Incentives for Businesses',
    'F': 'Expand Social Welfare Programs',
    'G': 'Decrease Infrastructure Spending',
    'H': 'Limit Exports',
    'J': 'Tax Increases for Businesses',
    'K': 'Cut Social Welfare Programs',
    'L': 'Minimal Intervention Approach'
}

EVENT_NAMES = {
    'I': 'Global Tech Boom',
    'II': 'Oil Price Crash',
    'III': 'Global Recession',
    'IV': 'Pandemic Outbreak',
    'V': 'International Trade War',
    'VI': 'Global Green Revolution',
    'VII': 'Cybersecurity Breach',
    'VIII': 'Natural Disaster Outbreaks',
    'IX': 'Breakthrough in Space Exploration',
    'X': 'Surge in Artificial Intelligence (AI) and Robotics'
}
POLICY_ABBREVIATIONS = {
    'A': 'Increase Infra. Spend',
    'B': 'Lower Interest Rates',
    'C': 'Promote Exports',
    'D': 'Raise Interest Rates',
    'E': 'Business Tax Incentives',
    'F': 'Expand Soc. Welfare',
    'G': 'Decrease Infra. Spend',
    'H': 'Limit Exports',
    'J': 'Business Tax Hike',
    'K': 'Cut Soc. Welfare Prog.',
    'L': 'Min. Intervention'
}
EVENT_NARRATIVES = {
    'I': [
        "The world witnesses a significant tech revolution as major innovations propel the tech industry forward.",
        "This global tech boom results in a remarkable surge in GDP growth, while also slightly tempering price inflation.",
        "The tech boom drives employment opportunities, causing a dip in unemployment rates."
    ],
    'II': [
        "A sudden glut in the global oil market leads to a significant crash in oil prices.",
        "This impacts economies globally, causing a dip in GDP growth.",
        "The crash also leads to a considerable fluctuation in price levels and an increase in unemployment as the energy sector feels the strain."
    ],
    'III': [
        "The world economy enters a downturn, causing a decline in GDP growth across the board.",
        "Inflation rates drop as consumer spending slows, and unemployment rises as businesses struggle to maintain operations."
    ],
    'IV': [
        "A health crisis emerges on a global scale, causing significant disruptions in trade and daily life.",
        "This results in a sharp contraction in GDP growth, a dip in inflation rates due to reduced consumer spending, and a spike in unemployment as businesses close or downsize."
    ],
    'V': [
        "Countries around the world engage in trade disputes, imposing tariffs and restrictions on each other.",
        "This can potentially boost a country's GDP if it manages to gain a trade advantage, but also leads to higher inflation rates as import costs rise.",
        "Employment opportunities fluctuate depending on the country's positioning in the trade war."
    ],
    'VI': [
        "A shift towards sustainable and green technologies gains momentum globally.",
        "This transition fuels GDP growth as new industries emerge and grow.",
        "Inflation sees a moderate rise due to the initial costs of green technologies, but employment opportunities in the green sector lead to a reduction in unemployment."
    ],
    'VII': [
        "A significant cybersecurity breach affects major corporations and government institutions.",
        "This leads to a decline in GDP growth due to lost revenues and the costs of damage control.",
        "Prices rise slightly as businesses pass on some of the costs to consumers, and unemployment increases as affected sectors struggle."
    ],
    'VIII': [
        "Multiple regions face severe natural disasters causing disruptions in supply chains and infrastructure.",
        "This results in a notable contraction in GDP growth, a moderate rise in inflation due to supply shortages, and fluctuations in unemployment as some sectors are hit harder than others."
    ],
    'IX': [
        "Major advancements in space technology and exploration open up new frontiers and possibilities.",
        "This leads to an uptick in GDP growth as the space sector booms.",
        "Inflation remains relatively stable, and the job market sees both gains and losses as industries adjust to the new space age."
    ],
    'X': [
        "A significant leap in artificial intelligence and robotics transforms industries across the board.",
        "This technological surge leads to a substantial boost in GDP growth.",
        "However, the rise of automation leads to mixed effects on inflation and causes fluctuations in the job market, with some sectors benefiting more than others."
    ]
}

EVENT_ABBREVIATIONS = {
    'I': 'Global Tech Boom',
    'II': 'Oil Price Crash',
    'III': 'Global Recession',
    'IV': 'Pandemic Outbreak',
    'V': 'Trade War',
    'VI': 'Green Revolution',
    'VII': 'Cybersecurity Breach',
    'VIII': 'Natural Disasters',
    'IX': 'Space Exploration',
    'X': 'AI and Robotics Surge'
}

POLICY_EFFECTS = {
     'A': {'gdp_growth': (2.45, 4.85),'CPI': (1.05, 2.45),'Unemployment': (-0.55, -0.15)},
     'B': {'gdp_growth': (1.15, 5.55),'CPI': (0.15, 1.55),'Unemployment': (-0.35, 0.05)},
     'C': {'gdp_growth': (2.25, 4.25),'CPI': (-0.25, 3.15),'Unemployment': (-0.25, 0.15)},
     'D': {'gdp_growth': (-0.5, 0.5),'CPI': (-3.0, -1.75),'Unemployment': (1.5, 2.5)},
     'E': {'gdp_growth': (1.35, 5.75),'CPI': (-1.5, 0.25),'Unemployment': (-0.45, -0.05)},
     'F': {'gdp_growth': (2.15, 3.05),'CPI': (-1.0, 0.75),'Unemployment': (-0.05, 0.35)},
     'G': {'gdp_growth': (-4.85, -2.45),'CPI': (-2.45, -1.05),'Unemployment': (0.15, 0.55)},
     'H': {'gdp_growth': (-4.25, -2.25),'CPI': (-3.15, 0.25),'Unemployment': (-0.15, 0.25)},
     'J': {'gdp_growth': (-5.75, -1.35),'CPI': (-0.25, 1.5),'Unemployment': (0.05, 0.45)},
     'K': {'gdp_growth': (-3.05, -2.15),'CPI': (-0.75, 1.0),'Unemployment': (-0.35, 0.05)},
     'L': {'gdp_growth': (0, 0),'CPI': (0, 0),'Unemployment': (0, 0)}
}

EVENT_EFFECTS = {
    'I': {'gdp_growth': (4.82, 5.22), 'CPI': (-0.82, 0.58), 'Unemployment': (-1.75, -1.00)},
    'II': {'gdp_growth': (-1.82, 0.22), 'CPI': (-1.28, 2.72), 'Unemployment': (0.86, 2.26)},
    'III': {'gdp_growth': (-1.12, -2.52), 'CPI': (-2.78, -1.32), 'Unemployment': (0.76, 2.66)},
    'IV': {'gdp_growth': (-0.92, -3.02), 'CPI': (-4.48, 0.88), 'Unemployment': (0.24, 5.86)},
    'V': {'gdp_growth': (-0.62, 4.02), 'CPI': (1.68, 3.08), 'Unemployment': (-0.56, 1.46)},
    'VI': {'gdp_growth': (1.5, 3.5), 'CPI': (1.1, 2.0), 'Unemployment': (-1.5, -0.5)},
    'VII': {'gdp_growth': (-2.0, -0.5), 'CPI': (0.5, 2.5), 'Unemployment': (0.2, 2.0)},
    'VIII': {'gdp_growth': (-3.50, -1.50), 'CPI': (0.85, 2.75), 'Unemployment': (-1.0, 3.0)},
    'IX': {'gdp_growth': (1.0, 3.5), 'CPI': (0.0, 1.0), 'Unemployment': (-1.5, -0.5)},
    'X': {'gdp_growth': (4.0, 5.5), 'CPI': (-1.0, 1.5), 'Unemployment': (0.5, 1.5)}
}


gdp_interaction_matrix = {
    ("A", "I"): (1.15, 1.2),
    ("A", "II"): (1.03, 1.07),
    ("A", "III"): (1.03, 1.07),
    ("A", "IV"): (0.93, 0.97),
    ("A", "V"): (0.99, 1.01),
    ('A', 'VI'): (1.1, 1.15),
    ('A', 'VII'): (1.0, 1.05),
    ('A', 'VIII'): (1.0, 1.05),
    ('A', 'IX'): (1.1, 1.15),
    ('A', 'X'): (1.1, 1.15),

    ("B", "I"): (1.15, 1.2),
    ("B", "II"): (1.12, 1.16),
    ("B", "III"): (1.03, 1.07),
    ("B", "IV"): (0.9, 0.94),
    ("B", "V"): (1.1, 1.15),
    ('B', 'VI'): (1.05, 1.1),
    ('B', 'VII'): (1.0, 1.05),
    ('B', 'VIII'): (1.0, 1.05),
    ('B', 'IX'): (1.05, 1.1),
    ('B', 'X'): (1.05, 1.1),

    ("C", "I"): (1.2, 1.25),
    ("C", "II"): (1.03, 1.07),
    ("C", "III"): (0.95, 0.99),
    ("C", "IV"): (0.9, 0.94),
    ("C", "V"): (0.9, 0.94),
    ('C', 'VI'): (1.1, 1.15),
    ('C', 'VII'): (1.0, 1.05),
    ('C', 'VIII'): (1.0, 1.05),
    ('C', 'IX'): (1.1, 1.15),
    ('C', 'X'): (1.1, 1.15),

    ("D", "I"): (0.95, 0.99),
    ("D", "II"): (0.95, 0.99),
    ("D", "III"): (0.9, 0.94),
    ("D", "IV"): (0.85, 0.89),
    ("D", "V"): (0.85, 0.89),
    ('D', 'VI'): (0.95, 1.0),
    ('D', 'VII'): (0.9, 0.95),
    ('D', 'VIII'): (0.9, 0.95),
    ('D', 'IX'): (0.95, 1.0),
    ('D', 'X'): (0.95, 1.0),

    ("E", "I"): (1.2, 1.25),
    ("E", "II"): (1.1, 1.15),
    ("E", "III"): (1.03, 1.07),
    ("E", "IV"): (0.93, 0.97),
    ("E", "V"): (1.1, 1.15),
    ('E', 'VI'): (1.1, 1.15),
    ('E', 'VII'): (1.0, 1.05),
    ('E', 'VIII'): (1.0, 1.05),
    ('E', 'IX'): (1.1, 1.15),
    ('E', 'X'): (1.1, 1.15),

    ("F", "I"): (1.05, 1.09),
    ("F", "II"): (1.05, 1.09),
    ("F", "III"): (1.0, 1.05),
    ("F", "IV"): (1.05, 1.09),
    ("F", "V"): (1.0, 1.05),
    ('F', 'VI'): (1.05, 1.1),
    ('F', 'VII'): (1.0, 1.05),
    ('F', 'VIII'): (1.0, 1.05),
    ('F', 'IX'): (1.05, 1.1),
    ('F', 'X'): (1.05, 1.1),

    ('G', 'I'): (0.9, 0.95),
    ('G', 'II'): (0.9, 0.95),
    ('G', 'III'): (0.95, 1.0),
    ('G', 'IV'): (0.9, 0.95),
    ('G', 'V'): (0.9, 0.95),
    ('G', 'VI'): (1.05, 1.1),
    ('G', 'VII'): (1.05, 1.1),
    ('G', 'VIII'): (1.05, 1.1),
    ('G', 'IX'): (1.0, 1.05),
    ('G', 'X'): (1.0, 1.05),

    ('H', 'I'): (0.8, 0.85),
    ('H', 'II'): (0.8, 0.85),
    ('H', 'III'): (0.85, 0.9),
    ('H', 'IV'): (0.8, 0.85),
    ('H', 'V'): (0.8, 0.85),
    ('H', 'VI'): (0.8, 0.85),
    ('H', 'VII'): (0.85, 0.9),
    ('H', 'VIII'): (0.8, 0.85),
    ('H', 'IX'): (0.85, 0.9),
    ('H', 'X'): (0.8, 0.85),

    ('J', 'I'): (0.85, 0.9),
    ('J', 'II'): (0.85, 0.9),
    ('J', 'III'): (0.9, 0.95),
    ('J', 'IV'): (0.85, 0.9),
    ('J', 'V'): (0.85, 0.9),
    ('J', 'VI'): (0.9, 0.95),
    ('J', 'VII'): (0.85, 0.9),
    ('J', 'VIII'): (0.85, 0.9),
    ('J', 'IX'): (0.9, 0.95),
    ('J', 'X'): (0.85, 0.9),

    ('K', 'I'): (0.9, 0.95),
    ('K', 'II'): (0.9, 0.95),
    ('K', 'III'): (0.9, 0.95),
    ('K', 'IV'): (0.9, 0.95),
    ('K', 'V'): (0.9, 0.95),
    ('K', 'VI'): (0.95, 1.0),
    ('K', 'VII'): (0.95, 1.0),
    ('K', 'VIII'): (0.9, 0.95),
    ('K', 'IX'): (0.95, 1.0),
    ('K', 'X'): (0.9, 0.95)

}

# CPI Interaction Matrix
cpi_interaction_matrix = {
    ('A', 'I'): (1.05, 1.1),
    ('A', 'II'): (0.95, 0.99),
    ('A', 'III'): (0.93, 0.97),
    ('A', 'IV'): (1.05, 1.1),
    ('A', 'V'): (1.05, 1.1),
    ('A', 'VI'): (1.05, 1.1),
    ('A', 'VII'): (1.05, 1.1),
    ('A', 'VIII'): (1.05, 1.1),
    ('A', 'IX'): (1.05, 1.1),
    ('A', 'X'): (1.05, 1.1),

    ('B', 'I'): (1.05, 1.1),
    ('B', 'II'): (0.95, 0.99),
    ('B', 'III'): (0.95, 0.99),
    ('B', 'IV'): (0.95, 0.99),
    ('B', 'V'): (1.05, 1.1),
    ('B', 'VI'): (1.05, 1.1),
    ('B', 'VII'): (1.05, 1.1),
    ('B', 'VIII'): (1.05, 1.1),
    ('B', 'IX'): (1.05, 1.1),
    ('B', 'X'): (1.05, 1.1),

    ('C', 'I'): (1.05, 1.1),
    ('C', 'II'): (0.99, 1.01),
    ('C', 'III'): (0.95, 0.99),
    ('C', 'IV'): (0.95, 0.99),
    ('C', 'V'): (0.93, 0.97),
    ('C', 'VI'): (1.0, 1.05),
    ('C', 'VII'): (1.05, 1.1),
    ('C', 'VIII'): (1.05, 1.1),
    ('C', 'IX'): (1.0, 1.05),
    ('C', 'X'): (1.0, 1.05),

    ('D', 'I'): (0.95, 0.99),
    ('D', 'II'): (0.95, 0.99),
    ('D', 'III'): (0.9, 0.94),
    ('D', 'IV'): (0.95, 0.99),
    ('D', 'V'): (0.95, 0.99),
    ('D', 'VI'): (0.95, 1.0),
    ('D', 'VII'): (0.95, 1.0),
    ('D', 'VIII'): (0.95, 1.0),
    ('D', 'IX'): (0.95, 1.0),
    ('D', 'X'): (0.95, 1.0),

    ('E', 'I'): (0.99, 1.01),
    ('E', 'II'): (0.95, 0.99),
    ('E', 'III'): (0.95, 0.99),
    ('E', 'IV'): (1.03, 1.07),
    ('E', 'V'): (0.93, 0.97),
    ('E', 'VI'): (1.0, 1.05),
    ('E', 'VII'): (1.0, 1.05),
    ('E', 'VIII'): (1.0, 1.05),
    ('E', 'IX'): (1.0, 1.05),
    ('E', 'X'): (1.0, 1.05),

    ('F', 'I'): (1.03, 1.07),
    ('F', 'II'): (0.99, 1.01),
    ('F', 'III'): (0.99, 1.01),
    ('F', 'IV'): (0.95, 0.99),
    ('F', 'V'): (0.99, 1.01),
    ('F', 'VI'): (1.05, 1.1),
    ('F', 'VII'): (1.05, 1.1),
    ('F', 'VIII'): (1.05, 1.1),
    ('F', 'IX'): (1.05, 1.1),
    ('F', 'X'): (1.05, 1.1),

    ('G', 'I'): (0.95, 1.0),
    ('G', 'II'): (1.0, 1.05),
    ('G', 'III'): (1.0, 1.05),
    ('G', 'IV'): (1.05, 1.1),
    ('G', 'V'): (1.05, 1.1),
    ('G', 'VI'): (0.95, 1.0),
    ('G', 'VII'): (1.0, 1.05),
    ('G', 'VIII'): (0.95, 1.0),
    ('G', 'IX'): (0.95, 1.0),
    ('G', 'X'): (0.95, 1.0),

    ('H', 'I'): (1.05, 1.1),
    ('H', 'II'): (1.0, 1.05),
    ('H', 'III'): (1.0, 1.05),
    ('H', 'IV'): (1.05, 1.1),
    ('H', 'V'): (1.05, 1.1),
    ('H', 'VI'): (1.05, 1.1),
    ('H', 'VII'): (0.95, 1.0),
    ('H', 'VIII'): (0.95, 1.0),
    ('H', 'IX'): (0.95, 1.0),
    ('H', 'X'): (0.95, 1.0),

    ('J', 'I'): (1.0, 1.05),
    ('J', 'II'): (1.0, 1.05),
    ('J', 'III'): (1.05, 1.1),
    ('J', 'IV'): (1.0, 1.05),
    ('J', 'V'): (1.0, 1.05),
    ('J', 'VI'): (1.0, 1.05),
    ('J', 'VII'): (1.0, 1.05),
    ('J', 'VIII'): (1.0, 1.05),
    ('J', 'IX'): (0.95, 1.0),
    ('J', 'X'): (0.95, 1.0),

    ('K', 'I'): (1.0, 1.05),
    ('K', 'II'): (1.0, 1.05),
    ('K', 'III'): (1.0, 1.05),
    ('K', 'IV'): (1.0, 1.05),
    ('K', 'V'): (1.0, 1.05),
    ('K', 'VI'): (0.95, 1.0),
    ('K', 'VII'): (0.95, 1.0),
    ('K', 'VIII'): (0.95, 1.0),
    ('K', 'IX'): (0.95, 1.0),
    ('K', 'X'): (0.95, 1.0)
}

unemployment_interaction_matrix = {
    ('A', 'I'): (0.85, 0.9),
    ('A', 'II'): (0.9, 0.95),
    ('A', 'III'): (0.9, 0.95),
    ('A', 'IV'): (0.95, 0.99),
    ('A', 'V'): (0.9, 0.95),
    ('A', 'VI'): (0.9, 0.95),
    ('A', 'VII'): (0.95, 1.0),
    ('A', 'VIII'): (0.95, 1.0),
    ('A', 'IX'): (0.9, 0.95),
    ('A', 'X'): (0.9, 0.95),

    ('B', 'I'): (0.85, 0.9),
    ('B', 'II'): (0.9, 0.95),
    ('B', 'III'): (0.95, 0.99),
    ('B', 'IV'): (0.95, 0.99),
    ('B', 'V'): (0.95, 0.99),
    ('B', 'VI'): (0.9, 0.95),
    ('B', 'VII'): (0.9, 0.95),
    ('B', 'VIII'): (0.9, 0.95),
    ('B', 'IX'): (0.9, 0.95),
    ('B', 'X'): (0.9, 0.95),

    ('C', 'I'): (0.85, 0.9),
    ('C', 'II'): (1.0, 1.05),  # assuming an oil-exporting scenario
    ('C', 'III'): (1.05, 1.1),
    ('C', 'IV'): (1.05, 1.1),
    ('C', 'V'): (1.05, 1.1),
    ('C', 'VI'): (0.95, 1.0),
    ('C', 'VII'): (0.9, 0.95),
    ('C', 'VIII'): (0.9, 0.95),
    ('C', 'IX'): (0.95, 1.0),
    ('C', 'X'): (0.95, 1.0),

    ('D', 'I'): (1.05, 1.1),
    ('D', 'II'): (1.05, 1.1),
    ('D', 'III'): (1.1, 1.15),
    ('D', 'IV'): (1.1, 1.15),
    ('D', 'V'): (1.1, 1.15),
    ('D', 'VI'): (1.05, 1.1),
    ('D', 'VII'): (1.05, 1.1),
    ('D', 'VIII'): (1.05, 1.1),
    ('D', 'IX'): (1.05, 1.1),
    ('D', 'X'): (1.05, 1.1),

    ('E', 'I'): (0.9, 0.95),
    ('E', 'II'): (0.9, 0.95),
    ('E', 'III'): (0.95, 0.99),
    ('E', 'IV'): (1.0, 1.05),
    ('E', 'V'): (0.95, 0.99),
    ('E', 'VI'): (0.95, 1.0),
    ('E', 'VII'): (0.95, 1.0),
    ('E', 'VIII'): (0.95, 1.0),
    ('E', 'IX'): (0.95, 1.0),
    ('E', 'X'): (0.95, 1.0),

    ('F', 'I'): (0.99, 1.01),
    ('F', 'II'): (0.99, 1.01),
    ('F', 'III'): (0.95, 0.99),
    ('F', 'IV'): (0.95, 0.99),
    ('F', 'V'): (0.99, 1.01),
    ('F', 'VI'): (0.9, 0.95),
    ('F', 'VII'): (0.9, 0.95),
    ('F', 'VIII'): (0.9, 0.95),
    ('F', 'IX'): (0.9, 0.95),
    ('F', 'X'): (0.9, 0.95),

    ('G', 'I'): (1.05, 1.1),
    ('G', 'II'): (1.0, 1.05),
    ('G', 'III'): (1.0, 1.05),
    ('G', 'IV'): (1.05, 1.1),
    ('G', 'V'): (1.05, 1.1),
    ('G', 'VI'): (1.05, 1.1),
    ('G', 'VII'): (1.05, 1.1),
    ('G', 'VIII'): (1.05, 1.1),
    ('G', 'IX'): (1.0, 1.05),
    ('G', 'X'): (1.0, 1.05),

    ('H', 'I'): (1.1, 1.15),
    ('H', 'II'): (1.05, 1.1),
    ('H', 'III'): (1.05, 1.1),
    ('H', 'IV'): (1.1, 1.15),
    ('H', 'V'): (1.1, 1.15),
    ('H', 'VI'): (1.05, 1.1),
    ('H', 'VII'): (1.1, 1.15),
    ('H', 'VIII'): (1.1, 1.15),
    ('H', 'IX'): (1.05, 1.1),
    ('H', 'X'): (1.1, 1.15),

    ('J', 'I'): (1.1, 1.15),
    ('J', 'II'): (1.1, 1.15),
    ('J', 'III'): (1.15, 1.2),
    ('J', 'IV'): (1.1, 1.15),
    ('J', 'V'): (1.1, 1.15),
    ('J', 'VI'): (1.1, 1.15),
    ('J', 'VII'): (1.15, 1.2),
    ('J', 'VIII'): (1.15, 1.2),
    ('J', 'IX'): (1.1, 1.15),
    ('J', 'X'): (1.15, 1.2),

    ('K', 'I'): (1.05, 1.1),
    ('K', 'II'): (1.05, 1.1),
    ('K', 'III'): (1.05, 1.1),
    ('K', 'IV'): (1.05, 1.1),
    ('K', 'V'): (1.05, 1.1),
    ('K', 'VI'): (1.0, 1.05),
    ('K', 'VII'): (1.05, 1.1),
    ('K', 'VIII'): (1.05, 1.1),
    ('K', 'IX'): (1.0, 1.05),
    ('K', 'X'): (1.0, 1.05)
}

COUNTRY_MULTIPLIERS = {
    "Developed": 1.0,
    "Emerging": (0.90, 1.1),
    "Resource-rich": (0.95, 1.05)
}


INTERACTIONS = {
    'A': {
        'I': {
            'GDP': "Infrastructure boosts tech, enhancing GDP.",
            'CPI': "High-tech infrastructure raises prices.",
            'Unemployment': "Tech projects create jobs."
        },
        'II': {
            'GDP': "Cheaper infrastructure boosts GDP.",
            'CPI': "Low oil prices mitigate inflation.",
            'Unemployment': "More infrastructure projects mean more jobs."
        },
        'III': {
            'GDP': "Infrastructure mitigates recession impacts.",
            'CPI': "Recession can reduce material costs.",
            'Unemployment': "Infrastructure provides jobs during downturns."
        },
        'IV': {
            'GDP': "Lockdowns may delay projects.",
            'CPI': "Disruptions raise material costs.",
            'Unemployment': "Infrastructure jobs likely persist."
        },
        'V': {
            'GDP': "Infrastructure resists trade war impacts.",
            'CPI': "Tariffs can increase material costs.",
            'Unemployment': "Domestic focus maintains jobs."
        },
        'VI': {
            'GDP': "Infrastructure supports green revolution.",
            'CPI': "Sustainable components rise in price.",
            'Unemployment': "Green projects create jobs."
        },
        'VII': {
            'GDP': "Infrastructure strengthens cybersecurity.",
            'CPI': "Demand for cyber tech raises prices.",
            'Unemployment': "Cyber projects create jobs."
        },
        'VIII': {
            'GDP': "Post-disaster spending boosts GDP.",
            'CPI': "Reconstruction increases material demand.",
            'Unemployment': "Rebuilding creates jobs."
        },
        'IX': {
            'GDP': "Infrastructure aids space exploration.",
            'CPI': "Space tech demand raises prices.",
            'Unemployment': "Space projects create tech jobs."
        },
        'X': {
            'GDP': "Infrastructure aids AI, robotics.",
            'CPI': "AI component demand raises prices.",
            'Unemployment': "Infrastructure creates tech jobs."
        }
    },
    'B': {
        'I': {
            'GDP': "Tech boom, low rates attract investment.",
            'CPI': "Tech demand raises prices.",
            'Unemployment': "Tech industries boom."
        },
        'II': {
            'GDP': "Low oil, rates boost investment.",
            'CPI': "Low oil prices counter inflation.",
            'Unemployment': "Low oil costs preserve jobs."
        },
        'III': {
            'GDP': "Low rates boost domestic demand.",
            'CPI': "Recessionary pressures offset inflation.",
            'Unemployment': "Domestic demand maintains jobs."
        },
        'IV': {
            'GDP': "Pandemic deters investment.",
            'CPI': "Pandemic reduces spending.",
            'Unemployment': "Borrowing ease preserves jobs."
        },
        'V': {
            'GDP': "Trade war hinders exports; low rates stimulate domestic demand.",
            'CPI': "Trade wars raise import prices.",
            'Unemployment': "Domestic demand retains jobs despite export challenges."
        },
        'VI': {
            'GDP': "Low rates boost green tech investments.",
            'CPI': "Green tech borrowing raises product prices.",
            'Unemployment': "Green tech investments create jobs."
        },
        'VII': {
            'GDP': "Low rates boost cybersecurity investments.",
            'CPI': "Cyber tech borrowing raises prices.",
            'Unemployment': "Cybersecurity sector growth creates jobs."
        },
        'VIII': {
            'GDP': "Post-disaster low rates encourage rebuilding.",
            'CPI': "Reconstruction borrowing raises material prices.",
            'Unemployment': "Reconstruction boosts job creation."
        },
        'IX': {
            'GDP': "Low rates boost space exploration investments.",
            'CPI': "Space tech borrowing raises prices.",
            'Unemployment': "Space tech investments create jobs."
        },
        'X': {
            'GDP': "Low rates boost AI, robotics investments.",
            'CPI': "AI tech borrowing raises product prices.",
            'Unemployment': "AI and robotics sectors create jobs."
        }
    },
    'C': {
        'I': {
            'GDP': "Tech exports boost revenue.",
            'CPI': "Tech exports may raise domestic prices.",
            'Unemployment': "Global tech demand creates jobs."
        },
        'II': {
            'GDP': "Reduced oil costs aid exports.",
            'CPI': "Exports stabilize CPI.",
            'Unemployment': "Oil price drop may boost jobs."
        },
        'III': {
            'GDP': "Global recession dampens export benefits.",
            'CPI': "Oversupply from recession stabilizes prices.",
            'Unemployment': "Recession reduces export jobs."
        },
        'IV': {
            'GDP': "Supply disruptions hinder exports.",
            'CPI': "Export reduction stabilizes domestic prices.",
            'Unemployment': "Disruptions affect export jobs."
        },
        'V': {
            'GDP': "Trade barriers hinder exports.",
            'CPI': "Barriers cause domestic oversupply.",
            'Unemployment': "Trade barriers risk export jobs."
        },
        'VI': {
            'GDP': "Green product exports raise revenue.",
            'CPI': "Green exports might raise domestic prices.",
            'Unemployment': "Green exports create jobs."
        },
        'VII': {
            'GDP': "Exporting cybersecurity solutions boosts revenue.",
            'CPI': "Exporting solutions may raise domestic prices.",
            'Unemployment': "Cybersecurity exports create tech jobs."
        },
        'VIII': {
            'GDP': "Exports post-disasters boost revenue.",
            'CPI': "Exporting reconstruction materials raises domestic prices.",
            'Unemployment': "Post-disaster exports create construction jobs."
        },
        'IX': {
            'GDP': "Space tech exports boost revenue.",
            'CPI': "Exporting space tech may raise domestic prices.",
            'Unemployment': "Space tech exports create research jobs."
        },
        'X': {
            'GDP': "AI, robotics exports boost revenue.",
            'CPI': "Exporting AI, robotics raises domestic prices.",
            'Unemployment': "AI exports create tech jobs."
        }
    },
    'D': {
        'I': {
            'GDP': "High borrowing costs dampen tech investments.",
            'CPI': "Less tech demand stabilizes prices.",
            'Unemployment': "Tech investments stagnate."
        },
        'II': {
            'GDP': "High rates deter investment despite low oil.",
            'CPI': "Low oil prices counter inflation.",
            'Unemployment': "High rates risk jobs."
        },
        'III': {
            'GDP': "High rates amplify recession impacts.",
            'CPI': "Less borrowing risks deflation.",
            'Unemployment': "High rates increase layoffs."
        },
        'IV': {
            'GDP': "Pandemic and rates hinder growth.",
            'CPI': "Low borrowing offsets inflation.",
            'Unemployment': "Pandemic and rates risk jobs."
        },
        'V': {
            'GDP': "Trade war and rates hurt GDP.",
            'CPI': "Trade war raises import prices.",
            'Unemployment': "Rates and trade war risk jobs."
        },
        'VI': {
            'GDP': "Rates deter green tech investments.",
            'CPI': "Low green demand stabilizes prices.",
            'Unemployment': "Rates hinder green job growth."
        },
        'VII': {
            'GDP': "Rates deter cyber investments.",
            'CPI': "Low cyber demand stabilizes prices.",
            'Unemployment': "Cyber job growth stagnates."
        },
        'VIII': {
            'GDP': "High rates post-disasters slow recovery.",
            'CPI': "Less borrowing stabilizes reconstruction prices.",
            'Unemployment': "High rates deter post-disaster jobs."
        },
        'IX': {
            'GDP': "Rates deter space investments.",
            'CPI': "Low space demand stabilizes prices.",
            'Unemployment': "Space job growth stagnates."
        },
        'X': {
            'GDP': "Rates deter AI investments.",
            'CPI': "Low AI demand stabilizes prices.",
            'Unemployment': "AI job growth stagnates."
        }
    },
    'E': {
        'I': {
            'GDP': "Tax boosts tech during boom.",
            'CPI': "Increased goods availability stabilizes prices.",
            'Unemployment': "Tax boosts tech jobs."
        },
        'II': {
            'GDP': "Tax encourages business growth.",
            'CPI': "Tax boosts production, reducing CPI.",
            'Unemployment': "Tax savings boost jobs."
        },
        'III': {
            'GDP': "Tax offsets global recession.",
            'CPI': "Tax keeps prices competitive.",
            'Unemployment': "Tax helps retain jobs."
        },
        'IV': {
            'GDP': "Pandemic outweighs tax benefits.",
            'CPI': "Tax doesn't offset inflation from disruptions.",
            'Unemployment': "Pandemic risks jobs despite tax."
        },
        'V': {
            'GDP': "Tax boosts domestic production.",
            'CPI': "Tax offsets trade war inflation.",
            'Unemployment': "Tax aids job retention."
        },
        'VI': {
            'GDP': "Tax boosts green sectors.",
            'CPI': "Tax stabilizes green product prices.",
            'Unemployment': "Tax incentives boost green jobs."
        },
        'VII': {
            'GDP': "Tax stimulates cybersecurity growth.",
            'CPI': "Tax boosts cyber product supply.",
            'Unemployment': "Tax boosts cyber jobs."
        },
        'VIII': {
            'GDP': "Tax aids post-disaster growth.",
            'CPI': "Tax stabilizes reconstruction prices.",
            'Unemployment': "Tax aids post-disaster jobs."
        },
        'IX': {
            'GDP': "Tax aids space sector growth.",
            'CPI': "Tax boosts space tech supply.",
            'Unemployment': "Tax boosts space jobs."
        },
        'X': {
            'GDP': "Tax aids AI, robotics growth.",
            'CPI': "Tax boosts AI supply.",
            'Unemployment': "Tax boosts AI, robotics jobs."
        }
    },
    'F': {
        'I': {
            'GDP': "Welfare ensures funds for tech products, bolstering the tech industry.",
            'CPI': "Increased funds may push prices up slightly.",
            'Unemployment': "Welfare supports those affected by tech changes."
        },
        'II': {
            'GDP': "Welfare ensures steady consumption despite oil sector challenges.",
            'CPI': "Welfare stabilizes demand, offsetting deflationary oil price effects.",
            'Unemployment': "Welfare supports those affected in the oil sector."
        },
        'III': {
            'GDP': "Welfare supports domestic consumption amidst reduced global demand.",
            'CPI': "Welfare-driven demand can stabilize prices during a recession.",
            'Unemployment': "Welfare prevents higher unemployment in a recession."
        },
        'IV': {
            'GDP': "Welfare provides support during pandemic lockdowns.",
            'CPI': "Welfare maintains demand during a pandemic.",
            'Unemployment': "Welfare supports job losses in a pandemic."
        },
        'V': {
            'GDP': "Welfare ensures steady consumption despite trade wars.",
            'CPI': "Welfare helps stabilize prices during trade wars.",
            'Unemployment': "Welfare supports those affected by trade wars."
        },
        'VI': {
            'GDP': "Welfare supports those during the green technology transition.",
            'CPI': "Welfare stabilizes green product prices.",
            'Unemployment': "Welfare acts as a net during the green revolution."
        },
        'VII': {
            'GDP': "Welfare supports those affected by cybersecurity threats.",
            'CPI': "Welfare stabilizes demand amidst cybersecurity threats.",
            'Unemployment': "Welfare supports jobs amidst cybersecurity breaches."
        },
        'VIII': {
            'GDP': "Welfare supports post-disaster recovery.",
            'CPI': "Welfare stabilizes post-disaster demand.",
            'Unemployment': "Welfare supports post-disaster job losses."
        },
        'IX': {
            'GDP': "Welfare supports those during space industry transition.",
            'CPI': "Welfare stabilizes space product prices.",
            'Unemployment': "Welfare acts as a net in space industry shifts."
        },
        'X': {
            'GDP': "Welfare supports those affected by AI and robotics.",
            'CPI': "Welfare stabilizes AI product prices.",
            'Unemployment': "Welfare supports jobs amidst AI transitions."
        }
    },
'G': {
        'I': {
            'GDP': "Less infrastructure spending dampens tech boom benefits.",
            'CPI': "Reduced spending might ease inflationary pressures.",
            'Unemployment': "Less spending misses job opportunities in tech."
        },
        'II': {
            'GDP': "Less infrastructure spending reduces oil price crash benefits.",
            'CPI': "Reduced spending stabilizes demand.",
            'Unemployment': "Less spending leads to potential job losses."
        },
        'III': {
            'GDP': "Reduced spending during a recession amplifies GDP decline.",
            'CPI': "Less projects stabilize construction material prices.",
            'Unemployment': "Less spending increases construction unemployment."
        },
        'IV': {
            'GDP': "Less spending during a pandemic hinders GDP.",
            'CPI': "Pandemic and less projects lead to price instability.",
            'Unemployment': "Reduced spending during a pandemic increases job losses."
        },
        'V': {
            'GDP': "Decreased spending during trade wars hits GDP.",
            'CPI': "Trade wars and reduced spending balance prices.",
            'Unemployment': "Less spending during trade wars increases job losses."
        },
        'VI': {
            'GDP': "Decreased spending hinders green technology transition.",
            'CPI': "Less spending stabilizes green tech prices.",
            'Unemployment': "Reduced green projects lead to job losses."
        },
        'VII': {
            'GDP': "Reduced spending makes economy vulnerable to cyber threats.",
            'CPI': "Reduced spending doesn't impact CPI amidst cyber threats.",
            'Unemployment': "Outdated infrastructure and cyber breaches cause job losses."
        },
        'VIII': {
            'GDP': "Decreased post-disaster spending hinders recovery.",
            'CPI': "Reduced reconstruction efforts stabilize prices.",
            'Unemployment': "Reduced post-disaster spending reduces jobs."
        },
        'IX': {
            'GDP': "Reduced spending hinders space industry growth.",
            'CPI': "Less space-related spending stabilizes prices.",
            'Unemployment': "Reduced space projects lead to job losses."
        },
        'X': {
            'GDP': "Decreased spending hinders AI, robotics growth.",
            'CPI': "Less AI-related spending stabilizes prices.",
            'Unemployment': "Reduced AI projects lead to job losses."
        }
    },

    'H': {
        'I': {
            'GDP': "During a tech boom, limiting exports curbs global demand benefits.",
            'CPI': "Export restrictions may reduce tech product prices.",
            'Unemployment': "Untapped global tech demand can limit job opportunities."
        },
        'II': {
            'GDP': "In an oil price crash, export limits reduce revenue potential.",
            'CPI': "Export reductions can lead to domestic price drops.",
            'Unemployment': "Export limits can increase sectoral layoffs."
        },
        'III': {
            'GDP': "During a recession, export limits deepen GDP impact.",
            'CPI': "Export limits can induce deflationary pressures.",
            'Unemployment': "Reduced exports amplify export sector job losses."
        },
        'IV': {
            'GDP': "In a pandemic, limiting exports exacerbates GDP drops.",
            'CPI': "Export restrictions could stabilize prices.",
            'Unemployment': "Export limits during a pandemic heighten job losses."
        },
        'V': {
            'GDP': "Trade wars and additional export limits contract GDP.",
            'CPI': "Export limits in trade wars might decrease prices.",
            'Unemployment': "Trade wars and export restrictions amplify job losses."
        },
        'VI': {
            'GDP': "During a green revolution, export limits curtail global market access.",
            'CPI': "Green product export restrictions may decrease prices.",
            'Unemployment': "Green sector faces job risks due to export limits."
        },
        'VII': {
            'GDP': "Export limits can reduce cybersecurity market opportunities.",
            'CPI': "Export restrictions may decrease cybersecurity product prices.",
            'Unemployment': "Reduced export opportunities can impact job growth."
        },
        'VIII': {
            'GDP': "Post-disasters, export limits hinder recovery opportunities.",
            'CPI': "Export limits can reduce prices post disasters.",
            'Unemployment': "Export restrictions post disasters risk job losses."
        },
        'IX': {
            'GDP': "Limiting space exports curtails global market growth.",
            'CPI': "Export limits may reduce space tech prices.",
            'Unemployment': "Space sector can face job risks from export limits."
        },
        'X': {
            'GDP': "Limiting AI exports curbs global market benefits.",
            'CPI': "AI export restrictions may reduce prices.",
            'Unemployment': "AI sector faces job risks due to export limits."
        }
    },

    'J': {
        'I': {
            'GDP': "Tax hikes during tech boom deter tech advancements.",
            'CPI': "Higher taxes can increase tech product prices.",
            'Unemployment': "Tax hikes during tech boom curtail job growth."
        },
        'II': {
            'GDP': "Tax hikes in an oil crash deepen GDP impacts.",
            'CPI': "Higher taxes and oil price crash unsettle prices.",
            'Unemployment': "Tax increases during oil crash risk more layoffs."
        },
        'III': {
            'GDP': "In a recession, tax hikes amplify GDP drops.",
            'CPI': "Higher taxes in a recession risk inflation.",
            'Unemployment': "Tax increases during recession amplify layoffs."
        },
        'IV': {
            'GDP': "During a pandemic, tax hikes restrain investments.",
            'CPI': "Tax hikes during a pandemic can inflate prices.",
            'Unemployment': "Increased taxes in a pandemic deepen job losses."
        },
        'V': {
            'GDP': "In trade wars, tax hikes further deter investments.",
            'CPI': "Trade wars and tax hikes inflate prices.",
            'Unemployment': "Tax hikes in trade wars amplify job losses."
        },
        'VI': {
            'GDP': "Tax hikes during green revolution deter green tech investments.",
            'CPI': "Higher taxes can raise green product prices.",
            'Unemployment': "Tax hikes during green revolution limit job growth."
        },
        'VII': {
            'GDP': "Tax hikes can deter cybersecurity investments.",
            'CPI': "Higher taxes can raise cybersecurity solution prices.",
            'Unemployment': "Increased taxes hinder job growth in cybersecurity."
        },
        'VIII': {
            'GDP': "Post-disaster tax hikes hinder recovery investments.",
            'CPI': "Higher taxes post disasters can inflate prices.",
            'Unemployment': "Tax hikes post disasters restrain job growth."
        },
        'IX': {
            'GDP': "Tax hikes hinder space industry investments.",
            'CPI': "Higher taxes can raise space tech prices.",
            'Unemployment': "Tax hikes limit job growth in space sector."
        },
        'X': {
            'GDP': "In AI surge, tax hikes deter advancements.",
            'CPI': "Higher taxes can increase AI tech prices.",
            'Unemployment': "Tax hikes during AI surge curtail job growth."
        }
    },

    'K': {
        'I': {
            'GDP': "Welfare cuts during tech boom slow GDP growth.",
            'CPI': "Welfare cuts stabilize tech product prices.",
            'Unemployment': "Tech boom welfare cuts risk financial stability."
        },
        'II': {
            'GDP': "In an oil crash, welfare cuts deepen GDP impacts.",
            'CPI': "Welfare cuts and oil crash induce deflation.",
            'Unemployment': "Welfare cuts during oil crash amplify financial risks."
        },
        'III': {
            'GDP': "During a recession, welfare cuts deepen GDP impacts.",
            'CPI': "Welfare cuts in a recession amplify deflation.",
            'Unemployment': "Recession welfare cuts amplify financial risks."
        },
        'IV': {
            'GDP': "In a pandemic, welfare cuts deepen GDP drops.",
            'CPI': "Welfare cuts during a pandemic stabilize prices.",
            'Unemployment': "Pandemic welfare cuts deepen financial risks."
        },
        'V': {
            'GDP': "Trade war welfare cuts impact domestic consumption.",
            'CPI': "Trade wars and welfare cuts may stabilize prices.",
            'Unemployment': "Welfare cuts during trade wars increase financial risks."
        },
        'VI': {
            'GDP': "During a green revolution, welfare cuts curtail consumption.",
            'CPI': "Welfare cuts stabilize green product prices.",
            'Unemployment': "Green revolution welfare cuts risk financial stability."
        },
        'VII': {
            'GDP': "Welfare cuts risk household stability during cybersecurity threats.",
            'CPI': "Welfare cuts stabilize prices during cybersecurity threats.",
            'Unemployment': "Cybersecurity threats and welfare cuts risk job losses."
        },
        'VIII': {
            'GDP': "Post-disaster welfare cuts hinder recovery consumption.",
            'CPI': "Welfare cuts post disasters may stabilize prices.",
            'Unemployment': "Post-disaster welfare cuts increase financial risks."
        },
        'IX': {
            'GDP': "Space industry welfare cuts curtail consumption.",
            'CPI': "Welfare cuts stabilize space tech prices.",
            'Unemployment': "Space industry welfare cuts risk financial stability."
        },
        'X': {
            'GDP': "In AI surge, welfare cuts curtail consumption.",
            'CPI': "Welfare cuts stabilize AI tech prices.",
            'Unemployment': "AI surge welfare cuts risk financial stability."
        },
    },
    'L': {  # No Policy
    'I': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'II': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'III': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'IV': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'V': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'VI': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'VII': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'VIII': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'IX': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
    'X': {
        'GDP': "GDP is driven by global events.",
        'CPI': "CPI is affected by global events.",
        'Unemployment': "Unemployment is influenced by global events."
    },
},

}


# Keep track of previously chosen events
previous_events = set()

def generate_random_event(previous_event=None):
    all_events = list(EVENT_EFFECTS.keys())

    # If there's a previous event, remove it from the list of choices
    if previous_event:
        all_events.remove(previous_event)

    # Remove events that have been chosen previously
    available_events = [event for event in all_events if event not in previous_events]

    if not available_events:
        # If all events have been chosen, reset the set of previous events
        previous_events.clear()
        available_events = all_events

    # Choose a random event from the available options
    chosen_event = random.choice(available_events)

    # Add the chosen event to the set of previous events
    previous_events.add(chosen_event)

    return chosen_event

def apply_policy_and_event_effects(game_data, policy_choice, random_event, country_type):
    print("Function apply_policy_and_event_effects is being called with random_event:", random_event)

    # Separate event effects for reporting
    event_effect = {
        'gdp_growth': random.uniform(*EVENT_EFFECTS[random_event]['gdp_growth']),
        'cpi': random.uniform(*EVENT_EFFECTS[random_event]['CPI']),
        'unemployment': random.uniform(*EVENT_EFFECTS[random_event]['Unemployment'])
    }

    if policy_choice == 'L':  # No Policy
        gdp_effect = event_effect['gdp_growth']
        cpi_effect = event_effect['cpi']
        unemployment_effect = event_effect['unemployment']
        gdp_interaction = 1
        cpi_interaction = 1
        unemployment_interaction = 1
    else:
        # Base effects based on the policy and the event alone
        gdp_effect = (random.uniform(*POLICY_EFFECTS[policy_choice]['gdp_growth']) + event_effect['gdp_growth']) / 2
        cpi_effect = (random.uniform(*POLICY_EFFECTS[policy_choice]['CPI']) + event_effect['cpi']) / 2
        unemployment_effect = (random.uniform(*POLICY_EFFECTS[policy_choice]['Unemployment']) + event_effect[
            'unemployment']) / 2
        # Adjustments based on policy and event combinations
        gdp_interaction = random.uniform(*gdp_interaction_matrix.get((policy_choice, random_event), (1, 1)))
        cpi_interaction = random.uniform(*cpi_interaction_matrix.get((policy_choice, random_event), (1, 1)))
        unemployment_interaction = random.uniform(
            *unemployment_interaction_matrix.get((policy_choice, random_event), (1, 1)))

    # Fetch the multipliers from the COUNTRY_MULTIPLIERS dictionary
    gdp_multiplier = random.uniform(*COUNTRY_MULTIPLIERS[country_type]) if isinstance(COUNTRY_MULTIPLIERS[country_type], tuple) else COUNTRY_MULTIPLIERS[country_type]
    cpi_multiplier = random.uniform(*COUNTRY_MULTIPLIERS[country_type]) if isinstance(COUNTRY_MULTIPLIERS[country_type], tuple) else COUNTRY_MULTIPLIERS[country_type]
    unemployment_multiplier = random.uniform(*COUNTRY_MULTIPLIERS[country_type]) if isinstance(COUNTRY_MULTIPLIERS[country_type], tuple) else COUNTRY_MULTIPLIERS[country_type]

    # Apply the combined effects
    game_data['gdp_growth'] += gdp_effect * gdp_interaction * gdp_multiplier
    game_data['cpi'] += cpi_effect * cpi_interaction * cpi_multiplier
    game_data['unemployment'] += unemployment_effect * unemployment_interaction * unemployment_multiplier

    return event_effect



def calculate_score(game_data):
    gdp_score = game_data.get('gdp_growth', 0)  # Reward GDP growth directly, default to 0 if not present

    # Calculate the difference from the target for CPI and Unemployment
    cpi_difference = game_data.get('cpi', 2) - 2
    unemployment_difference = game_data.get('unemployment', 4) - 4

    # Apply a larger penalty for values above the target
    cpi_penalty = 2 * cpi_difference if cpi_difference > 0 else cpi_difference
    unemployment_penalty = 2 * unemployment_difference if unemployment_difference > 0 else unemployment_difference

    # Calculate bonus points based on CPI and Unemployment differences
    cpi_bonus = 0
    unemployment_bonus = 0

    # Check if CPI difference is within 0.5 in absolute value
    if abs(cpi_difference) < 0.5:
        cpi_bonus = 1

        # Check if CPI difference is within 0.1 in absolute value
        if abs(cpi_difference) < 0.1:
            cpi_bonus = 3

    # Check if Unemployment difference is within 0.5 in absolute value
    if abs(unemployment_difference) < 0.5:
        unemployment_bonus = 1

        # Check if Unemployment difference is within 0.1 in absolute value
        if abs(unemployment_difference) < 0.1:
            unemployment_bonus = 3

    # Calculate the final score with bonus points
    score = gdp_score - abs(cpi_penalty) - abs(unemployment_penalty) + cpi_bonus + unemployment_bonus
    return score


@macro1.route('/home', methods=['GET'])
def home():
    session['current_round'] = 1
    # Fetch all data from Firestore
    all_docs = client.collection('macro_leaderboard1').stream()

    # Convert the data to a list of dictionaries
    all_data = [{"id": doc.id, **doc.to_dict()} for doc in all_docs]

    leaderboard_by_class = {}
    for entry in all_data:
        class_number = entry['class_number']
        if class_number not in leaderboard_by_class:
            leaderboard_by_class[class_number] = []
        leaderboard_by_class[class_number].append(entry)

    # Order each class's scores
    for class_number, entries in leaderboard_by_class.items():
        entries.sort(key=itemgetter('score'), reverse=True)
        leaderboard_by_class[class_number] = entries[:5]

    return render_template('macro1home.html', leaderboard_by_class=leaderboard_by_class)

@macro1.route('/macro_1_start_game', methods=['GET', 'POST'])
def start_game():
    if 'student_id' in session:
        session.pop('student_id')  # Clear student_id from the session.
    if 'class_number' in session:
        session.pop('class_number')  # Clear class_number from the session.

    if request.method == 'POST':
        country_type = request.form.get('country_type')  # Get the country type selected by the user.
        student_id = session.get('student_id')  # Assuming you've stored student_id in the session.
        class_number = session.get('class_number')  # Assuming you've stored class_number in the session.

        game_data = {
            'student_id': student_id,
            'class_number': class_number,
            'country_type': country_type,
            'current_quarter': 1,
            'cpi': 2,
            'unemployment': 4,
            'score': 0,
            'gdp_growth': 0,
            'game_history': []
        }

        # Assign the 'gdp_score' key after initializing the dictionary.
        game_data['gdp_score'] = game_data.get('gdp_growth', 0)

        _, game_ref = client.collection('macro_leaderboard1').add(game_data)

        # Store the game_data in the session
        session['game_data'] = game_data

        # Redirect to the show_event route to begin the game
        return redirect(url_for('macro1.show_event'))

    return render_template('macro1_start_game.html')

@macro1.route('/show_event', methods=['GET', 'POST'])
def show_event():
    game_data = session.get('game_data')


    # Generate a random event.
    random_event_key = generate_random_event()
    game_data['random_event'] = random_event_key  # Store the event key, not the whole event.

    # Extract event effects for current random event
    event_effects = EVENT_EFFECTS[game_data['random_event']]

    # Generate round report, similar to what was done in play_game
    policy_choice = game_data.get('policy_choice', None)

    # Print game_data and last_round for debugging
    print("game_data in show_event:", game_data)
    last_round = game_data['game_history'][-1] if game_data['game_history'] else None
    print("last_round in show_event:", last_round)

    # Calculate changes if last round exists
    changes = {
            'gdp_growth': game_data['gdp_growth'] - (last_round['final_values']['gdp_growth'] if last_round else 0),
        'cpi': (game_data['cpi'] - last_round['final_values']['cpi']) if last_round else 0,
        'unemployment': (game_data['unemployment'] - last_round['final_values']['unemployment']) if last_round else 0
    }

    round_report = {
        'quarter': game_data['current_quarter'],
        'policy_choice': policy_choice,
        'random_event': random_event_key,
        'initial_values': {
            'gdp_growth': game_data['gdp_growth'],
            'cpi': game_data['cpi'],
            'unemployment': game_data['unemployment']
        },
        'changes': changes
    }
    print("changes in show_event:", changes)
    print("round_report in show_event:", round_report)
    session['game_data'] = game_data

    # Show the event's effects to the user in a template.
    return render_template('macro1_show_event.html', game_data=game_data, EVENT_NAMES=EVENT_NAMES,
                           POLICY_NAMES=POLICY_NAMES,
                           EVENT_EFFECTS=EVENT_EFFECTS, round_report=round_report, event_effects=event_effects,
                           EVENT_NARRATIVES=EVENT_NARRATIVES)

@macro1.route('/choose_policy', methods=['GET', 'POST'])
def choose_policy():
    if 'current_round' not in session:
        session['current_round'] = 1
    else:
        session['current_round'] += 1
    # Check game state
    game_data = session.get('game_data')
    round_report = None
    event_effect = None

    # Initialize changes_after_effects here
    changes_after_effects = {
        'gdp_growth': 0,
        'cpi': 2,
        'unemployment': 4
    }

    # Extract event effects for current random event
    event_effects = EVENT_EFFECTS[game_data['random_event']]

    # Determine bar color based on impact range
    gdp_growth_color = 'green' if event_effects['gdp_growth'][1] >= 0 else 'red'
    cpi_min, cpi_max = min(event_effects['CPI']), max(event_effects['CPI'])
    cpi_color = 'yellow' if -1 <= cpi_min <= 1 and -1 <= cpi_max <= 1 else 'red'
    unemployment_min, unemployment_max = min(event_effects['Unemployment']), max(event_effects['Unemployment'])
    unemployment_color = 'yellow' if -1 <= unemployment_min <= 1 and -1 <= unemployment_max <= 1 else 'red'

    last_round = game_data['game_history'][-1] if game_data['game_history'] else None

    if request.method == 'POST':
        policy_choice = request.form.get('policy_choice')
        print(f"Chosen policy: {policy_choice}")
        game_data['policy_choice'] = policy_choice

        event_effect = apply_policy_and_event_effects(game_data, policy_choice, game_data['random_event'], game_data['country_type'])


        # Update changes_after_effects directly within the POST block
        if game_data['current_quarter'] == 1:
            # For the first round, just take the event and policy effects
            changes_after_effects['gdp_growth'] = game_data['gdp_growth']
            changes_after_effects['cpi'] = game_data['cpi'] - 2  # Starting value for CPI is 2%
            changes_after_effects['unemployment'] = game_data[
                                                        'unemployment'] - 4  # Starting value for Unemployment is 4%
        else:
            changes_after_effects['gdp_growth'] = game_data['gdp_growth'] - (
                last_round['final_values']['gdp_growth'] if last_round else 0)
            changes_after_effects['cpi'] = game_data['cpi'] - (last_round['final_values']['cpi'] if last_round else 0)
            changes_after_effects['unemployment'] = game_data['unemployment'] - (
                last_round['final_values']['unemployment'] if last_round else 0)

        game_data['score'] = calculate_score(game_data)

        round_report = {
            'quarter': game_data['current_quarter'],
            'policy_choice': policy_choice,
            'random_event': game_data['random_event'],
            'event_effect': event_effect,
            'final_values': {
                'gdp_growth': game_data['gdp_growth'],
                'cpi': game_data['cpi'],
                'unemployment': game_data['unemployment']
            },
            'changes_after_effects': changes_after_effects,  # Add this line
            'score': game_data['score']
        }

        game_data['game_history'].append(round_report)
        game_data['current_quarter'] += 1
        next_event = generate_random_event(game_data['random_event'])
        game_data['random_event'] = next_event

        session['game_data'] = game_data


        if game_data['current_quarter'] > 4:
            return redirect(url_for('macro1.game_results'))

    return render_template('macro1_choose_policy.html',
                           game_data=game_data,
                           POLICY_NAMES=POLICY_NAMES,
                           EVENT_NAMES=EVENT_NAMES,
                           EVENT_EFFECTS=EVENT_EFFECTS,
                           round_report=round_report,
                           cpi_color=cpi_color,
                           unemployment_color=unemployment_color,
                           gdp_growth_color=gdp_growth_color,
                           event_effects=EVENT_EFFECTS[game_data['random_event']],
                           cpi_min=cpi_min,
                           cpi_max=cpi_max,
                           unemployment_min=unemployment_min,
                           unemployment_max=unemployment_max, event_effect=event_effect, last_round=last_round,
                           interactions=json.dumps(INTERACTIONS),
                           total_round_change=changes_after_effects,
                           EVENT_ABBREVIATIONS=EVENT_ABBREVIATIONS, POLICY_ABBREVIATIONS=POLICY_ABBREVIATIONS)  # Change this line

@macro1.route('/game_results', methods=['GET'])
def game_results():
    game_data = session.get('game_data', {})
    print("Game Data in game_results:", game_data)  # Debugging line

    # Get the student's score from the game data
    score = game_data.get('score', 0)
    student_id = session.get('student_id')
    username = session.get('username')
    class_number = session.get('class')

    # Update the leaderboard with the student's score
    update_leaderboard(student_id, class_number, username, score)

    # Fetch the leaderboard to display to the student
    leaderboard = get_leaderboard(class_number)


    return render_template('macro1_game_results.html',
                           game_data=game_data,
                           leaderboard=leaderboard,
                           POLICY_NAMES=POLICY_NAMES,
                           EVENT_NAMES=EVENT_NAMES, EVENT_ABBREVIATIONS=EVENT_ABBREVIATIONS,POLICY_ABBREVIATIONS=POLICY_ABBREVIATIONS)

@macro1.route('/leaderboard', methods=['GET'])
def leaderboard():
    # Get the class_number from the session
    class_number = session.get('class')

    # If there's no class_number in the session, you might want to handle this case differently.
    # For now, let's assume we return an empty leaderboard.
    if not class_number:
        return render_template('macro1_leaderboard.html', leaderboard=[])

    # Use the get_leaderboard function to fetch class-specific scores
    leaderboard_data = get_leaderboard(class_number)

    return render_template('macro1_leaderboard.html', leaderboard=leaderboard_data)


@macro1.route('/instructions')
def instructions():
    current_username = session.get('username')
    return render_template('macro1_instructions.html', current_username=current_username)

def update_leaderboard(student_id, class_number, username, score):
    # Fetch the student's current leaderboard entry
    doc_ref = client.collection('macro_leaderboard1').document(student_id)
    doc = doc_ref.get()

    # If the student has an entry and the new score is higher, or if the student has no entry, update/add the entry
    if not doc.exists or (doc.exists and doc.to_dict().get('score', 0) < score):
        doc_ref.set({
            'student_id': student_id,
            'class_number': class_number,
            'username': username,
            'score': score
        }, merge=True)


def get_leaderboard(class_number):
    # Fetch all scores from Firestore
    all_scores = client.collection('macro_leaderboard1').stream()

    # Convert the data to a list of dictionaries
    all_data = [{'id': doc.id, **doc.to_dict()} for doc in all_scores]

    # Filter by class_number
    filtered_data = [entry for entry in all_data if entry['class_number'] == class_number]

    # Group by usernames and take the maximum score for each user
    user_max_scores = {}
    for entry in filtered_data:
        username = entry['username']
        if username not in user_max_scores or entry['score'] > user_max_scores[username]['score']:
            user_max_scores[username] = entry

    leaderboard_data = sorted(user_max_scores.values(), key=lambda x: x['score'], reverse=True)[:10]

    return leaderboard_data

