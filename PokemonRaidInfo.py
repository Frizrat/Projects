import requests, os, webbrowser
from bs4 import BeautifulSoup, SoupStrainer
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def scrap(typePokemons={}, pokemonEffect={}):
    print('Scrap')
    session = requests.Session()
    typeDict = {
        'Acier': ['379', '66'],
        'Acier/Combat': ['638', '69'],
        'Acier/Dragon': ['483', '66'],
        'Acier/Fée': ['888', '562'],
        'Acier/Feu': ['485', '394'],
        'Acier/Insecte': ['649', '299'],
        'Acier/Plante': ['798', '73'],
        'Acier/Psy': ['791', '86'],
        'Acier/Roche': ['805', '79'],
        'Acier/Vol': ['797', '283'],

        'Combat': ['493', '69'],
        'Combat/Eau': ['647', '292'],
        'Combat/Insecte': ['794', '69'],
        'Combat/Normal': ['648', '295'],
        'Combat/Plante': ['640', '73'],
        'Combat/Roche': ['639', '69'],
        'Combat/Spectre': ['802', '69'],
        'Combat/Vol': ['145', '673'],

        'Dragon': ['493', '66'],
        'Dragon/Eau': ['484', '292'],
        'Dragon/Elec': ['644', '393'],
        'Dragon/Feu': ['643', '513'],
        'Dragon/Glace': ['646', '290'],
        'Dragon/Poison': ['890', '567'],
        'Dragon/Sol': ['718', '567'],
        'Dragon/Spec': ['487', '60'],
        'Dragon/Tén': ['799', '66'],
        'Dragon/Vol': ['384', '283'],

        'Eau': ['245', '395'],
        'Eau/Fée': ['788', '292'],
        'Eau/Feu': ['721', '513'],

        'Elec': ['243', '393'],
        'Elec/Fée': ['785', '393'],
        'Elec/Vol': ['145', '332'],

        'Fée': ['716', '562'],
        'Fée/Plante': ['787', '73'],
        'Fée/Roche': ['719', '79'],

        'Feu': ['244', '394'],
        'Feu/Spectre': ['806', '546'],

        'Glace': ['493', '75'],
        'Glace/Psy': ['898', '570'],
        'Glace/Vol': ['144', '331'],

        'Insecte': ['493', '64'],

        'Normal': ['486', '56'],
        'Normal/Psy': ['648', '294'],

        'Plante': ['493', '73'],
        'Plante/Psy': ['251', '73'],
        'Plante/Vol': ['492', '63'],

        'Poison': ['493', '77'],
        'Poison/Roche': ['793', '567'],

        'Psy': ['150', '86'],
        'Psy/Spectre': ['792', '86'],
        'Psy/Tén': ['720', '548'],
        'Psy/Vol': ['249', '583'],

        'Roche': ['493', '79'],

        'Sol': ['383', '567'],
        'Sol/Vol': ['645', '287'],

        'Spec': ['493', '72'],

        'Tén': ['491', '66'],
        'Tén/Vol': ['717', '583'],

        'Vol': ['641', '283'],
    }
    
    for type, id in typeDict.items():
        url = f'https://pokemon.gameinfo.io/fr/pokemon/counters?id={id[0]}&form={id[1]}'
        response = session.get(url)
        typePokemons[type] = []
        if response.ok:
            soup = BeautifulSoup(response.content, 'lxml', parse_only=SoupStrainer('tbody'))
            pokemonList = soup.find('tbody').find_all('tr')
            
            x = 0
            try:
                while int(pokemonList[x].find_all('td')[3].text.replace('%', '')) >= 80:
                    pkmn = [pkmn.text.strip() for pkmn in pokemonList[x].find_all('td')]
                    pkmnDict = {'Pokemon': pkmn[0], 'Quick move': pkmn[1], 'Main move': pkmn[2]}
                    typePokemons[type].append(pkmnDict | {'Effective damage': pkmn[3]})
                    pkmnTuple = str(list(pkmnDict.values()))
                    try:
                        pokemonEffect[pkmnTuple]['nb'] += 1
                        pokemonEffect[pkmnTuple]['EffectTotal'] += int(pkmn[3].replace('%', ''))
                        pokemonEffect[pkmnTuple]['type'].append(type)
                    except: pokemonEffect[pkmnTuple] = {'nb': 1, 'EffectTotal': int(pkmn[3].replace('%', '')), 'type': [type]}
                    pokemonEffect[pkmnTuple]['EffectMoyen'] = int(pokemonEffect[pkmnTuple]['EffectTotal']/pokemonEffect[pkmnTuple]['nb'])
                    x+=1
            except: print(url, pokemonList)
            
    pokemonEffect = sorted([{'name': pkmn} | pkmnDict for pkmn, pkmnDict in pokemonEffect.items()], key=lambda k: k['nb'], reverse=True)
    sortPokemon(typePokemons, pokemonEffect)

def sortPokemon(typePokemons, pokemonEffect):
    print('Sort Pokemon')
    for i, pokemon in enumerate(pokemonEffect):
        name = eval(pokemon['name'])[0]
        for compare in pokemonEffect[i+1:]:
            evalCpr = eval(compare['name'])
            if name == evalCpr[0]:
                moreType = all(type in pokemon['type'] for type in compare['type'])
                if moreType:
                    pokemonEffect.remove(compare)
                    for type in compare['type']:
                        for pkmn in typePokemons[type]:
                            if [pkmn['Pokemon'], pkmn['Quick move'], pkmn['Main move']] == evalCpr:
                                typePokemons[type].remove(pkmn)
                                break
    x = -1
    while len(pokemonEffect[x]['type']) == 1:
        pokemon = pokemonEffect[x]
        evalPkmn = eval(pokemon['name'])
        type = pokemon['type'][0]

        if len(typePokemons[type]) > 6 and pokemon['EffectMoyen'] < 90:
            for pkmn in typePokemons[type][::-1]:
                if [pkmn['Pokemon'], pkmn['Quick move'], pkmn['Main move']] == evalPkmn:
                    typePokemons[type].remove(pkmn)
                    break
            del pokemonEffect[x]
        else: x-=1
    fusionName(typePokemons, pokemonEffect)
        
def fusionName(typePokemons, pokemonEffect):
    print('Fusion Name')
    for i, pkmn in enumerate(pokemonEffect):
        evalPkmn = eval(pkmn['name'])
        name = evalPkmn[0].split('(')[0].strip()
        evalPkmn[0] = evalPkmn[0].replace(name, '').replace('(', '').replace(')', '').strip()
        evalPkmn[0] = '""' if evalPkmn[0] == '' else evalPkmn[0]
        newName = ''
        for cmpr in pokemonEffect[i+1:]:
            evalCmpr = eval(cmpr['name'])
            nameCmpr = evalCmpr[0].split('(')[0].strip()
            evalCmpr[0] = evalCmpr[0].replace(nameCmpr, '').replace('(', '').replace(')', '').strip()
            evalCmpr[0] = '``' if evalCmpr[0] == '' else evalCmpr[0]
            if name == nameCmpr and evalPkmn[1:] == evalCmpr[1:] and pkmn['EffectTotal'] == cmpr['EffectTotal'] and pkmn['type'] == cmpr['type']:
                newName += f'{evalPkmn[0]}, {evalCmpr[0]}, '
                for type in cmpr['type']:
                    for pokemon in typePokemons[type]:
                        if [pokemon['Pokemon'], pokemon['Quick move'], pokemon['Main move']] == eval(cmpr['name']):
                            typePokemons[type].remove(pokemon)
                pokemonEffect.remove(cmpr)
        if newName != '':
            evalPkmn[0] = f"{name} ({', '.join(sorted(newName.split(', ')))})".replace('(, ','(')
            for type in pkmn['type']:
                for pokemon in typePokemons[type]:
                    if [pokemon['Pokemon'], pokemon['Quick move'], pokemon['Main move']] == eval(pkmn['name']):
                        pokemon['Pokemon'] = evalPkmn[0]
            pkmn['name'] = str(evalPkmn)
    visuel(typePokemons, pokemonEffect)
        
def visuel(typePokemons, pokemonEffect):
    print('Visuel')
    types = list(typePokemons)
    pokemons = [' | '.join(eval(pkmn['name'])[::-1]) for pkmn in pokemonEffect]
        
    l = []
    for i, compare in enumerate(pokemonEffect):
        l.append([])
        for type in types:
            if type in compare['type']: l[i].append(1)
            else:  l[i].append(0)

    harvest = np.array(l)
    fig, ax = plt.subplots(figsize=(29, 50))
        
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.imshow(harvest)
    plt.grid()
    
    ax.set_xticks(np.arange(len(types)), labels=types)
    ax.set_yticks(np.arange(len(pokemons)), labels=pokemons)
    plt.setp(ax.get_xticklabels(), rotation=40, ha='left', va='top', rotation_mode='anchor')

    fig.tight_layout()
    pdf = 'PokemonRaidInfo.pdf'
    plt.savefig(fname=pdf, format='pdf', orientation='portrait')
    webbrowser.open(f'file:///{Path(__file__).resolve().parent}/{pdf}')
    plt.savefig(fname='PokemonRaidInfo.png', format='png', orientation='portrait')
    os.remove(pdf)

scrap()
