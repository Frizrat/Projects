from django.shortcuts import render, redirect
import urllib.parse 

class Noeud:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class ABR:
    def __init__(self): self.racine = None

    def insere(self, noeud: object):
        if self.racine is None: self.racine = noeud
        else:
            n = self.racine
            while noeud.value['index'] != n.value['index']:
                if noeud.value['index'] < n.value['index']:
                    if n.left is None: n.left = noeud
                    else: n = n.left
                elif n.right is None: n.right = noeud
                else: n = n.right

    def insereTout(self, noeudsValue: list):
        for noeudValue in noeudsValue: self.insere(Noeud(noeudValue))

    def chercherParIndex(self, index):
        n = self.racine
        while n.value['index'] != index:
            if n.value['index'] > index:
                if n.left is None: return {'index':False}
                else: n = n.left
            elif n.right is None: return {'index':False}
            else: n = n.right
        return n.value

    def taille(self, noeud=None):
        noeud = self.racine if noeud is None else noeud
        taille = 1
        if noeud.left is not None: taille += self.taille(noeud.left)
        if noeud.right is not None: taille += self.taille(noeud.right)
        return taille

    def hauteur(self, noeud=None):
        noeud = self.racine if noeud is None else noeud
        left = self.hauteur(noeud.left) if noeud.left is not None else -1
        right = self.hauteur(noeud.right) if noeud.right is not None else -1
        return 1+max(left, right)

    def parcoursLargeur(self):
        largeur = []
        parcours = [self.racine]
        while parcours:
            noeud = parcours.pop()
            largeur.append(noeud.value)
            if noeud.left: parcours.insert(0, noeud.left)
            if noeud.right: parcours.insert(0, noeud.right)
        return largeur
    
    def parcoursPrefixe(self, noeud=None):
        noeud = self.racine if noeud is None else noeud
        prefixe = [noeud.value]
        if noeud.left is not None: prefixe += self.parcoursPrefixe(noeud.left)
        if noeud.right is not None: prefixe += self.parcoursPrefixe(noeud.right)
        return prefixe

    def parcoursInfixe(self, noeud=None):
        noeud = self.racine if noeud is None else noeud
        infixe = []
        if noeud.left is not None: infixe += self.parcoursInfixe(noeud.left)
        infixe.append(noeud.value)
        if noeud.right is not None: infixe += self.parcoursInfixe(noeud.right)
        return infixe

    def parcoursSuffixe(self, noeud=None):
        noeud = self.racine if noeud is None else noeud
        suffixe = []
        if noeud.left is not None: suffixe += self.parcoursSuffixe(noeud.left)
        if noeud.right is not None: suffixe += self.parcoursSuffixe(noeud.right)
        return suffixe + [noeud.value]

    def min(self):
        noeud = self.racine
        while noeud.left is not None: noeud = noeud.left
        return noeud.value['index']
    def max(self):
        noeud = self.racine
        while noeud.right is not None: noeud = noeud.right
        return noeud.value['index']

    def graphviz(self):
        lines = ['graph {', '}']
        parcours = [self.racine]
        while parcours:
            noeud = parcours.pop()
            phraseValue = f'"Index: {noeud.value["index"]}" --'
            phraseLeft = ''
            phraseRight = ''
            if noeud.left:
                parcours.insert(0, noeud.left)
                phraseLeft = f'\t{phraseValue} "Index: {noeud.left.value["index"]}"\n'
            if noeud.right:
                parcours.insert(0, noeud.right)
                phraseRight = f'\t{phraseValue} "Index: {noeud.right.value["index"]}"'
            lines.insert(-1, phraseLeft+phraseRight)
        return 'https://dreampuf.github.io/GraphvizOnline/#'+urllib.parse.quote('\n'.join(lines))


class Charac:
    def __init__(self, nom, image, css):
        self.nom = nom
        self.image = image
        self.css = css

class Text:
    def __init__(self, nom, text):
        self.nom = nom
        self.text = text

class Choix:
    def __init__(self, reponse, index):
        self.reponse = reponse
        self.index = index

class Question:
    def __init__(self, question, choix1: object, choix2: object):
        self.question = question
        self.choix = [choix1, choix2]


class Histoire:
    def __init__(self):
        self.abr = ABR()
        self.variables = {}
        self.index: int

    def ajoutPage(self, index: int, bg: str, characs: list, texts: list, question: object):
        self.abr.insere(Noeud({
            'index': index,
            'background': bg,
            'characters': characs,
            'texts': texts,
            'question': question
        }))

background = 'https://www.allamericanspa.co.uk/wp-content/uploads/2017/02/black-bg.jpg'

olive = Charac('Olive', 'https://static.wikia.nocookie.net/cluedo/images/d/db/05-24---Rev-Green.jpg/revision/latest?cb=20171017113209&path-prefix=fr', 'left: 50%')
pervenche = Charac('Pervenche', 'https://static.wikia.nocookie.net/cluedo/images/7/75/C8QfsioWsAAv_L5.jpg/revision/latest?cb=20171016164322&path-prefix=fr', 'transform: scaleX(-1); transform-origin: center; transform-box: fill-box; top: 75px; left: 15px')
rose = Charac('Rose', 'https://static.wikia.nocookie.net/cluedo/images/e/e1/05-21---Miss-Scarlett.jpg/revision/latest?cb=20171015125800&path-prefix=fr', 'transform: scaleX(-1); transform-origin: center; transform-box: fill-box; top: 75px; left: 320px')
leblanc = Charac('Leblanc', 'https://static.wikia.nocookie.net/cluedo/images/c/cb/05-15---Mrs-White.jpg/revision/latest?cb=20171017114401&path-prefix=fr', 'transform: scaleX(-1); transform-origin: center; transform-box: fill-box; top: 75px; left: 650px')
violet = Charac('Violet', 'https://static.wikia.nocookie.net/cluedo/images/0/06/05-26---Professor-Plum.jpg/revision/latest?cb=20171015130240&path-prefix=fr', 'transform: scaleX(-1); transform-origin: center; transform-box: fill-box; top: 75px; right: 400px')
moutarde = Charac('Moutarde', 'https://static.wikia.nocookie.net/cluedo/images/f/f7/05-22---Colonel-Mustard.jpg/revision/latest?cb=20171015125500&path-prefix=fr', 'top: 75px; right: 30px')

histoire = Histoire()
histoire.ajoutPage(
    79, background, [olive],
    [
        Text('Olive', "Monsieur Olive c'est toi ! Particulièrement charismatique, tu as la capacité de te faire des amis et de l'argent en claquant des doigts ! Beaucoup de personnes t'envient cette qualité : en effet, ce n'est pas donné à tout le monde de pouvoir jauger aussi rapidement le profit à retirer de n'importe quelle situation... "),
        Text('Olive', "Le revers de la médaille, c'est que tes spéculations sont incertaines, et tu te fies parfois un peu trop à ton jugement. Mais si c'est le jeu en affaires, sauras-tu être aussi brillant lors d'une enquête ?")
    ],
    Question('Voulez-vous passer à la présentation des autres convives ?', Choix('Oui', 78), Choix('Non', 79))
)
histoire.ajoutPage(
    78, background, [ pervenche, rose, leblanc, violet, moutarde ],
    [
        Text('Pervenche', 'Madame Pervenche a su se faire une place de politicienne dans ce milieu principalement masculin. Elle y est respectée... et crainte aussi !'),
        Text('Rose', "Mademoiselle Rose est sublime. C'est simple, elle pourrait être top modèle ! L'ennui, avec les jolies femmes, c'est qu'elles doivent se battre pour prouver qu'elles sont autre chose qu'un physique..."),
        Text('Leblanc', "Madame Leblanc est une éminente avocate. Prête à tout pour faire régner la justice, elle en fait trembler plus d'un..."),
        Text('Violet', "Monsieur Violet pourrait être qualifié de génie ! Inventeur de renommée internationale, il est doté d'une intelligence hors normes..."),
        Text('Moutarde', "Monsieur Moutarde est un expert en art martiaux. Mieux vaut ne pas le mettre en colère : sa force herculéenne est une légende dans le monde sportif !")
    ],
    Question('Voulez-vous lire l\'histoire ?', Choix('Oui', 77), Choix('Non', 78))
)
histoire.ajoutPage(
    77, background, [],
    [Text('', "En participant à cette aventure Cluedo, toi, Mr Olive tu devras élucider un meurtre. Pour cela, il te faudra faire preuve d'intelligence, de psychologie et de persipacité. Tu vas avoir pour lourde tâche de découvir l'identité du coupable, l'arme qu'il a utilisée, ainsi que son mobile.")],
    Question("Si tu ne crains pas le sang et les cadavres, continue...", Choix('Je ne crains rien', 33), Choix("Je suis hématophobe", 77))
)

olive.css = pervenche.css
histoire.ajoutPage(
    33, background, [rose, olive, leblanc, violet, moutarde],
    [
        Text('', "Vous venez de découvrir le corps sans vie du docteur..."),
        Text('Rose', "Oh mon Dieu !!!"),
        Text('Olive', "Allez vite prévenir les autres"),
        Text('', "Tous les convives vous rejoignent et reste muet face au drame."),
        Text('Olive', "Que faire ?"),
        Text('Leblanc', "Ne touchez à rien ! J'appelle la police."),
        Text('', "Elle sort immédiatement son téléphone et compose un numéro. En quelques phrases claires et concices, elle résuma la situtation et donne l'addresse."),
        Text('Leblanc', "Ils envoient une équipe dès que possible. Malheureusement, ils ont peu d'effectifs, et, apparement, le travail ne manque pas..."),
        Text('', "\"Comme si les tueurs en série avaient attendu l'été pour reprendre leurs activités\", te dis-tu."),
        Text('Violet', "Qu'est-ce qu'on fait ?"),
        Text('Olive', "On va attendre la police. Que voulez-vous faire d'autre ? Il s'agit d'un meurtre, les enquêteurs voudront tous nous entendre !"),
        Text('Moutarde', "Peut-être s'est-il suicidé ?"),
        Text('Olive', "Non ! S'il s'était suicidé avec un revolver, un poignard ou ce que vous voulez, l'arme serait visible. Il s'agit d'un meurtre et j'en suis certain ! Et l'assassin et forcément parmis nous !"),
        Text('', "Tu comptes bien découvir par toi même l'identité du coupable. Tout le monde est suspect puisque tout le monde à quitté le parc avant la macabre découverte."),
        Text('', "Mr Violet avait oublié ses cigarettes et Mr Moutarde son téléphone. Mlle Rose est allée se refaire une beauté ce qui semblait superflu tant elle rayonnait. Mme Leblanc à récupéré son gilet car elle souffre d'un léger début d'angine. Quant à Mme Pervenche, elle n'a pas donné d'explication, que chacun à traduit par un besoin soudain de se soulager."),
        Text('', "Toi aussi, tu t'es brièvement absenté pour porter une gamelle d'eau à Watson, ton fidèle épagneul resté dans la voiture au garage. Les autres aussi peuvent donc te considérer comme un suspect."),
        Text('', "Puisque Mme Pervenche est la première à être retournée dans la maison. Cet élément est de nature à l'innocenter."),
    ],
    Question("Choisis : ", Choix("Je me méfie de tout le monde et j'enquête seul", 11), Choix("Je suis convaincu que Mme Pervenche est innocente et j'enquête avec elle: Pas fait", 76))
)

histoire.ajoutPage(11, background, [olive], [Text('Olive', "30: En attente...")], Question("Choisis : ", Choix("60", 10), Choix("61: Pas fait", 18)))
histoire.ajoutPage(10, background, [olive], [Text('Olive', "60: En attente...")], Question("Choisis : ", Choix("15", 2), Choix("60", 10)))
histoire.ajoutPage(2, background, [olive], [Text('Olive', "15: En attente...")], Question("Choisis : ", Choix("41", 1), Choix("76", 7)))
histoire.ajoutPage(1, background, [olive], [Text('Olive', "41: Perdu...")], Question("Choisis : ", Choix("Recommencer", 79), Choix("Recommencer", 79)))
histoire.ajoutPage(7, background, [olive], [Text('Olive', "76: En attente...")], 
Question("Choisis : ", Choix("88", 6), Choix("55", 9)))
histoire.ajoutPage(6, background, [olive], [Text('Olive', "88: En attente...")], Question("Choisis : ", Choix("47", 5), Choix("88", 6)))
histoire.ajoutPage(5, background, [olive], [Text('Olive', "47: En attente...")], Question("Choisis : ", Choix("6", 4), Choix("47", 5)))
histoire.ajoutPage(4, background, [olive], [Text('Olive', "6: En attente...")], Question("Choisis : ", Choix("27", 3), Choix("6", 4)))
histoire.ajoutPage(3, background, [olive], [Text('Olive', "27: Gagné...")], Question("Choisis : ", Choix("Recommencer", 79), Choix("Recommencer", 79)))
histoire.ajoutPage(9, background, [olive], [Text('Olive', "55: En attente...")], Question("Choisis : ", Choix("40", 8), Choix("55", 9)))
histoire.ajoutPage(8, background, [olive], [Text('Olive', "40: Perdu...")], Question("Choisis : ", Choix("Recommencer", 79), Choix("Recommencer", 79)))

histoire.index = histoire.abr.racine.value['index']

def index(request):
    histoire.index = int(request.GET['index']) if 'index' in list(request.GET) else histoire.index
    arbre = histoire.abr.chercherParIndex(histoire.index) | {'taille': histoire.abr.taille(), 'hauteur': histoire.abr.hauteur()}
    return render(request, 'index.html', context=arbre)

def changeIndex(request):
    histoire.index = int(request.POST['index'])
    return redirect(f'/?index={histoire.index}')

def chercheIndex(request): return render(request, 'chercheIndex.html', context={'min': histoire.abr.min(), 'max': histoire.abr.max()})

def ajout(request): return render(request, 'ajout.html', context={'taille': histoire.abr.taille(), 'hauteur': histoire.abr.hauteur()})

def ajoutPOST(request):
    postDict = dict(request.POST)
    index = int(request.POST['index'])
    characters = []
    try:
        characters.extend(
            Charac(charac, postDict['image'][i], postDict['css'][i])
            for i, charac in enumerate(postDict['character'])
        )
    except: pass
    texts = [Text(postDict['text'][i], text) for i, text in enumerate(postDict['texte'])]
    choix1 = postDict['choix1']
    choix2 = postDict['choix2']
    histoire.ajoutPage(
        index, request.POST['background'], characters, texts,
        Question(request.POST['question'], Choix(choix1[0], int(choix1[1])), Choix(choix2[0], int(choix2[1])))
    )
    return redirect(f'/?index={index}')

def parcoursLargeur(request): return render(request, 'parcours.html', context={'parcours':histoire.abr.parcoursLargeur()})
def parcoursPrefixe(request): return render(request, 'parcours.html', context={'parcours':histoire.abr.parcoursPrefixe()})
def parcoursInfixe(request): return render(request, 'parcours.html', context={'parcours':histoire.abr.parcoursInfixe()})
def parcoursSuffixe(request): return render(request, 'parcours.html', context={'parcours':histoire.abr.parcoursSuffixe()})
def graphviz(request): return redirect(histoire.abr.graphviz())