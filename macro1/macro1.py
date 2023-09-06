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
        'GDP': "Infrastructure spending supercharges the tech-induced GDP growth by catalyzing tech infrastructure projects.",
        'CPI': "A heightened demand from tech and construction can lead to a mild CPI increase.",
        'Unemployment': "A surge in construction jobs reduces unemployment."
    },
    'II': {
        'GDP': "The downturn in GDP from the oil sector is alleviated by the stimulus from infrastructure projects.",
        'CPI': "CPI experiences a slight uptick due to increased activity in construction.",
        'Unemployment': "Construction jobs counterbalance oil sector job losses."
    },
    'III': {
        'GDP': "Infrastructure spending acts as a counter-cyclical buffer, reducing the severity of GDP decline.",
        'CPI': "CPI remains relatively stable due to countervailing forces of recession and spending.",
        'Unemployment': "The recession's unemployment rise is mitigated by government-induced construction jobs."
    },
    'IV': {
        'GDP': "Infrastructure spending provides some relief to GDP, although full benefits might be delayed due to pandemic-related disruptions.",
        'CPI': "CPI remains relatively stable, balancing pandemic-induced deflationary pressures against inflation from government spending.",
        'Unemployment': "Potential job creation is offset by pandemic restrictions, leading to a marginal impact."
    },
    'V': {
        'GDP': "Infrastructure spending bolsters domestic production, helping offset GDP losses from reduced trade.",
        'CPI': "CPI increases due to reduced imports and higher domestic demand.",
        'Unemployment': "Infrastructure projects create jobs, offsetting losses from reduced exports."
    },
    'VI': {
        'GDP': "GDP gets a boost from the construction of green infrastructure projects.",
        'CPI': "CPI might see a moderate increase due to demand for green technologies and materials.",
        'Unemployment': "Green projects create new jobs, reducing unemployment."
    },
    'VII': {
        'GDP': "Infrastructure spending unrelated to cybersecurity might not significantly impact GDP affected by breaches.",
        'CPI': "CPI remains stable, with infrastructure spending having minimal direct effects on prices amidst cybersecurity concerns.",
        'Unemployment': "New construction jobs might be offset by job losses in sectors impacted by breaches."
    },
    'VIII': {
        'GDP': "Infrastructure rebuilding projects following disasters boost GDP.",
        'CPI': "CPI rises due to demand for rebuilding resources and potential supply chain disruptions.",
        'Unemployment': "Rebuilding efforts create jobs, decreasing unemployment."
    },
    'IX': {
        'GDP': "Infrastructure spending, especially on space-related projects, further amplifies GDP growth.",
        'CPI': "CPI sees a mild increase due to heightened demand from combined space and construction activities.",
        'Unemployment': "Space-related infrastructure projects generate jobs, reducing unemployment."
    },
    'X': {
        'GDP': "Infrastructure projects, especially those integrating AI and robotics, boost GDP.",
        'CPI': "Increased demand for advanced materials and tech can lead to a moderate CPI rise.",
        'Unemployment': "While construction jobs increase, the integration of AI might limit the net job growth."
    }
},
    'B': {
        'I': {
            'GDP': "Easier borrowing stimulates tech investments, amplifying GDP growth.",
            'CPI': "Increased demand from borrowing can cause a moderate CPI increase.",
            'Unemployment': "Investment-led growth provides more job opportunities, decreasing unemployment."
        },
        'II': {
            'GDP': "Lower interest rates encourage non-oil sectors to borrow and invest, providing a buffer to GDP.",
            'CPI': "Increased borrowing might push up prices slightly, causing a CPI rise.",
            'Unemployment': "Investment in non-oil sectors could mitigate job losses from the oil crash."
        },
        'III': {
        'GDP': "Reduced interest rates can act as a buffer, promoting borrowing and investment, thus alleviating the recession's impact on GDP.",
        'CPI': "A potential increase in borrowing may offset deflationary pressures, leading to a stabilized CPI.",
        'Unemployment': "Increased business activity due to borrowing can mitigate the rise in unemployment during a recession."
    },
    'IV': {
        'GDP': "Lower interest rates might boost borrowing and spending, but the full effect on GDP may be hindered by health concerns.",
        'CPI': "While borrowing can exert upward pressure on CPI, pandemic-induced reduced consumer spending can balance it out.",
        'Unemployment': "Potential borrowing-induced job growth is offset by job losses from pandemic restrictions."
    },
    'V': {
        'GDP': "Reduced interest rates encourage domestic borrowing and investment, potentially offsetting some GDP losses from reduced trade.",
        'CPI': "Potential inflationary effects from borrowing can be offset by deflationary pressures from reduced trade.",
        'Unemployment': "Increased domestic investments may offset some job losses from trade disruptions."
    },
    'VI': {
        'GDP': "Lower interest rates might stimulate borrowing for green initiatives, supporting GDP growth.",
        'CPI': "Increased green projects can lead to a moderate rise in CPI due to demand.",
        'Unemployment': "Green projects funded through easier borrowing can create jobs."
    },
    'VII': {
        'GDP': "Lower interest rates could encourage borrowing and investment, helping mitigate GDP losses from cybersecurity disruptions.",
        'CPI': "Increased economic activity from borrowing might exert mild upward pressure on CPI.",
        'Unemployment': "Any potential job growth from borrowing might be offset by job losses in affected industries."
    },
    'VIII': {
        'GDP': "Reduced interest rates can stimulate disaster recovery investments, supporting GDP.",
        'CPI': "Increased demand for rebuilding can exert upward pressure on CPI.",
        'Unemployment': "Rebuilding and recovery efforts funded through borrowing can generate jobs."
    },
    'IX': {
        'GDP': "Lower interest rates could further stimulate investments in space-related ventures, enhancing GDP growth.",
        'CPI': "Increased economic activity in the space sector might lead to a mild CPI rise.",
        'Unemployment': "Space-related ventures and projects can create new employment opportunities."
    },
    'X': {
        'GDP': "Easier borrowing can accelerate investments in AI and robotics, enhancing GDP growth.",
        'CPI': "Increased demand for tech-driven solutions can lead to a moderate CPI rise.",
        'Unemployment': "While AI and robotics might replace some jobs, new opportunities in R&D and tech sectors can emerge."
    }
    },
    'C': {
        'I': {
        'GDP': "Promotion of exports during a tech boom amplifies GDP growth by accessing larger, global markets for new technologies.",
        'CPI': "Increased demand for exported tech goods can cause a slight rise in CPI.",
        'Unemployment': "Growing export sectors, especially in tech, generate more jobs, decreasing unemployment."
    },
    'II': {
        'GDP': "Promoting exports aids GDP by diversifying revenue sources, especially in non-oil sectors.",
        'CPI': "Increased demand for exported goods can cause a slight rise in CPI.",
        'Unemployment': "Growing export sectors can counteract job losses in the oil industry."
    },
    'III': {
        'GDP': "Promotion of exports can act as a buffer, potentially securing foreign revenue to counterbalance the domestic recession's impact on GDP.",
        'CPI': "Increased export activity might exert upward pressure on CPI due to export demand.",
        'Unemployment': "Increased export activities can create jobs, helping to alleviate recession-induced unemployment."
    },
    'IV': {
        'GDP': "While promoting exports can boost GDP, global health restrictions might hinder trade.",
        'CPI': "Reduced global demand due to the pandemic might counteract any potential CPI rise from increased export activity.",
        'Unemployment': "Potential job growth in export sectors might be balanced out by pandemic-induced global trade disruptions."
    },
    'V': {
        'GDP': "Promoting exports during a trade war can be challenging, and might not significantly benefit GDP.",
        'CPI': "Trade restrictions and tariffs might exert upward pressure on CPI.",
        'Unemployment': "A trade war environment can neutralize potential job growth from export promotion."
    },
    'VI': {
        'GDP': "Promoting exports of green technologies can significantly boost GDP in the face of global green demand.",
        'CPI': "Increased export activity in green sectors might lead to a slight rise in CPI.",
        'Unemployment': "Green tech exports generate jobs, decreasing unemployment."
    },
    'VII': {
        'GDP': "Promotion of exports might be hampered by concerns over cybersecurity, leading to cautious GDP growth.",
        'CPI': "Cybersecurity concerns might exert a neutral effect on CPI, regardless of export promotions.",
        'Unemployment': "Cyber breaches could deter potential job growth in the export sector."
    },
    'VIII': {
        'GDP': "Natural disasters might disrupt export capabilities, limiting the positive effect on GDP.",
        'CPI': "Supply chain disruptions due to disasters can lead to a rise in CPI.",
        'Unemployment': "While export promotion can create jobs, natural disasters might disrupt these sectors, leading to potential job losses."
    },
    'IX': {
        'GDP': "Exporting space-related goods and technologies can significantly enhance GDP growth.",
        'CPI': "Space tech exports could cause a moderate rise in CPI due to their high value.",
        'Unemployment': "Space tech export sectors create specialized jobs, reducing unemployment."
    },
    'X': {
        'GDP': "Exporting AI and robotics technologies boosts GDP by tapping into global demand for automation.",
        'CPI': "AI and robotics exports might lead to a moderate rise in CPI due to the high value of these technologies.",
        'Unemployment': "While AI and robotics exports create jobs, widespread automation might reduce employment in other sectors."
    }
    },

    'D': {
        'I': {
        'GDP': "Raising interest rates might temper the tech-driven GDP growth by making borrowing costlier for tech ventures.",
        'CPI': "Higher rates can lead to decreased spending and a potential drop in CPI.",
        'Unemployment': "Increased borrowing costs might lead to slower business expansion, leading to a stable or slightly increased unemployment."
    },
    'II': {
        'GDP': "Higher interest rates could exacerbate the GDP decline caused by the oil price crash, by reducing borrowing and investment.",
        'CPI': "Reduced spending and borrowing due to higher rates can lead to a further drop in CPI amidst the oil crash.",
        'Unemployment': "The combined effect of oil sector downturn and reduced borrowing might increase unemployment."
    },
    'III': {
        'GDP': "Raising interest rates during a recession might further dampen GDP by discouraging borrowing and spending.",
        'CPI': "Higher rates can lead to deflationary pressures, further decreasing CPI in a recessionary environment.",
        'Unemployment': "Decreased economic activity due to high rates can exacerbate the recession's unemployment."
    },
    'IV': {
        'GDP': "Increasing interest rates during a pandemic might exacerbate the downturn, as both consumer and business spending are discouraged.",
        'CPI': "Less borrowing and spending due to higher rates might exert a downward pressure on CPI.",
        'Unemployment': "Increased borrowing costs combined with pandemic-induced business closures might amplify unemployment."
    },
    'V': {
        'GDP': "Raising interest rates during a trade war might intensify the GDP decline, discouraging both domestic and international investment.",
        'CPI': "Less borrowing and spending due to higher rates might combine with trade disruptions to push CPI downwards.",
        'Unemployment': "Increased borrowing costs and trade disruptions can jointly exacerbate unemployment."
    },
    'VI': {
        'GDP': "Higher interest rates could slow down green initiatives by making borrowing more expensive, potentially stunting GDP growth from this sector.",
        'CPI': "Reduced borrowing due to higher rates might put a damper on CPI growth despite increased green projects.",
        'Unemployment': "Potential job growth from green projects could be balanced out by reduced borrowing and investments."
    },
    'VII': {
        'GDP': "Raising interest rates amidst cybersecurity concerns could deter investments, hindering GDP recovery.",
        'CPI': "Higher interest rates might exert a downward pressure on CPI, in addition to concerns over cyber breaches.",
        'Unemployment': "The combined effect of increased borrowing costs and cyber concerns might suppress job growth."
    },
    'VIII': {
        'GDP': "Higher interest rates can make recovery more expensive post-disasters, potentially hindering GDP recovery.",
        'CPI': "Increased borrowing costs can combine with supply chain disruptions to exert mixed pressures on CPI.",
        'Unemployment': "While disaster recovery creates jobs, increased borrowing costs might deter large-scale reconstruction projects."
    },
    'IX': {
        'GDP': "Raising interest rates could slow investments in space-related ventures, potentially reducing the GDP boost from such a breakthrough.",
        'CPI': "Higher borrowing costs might exert a downward pressure on CPI despite increased space-related activities.",
        'Unemployment': "While space exploration offers new job avenues, increased borrowing costs might slow down these opportunities."
    },
    'X': {
        'GDP': "Increased interest rates can deter rapid investments in AI and robotics, potentially slowing GDP growth from these sectors.",
        'CPI': "Despite the growth in AI and robotics, higher borrowing costs might put downward pressure on CPI.",
        'Unemployment': "AI and robotics might replace certain jobs, and increased borrowing costs could deter new tech-driven employment opportunities."
    }
},
    'E': {
        'I': {
        'GDP': "Tax incentives during a tech boom can supercharge GDP growth by promoting further investments in emerging technologies.",
        'CPI': "Increased business activity due to tax incentives can cause a rise in CPI.",
        'Unemployment': "Enhanced business growth due to tax breaks can lead to more job creation, decreasing unemployment."
    },
    'II': {
        'GDP': "Tax incentives can mitigate some of the GDP decline caused by the oil price crash by stimulating non-oil sectors.",
        'CPI': "Increased business activity from tax breaks can push up CPI despite declining oil prices.",
        'Unemployment': "Stimulated sectors due to tax incentives might offset job losses in the oil industry."
    },
    'III': {
        'GDP': "Tax incentives during a recession can provide a buffer, encouraging businesses to invest and potentially lifting GDP.",
        'CPI': "Business stimulation through tax breaks might counteract some deflationary pressures, stabilizing CPI.",
        'Unemployment': "Tax incentives can encourage businesses to retain or hire staff, potentially curbing unemployment rises."
    },
    'IV': {
        'GDP': "Tax incentives can encourage businesses to persevere and invest during pandemic challenges, potentially mitigating GDP declines.",
        'CPI': "While a pandemic can create deflationary pressures, tax incentives might bolster business activity, countering some CPI drops.",
        'Unemployment': "Tax breaks can help businesses retain staff during pandemic disruptions, potentially reducing unemployment surges."
    },
    'V': {
        'GDP': "During a trade war, tax incentives can encourage domestic investments, acting as a counterbalance to GDP declines from disrupted trade.",
        'CPI': "Tax breaks might bolster domestic business activity, influencing a rise in CPI amidst trade challenges.",
        'Unemployment': "By stimulating domestic businesses with tax incentives, some trade war-induced job losses might be offset."
    },
    'VI': {
        'GDP': "Tax incentives can accelerate green investments, amplifying GDP gains from the green revolution.",
        'CPI': "Increased green business activity from tax breaks can contribute to a rise in CPI.",
        'Unemployment': "The green sector's growth, spurred by tax incentives, can create jobs, reducing unemployment."
    },
    'VII': {
        'GDP': "Tax incentives can promote business resilience and investment amidst cybersecurity challenges, potentially mitigating GDP impacts.",
        'CPI': "Businesses bolstered by tax breaks might maintain activity levels, stabilizing CPI despite cybersecurity concerns.",
        'Unemployment': "Tax incentives can aid businesses in navigating cyber challenges, potentially avoiding larger unemployment spikes."
    },
    'VIII': {
        'GDP': "Tax breaks can aid businesses in disaster-stricken areas, potentially softening the GDP impact of natural disasters.",
        'CPI': "By sustaining business activity with tax incentives, CPI declines from disaster-induced disruptions might be moderated.",
        'Unemployment': "Tax incentives can support businesses in retaining staff post-disaster, potentially curbing unemployment rises."
    },
    'IX': {
        'GDP': "Tax incentives can spur investments in space ventures, amplifying GDP gains from space exploration breakthroughs.",
        'CPI': "Increased space-related business activity due to tax incentives might push up CPI.",
        'Unemployment': "Tax breaks can encourage hiring in space-related fields, potentially driving down unemployment."
    },
    'X': {
        'GDP': "Tax incentives can expedite investments in AI and robotics, maximizing the potential GDP boost from these sectors.",
        'CPI': "Business growth in AI and robotics from tax breaks might contribute to a CPI rise.",
        'Unemployment': "While AI and robotics can lead to job displacement, tax incentives might also support new job creation, balancing unemployment impacts."
    }
    },
    'F': {
        'I': {
        'GDP': "Welfare expansion during a tech boom can support those not involved in tech, possibly leading to increased consumer spending and a GDP rise.",
        'CPI': "Increased consumer demand from welfare expansion might lead to a rise in CPI.",
        'Unemployment': "While tech industries boom, expanded welfare supports those outside of tech, potentially reducing the overall unemployment rate."
    },
    'II': {
        'GDP': "Welfare expansion during an oil price crash can act as a GDP stabilizer by bolstering consumer spending.",
        'CPI': "The increased consumer spending from welfare benefits might push CPI upwards.",
        'Unemployment': "Expanded welfare offers a safety net to those affected by job losses in the oil sector, potentially stabilizing the unemployment rate."
    },
    'III': {
        'GDP': "Amidst a global recession, expanding welfare can mitigate GDP declines by supporting consumer spending.",
        'CPI': "The bolstered consumer activity from welfare can counteract deflationary pressures, potentially stabilizing CPI.",
        'Unemployment': "Enhanced welfare support provides relief for those affected by a recession, potentially curbing steep unemployment rises."
    },
    'IV': {
        'GDP': "Welfare expansion during a pandemic can support households affected by disruptions, potentially reducing the GDP downturn.",
        'CPI': "With increased consumer spending due to welfare, CPI might see upward pressures even amidst pandemic challenges.",
        'Unemployment': "Expanded welfare acts as a buffer for those unemployed due to pandemic-related business closures, potentially moderating unemployment spikes."
    },
    'V': {
        'GDP': "Expanding welfare during a trade war can act as an economic stabilizer, potentially offsetting some GDP declines from reduced trade.",
        'CPI': "Welfare-induced consumer spending might push CPI upwards, despite trade disruptions.",
        'Unemployment': "Welfare expansion supports those affected by the trade war, potentially preventing a steeper unemployment rise."
    },
    'VI': {
        'GDP': "Welfare expansion in the wake of a green revolution ensures that benefits are distributed widely, potentially leading to broader consumer spending and a GDP rise.",
        'CPI': "Consumer demand, bolstered by welfare, might push CPI up, even amidst a shift to green technologies and practices.",
        'Unemployment': "While the green sector grows, expanded welfare supports workers from displaced industries, potentially moderating unemployment rates."
    },
    'VII': {
        'GDP': "During cybersecurity crises, expanded welfare provides a safety net for affected households, offering some stability to GDP.",
        'CPI': "Welfare-backed consumer spending might remain steady or even rise, influencing CPI, despite cybersecurity challenges.",
        'Unemployment': "Expanded welfare can offer support to those unemployed due to cyber disruptions, potentially moderating unemployment increases."
    },
    'VIII': {
        'GDP': "In the aftermath of natural disasters, welfare expansion supports affected communities, potentially buffering GDP declines.",
        'CPI': "Sustained consumer activity due to welfare might stabilize or increase CPI, even amidst disaster challenges.",
        'Unemployment': "Welfare acts as a safety net post-disaster, supporting those who've lost jobs, potentially stabilizing the unemployment rate."
    },
    'IX': {
        'GDP': "While space exploration advances, expanded welfare ensures the broader population benefits, potentially stimulating consumer spending and aiding GDP.",
        'CPI': "With welfare support, consumer spending might remain buoyant, pushing CPI upwards.",
        'Unemployment': "As space sectors grow, welfare offers a buffer to those not involved, potentially moderating overall unemployment rates."
    },
    'X': {
        'GDP': "As AI and robotics sectors surge, welfare expansion ensures benefits are felt more broadly, potentially stimulating GDP through wider consumer spending.",
        'CPI': "Robust consumer spending backed by welfare can push CPI upwards, even as AI and robotics transform industries.",
        'Unemployment': "Expanded welfare offers a safety net to workers displaced by AI and robotics, potentially preventing a steep rise in unemployment."
    }
    },
'G': {
        'I': {
        'GDP': "Reduced infrastructure spending during a tech boom might hinder broader economic benefits, potentially leading to a subdued GDP rise.",
        'CPI': "A decline in public spending might have a neutral or deflationary effect on CPI amidst a tech boom.",
        'Unemployment': "The decreased public sector infrastructure jobs combined with a tech surge might lead to a mixed impact on unemployment."
    },
    'II': {
        'GDP': "Decreasing infrastructure spending amidst an oil price crash could exacerbate GDP declines, with two major sectors slowing down.",
        'CPI': "Reduced public spending might contribute to deflationary pressures, further pulling CPI down during an oil crash.",
        'Unemployment': "Cuts in infrastructure projects could lead to job losses, amplifying unemployment challenges from the oil sector downturn."
    },
    'III': {
        'GDP': "Reduced infrastructure spending during a global recession might deepen GDP declines, removing a potential stabilizing factor.",
        'CPI': "Declines in public infrastructure spending can contribute to further deflationary pressures during a recession, potentially lowering CPI.",
        'Unemployment': "Withholding investments in infrastructure can exacerbate job losses during a recession, pushing unemployment higher."
    },
    'IV': {
        'GDP': "Decreasing infrastructure spending during a pandemic could lead to compounded economic slowdowns, further pressuring GDP.",
        'CPI': "Reduced public spending in the midst of pandemic disruptions might contribute to deflationary pressures, potentially decreasing CPI.",
        'Unemployment': "Cuts in infrastructure might mean fewer public sector jobs, intensifying unemployment challenges during pandemic times."
    },
    'V': {
        'GDP': "Decreased infrastructure spending during a trade war could compound economic challenges, leading to a more pronounced GDP downturn.",
        'CPI': "The pullback in public spending might exert additional deflationary pressures on CPI amidst trade disruptions.",
        'Unemployment': "Reduced spending on infrastructure can amplify job losses during a trade war, pushing the unemployment rate higher."
    },
    'VI': {
        'GDP': "While the green sector might grow, reducing infrastructure spending can dampen the broader GDP benefits of the green revolution.",
        'CPI': "Decreased public spending can have a neutral or deflationary impact on CPI, even amidst green sector growth.",
        'Unemployment': "The growth of the green sector might be offset by job losses from reduced infrastructure spending, leading to mixed unemployment impacts."
    },
    'VII': {
        'GDP': "Reduced infrastructure spending during cyber crises might hinder recovery efforts, potentially leading to a subdued GDP response.",
        'CPI': "A pullback in public spending during cyber challenges might stabilize or decrease CPI.",
        'Unemployment': "Decreased investments in infrastructure during a cyber crisis can amplify job losses, pushing unemployment upwards."
    },
    'VIII': {
        'GDP': "Cutting back on infrastructure post-natural disasters can hinder recovery efforts, potentially deepening GDP impacts.",
        'CPI': "Reduced public spending in disaster-hit regions might exert deflationary pressures, pulling CPI downwards.",
        'Unemployment': "Withholding infrastructure spending post-disasters can lead to job losses, exacerbating unemployment challenges."
    },
    'IX': {
        'GDP': "While the space sector might advance, cutting infrastructure spending can limit broader GDP gains from spin-off industries.",
        'CPI': "Decreased public spending might have a neutral or deflationary impact on CPI, despite space sector growth.",
        'Unemployment': "The growth in space-related industries might be offset by job losses from infrastructure spending cuts, leading to mixed unemployment outcomes."
    },
    'X': {
        'GDP': "As AI and robotics grow, decreased infrastructure spending can limit the broader economic benefits, potentially leading to a more muted GDP rise.",
        'CPI': "Reduced public infrastructure investments might have a neutral or deflationary effect on CPI, even amidst AI and robotics growth.",
        'Unemployment': "The job creation in AI and robotics might be balanced by losses from infrastructure cutbacks, leading to mixed unemployment impacts."
    }
    },

    'H': {
        'I': {
        'GDP': "Limiting exports during a tech boom might reduce GDP growth as tech firms are restricted from capitalizing on global markets.",
        'CPI': "Restricted exports can lead to an oversupply domestically, potentially reducing CPI.",
        'Unemployment': "Tech firms might see limited job growth or even job cuts due to export restrictions, raising unemployment."
    },
    'II': {
        'GDP': "Limiting exports amidst an oil price crash can further strain GDP as oil producers can't capitalize on possible favorable external markets.",
        'CPI': "With restricted exports, local markets might experience oversupply, potentially decreasing CPI.",
        'Unemployment': "Oil sector job losses might be compounded with limited export avenues, pushing unemployment higher."
    },
    'III': {
        'GDP': "During a global recession, limiting exports can exacerbate GDP declines, depriving domestic companies of external demand.",
        'CPI': "Domestic oversupply due to export restrictions might exert further deflationary pressures, reducing CPI.",
        'Unemployment': "Job losses might increase as firms face both local and global demand shocks, further raising unemployment."
    },
        'IV': {
        'GDP': "During a pandemic, limiting exports can further suppress GDP by restricting firms from diversifying risks across markets.",
        'CPI': "Domestic oversupply due to export restrictions may lead to a decrease in CPI.",
        'Unemployment': "As companies face reduced export opportunities, they might lay off workers, leading to increased unemployment."
    },
    'V': {
        'GDP': "In a trade war scenario, limiting exports can be redundant and can intensify negative GDP impacts.",
        'CPI': "Trade restrictions might cause scarcity of some goods, potentially increasing CPI.",
        'Unemployment': "Reduced global trade avenues can lead to layoffs, thus raising unemployment."
    },
    'VI': {
        'GDP': "Limiting exports during a green revolution can impede GDP growth by restricting green businesses from accessing broader markets.",
        'CPI': "Domestic oversupply of green goods might lead to a decrease in CPI.",
        'Unemployment': "Green industries might experience reduced growth or layoffs due to export limitations, increasing unemployment."
    },
    'VII': {
        'GDP': "Limiting exports after a cybersecurity breach might be seen as a protective measure, but can hinder GDP recovery by reducing market access for affected businesses.",
        'CPI': "Reduced exports may not significantly affect CPI in the short term following a breach.",
        'Unemployment': "Affected industries might see additional job cuts if they are also limited from exporting, exacerbating unemployment."
    },
    'VIII': {
        'GDP': "During natural disasters, limiting exports can be detrimental to GDP as domestic production capabilities might be impaired and external markets could provide relief.",
        'CPI': "Export limitations combined with disaster-related supply shortages might drive up CPI.",
        'Unemployment': "Job losses from disaster impacts might be compounded if industries are also barred from exporting, pushing unemployment up."
    },
    'IX': {
        'GDP': "Limiting exports during a period of space exploration advancements might hinder GDP growth by restricting aerospace industries from global collaborations and market access.",
        'CPI': "Reduced exports in aerospace might not have a significant direct impact on CPI.",
        'Unemployment': "The aerospace sector could face growth limitations or job cuts due to export restrictions, affecting unemployment."
    },
    'X': {
        'GDP': "Limiting exports in an era of AI and robotics surge can dampen GDP growth by restricting these industries from accessing global markets.",
        'CPI': "A domestic oversupply of AI and robotics products might lead to a decrease in CPI.",
        'Unemployment': "AI and robotics industries might see limited growth or layoffs due to export restrictions, increasing unemployment."
    }
    },

    'J': {
        'I': {
        'GDP': "Increasing taxes on businesses during a tech boom can dampen the GDP growth, as tech firms have reduced profits for reinvestment.",
        'CPI': "Higher business costs due to tax hikes might be passed onto consumers, raising CPI.",
        'Unemployment': "Tax increases can slow hiring or even lead to layoffs in the tech sector, potentially increasing unemployment."
    },
    'II': {
        'GDP': "Raising taxes amidst an oil price crash can deepen GDP declines, further stressing an already vulnerable sector.",
        'CPI': "Higher production costs due to tax increases can contribute to inflationary pressures, potentially raising CPI.",
        'Unemployment': "The oil sector, already struggling, might face further job cuts due to increased taxation, exacerbating unemployment."
    },
    'III': {
        'GDP': "During a global recession, tax hikes on businesses can exacerbate economic downturns, further depressing GDP.",
        'CPI': "Increased business costs from tax hikes might drive up prices, exerting inflationary pressures on CPI.",
        'Unemployment': "Raising taxes can lead to business contractions and layoffs during a recession, further escalating unemployment."
    },
        'IV': {
        'GDP': "Increasing business taxes during a pandemic can further depress GDP as businesses might be already struggling with reduced revenues.",
        'CPI': "Higher business costs due to tax hikes might be passed onto consumers, leading to an increase in CPI.",
        'Unemployment': "Increased taxation during a pandemic can lead to business closures and job cuts, pushing unemployment up."
    },
    'V': {
        'GDP': "In a trade war, raising business taxes can be detrimental, amplifying GDP declines due to double stress on businesses.",
        'CPI': "Increased production costs due to both trade restrictions and tax hikes can contribute to inflationary pressures on CPI.",
        'Unemployment': "Businesses facing both trade barriers and tax hikes might opt for job cuts, exacerbating unemployment."
    },
    'VI': {
        'GDP': "Taxing businesses more during a green revolution might slow down the GDP growth derived from green industries.",
        'CPI': "Increased costs for green businesses might be passed onto consumers, potentially raising CPI.",
        'Unemployment': "Green businesses might see slower hiring or even layoffs due to higher taxes, affecting unemployment rates."
    },
    'VII': {
        'GDP': "Raising taxes after a cybersecurity breach can hinder GDP recovery by placing additional financial burdens on already vulnerable businesses.",
        'CPI': "Higher business costs due to tax hikes might lead to inflationary pressures on CPI.",
        'Unemployment': "Affected industries might face additional layoffs if also subjected to increased taxation, pushing unemployment higher."
    },
    'VIII': {
        'GDP': "Increasing taxes post-natural disasters can suppress GDP recovery by straining businesses already coping with physical damages.",
        'CPI': "Higher costs for businesses recovering from disasters might be passed onto consumers, raising CPI.",
        'Unemployment': "Business recovery might be slower with higher taxes, potentially leading to sustained or increased unemployment."
    },
    'IX': {
        'GDP': "Increasing taxes during a space exploration surge might slow GDP growth by reducing profitability and reinvestment capabilities for aerospace industries.",
        'CPI': "Increased costs in aerospace due to higher taxes might lead to inflationary pressures on CPI.",
        'Unemployment': "Aerospace industries might face hiring slowdowns or layoffs due to higher taxation, affecting unemployment."
    },
    'X': {
        'GDP': "Raising taxes during an AI and robotics surge can dampen the GDP growth as these sectors might have reduced funds for R&D and expansion.",
        'CPI': "Increased costs in AI and robotics due to taxation might contribute to inflationary pressures on CPI.",
        'Unemployment': "The AI and robotics sectors could see reduced growth or layoffs due to higher taxation, potentially raising unemployment."
    }
    },

    'K': {
        'I': {
        'GDP': "In the midst of a global tech boom, cutting social welfare might reduce consumer spending, potentially slowing the overall GDP growth slightly.",
        'CPI': "With decreased consumer demand due to welfare cuts, there might be deflationary pressures leading to a decrease in CPI, despite the tech growth.",
        'Unemployment': "The tech industry might see significant job creation, but the broader impact of welfare cuts could lead to employment challenges in other sectors."
    },
    'II': {
        'GDP': "Following an oil price crash, cutting welfare can depress GDP further by reducing consumer spending power, especially in economies dependent on oil revenues.",
        'CPI': "The combined effect of reduced oil prices and decreased consumer spending due to welfare cuts might lead to significant deflationary pressures on CPI.",
        'Unemployment': "While the oil sector might see layoffs due to price crashes, welfare cuts can exacerbate unemployment as other sectors feel the pinch from reduced consumer spending."
    },
    'III': {
        'GDP': "During a global recession, cutting social welfare can have a detrimental effect on GDP, deepening the recession by further suppressing consumer demand.",
        'CPI': "With a global recession and reduced consumer spending power due to welfare cuts, strong deflationary pressures might pull down CPI.",
        'Unemployment': "The recession itself might lead to significant job losses, and welfare cuts can intensify unemployment as people have fewer safety nets and decreased spending affects various sectors."
    },
        'IV': {
        'GDP': "Cutting social welfare during a pandemic can depress consumer spending, potentially leading to a further decline in GDP.",
        'CPI': "With reduced consumer spending power, deflationary pressures might increase, leading to a potential decrease in CPI.",
        'Unemployment': "With reduced welfare support, many affected by the pandemic might seek jobs, but opportunities might be scarce, leading to high unemployment."
    },
    'V': {
        'GDP': "In a trade war scenario, cutting welfare can exacerbate GDP declines by further reducing domestic consumer spending.",
        'CPI': "Reduced spending power from welfare cuts can lead to deflationary pressures, potentially reducing CPI.",
        'Unemployment': "Reduced domestic demand due to welfare cuts combined with trade restrictions can lead to job losses, raising unemployment."
    },
    'VI': {
        'GDP': "Cutting social welfare during a green revolution can reduce consumer spending on green products, potentially slowing GDP growth.",
        'CPI': "Decreased consumer demand for green products due to welfare cuts might exert deflationary pressures, reducing CPI.",
        'Unemployment': "While green industries grow, other sectors affected by welfare cuts might see job losses, leading to mixed unemployment outcomes."
    },
    'VII': {
        'GDP': "Reducing social welfare after a cybersecurity breach might not directly affect GDP recovery but can affect overall consumer confidence and spending.",
        'CPI': "Reduced consumer spending power from welfare cuts can exert deflationary pressures, potentially pulling down CPI.",
        'Unemployment': "Job market recovery post-breach might be slowed if affected populations also face welfare cuts, potentially keeping unemployment high."
    },
    'VIII': {
        'GDP': "Cutting welfare post-disasters can hinder GDP recovery by depriving affected populations of necessary financial support and depressing consumer spending.",
        'CPI': "With decreased consumer spending power post-disaster, deflationary pressures might pull down CPI.",
        'Unemployment': "Post-disaster job market recovery might be slowed if affected communities also face welfare cuts, potentially exacerbating unemployment."
    },
    'IX': {
        'GDP': "Cutting welfare during a space exploration surge might not directly influence aerospace GDP growth but can impact broader consumer spending patterns.",
        'CPI': "Reduced spending power due to welfare cuts might exert some deflationary pressures, potentially affecting CPI.",
        'Unemployment': "While aerospace sectors might see growth, other sectors impacted by welfare cuts can face job losses, leading to mixed unemployment outcomes."
    },
    'X': {
        'GDP': "During an AI and robotics surge, cutting welfare can depress broader consumer spending, potentially slowing down overall GDP growth.",
        'CPI': "Reduced spending power due to welfare cuts can lead to deflationary pressures, affecting CPI.",
        'Unemployment': "While AI and robotics sectors might thrive, reduced welfare can impact other sectors leading to job losses, potentially raising unemployment."
    }
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

