import requests
import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recettes.models import Recipe, Category, Ingredient
from django.core.files.base import ContentFile
import random
import os
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Ajoute 12 recettes internationales (Europe, Asie, Amérique)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Démarrage de l\'importation Cuisine du Monde ---'))

        # 1. CRÉATION DE NOUVEAUX AUTEURS INTERNATIONAUX
        nouveaux_auteurs = [
            ('chef_luigi', 'luigi@test.com'),
            ('julia_child', 'julia@test.com'),
            ('mike_grill', 'mike@test.com'),
            ('sara_bakes', 'sara@test.com')
        ]

        for username, email in nouveaux_auteurs:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, email, 'password123')

        tous_les_auteurs = list(User.objects.all())

        # 2. LISTE DES RECETTES (Non-Arabes)
        NEW_RECIPES = [
            {
                "title": "Bœuf Bourguignon Traditionnel",
                "category": "Français",
                "prep_time": 180,
                "rating": 4.9,
                "image_url": "https://images.pexels.com/photos/5737259/pexels-photo-5737259.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Le monument de la cuisine française. Des morceaux de bœuf mijotés longuement dans du vin rouge avec des carottes, des oignons grelots et des champignons.",
                "ingredients": ["Bœuf à braiser", "Vin rouge (Bourgogne)", "Lardons", "Champignons", "Carottes", "Oignons grelots", "Bouquet garni"],
                "instructions": "1. Faire revenir la viande et les lardons.\n2. Singer (ajouter la farine) et roussir.\n3. Mouiller avec le vin rouge et le bouillon.\n4. Ajouter les légumes et laisser mijoter 3h à feu doux.\n5. Servir avec des pommes de terre vapeur."
            },
            {
                "title": "Mac & Cheese Crémeux",
                "category": "Américain",
                "prep_time": 30,
                "rating": 4.5,
                "image_url": "https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Le confort food ultime. Des macaronis enrobés d'une sauce béchamel riche au cheddar et au gruyère, gratinés au four pour une croûte dorée.",
                "ingredients": ["Macaronis", "Cheddar", "Gruyère", "Lait", "Beurre", "Farine", "Chapelure", "Paprika"],
                "instructions": "1. Cuire les pâtes al dente.\n2. Préparer une béchamel (roux + lait).\n3. Faire fondre les fromages dans la sauce.\n4. Mélanger avec les pâtes et verser dans un plat.\n5. Saupoudrer de chapelure et gratiner 15 min."
            },
            {
                "title": "Risotto aux Champignons Sauvages",
                "category": "Italien",
                "prep_time": 40,
                "rating": 4.7,
                "image_url": "https://images.pexels.com/photos/5638527/pexels-photo-5638527.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Un plat élégant et onctueux. Du riz Arborio cuit lentement avec du bouillon, du vin blanc et un mélange de champignons forestiers.",
                "ingredients": ["Riz Arborio", "Champignons de Paris", "Cèpes séchés", "Vin blanc", "Bouillon de légumes", "Parmesan", "Beurre"],
                "instructions": "1. Faire revenir l'oignon et les champignons.\n2. Nacrer le riz.\n3. Déglacer au vin blanc.\n4. Ajouter le bouillon louche après louche en remuant.\n5. Monter au beurre et au parmesan (mantecare) hors du feu."
            },
            {
                "title": "Poulet Kung Pao",
                "category": "Chinois",
                "prep_time": 25,
                "rating": 4.6,
                "image_url": "https://images.pexels.com/photos/2673353/pexels-photo-2673353.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Un sauté classique du Sichuan. Du poulet tendre, des cacahuètes croquantes et des légumes dans une sauce soja-vinaigre légèrement pimentée.",
                "ingredients": ["Blancs de poulet", "Cacahuètes grillées", "Piments séchés", "Sauce soja", "Vinaigre de riz", "Poivron vert", "Ail", "Gingembre"],
                "instructions": "1. Couper le poulet en dés et mariner.\n2. Préparer la sauce (soja, vinaigre, sucre, fécule).\n3. Faire sauter les piments et le poivre de Sichuan.\n4. Ajouter le poulet puis les légumes.\n5. Verser la sauce et les cacahuètes en fin de cuisson."
            },
            {
                "title": "Moussaka Grecque",
                "category": "Grec",
                "prep_time": 90,
                "rating": 4.8,
                "image_url": "https://images.pexels.com/photos/5639931/pexels-photo-5639931.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Un gratin méditerranéen riche. Des couches d'aubergines frites, de pommes de terre et une sauce à la viande parfumée à la cannelle, nappées de béchamel.",
                "ingredients": ["Aubergines", "Pommes de terre", "Bœuf ou Agneau haché", "Oignon", "Tomates", "Cannelle", "Lait", "Oeufs"],
                "instructions": "1. Trancher et frire les aubergines et pommes de terre.\n2. Cuire la viande avec la tomate et la cannelle.\n3. Préparer une béchamel épaisse avec des œufs.\n4. Monter en couches dans un plat.\n5. Cuire 45 min au four."
            },
            {
                "title": "Fish and Chips",
                "category": "Britannique",
                "prep_time": 45,
                "rating": 4.5,
                "image_url": "https://images.pexels.com/photos/1565982/pexels-photo-1565982.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Le classique de la street-food anglaise. Du cabillaud frais dans une pâte à frire croustillante à la bière, servi avec des frites épaisses et des petits pois.",
                "ingredients": ["Cabillaud", "Pommes de terre", "Farine", "Bière blonde", "Levure", "Petits pois", "Vinaigre de malt"],
                "instructions": "1. Couper les pommes de terre en grosses frites et pré-cuire.\n2. Préparer la pâte avec farine et bière.\n3. Tremper le poisson et frire à 180°C.\n4. Frire les pommes de terre une seconde fois.\n5. Servir avec de la purée de pois (mushy peas)."
            },
            {
                "title": "Tiramisu Classique",
                "category": "Italien",
                "prep_time": 30,
                "rating": 5.0,
                "image_url": "https://images.pexels.com/photos/6097829/pexels-photo-6097829.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Le dessert italien par excellence. Des biscuits imbibés de café fort, alternés avec une crème au mascarpone aérienne et saupoudrés de cacao.",
                "ingredients": ["Mascarpone", "Oeufs", "Sucre", "Biscuits à la cuillère", "Café fort", "Amaretto (optionnel)", "Cacao amer"],
                "instructions": "1. Séparer les blancs des jaunes.\n2. Battre les jaunes avec le sucre et le mascarpone.\n3. Monter les blancs en neige et incorporer délicatement.\n4. Tremper les biscuits dans le café et tapisser le plat.\n5. Alterner crème et biscuits. Réfrigérer 4h minimum."
            },
            {
                "title": "Chili con Carne",
                "category": "Mexicain / Tex-Mex",
                "prep_time": 60,
                "rating": 4.6,
                "image_url": "https://images.pexels.com/photos/4062274/pexels-photo-4062274.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Un ragoût épicé et réconfortant. Viande de bœuf, haricots rouges, tomates et piments mijotés ensemble pour des saveurs profondes.",
                "ingredients": ["Bœuf haché", "Haricots rouges", "Tomates concassées", "Oignon", "Poivron rouge", "Cumin", "Piment en poudre"],
                "instructions": "1. Faire revenir oignon, ail et poivron.\n2. Ajouter la viande et dorer.\n3. Ajouter les épices, les tomates et un peu d'eau.\n4. Laisser mijoter 45 min.\n5. Ajouter les haricots rouges 10 min avant la fin."
            },
            {
                "title": "Pancakes aux Myrtilles",
                "category": "Petit-déjeuner",
                "prep_time": 20,
                "rating": 4.8,
                "image_url": "https://images.pexels.com/photos/376464/pexels-photo-376464.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Des pancakes américains épais et moelleux, remplis de myrtilles juteuses et servis avec une généreuse dose de sirop d'érable.",
                "ingredients": ["Farine", "Lait", "Oeuf", "Beurre fondu", "Levure chimique", "Sucre", "Myrtilles fraîches", "Sirop d'érable"],
                "instructions": "1. Mélanger les ingrédients secs.\n2. Mélanger les liquides et incorporer aux secs sans trop travailler.\n3. Incorporer délicatement les myrtilles.\n4. Cuire dans une poêle beurrée jusqu'à apparition de bulles.\n5. Retourner et dorer l'autre face."
            },
            {
                "title": "Salade Niçoise",
                "category": "Salade",
                "prep_time": 25,
                "rating": 4.4,
                "image_url": "https://images.pexels.com/photos/2863684/pexels-photo-2863684.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Le soleil de la Côte d'Azur. Une salade composée fraîche avec thon, œufs durs, anchois, olives de Nice et légumes croquants.",
                "ingredients": ["Thon à l'huile", "Oeufs durs", "Tomates", "Haricots verts", "Olives noires", "Anchois", "Radis", "Huile d'olive"],
                "instructions": "1. Cuire les œufs et les haricots verts (al dente).\n2. Couper les tomates en quartiers et les radis en rondelles.\n3. Frotter le saladier avec de l'ail.\n4. Disposer tous les ingrédients harmonieusement.\n5. Arroser d'huile d'olive et de basilic."
            },
            {
                "title": "Saumon Grillé aux Asperges",
                "category": "Sain / Poisson",
                "prep_time": 20,
                "rating": 4.7,
                "image_url": "https://images.pexels.com/photos/842142/pexels-photo-842142.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Un dîner léger et rapide. Pavé de saumon grillé à la peau croustillante, servi avec des asperges vertes et une sauce hollandaise rapide.",
                "ingredients": ["Pavé de saumon", "Asperges vertes", "Citron", "Beurre", "Aneth", "Huile d'olive", "Sel & Poivre"],
                "instructions": "1. Assaisonner le saumon.\n2. Cuire le saumon côté peau dans une poêle chaude.\n3. Faire sauter les asperges dans la même poêle 5 min.\n4. Arroser le poisson de jus de citron.\n5. Servir avec une noisette de beurre et de l'aneth."
            },
            {
                "title": "Gaufres de Liège",
                "category": "Dessert",
                "prep_time": 40,
                "rating": 4.9,
                "image_url": "https://images.pexels.com/photos/1191639/pexels-photo-1191639.jpeg?auto=compress&cs=tinysrgb&w=600",
                "description": "Les vraies gaufres belges, denses et briochées, avec des perles de sucre qui caramélisent à la cuisson. Irrésistible.",
                "ingredients": ["Farine", "Lait tiède", "Levure boulangère", "Beurre mou", "Oeufs", "Sucre perlé", "Vanille"],
                "instructions": "1. Faire une pâte levée avec farine, lait, levure et œufs.\n2. Laisser pousser 30 min.\n3. Incorporer le beurre mou et le sucre perlé.\n4. Laisser reposer encore 15 min.\n5. Cuire dans un gaufrier chaud jusqu'à caramélisation."
            }
        ]

        # 3. BOUCLE D'IMPORTATION
        count = 0
        for data in NEW_RECIPES:
            # Vérification anti-doublon
            if Recipe.objects.filter(title=data['title']).exists():
                self.stdout.write(f" - {data['title']} existe déjà. Ignorée.")
                continue

            try:
                cat, _ = Category.objects.get_or_create(name=data['category'])

                recipe = Recipe.objects.create(
                    title=data['title'],
                    description=data['description'],
                    instructions=data['instructions'],
                    preparation_time=data['prep_time'],
                    rating=data['rating'],
                    category=cat,
                    author=random.choice(tous_les_auteurs)
                )

                self.stdout.write(f"   Téléchargement image pour {data['title']}...")
                headers = {'User-Agent': 'Mozilla/5.0'}
                img_response = requests.get(data['image_url'], headers=headers, timeout=10)

                if img_response.status_code == 200:
                    file_name = f"recipe_world_{count}_{random.randint(1000, 9999)}.jpg"
                    recipe.image.save(file_name, ContentFile(img_response.content), save=True)

                for ing_name in data['ingredients']:
                    ing_obj, _ = Ingredient.objects.get_or_create(name=ing_name)
                    recipe.ingredients.add(ing_obj)

                self.stdout.write(self.style.SUCCESS(f"✅ {data['title']} ajoutée !"))
                count += 1
                time.sleep(0.5)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur sur {data['title']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"--- Terminé ! {count} nouvelles recettes internationales ajoutées. ---"))