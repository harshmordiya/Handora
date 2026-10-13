import os
import shutil
import random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Category, Product


CATEGORY_MAP = {
    'accessories': {
        'name': 'Accessories',
        'slug': 'accessories',
        'description': 'Handcrafted accessories to complement your style',
    },
    'Home Decor & Art': {
        'name': 'Home Decor & Art',
        'slug': 'home-decor-art',
        'description': 'Artistic pieces that transform your living spaces',
    },
    'Texttile & clothing': {
        'name': 'Textile & Clothing',
        'slug': 'textile-clothing',
        'description': 'Comfortable and stylish handwoven textiles',
    },
    'Wooden & Craft Items': {
        'name': 'Wooden & Craft',
        'slug': 'wooden-craft',
        'description': 'Exquisite wooden craftsmanship for your home',
    },
}

PRODUCT_NAMES = [
    'Elegant Handcrafted Piece', 'Artisan Premium Creation', 'Traditional Craftwork',
    'Authentic Handmade Item', 'Skilled Artisan Product', 'Heritage Craft Collection',
    'Rustic Woodland Design', 'Bohemian Style Piece', 'Ethnic Handicraft',
    'Mastercraft Signature Item', 'Cultural Heritage Art', 'Premium Artisan Made',
]


class Command(BaseCommand):
    help = 'Import existing product images into the database'

    def handle(self, *args, **options):
        pics_dir = settings.BASE_DIR / 'pics'
        media_dir = settings.BASE_DIR / 'media' / 'products'
        media_dir.mkdir(parents=True, exist_ok=True)

        for folder, info in CATEGORY_MAP.items():
            category, created = Category.objects.get_or_create(
                slug=info['slug'],
                defaults={
                    'name': info['name'],
                    'description': info['description'],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )

            img_dir = pics_dir / folder
            if not img_dir.exists():
                self.stdout.write(
                    self.style.WARNING(f'Image folder missing: {folder}')
                )
                continue

            first_image = None
            for f in sorted(img_dir.iterdir()):
                if not f.is_file() or f.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
                    continue
                if first_image is None:
                    first_image = f
                dest_name = f'{category.slug}_{f.name}'
                dest_path = media_dir / dest_name
                if not dest_path.exists():
                    shutil.copy2(f, dest_path)

                title = f'{random.choice(PRODUCT_NAMES)} #{f.stem}'
                price = round(random.uniform(199.0, 2499.0), 2)
                rel_image = f'products/{dest_name}'

                Product.objects.get_or_create(
                    slug=dest_path.stem,
                    defaults={
                        'category': category,
                        'name': title,
                        'description': 'A beautifully handcrafted item sourced directly from skilled artisans across India.',
                        'price': price,
                        'image': rel_image,
                        'is_featured': random.random() < 0.4,
                        'is_bestseller': random.random() < 0.3,
                    },
                )

            if first_image and not category.image:
                cat_dest = media_dir.parent / 'categories' / f'{category.slug}_{first_image.name}'
                cat_dest.parent.mkdir(parents=True, exist_ok=True)
                if not cat_dest.exists():
                    shutil.copy2(first_image, cat_dest)
                category.image = f'categories/{cat_dest.name}'
                category.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeding complete. Categories: {Category.objects.count()}, '
                f'Products: {Product.objects.count()}'
            )
        )
