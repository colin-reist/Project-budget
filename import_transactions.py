#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import time

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc1NzI5ODAxLCJpYXQiOjE3NzU3Mjg5MDEsImp0aSI6IjFiZmMwNjYzNTFkODQxOGU5YjdmNjI0NmYyMWFhYzk2IiwidXNlcl9pZCI6MX0.mYqUpO-Z8S6TnM7l4tQuIfmzSIJamaSaKM3DbHy9E-8"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

TRANSACTIONS = [
  {
    "account": 1,
    "type": "expense",
    "amount": 5.0,
    "description": "Achat online McDonalds 780151 29.12.2025, 16:59, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.9,
    "description": "Paiement TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 11.0,
    "description": "Achat Coop Pronto 5176 01.01.2026, 19:33, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 26.0,
    "description": "Achat Bains de Saillon SA 01.01.2026, 16:07, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 281.35,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 281.35,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-05",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 18.3,
    "description": "Achat MCDONALDS 02.01.2026, 18:45, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 281.35,
    "description": "Paiement Avenir Assurance Maladie SA",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 280.25,
    "description": "Paiement Avenir Assurance Maladie SA",
    "date": "2026-01-05",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 19.0,
    "description": "Achat online CANALPLUSSUISSE 02.01.2026, 16:44, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-06",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.5,
    "description": "Achat Eldora c/o CEJEF 05.01.2026, 09:59, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.0,
    "description": "Achat Eldora c/o CEJEF 05.01.2026, 12:25, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.55,
    "description": "Achat Coop Pronto 3955 05.01.2026, 08:52, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 18.9,
    "description": "Achat online McDonalds 780083 04.01.2026, 16:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 95.0,
    "description": "Paiement TWINT , MONITEUR",
    "date": "2026-01-07",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 95.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-07",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 95.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-07",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 06.01.2026, 08:25, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-08",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.5,
    "description": "Achat 220.55 Avec 06.01.2026, 17:13, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-08",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 4.65,
    "description": "Achat Coop Pronto 3955 07.01.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.2,
    "description": "Achat Coop Pronto 3955 07.01.2026, 18:03, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 13.3,
    "description": "Achat Eldora c/o CEJEF 07.01.2026, 12:35, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 6.95,
    "description": "Achat 220.55 Avec 08.01.2026, 08:49, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 13.0,
    "description": "Achat online APPLE.COM/BILL 08.01.2026, 12:04, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "income",
    "amount": 136.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 136.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-12",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 136.0,
    "description": "Achat TWINT SBB CFF FFS",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 8
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 17.3,
    "description": "Achat 220.55 Avec 09.01.2026, 08:50, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 15.99,
    "description": "Achat online MICROSOFT*STORE 09.01.2026, 21:08, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "income",
    "amount": 50.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-12",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 50.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-12",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.26,
    "description": "Achat online G2A.COM 11.01.2026, 17:58, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-13",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 23.75,
    "description": "Achat online G2A.COM 12.01.2026, 19:03, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-14",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 12.01.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-14",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.25,
    "description": "Achat Coop Pronto 3955 14.01.2026, 17:01, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-16",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.55,
    "description": "Achat online STEAM PURCHASE 13.01.2026, 20:16, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-16",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 612.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-16",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 612.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-16",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "income",
    "amount": 7.0,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-16",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 612.3,
    "description": "Achat CFF Gare Delemont 16.01.2026, 17:35, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-19",
    "is_recurring": False,
    "category": 8
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 17.9,
    "description": "Achat MCDONALD S 16.01.2026, 20:31, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-19",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 17.01.2026, 11:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-19",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.9,
    "description": "Achat Coop-1978 Porrentr 17.01.2026, 13:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-19",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.9,
    "description": "Achat Coop Pronto 3955 17.01.2026, 17:32, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-19",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 300.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-19",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 300.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-19",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.95,
    "description": "Paiement TWINT , MAXIK",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.0,
    "description": "Paiement TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.5,
    "description": "Paiement TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 12.25,
    "description": "Paiement TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 36.0,
    "description": "Achat TWINT LA BELLA CIAO",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 100.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 100.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-20",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.3,
    "description": "Paiement TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 12.0,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "income",
    "amount": 12.0,
    "description": "Crédit TWINT ROSSI, XAVIER",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "income",
    "amount": 12.0,
    "description": "Crédit TWINT RYF, FREDERIC",
    "date": "2026-01-20",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.9,
    "description": "Achat Migros MM Porrentruy 19.01.2026, 12:38, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-21",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 19.01.2026, 08:22, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-21",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 56.0,
    "description": "Paiement TWINT , DANIELLA",
    "date": "2026-01-22",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.85,
    "description": "Achat Aldi Suisse 35 21.01.2026, 13:44, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-23",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 1558.15,
    "description": "Crédit Republique . Canton du Jura Tresorerie generale",
    "date": "2026-01-23",
    "is_recurring": False,
    "category": 1
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.0,
    "description": "Paiement TWINT RONDEZ, RAYAN",
    "date": "2026-01-23",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.0,
    "description": "Achat online STEAMGAMES.COM 425952298 21.01.2026, 12:14, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-26",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.75,
    "description": "Achat 220.55 Avec 22.01.2026, 07:54, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 2.9,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-01-26",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 13.95,
    "description": "Achat 220.55 Avec 23.01.2026, 08:53, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 18.3,
    "description": "Achat Burger King - Drijur 24.01.2026, 18:08, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.3,
    "description": "Achat Burger King - Drijur 24.01.2026, 18:51, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 74.0,
    "description": "LSV Aristote Concept Porrentruy",
    "date": "2026-01-28",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.0,
    "description": "Achat Eldora c/o CEJEF 26.01.2026, 15:02, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-28",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 26.01.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-28",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.0,
    "description": "Achat Shop Auto GT 26.01.2026, 12:31, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-28",
    "is_recurring": False,
    "category": 8
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.9,
    "description": "Achat Coop Pronto 3955 27.01.2026, 10:46, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-29",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 84.1,
    "description": "Paiement Visana Services AG",
    "date": "2026-01-30",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 385.6,
    "description": "Ordre permanent Reist Béatrice",
    "date": "2026-01-30",
    "is_recurring": False,
    "category": 7
  },
  {
    "account": 1,
    "type": "income",
    "amount": 200.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-30",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 200.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-01-30",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.1,
    "description": "Achat Coop Pronto 3955 28.01.2026, 08:52, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-30",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.0,
    "description": "Achat Eldora c/o CEJEF 28.01.2026, 15:06, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-01-30",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 5.0,
    "description": "Crédit TWINT SCHAFFNER, KATIANNA",
    "date": "2026-02-02",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.8,
    "description": "Achat 220.55 Avec 29.01.2026, 07:22, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.45,
    "description": "Achat 220.55 Avec 30.01.2026, 08:51, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 12.5,
    "description": "Achat Coop Pronto 3484 30.01.2026, 20:10, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 11.0,
    "description": "Achat Istanbul Grill 30.01.2026, 20:04, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-02",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.3,
    "description": "Achat online Post BillingOnline 30.01.2026, 08:23, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-02",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 281.35,
    "description": "Paiement Avenir Assurance Maladie SA",
    "date": "2026-02-03",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 22.0,
    "description": "Achat TWINT LA BELLA CIAO",
    "date": "2026-02-03",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 17.0,
    "description": "Crédit TWINT ROSSI, XAVIER",
    "date": "2026-02-03",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.9,
    "description": "Achat Coop-1978 Porrentr 03.02.2026, 12:37, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.5,
    "description": "Achat Coop Pronto 3955 03.02.2026, 08:22, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.0,
    "description": "Achat Eldora c/o CEJEF 03.02.2026, 15:05, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 95.0,
    "description": "Paiement TWINT , MONITEUR",
    "date": "2026-02-05",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 19.0,
    "description": "Achat online CANALPLUSSUISSE 03.02.2026, 11:51, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-06",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.5,
    "description": "Achat Eldora c/o CEJEF 04.02.2026, 10:08, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-06",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 4.8,
    "description": "Achat Coop-1978 Porrentr 04.02.2026, 12:43, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-06",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.5,
    "description": "Achat 220.55 Avec 05.02.2026, 15:19, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 40.0,
    "description": "Achat Le Suisse Restaurant 06.02.2026, 22:11, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-09",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 11.45,
    "description": "Achat 220.55 Avec 06.02.2026, 08:51, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 27.11,
    "description": "Achat online UBER   * EATS PENDING 07.02.2026, 12:36, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-09",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 15.99,
    "description": "Achat online Microsoft*PC Game Pa 09.02.2026, 04:42, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-10",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.5,
    "description": "Achat online STEAMGAMES.COM 425952298 07.02.2026, 15:15, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-10",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 78.4,
    "description": "Achat online Ticketcorner*9015821 08.02.2026, 16:38, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-10",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.2,
    "description": "Achat online McDonalds 780083 07.02.2026, 18:58, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-10",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 16.0,
    "description": "Achat online McDonalds 780083 07.02.2026, 18:24, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-10",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.9,
    "description": "Achat Coop-1978 Porrentr 09.02.2026, 12:36, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-11",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.2,
    "description": "Achat Coop Pronto 3955 09.02.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-11",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.95,
    "description": "Achat Coop Pronto 3955 09.02.2026, 17:50, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-11",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.8,
    "description": "Achat FRI DIVCOM 10.02.2026, 12:57, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-12",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.45,
    "description": "Achat 220.55 Avec 10.02.2026, 07:23, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-12",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 104.9,
    "description": "Remboursement achat, 10.02.2026, 17:34 Ochsner Sport / 969, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-12",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.3,
    "description": "Achat Eldora c/o CEJEF 11.02.2026, 12:38, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-13",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.0,
    "description": "Achat Eldora c/o CEJEF 11.02.2026, 15:01, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-13",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.5,
    "description": "Achat Coop Pronto 3955 11.02.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-13",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 4.95,
    "description": "Achat Coop Pronto 3955 11.02.2026, 17:01, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-13",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 12.02.2026, 08:10, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-16",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 13.02.2026, 08:49, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-16",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 37.0,
    "description": "Paiement TWINT ANTONIETTA, MAURER",
    "date": "2026-02-17",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.09,
    "description": "Achat Aldi Suisse 35 16.02.2026, 18:05, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-18",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 16.02.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-18",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 17.02.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-19",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 18.02.2026, 08:50, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-20",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 2.75,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-02-23",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 14.5,
    "description": "Paiement TWINT ROSSI, XAVIER",
    "date": "2026-02-23",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 11.9,
    "description": "Paiement TWINT ROSSI, XAVIER",
    "date": "2026-02-23",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.55,
    "description": "Achat Coop Pronto 3955 23.02.2026, 08:52, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-25",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.8,
    "description": "Achat Coop Pronto 3955 23.02.2026, 16:54, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-25",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 1558.15,
    "description": "Crédit Republique . Canton du Jura Tresorerie generale",
    "date": "2026-02-25",
    "is_recurring": False,
    "category": 1
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 40.0,
    "description": "Achat TWINT GALAXI PIZZA&KEBAB",
    "date": "2026-02-25",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 10.0,
    "description": "Crédit TWINT ROSSI, XAVIER",
    "date": "2026-02-25",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.05,
    "description": "Achat Coop-1978 Porrentr 24.02.2026, 12:39, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 24.02.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 10.0,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-02-26",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 95.0,
    "description": "Paiement TWINT , MONITEUR",
    "date": "2026-02-26",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 74.0,
    "description": "LSV Aristote Concept Porrentruy",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 84.1,
    "description": "Paiement Visana Services AG",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 281.35,
    "description": "Paiement Avenir Assurance Maladie SA",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 25.02.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 13.54,
    "description": "Achat online EPC*FORTNITE 25.02.2026, 21:22, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.1,
    "description": "Achat Coop-1978 Porrentr 25.02.2026, 12:42, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.25,
    "description": "Achat Coop Pronto 3955 25.02.2026, 17:00, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 300.0,
    "description": "Ordre permanent Reist Béatrice",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 7
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 150.0,
    "description": "Ordre permanent Republique et Canton du Jura-Tresorerie generale",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 6
  },
  {
    "account": 1,
    "type": "income",
    "amount": 200.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-02-27",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 200.0,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-02-27",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 36.0,
    "description": "Paiement TWINT FALLET, STEVE",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 26.02.2026, 07:51, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.8,
    "description": "Achat 220.55 Avec 26.02.2026, 17:38, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 17.75,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 21.2,
    "description": "Achat 220.55 Avec 27.02.2026, 07:52, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 14.0,
    "description": "Remboursement achat, 27.02.2026, 21:57 Buvettes, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 35.5,
    "description": "Achat Le Bleu Lezard 28.02.2026, 17:48, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.1,
    "description": "Achat Volg Laden Courtetel 28.02.2026, 16:34, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 200.0,
    "description": "Transfert sur Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-03-02",
    "is_recurring": False
  },
  {
    "account": 2,
    "type": "income",
    "amount": 200.0,
    "description": "Transfert sur Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-03-02",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 25.0,
    "description": "Achat TWINT ARISTOTE CONCEPT DELEMONT",
    "date": "2026-03-03",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "income",
    "amount": 10.0,
    "description": "Remboursement achat, 27.02.2026, 22:43 HC Ajoie SA, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-04",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.0,
    "description": "Achat Eldora c/o CEJEF 02.03.2026, 12:25, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-04",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 0.6,
    "description": "Achat Eldora c/o CEJEF 02.03.2026, 12:26, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-04",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.0,
    "description": "Achat Eldora c/o CEJEF 02.03.2026, 15:03, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-04",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 4.55,
    "description": "Achat Coop Pronto 3955 02.03.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-04",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.4,
    "description": "Achat Coop Pronto 3955 02.03.2026, 16:52, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-04",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 324.75,
    "description": "Paiement Caisse pour médecins-dentistes SA",
    "date": "2026-03-05",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 14.23,
    "description": "Achat online BITWARDEN 04.03.2026, 01:52, No carte Visa Debit 427347xxxxxx0303 USD 16.05, taux de ch",
    "date": "2026-03-05",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 03.03.2026, 07:50, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-05",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 3.3,
    "description": "Remboursement achat, 02.03.2026, 02:00 Post BillingOnline, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-05",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 31.4,
    "description": "Achat Otto's SA 20, Delemo 03.03.2026, 17:58, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-05",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.55,
    "description": "Achat Migros MM Porrentruy 04.03.2026, 12:49, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-06",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.5,
    "description": "Achat Eldora c/o CEJEF 04.03.2026, 09:53, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-06",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.75,
    "description": "Achat Coop Pronto 3955 04.03.2026, 17:00, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-06",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 19.0,
    "description": "Achat online CANALPLUSSUISSE 03.03.2026, 20:13, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-06",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 20.81,
    "description": "Achat online UNITY 04.03.2026, 15:18, No carte Visa Debit 427347xxxxxx0303 USD 24.32, taux de change",
    "date": "2026-03-06",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 2.9,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-03-06",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 22.4,
    "description": "Achat Burger King - Drijur 06.03.2026, 18:37, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.8,
    "description": "Achat Burger King - Drijur 06.03.2026, 19:04, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 4.95,
    "description": "Achat 220.55 Avec 06.03.2026, 08:22, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 16.4,
    "description": "Achat online UBER   *ONE MEMBERSHIP 06.03.2026, 12:27, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 55.0,
    "description": "Achat TWINT DIGITEC GALAXUS",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 2.0,
    "description": "Remboursement achat, 07.03.2026, 21:54 Buvettes, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 6.0,
    "description": "Achat HC Ajoie SA 07.03.2026, 21:13, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 248.5,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 2,
    "type": "expense",
    "amount": 248.5,
    "description": "Transfert depuis Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-03-09",
    "is_recurring": False
  },
  {
    "account": 1,
    "type": "income",
    "amount": 50.0,
    "description": "Dépot au Bancomat BR Porrentruy 3 09.03.2026, 12:58, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-09",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 15.99,
    "description": "Achat online MICROSOFT*PC GAME PA 09.03.2026, 02:09, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-11",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.85,
    "description": "Achat Coop-1978 Porrentr 09.03.2026, 12:35, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-11",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 09.03.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-11",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.0,
    "description": "Achat Coop-1978 Porrentr 10.03.2026, 12:39, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-12",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 10.03.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-12",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 28.9,
    "description": "Achat Pharmacie Benu 11.03.2026, 08:40, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-13",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.75,
    "description": "Achat 220.55 Avec 11.03.2026, 08:43, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-13",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 26.9,
    "description": "Paiement TWINT MORITZ, MAXIMILIEN",
    "date": "2026-03-16",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.45,
    "description": "Achat 220.55 Avec 12.03.2026, 08:49, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-16",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 23.57,
    "description": "Crédit TWINT FRESARD, ALEXIS",
    "date": "2026-03-16",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 47.15,
    "description": "Paiement Post CH AG",
    "date": "2026-03-17",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 5.49,
    "description": "Achat online STEAMGAMES.COM 425952298 14.03.2026, 15:48, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-17",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 369.7,
    "description": "Crédit TWINT REIST, BEATRICE",
    "date": "2026-03-17",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.8,
    "description": "Achat Coop Pronto 3955 16.03.2026, 16:59, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-18",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.6,
    "description": "Achat Eldora c/o CEJEF 16.03.2026, 12:27, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-18",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.6,
    "description": "Achat Coop Pronto 3955 16.03.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-18",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.8,
    "description": "Achat TWINT COOP PRONTO 3955 PORRENTRUY",
    "date": "2026-03-18",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 0.9,
    "description": "Crédit TWINT MORITZ, MAXIMILIEN",
    "date": "2026-03-18",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.85,
    "description": "Achat 220.55 Avec 17.03.2026, 08:50, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-19",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.0,
    "description": "Achat Coop-1978 Porrentr 18.03.2026, 12:50, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-20",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.4,
    "description": "Achat Migros MM Porrentruy 18.03.2026, 12:55, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-20",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.5,
    "description": "Achat Eldora c/o CEJEF 18.03.2026, 10:10, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-20",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 6.99,
    "description": "Achat online Twitch Interactive, Inc 18.03.2026, 08:35, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-20",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.05,
    "description": "Achat 220.55 Avec 19.03.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-23",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 410.8,
    "description": "Paiement fussundschuh sa",
    "date": "2026-03-24",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 18.3,
    "description": "Achat online McDonalds 780083 21.03.2026, 15:55, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-24",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 6.65,
    "description": "Achat Coop-1978 Porrentr 23.03.2026, 12:52, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-25",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.4,
    "description": "Achat Coop Pronto 3955 23.03.2026, 08:21, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-25",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.35,
    "description": "Achat online TWITCH 23.03.2026, 07:29, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-25",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.55,
    "description": "Achat Migros MM Porrentruy 23.03.2026, 12:34, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-25",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.35,
    "description": "Achat online TWITCH 23.03.2026, 07:38, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-25",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "income",
    "amount": 1528.75,
    "description": "Crédit Republique . Canton du Jura Tresorerie generale",
    "date": "2026-03-25",
    "is_recurring": False,
    "category": 1
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 17.5,
    "description": "Achat LS Jurassic Food 24.03.2026, 12:41, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-26",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.7,
    "description": "Achat Coop Pronto 3955 24.03.2026, 08:53, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.4,
    "description": "Achat Coop-1978 Porrentr 24.03.2026, 13:06, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-26",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 6.82,
    "description": "Achat online Kinguin Games 24.03.2026, 22:18, No carte Visa Debit 427347xxxxxx0303 EUR 5.71, taux de",
    "date": "2026-03-26",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 74.0,
    "description": "LSV Aristote Concept Porrentruy",
    "date": "2026-03-27",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 150.0,
    "description": "Ordre permanent Republique et Canton du Jura-Tresorerie generale",
    "date": "2026-03-27",
    "is_recurring": False,
    "category": 6
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.78,
    "description": "Achat online Etsy.com*PwrUpCreations 25.03.2026, 12:23, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-27",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.7,
    "description": "Achat Coop Pronto 3955 25.03.2026, 08:53, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-27",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.8,
    "description": "Achat Coop Pronto 3955 25.03.2026, 16:36, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-27",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 11.3,
    "description": "Achat Eldora c/o CEJEF 25.03.2026, 12:35, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-27",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 19.07,
    "description": "Achat online CLAUDE.AI SUBSCRIPTION 26.03.2026, 04:20, No carte Visa Debit 427347xxxxxx0303 USD 21.6",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 6.99,
    "description": "Achat online TWITCH 26.03.2026, 09:37, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.05,
    "description": "Achat 220.55 Avec 26.03.2026, 08:19, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 7.85,
    "description": "Achat Volg Laden Courtetel 26.03.2026, 17:18, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 1.8,
    "description": "Crédit TWINT MERTZ, MATHILDE",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 8.39,
    "description": "Achat online Xsolla  Xsolla 27.03.2026, 18:24, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 28.3,
    "description": "Achat Burger King - Drijur 28.03.2026, 17:38, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "income",
    "amount": 5.16,
    "description": "Remboursement achat, 28.03.2026, 22:44 Kinguin Games, No carte Visa Debit 427347xxxxxx0303 EUR 5.71,",
    "date": "2026-03-30",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 281.35,
    "description": "Paiement Avenir Assurance Maladie SA",
    "date": "2026-03-31",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 300.0,
    "description": "Ordre permanent Reist Béatrice",
    "date": "2026-03-31",
    "is_recurring": False,
    "category": 7
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 200.0,
    "description": "Transfert sur Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-03-31",
    "is_recurring": False
  },
  {
    "account": 2,
    "type": "income",
    "amount": 200.0,
    "description": "Transfert sur Cpt. épargne YoungMember CH39 8080 8002 4531 8721 4",
    "date": "2026-03-31",
    "is_recurring": False,
    "category": 9
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 84.1,
    "description": "Paiement Visana Services AG",
    "date": "2026-04-01",
    "is_recurring": False,
    "category": 10
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.0,
    "description": "Achat Eldora c/o CEJEF 30.03.2026, 12:30, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-01",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 26.99,
    "description": "Achat online STEAM PURCHASE 29.03.2026, 20:25, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-01",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 10.99,
    "description": "Achat online STEAM PURCHASE 28.03.2026, 22:53, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-01",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.8,
    "description": "Achat Coop Pronto 3955 30.03.2026, 08:20, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-01",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 2.1,
    "description": "Achat 220.55 Avec 31.03.2026, 07:41, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-02",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 3.4,
    "description": "Achat Coop Pronto 3955 01.04.2026, 16:27, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 1.8,
    "description": "Achat Coop Pronto 3955 01.04.2026, 08:19, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.0,
    "description": "Achat Eldora c/o CEJEF 01.04.2026, 12:36, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 0.6,
    "description": "Achat Eldora c/o CEJEF 01.04.2026, 12:37, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.05,
    "description": "Achat 220.55 Avec 02.04.2026, 12:10, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 2
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 19.9,
    "description": "Paiement TWINT , MAXIK",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 32.17,
    "description": "Achat online Etsy.com*Multiple Shops 03.04.2026, 01:42, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 9.87,
    "description": "Achat online Etsy.com*Multiple Shops 05.04.2026, 01:51, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 3
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 19.0,
    "description": "Achat online CANALPLUSSUISSE 02.04.2026, 08:36, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-07",
    "is_recurring": False,
    "category": 5
  },
  {
    "account": 1,
    "type": "expense",
    "amount": 16.4,
    "description": "Achat online UBER   *ONE MEMBERSHIP 06.04.2026, 12:27, No carte Visa Debit 427347xxxxxx0303",
    "date": "2026-04-08",
    "is_recurring": False,
    "category": 3
  }
]

def run():
    ok = 0
    errors = 0
    total = len(TRANSACTIONS)

    for i, tx in enumerate(TRANSACTIONS):
        body = json.dumps(tx).encode()
        req = urllib.request.Request(
            f"{BASE_URL}/transactions/",
            data=body,
            headers=HEADERS,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                ok += 1
                if (i + 1) % 20 == 0:
                    print(f"  {i+1}/{total} importées...")
        except urllib.error.HTTPError as e:
            errors += 1
            desc = tx.get("description", "")[:50]
            detail = e.read().decode()[:200]
            print(f"  ERREUR {e.code} | {desc} | {detail}")

        time.sleep(0.05)

    print(f"\n✅ {ok}/{total} importées, {errors} erreurs")

if __name__ == "__main__":
    print(f"Démarrage import de {len(TRANSACTIONS)} transactions...")
    run()