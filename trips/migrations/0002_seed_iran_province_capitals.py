from django.db import migrations


IRAN_PROVINCE_CAPITALS = [
    ("تهران", "tehran"),
    ("کرج", "karaj"),
    ("اردبیل", "ardabil"),
    ("اصفهان", "isfahan"),
    ("اهواز", "ahvaz"),
    ("ایلام", "ilam"),
    ("بوشهر", "bushehr"),
    ("شهرکرد", "shahrekord"),
    ("بیرجند", "birjand"),
    ("بجنورد", "bojnord"),
    ("تبریز", "tabriz"),
    ("ارومیه", "urmia"),
    ("خرم‌آباد", "khorramabad"),
    ("گرگان", "gorgan"),
    ("رشت", "rasht"),
    ("زاهدان", "zahedan"),
    ("سنندج", "sanandaj"),
    ("سمنان", "semnan"),
    ("شیراز", "shiraz"),
    ("قزوین", "qazvin"),
    ("قم", "qom"),
    ("کرمان", "kerman"),
    ("کرمانشاه", "kermanshah"),
    ("یاسوج", "yasuj"),
    ("یزد", "yazd"),
    ("همدان", "hamedan"),
    ("اراک", "arak"),
    ("بندرعباس", "bandar-abbas"),
    ("مشهد", "mashhad"),
    ("زنجان", "zanjan"),
    ("ساری", "sari"),
]


def seed_cities(apps, schema_editor):
    City = apps.get_model("trips", "City")

    for name, slug in IRAN_PROVINCE_CAPITALS:
        City.objects.update_or_create(slug=slug, defaults={"name": name})


def remove_seeded_cities(apps, schema_editor):
    City = apps.get_model("trips", "City")
    slugs = [slug for _, slug in IRAN_PROVINCE_CAPITALS]

    City.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_cities, remove_seeded_cities),
    ]
