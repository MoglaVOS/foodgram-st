import json
import os

from django.core.management.base import BaseCommand, CommandError

from api.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            raise CommandError(f'Файл не найден: {file_path}')

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise CommandError(f'Ошибка парсинга JSON: {e}')

        count = 0
        for item in data:
            name = item.get('name')
            unit = item.get('measurement_unit')
            if name and unit:
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=unit
                )
                count += 1
            else:
                self.stderr.write(f'Пропущен некорректный элемент: {item}')

        self.stdout.write(
            self.style.SUCCESS(f'Загружено ингредиентов: {count}')
        )
