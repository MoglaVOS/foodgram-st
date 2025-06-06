# Generated by Django 5.2.1 on 2025-05-22 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_favorite_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favorites', 'ordering': ('user__username', 'recipe__name'), 'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_carts', 'ordering': ('user__username', 'recipe__name'), 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
    ]
